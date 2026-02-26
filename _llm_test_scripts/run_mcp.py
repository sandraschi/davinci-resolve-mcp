#!/usr/bin/env python3
"""
Direct MCP server runner for DaVinci Resolve MCP.
This script can be used directly without package installation.
"""
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run MCP server
from davinci_resolve_mcp.main import mcp

if __name__ == "__main__":
    mcp()
