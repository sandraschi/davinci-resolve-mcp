"""
DaVinci Resolve MCP Plugin Setup

This module provides the plugin setup function for FastMCP integration.
"""

import logging

from .server import app

logger = logging.getLogger(__name__)


def setup_plugin():
    """
    Setup function for FastMCP plugin system.

    This function is called by FastMCP to initialize the plugin.
    It ensures the server is properly configured for MCP protocol.
    """
    logger.info("Setting up DaVinci Resolve MCP plugin...")

    # The app is already configured in server.py
    # This function just needs to return the FastMCP app instance
    return app
