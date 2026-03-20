#!/usr/bin/env python3
"""
Run the DaVinci Resolve MCP server in stdio mode.
Used by Cursor/Glama configs that reference run_mcp.py with cwd and PYTHONPATH.
Usage: python run_mcp.py   (from repo root, or with PYTHONPATH=src)
"""
import sys
from pathlib import Path

# Ensure src is on path when run from repo root
_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

# Invoke MCP stdio entry point
from davinci_resolve_mcp.main import mcp

if __name__ == "__main__":
    mcp()
