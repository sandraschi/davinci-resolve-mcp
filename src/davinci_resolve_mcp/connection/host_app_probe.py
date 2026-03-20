"""
host_app_probe.py - Reusable host application lifecycle probe.

Part of the sandraschi MCP fleet HOST_APP_LIFECYCLE standard v1.0.
Reference: mcp-central-docs/standards/HOST_APP_LIFECYCLE.md

Provides 4-state detection for any host application:
  NOT_INSTALLED -> INSTALLED_STOPPED -> RUNNING_UNREACHABLE -> READY
"""

import socket
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import psutil


class AppState(str, Enum):
    NOT_INSTALLED = "not_installed"
    INSTALLED_STOPPED = "installed_stopped"
    RUNNING_UNREACHABLE = "running_unreachable"
    READY = "ready"


APP_STATE_LABELS = {
    AppState.NOT_INSTALLED: "Not Installed",
    AppState.INSTALLED_STOPPED: "Installed, Not Running",
    AppState.RUNNING_UNREACHABLE: "Starting Up...",
    AppState.READY: "Ready",
}

APP_STATE_COLORS = {
    AppState.NOT_INSTALLED: "red",
    AppState.INSTALLED_STOPPED: "gray",
    AppState.RUNNING_UNREACHABLE: "amber",
    AppState.READY: "green",
}


@dataclass
class HostAppStatus:
    state: AppState
    app_name: str
    message: str = ""
    version: Optional[str] = None
    install_path: Optional[Path] = None
    pid: Optional[int] = None
    download_url: str = ""
    launch_cmd: Optional[list] = field(default=None)

    @property
    def can_launch(self) -> bool:
        return self.launch_cmd is not None and self.state == AppState.INSTALLED_STOPPED

    @property
    def label(self) -> str:
        return APP_STATE_LABELS.get(self.state, self.state.value)

    @property
    def color(self) -> str:
        return APP_STATE_COLORS.get(self.state, "gray")

    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "label": self.label,
            "color": self.color,
            "app_name": self.app_name,
            "message": self.message,
            "version": self.version,
            "install_path": str(self.install_path) if self.install_path else None,
            "pid": self.pid,
            "download_url": self.download_url,
            "can_launch": self.can_launch,
        }


def probe_host_app(
    app_name: str,
    process_names: list[str],
    install_paths: list,
    download_url: str = "",
    launch_cmd: Optional[list] = None,
    check_port: Optional[int] = None,
    http_health_url: Optional[str] = None,
) -> HostAppStatus:
    """
    Probe a host application and return its current lifecycle state.

    Args:
        app_name: Human-readable app name, e.g. "DaVinci Resolve"
        process_names: Process name fragments to match (case-insensitive)
        install_paths: List of known executable paths to check. First existing wins.
        download_url: Where to download the app if not installed.
        launch_cmd: Command list to launch the app.
        check_port: TCP port to test for API readiness (optional).
        http_health_url: HTTP URL to GET for API readiness check (optional).

    Returns:
        HostAppStatus with state, message, pid, install_path, etc.
    """
    # --- State 1: NOT_INSTALLED ---
    found_path = None
    for p in install_paths:
        candidate = Path(p)
        if candidate.exists():
            found_path = candidate
            break

    if not found_path:
        return HostAppStatus(
            state=AppState.NOT_INSTALLED,
            app_name=app_name,
            message=f"{app_name} installation not found on this system.",
            download_url=download_url,
        )

    # --- State 2: INSTALLED_STOPPED ---
    pid = None
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            proc_name = proc.info.get("name", "") or ""
            if any(pn.lower() in proc_name.lower() for pn in process_names):
                pid = proc.info["pid"]
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if pid is None:
        return HostAppStatus(
            state=AppState.INSTALLED_STOPPED,
            app_name=app_name,
            message=f"{app_name} is installed but not running.",
            install_path=found_path,
            download_url=download_url,
            launch_cmd=launch_cmd,
        )

    # --- State 3: RUNNING_UNREACHABLE (port check) ---
    if check_port is not None:
        try:
            s = socket.create_connection(("127.0.0.1", check_port), timeout=1.5)
            s.close()
        except OSError:
            return HostAppStatus(
                state=AppState.RUNNING_UNREACHABLE,
                app_name=app_name,
                message=(
                    f"{app_name} is running (PID {pid}) but API port {check_port} "
                    f"is not responding yet. Give it a moment."
                ),
                install_path=found_path,
                pid=pid,
            )

    # --- State 3: RUNNING_UNREACHABLE (HTTP health check) ---
    if http_health_url is not None:
        try:
            import httpx
            r = httpx.get(http_health_url, timeout=2.0)
            r.raise_for_status()
        except Exception as exc:
            return HostAppStatus(
                state=AppState.RUNNING_UNREACHABLE,
                app_name=app_name,
                message=(
                    f"{app_name} is running (PID {pid}) but HTTP API at "
                    f"{http_health_url} is not responding: {exc}"
                ),
                install_path=found_path,
                pid=pid,
            )

    # --- State 4: READY ---
    return HostAppStatus(
        state=AppState.READY,
        app_name=app_name,
        message=f"{app_name} is running and API is ready (PID {pid}).",
        install_path=found_path,
        pid=pid,
    )


def launch_app(status: HostAppStatus) -> tuple[bool, str]:
    """
    Launch the host application.

    Returns:
        (success: bool, message: str)
    """
    if status.state == AppState.READY:
        return True, f"{status.app_name} is already running."

    if status.state == AppState.NOT_INSTALLED:
        msg = f"{status.app_name} is not installed."
        if status.download_url:
            msg += f" Download from: {status.download_url}"
        return False, msg

    if status.state == AppState.RUNNING_UNREACHABLE:
        return False, (
            f"{status.app_name} is already starting up. "
            f"Wait a few seconds and retry get_host_app_status."
        )

    # INSTALLED_STOPPED
    if not status.launch_cmd:
        return False, f"No launch command configured for {status.app_name}."

    try:
        subprocess.Popen(
            status.launch_cmd,
            close_fds=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        return (
            True,
            f"Launch command sent for {status.app_name}. "
            f"Allow 10-20 seconds to start, then retry get_host_app_status.",
        )
    except Exception as exc:
        return False, f"Launch failed for {status.app_name}: {exc}"
