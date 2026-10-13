"""PyInstaller entrypoint for davinci-resolve-mcp HTTP sidecar.

Serves the full api_app (REST /api/v1 + dashboard banner), NOT a bare /mcp
mount: the Tauri WebView needs the REST API from this process.

Frozen layout (per spec datas): <MEIPASS>/davinci_resolve_mcp, so the bundle
root goes on sys.path. Dev layout: repo root + src/ (mirror the package).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
else:
    base = Path(__file__).resolve().parent
    if str(base / "src") not in sys.path:
        sys.path.insert(0, str(base / "src"))
if str(base) not in sys.path:
    sys.path.insert(0, str(base))

# Eager imports before any tool code (fleet Tauri checklist E):
# freeze stdlib C extensions + the mcp bootstrap so frozen startup matches dev.
import _datetime  # noqa: F401
import _strptime  # noqa: F401

import mcp.types  # noqa: F401

os.environ.setdefault("MCP_TRANSPORT", "http")


def _port() -> int:
    """Operator port first (Tauri spawn), then dev fallbacks."""
    for var in ("PORT", "RESOLVE_PORT", "MCP_PORT"):
        raw = os.environ.get(var)
        if raw:
            try:
                return int(raw)
            except ValueError:
                continue
    return 10843


if __name__ == "__main__":
    import uvicorn

    from davinci_resolve_mcp.server import api_app

    host = os.environ.get("RESOLVE_HOST", "127.0.0.1")
    log_level = os.environ.get("RESOLVE_LOG_LEVEL", "info")
    uvicorn.run(api_app, host=host, port=_port(), log_level=log_level)
