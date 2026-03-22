"""
DaVinci Resolve Environment Detection and Setup.

This module handles detection of DaVinci Resolve installations across different
operating systems and sets up the required environment for API access.
"""

import os
import platform
import subprocess
from pathlib import Path

import psutil


class ResolveEnvironment:
    """
    DaVinci Resolve environment detection and configuration.

    This class handles cross-platform detection of DaVinci Resolve
    installations and sets up the necessary environment variables
    for API access.
    """

    def __init__(self):
        """Initialize the environment detector."""
        self.system = platform.system().lower()
        self.architecture = platform.architecture()[0]

    def detect_resolve_installation(self) -> str | None:
        """
        Detect DaVinci Resolve installation path.

        Returns:
            Optional[str]: Path to DaVinci Resolve executable or None if not found
        """
        search_paths = self._get_search_paths()

        for path in search_paths:
            if path.exists():
                executable = self._find_resolve_executable(path)
                if executable:
                    return str(executable)

        return None

    def _get_search_paths(self) -> list[Path]:
        """Get platform-specific search paths for DaVinci Resolve."""

        if self.system == "windows":
            return [
                Path("C:/Program Files/Blackmagic Design/DaVinci Resolve"),
                Path("C:/Program Files (x86)/Blackmagic Design/DaVinci Resolve"),
                Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
                / "Blackmagic Design"
                / "DaVinci Resolve",
                Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)"))
                / "Blackmagic Design"
                / "DaVinci Resolve",
            ]

        elif self.system == "darwin":  # macOS
            return [
                Path("/Applications/DaVinci Resolve"),
                Path("/Applications/DaVinci Resolve Studio"),
                Path("~/Applications/DaVinci Resolve").expanduser(),
                Path("~/Applications/DaVinci Resolve Studio").expanduser(),
            ]

        elif self.system == "linux":
            return [
                Path("/opt/resolve"),
                Path("/usr/local/resolve"),
                Path("~/resolve").expanduser(),
                Path("/opt/blackmagic/DaVinci Resolve"),
            ]

        else:
            return []

    def _find_resolve_executable(self, base_path: Path) -> Path | None:
        """Find the DaVinci Resolve executable in the given path."""

        if self.system == "windows":
            executable_names = ["Resolve.exe", "DaVinciResolve.exe"]

        elif self.system == "darwin":  # macOS
            executable_names = [
                "DaVinci Resolve.app/Contents/MacOS/Resolve",
                "DaVinci Resolve Studio.app/Contents/MacOS/Resolve",
            ]

        elif self.system == "linux":
            executable_names = ["resolve", "DaVinciResolve"]

        else:
            return None

        for exe_name in executable_names:
            exe_path = base_path / exe_name
            if exe_path.exists():
                return exe_path

        return None

    def validate_resolve_version(self, resolve_path: str) -> str | None:
        """
        Validate DaVinci Resolve version and check API compatibility.

        Args:
            resolve_path: Path to DaVinci Resolve executable

        Returns:
            Optional[str]: Version string if valid, None if incompatible
        """
        try:
            # Try to get version information
            if self.system == "windows":
                # On Windows, we can check file properties
                return self._get_windows_version(resolve_path)
            elif self.system == "darwin":
                # On macOS, check Info.plist
                return self._get_macos_version(resolve_path)
            elif self.system == "linux":
                # On Linux, try command line version check
                return self._get_linux_version(resolve_path)

        except Exception:
            # If version detection fails, assume it's compatible
            return "Unknown (Assumed Compatible)"

        return None

    def _get_windows_version(self, resolve_path: str) -> str | None:
        """Get version from Windows executable properties."""
        try:
            import win32api

            info = win32api.GetFileVersionInfo(resolve_path, "\\")
            ms = info["FileVersionMS"]
            ls = info["FileVersionLS"]
            version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
            return version
        except ImportError:
            # win32api not available, try alternative method
            return "Unknown"
        except Exception:
            return None

    def _get_macos_version(self, resolve_path: str) -> str | None:
        """Get version from macOS app bundle."""
        try:
            import plistlib

            app_path = Path(resolve_path)
            if app_path.name == "Resolve":
                # Navigate to Info.plist
                plist_path = app_path.parent.parent / "Info.plist"
            else:
                plist_path = app_path / "Contents" / "Info.plist"

            if plist_path.exists():
                with open(plist_path, "rb") as f:
                    plist = plistlib.load(f)
                    return plist.get("CFBundleShortVersionString", "Unknown")
        except Exception:
            pass

        return "Unknown"

    def _get_linux_version(self, resolve_path: str) -> str | None:
        """Get version from Linux executable."""
        try:
            # Try running with --version flag
            result = subprocess.run(
                [resolve_path, "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        return "Unknown"

    def check_resolve_running(self) -> bool:
        """
        Check if DaVinci Resolve is currently running.

        Returns:
            bool: True if Resolve is running, False otherwise
        """
        resolve_processes = [
            "Resolve.exe",
            "DaVinciResolve.exe",  # Windows
            "Resolve",
            "DaVinci Resolve",  # macOS/Linux
        ]

        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                proc_name = proc.info.get("name", "").lower()
                for resolve_proc in resolve_processes:
                    if resolve_proc.lower() in proc_name:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False

    def setup_environment_variables(self) -> bool:
        """
        Set up environment variables for DaVinci Resolve API access.

        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            api_path, lib_path = self._get_api_paths()

            if api_path:
                os.environ["RESOLVE_SCRIPT_API"] = str(api_path)

                # Add modules path to PYTHONPATH
                modules_path = api_path / "Modules"
                if modules_path.exists():
                    current_pythonpath = os.environ.get("PYTHONPATH", "")
                    new_path = str(modules_path)

                    if new_path not in current_pythonpath:
                        if current_pythonpath:
                            separator = ";" if self.system == "windows" else ":"
                            os.environ["PYTHONPATH"] = f"{current_pythonpath}{separator}{new_path}"
                        else:
                            os.environ["PYTHONPATH"] = new_path

            if lib_path and lib_path.exists():
                os.environ["RESOLVE_SCRIPT_LIB"] = str(lib_path)

            return True

        except Exception:
            return False

    def _get_api_paths(self) -> tuple[Path | None, Path | None]:
        """Get platform-specific API paths."""

        if self.system == "windows":
            api_path = (
                Path(os.environ.get("PROGRAMDATA", "C:/ProgramData"))
                / "Blackmagic Design"
                / "DaVinci Resolve"
                / "Support"
                / "Developer"
                / "Scripting"
            )

            lib_path = Path("C:/Program Files/Blackmagic Design/DaVinci Resolve/fusionscript.dll")

        elif self.system == "darwin":  # macOS
            api_path = Path(
                "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
            )
            lib_path = Path(
                "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
            )

        elif self.system == "linux":
            api_path = Path("/opt/resolve/Developer/Scripting")
            lib_path = Path("/opt/resolve/libs/Fusion/fusionscript.so")

        else:
            return None, None

        return api_path, lib_path

    def validate_api_access(self) -> bool:
        """
        Validate that DaVinci Resolve API can be accessed.

        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            # First ensure environment is set up
            if not self.setup_environment_variables():
                return False

            # Try to import the DaVinci Resolve script module
            try:
                import DaVinciResolveScript as dvr_script

                # Try to connect to Resolve (this will fail if Resolve isn't running, but validates API)
                resolve = dvr_script.scriptapp("Resolve")
                if resolve:
                    return True

            except ImportError:
                # DaVinciResolveScript module not available
                return False
            except Exception:
                # Connection failed (Resolve not running), but API is available
                return True

        except Exception:
            return False

        return False

    def get_environment_status(self) -> dict[str, any]:
        """
        Get comprehensive environment status.

        Returns:
            Dict[str, any]: Environment status information
        """
        status = {
            "system": self.system,
            "architecture": self.architecture,
            "resolve_installation": None,
            "resolve_running": False,
            "api_available": False,
            "environment_variables": {},
            "api_paths": {},
        }

        # Check installation
        resolve_path = self.detect_resolve_installation()
        if resolve_path:
            status["resolve_installation"] = resolve_path
            status["resolve_version"] = self.validate_resolve_version(resolve_path)

        # Check if running
        status["resolve_running"] = self.check_resolve_running()

        # Check API access
        status["api_available"] = self.validate_api_access()

        # Environment variables
        status["environment_variables"] = {
            "RESOLVE_SCRIPT_API": os.environ.get("RESOLVE_SCRIPT_API"),
            "RESOLVE_SCRIPT_LIB": os.environ.get("RESOLVE_SCRIPT_LIB"),
            "PYTHONPATH": os.environ.get("PYTHONPATH"),
        }

        # API paths
        api_path, lib_path = self._get_api_paths()
        status["api_paths"] = {
            "script_api_exists": api_path.exists() if api_path else False,
            "script_lib_exists": lib_path.exists() if lib_path else False,
            "script_api_path": str(api_path) if api_path else None,
            "script_lib_path": str(lib_path) if lib_path else None,
        }

        return status

    def launch_resolve_headless(self, resolve_path: str) -> bool:
        """
        Launch DaVinci Resolve in headless mode.

        Args:
            resolve_path: Path to DaVinci Resolve executable

        Returns:
            bool: True if launch successful, False otherwise
        """
        try:
            if self.check_resolve_running():
                return True  # Already running

            # Launch with -nogui flag for headless mode
            subprocess.Popen(
                [resolve_path, "-nogui"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )

            # Give Resolve time to start
            import time

            time.sleep(5)

            return self.check_resolve_running()

        except Exception:
            return False

    def create_environment_setup_script(self, output_path: str) -> bool:
        """
        Create a script to set up environment variables.

        Args:
            output_path: Path to save the setup script

        Returns:
            bool: True if script created successfully
        """
        try:
            api_path, lib_path = self._get_api_paths()

            if self.system == "windows":
                script_content = f"""@echo off
REM DaVinci Resolve MCP Environment Setup Script
echo Setting up DaVinci Resolve API environment...

set RESOLVE_SCRIPT_API={api_path}
set RESOLVE_SCRIPT_LIB={lib_path}
set PYTHONPATH=%PYTHONPATH%;{api_path}\\Modules

echo Environment variables set:
echo RESOLVE_SCRIPT_API=%RESOLVE_SCRIPT_API%
echo RESOLVE_SCRIPT_LIB=%RESOLVE_SCRIPT_LIB%
echo PYTHONPATH=%PYTHONPATH%
echo.
echo DaVinci Resolve API environment is ready!
pause
"""
                script_path = Path(output_path) / "setup_resolve_env.bat"

            else:  # macOS/Linux
                script_content = f"""#!/bin/bash
# DaVinci Resolve MCP Environment Setup Script
echo "Setting up DaVinci Resolve API environment..."

export RESOLVE_SCRIPT_API="{api_path}"
export RESOLVE_SCRIPT_LIB="{lib_path}"
export PYTHONPATH="$PYTHONPATH:{api_path}/Modules"

echo "Environment variables set:"
echo "RESOLVE_SCRIPT_API=$RESOLVE_SCRIPT_API"
echo "RESOLVE_SCRIPT_LIB=$RESOLVE_SCRIPT_LIB"
echo "PYTHONPATH=$PYTHONPATH"
echo ""
echo "DaVinci Resolve API environment is ready!"
"""
                script_path = Path(output_path) / "setup_resolve_env.sh"

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            if self.system != "windows":
                # Make script executable on Unix-like systems
                os.chmod(script_path, 0o755)

            return True

        except Exception:
            return False
