#!/usr/bin/env python3
"""
DaVinci Resolve MCP - CLI Entry Point

This module provides the command-line interface for the DaVinci Resolve MCP server.
"""
import asyncio
import logging
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from .server import start_server, app, initialize_server
from .connection.environment import verify_resolve_environment
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("davinci_resolve_mcp")

# Create Typer app
app = typer.Typer(
    name="davinci-resolve-mcp",
    help="DaVinci Resolve MCP Server - Control DaVinci Resolve through AI agents",
    add_completion=False
)

# Global console instance for consistent output
console = Console()


def version_callback(value: bool):
    """Display version and exit."""
    if value:
        from importlib.metadata import version
        v = version("davinci-resolve-mcp")
        console.print(f"DaVinci Resolve MCP v{v}")
        raise typer.Exit()


@app.command()
def start(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the server on"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", 
        help="Show version and exit",
        callback=version_callback,
        is_eager=True
    )
):
    """Start the DaVinci Resolve MCP server."""
    # Set log level based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(log_level)
    
    # Verify DaVinci Resolve environment
    try:
        console.print("🔍 Verifying DaVinci Resolve environment...")
        env_info = verify_resolve_environment()
        console.print(f"✅ Found DaVinci Resolve {env_info.get('version', 'unknown')} at {env_info.get('install_path', 'unknown')}")
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        if debug:
            logger.exception("Detailed error:")
        raise typer.Exit(1)
    
    # Start the server
    console.print(f"🚀 Starting DaVinci Resolve MCP server on {host}:{port}")
    try:
        asyncio.run(start_server(host=host, port=port))
    except KeyboardInterrupt:
        console.print("\n👋 Shutting down server...")
    except Exception as e:
        console.print(f"❌ Server error: {str(e)}", style="red")
        if debug:
            logger.exception("Detailed error:")
        raise typer.Exit(1)


@app.command()
def mcp():
    """Run the MCP server in stdio mode for Claude Desktop."""
    # Set up logging for MCP mode (less verbose)
    logging.basicConfig(
        level=logging.WARNING,  # Only show warnings and errors in MCP mode
        format="%(levelname)s: %(message)s"
    )

    logger.info("Starting DaVinci Resolve MCP server in stdio mode...")

    # Initialize the server
    try:
        initialize_server()
    except Exception as e:
        logger.error(f"Failed to initialize server: {str(e)}")
        sys.exit(1)

    # Run the MCP server in stdio mode
    try:
        # Import here to avoid circular imports
        import asyncio
        from .server import app as mcp_app

        # Run the FastMCP app in stdio mode
        asyncio.run(mcp_app.run())
    except KeyboardInterrupt:
        logger.info("MCP server stopped")
    except Exception as e:
        logger.error(f"MCP server error: {str(e)}")
        sys.exit(1)


@app.command()
def check():
    """Check the DaVinci Resolve environment and connection."""
    console.print("🔍 Checking DaVinci Resolve environment...")
    try:
        env_info = verify_resolve_environment()
        console.print("✅ [green]DaVinci Resolve Environment:[/green]")
        console.print(f"   • Version: {env_info.get('version', 'Unknown')}")
        console.print(f"   • Install Path: {env_info.get('install_path', 'Unknown')}")
        console.print(f"   • Python Version: {env_info.get('python_version', 'Unknown')}")
        console.print(f"   • API Access: {'✅ Available' if env_info.get('api_available', False) else '❌ Not Available'}")
        
        if not env_info.get('api_available', False):
            console.print("\n❌ [yellow]Warning:[/yellow] Could not access DaVinci Resolve API.")
            console.print("   Make sure DaVinci Resolve is installed and the Python module is in your PYTHONPATH.")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ [red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
