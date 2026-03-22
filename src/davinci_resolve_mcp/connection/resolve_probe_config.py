"""
resolve_probe_config.py - DaVinci Resolve host app probe configuration.

Used by get_host_app_status and launch_host_app MCP tools.
Implements the HOST_APP_LIFECYCLE standard v1.0.
"""

import os
from pathlib import Path

# Build list of candidate install paths, including env-var-based locations
_prog_files = os.environ.get("PROGRAMFILES", "C:/Program Files")
_prog_files_x86 = os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")

RESOLVE_PROBE_CONFIG = dict(
    app_name="DaVinci Resolve",
    process_names=["Resolve"],  # matches "Resolve.exe" on Windows
    install_paths=[
        Path(f"{_prog_files}/Blackmagic Design/DaVinci Resolve/Resolve.exe"),
        Path(f"{_prog_files_x86}/Blackmagic Design/DaVinci Resolve/Resolve.exe"),
        Path("C:/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe"),
        Path("C:/Program Files/DaVinci Resolve/Resolve.exe"),
        # macOS
        Path("/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/MacOS/Resolve"),
        Path(
            "/Applications/DaVinci Resolve Studio/DaVinci Resolve Studio.app/Contents/MacOS/Resolve"
        ),
        # Linux
        Path("/opt/resolve/bin/resolve"),
        Path("/usr/local/resolve/bin/resolve"),
    ],
    # Resolve scripting API listens on this port when running with scripting enabled
    check_port=9990,
    download_url="https://www.blackmagicdesign.com/products/davinciresolve",
    launch_cmd=[str(Path(f"{_prog_files}/Blackmagic Design/DaVinci Resolve/Resolve.exe"))],
)
