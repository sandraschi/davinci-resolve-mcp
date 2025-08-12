"""
DaVinci Resolve MCP Server - Professional Video Editing through Model Context Protocol

This package provides a FastMCP server that enables AI agents like Claude
to perform professional video editing, color grading, and post-production
operations using DaVinci Resolve.

Key Features:
- Cross-platform DaVinci Resolve integration (Windows, macOS, Linux)
- Professional video editing tools via MCP protocol
- Timeline creation and editing
- Media pool management
- Color grading and correction
- Audio processing
- Rendering and export
- Batch processing capabilities
- Error handling and recovery

Author: Sandra Schieder
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Sandra Schieder"
__email__ = "sandra@sandraschi.dev"

from .server import DaVinciResolveMcpServer

__all__ = ["DaVinciResolveMcpServer"]
