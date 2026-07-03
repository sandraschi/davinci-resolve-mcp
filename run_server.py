"""PyInstaller entrypoint for davinci-resolve-mcp HTTP sidecar."""

from __future__ import annotations

import _strptime  # noqa: F401 -- PyInstaller must bundle this eagerly
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base = Path(sys._MEIPASS)
else:
    base = Path(__file__).resolve().parent
if str(base / "src") not in sys.path:
    sys.path.insert(0, str(base / "src"))

os.environ.setdefault("MCP_TRANSPORT", "http")

if __name__ == "__main__":
    from fastapi import FastAPI
    from davinci_resolve_mcp.server import app as _mcp

    app = FastAPI(title="davinci-resolve-mcp")
    app.mount("/mcp", _mcp.http_app())

    host = os.environ.get("RESOLVE_HOST", "127.0.0.1")
    port = int(os.environ.get("RESOLVE_PORT", os.environ.get("MCP_PORT", "10843")))
    log_level = os.environ.get("RESOLVE_LOG_LEVEL", "info")
    uvicorn.run(app, host=host, port=port, log_level=log_level)

