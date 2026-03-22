"""
DaVinci Resolve MCP - Professional Video Editing through Model Context Protocol

This package provides a FastMCP server and Python API that enables AI agents like Claude
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
- Built-in help system with multiple user levels

Getting Started:
    >>> from davinci_resolve_mcp import help, get_help
    >>> help()  # Show general help
    >>> help("Project")  # Get help on a specific topic
    >>> get_help("create_project", level="beginner")  # Get help at a specific level

Author: Sandra Schieder
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Sandra Schieder"
__email__ = "sandra@sandraschi.dev"

from .tools import UserLevel, get_help

# Import the help system
from .tools import help as _help_tool

# Re-export commonly used components for easier access
__all__ = [
    "help",  # Help function
    "get_help",  # Help function
    "UserLevel",  # User level enum
]


# Create a more user-friendly help function that delegates to the help tool
def help(topic: str = None, level: str | UserLevel = None) -> str:
    """
    Display help information for the DaVinci Resolve MCP package.

    Args:
        topic: The topic to get help on. If None, shows general help.
        level: The user level for the help content ('beginner', 'intermediate', 'advanced', or 'developer').

    Returns:
        str: The formatted help text.
    """
    if level is not None:
        return get_help(topic, level)
    return _help_tool(topic) if topic is not None else _help_tool()
