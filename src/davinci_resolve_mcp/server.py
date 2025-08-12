"""
DaVinci Resolve MCP - FastMCP Server

This module implements the FastMCP server for DaVinci Resolve integration.
"""
import asyncio
import logging
import sys
import signal
from typing import Dict, Any, Optional, List, Type, Callable, Awaitable

from fastmcp import FastMCP
from fastmcp.tools import Tool
from pydantic import BaseModel, Field

from .connection.manager import ResolveConnectionManager, ResolveConnectionPool
from .config import DaVinciResolveConfig, load_default
from .utils.error_handling import (
    handle_errors,
    register_error_handlers,
    ErrorResponse,
    SuccessResponse,
    create_tool
)
from .utils.error_handling import ResolveError
from .utils.exceptions import (
    ResolveConnectionError,
    ResolveOperationError,
    ResolveAPIError,
    ResolveNotRunningError
)

logger = logging.getLogger(__name__)

# Global application state
class AppState:
    """Global application state."""
    def __init__(self):
        self.config: Optional[DaVinciResolveConfig] = None
        self.connection_manager: Optional[ResolveConnectionManager] = None
        self.connection_pool: Optional[ResolveConnectionPool] = None
        self.should_exit = False

# Initialize the FastMCP app
app = FastMCP(
    name="DaVinci Resolve MCP",
    version="0.1.0"
)

# Initialize application state
app.state = AppState()

# Register signal handlers for graceful shutdown
def handle_shutdown(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal, cleaning up...")
    app.state.should_exit = True
    if app.state.connection_pool:
        app.state.connection_pool.close_all_connections()
    if app.state.connection_manager:
        asyncio.create_task(app.state.connection_manager.close())
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# Error handling is now done via the @handle_errors decorator on individual route handlers

class ConnectionParams(BaseModel):
    """Parameters for connecting to DaVinci Resolve."""
    host: str = Field("localhost", description="Hostname or IP address of the DaVinci Resolve API")
    port: int = Field(8080, description="Port number of the DaVinci Resolve API")
    timeout: int = Field(30, description="Connection timeout in seconds")


@app.on_event("startup")
async def startup_event():
    """Initialize resources when the server starts."""
    try:
        # Load configuration
        app.state.config = load_default_config()
        
        # Initialize connection manager
        app.state.connection_manager = ResolveConnectionManager(app.state.config)
        
        # Initialize connection pool
        app.state.connection_pool = ResolveConnectionPool(
            app.state.config,
            max_connections=app.state.config.max_workers
        )
        
        # Set up environment
        app.state.config.setup_environment()
        
        logger.info("DaVinci Resolve MCP server initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {str(e)}")
        logger.exception("Initialization error:")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when the server shuts down."""
    try:
        if app.state.connection_pool:
            app.state.connection_pool.close_all_connections()
            
        if app.state.connection_manager:
            await app.state.connection_manager.close()
            
        logger.info("DaVinci Resolve MCP server shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        logger.exception("Shutdown error:")


@create_tool
def get_resolve_info() -> Dict[str, Any]:
    """
    Get information about the connected DaVinci Resolve instance.
    
    Returns:
        Dict containing DaVinci Resolve version and status information.
        
    Example:
        {
            "status": "success",
            "data": {
                "version": "18.5.0",
                "api_version": "1.0",
                "is_console": false,
                "is_rendering": false,
                "project_name": "My Project"
            }
        }
    """
    if not app.state.connection_manager:
        raise ResolveConnectionError("Connection manager not initialized")
    
    resolve = app.state.connection_manager.get_connection()
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    
    return {
        "version": resolve.GetVersionString(),
        "api_version": resolve.GetApiVersion() if hasattr(resolve, 'GetApiVersion') else "N/A",
        "is_console": resolve.IsConsole() if hasattr(resolve, 'IsConsole') else False,
        "is_rendering": resolve.IsRenderingInProgress() if hasattr(resolve, 'IsRenderingInProgress') else False,
        "project_name": current_project.GetName() if current_project else None
    }


@create_tool
def list_projects() -> Dict[str, Any]:
    """
    List all available projects in DaVinci Resolve.
    
    Returns:
        Dict containing a list of project names and the current project.
        
    Example:
        {
            "status": "success",
            "data": {
                "current_project": "My Project",
                "projects": ["Project 1", "My Project", "Test Project"]
            }
        }
    """
    if not app.state.connection_manager:
        raise ResolveConnectionError("Connection manager not initialized")
    
    resolve = app.state.connection_manager.get_connection()
    project_manager = resolve.GetProjectManager()
    
    current_project = project_manager.GetCurrentProject()
    current_project_name = current_project.GetName() if current_project else None
    
    projects = project_manager.GetProjectListInCurrentFolder() or []
    
    return {
        "current_project": current_project_name,
        "projects": projects
    }


def register_tools():
    """Register all tools with the FastMCP app."""
    # Import tool modules
    from .tools.project_tools import register_tools as register_project_tools
    from .tools.media_tools import register_tools as register_media_tools
    
    # Register tools from modules
    register_project_tools(app)
    register_media_tools(app)
    
    logger.info("All tools registered successfully")


async def start_server(host: str = "127.0.0.1", port: int = 8000, debug: bool = False):
    """
    Start the FastMCP server.
    
    Args:
        host: Host to bind the server to
        port: Port to run the server on
        debug: Enable debug mode with verbose logging
    """
    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('davinci_resolve_mcp.log')
        ]
    )
    
    # Suppress noisy loggers
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Register all tools
    register_tools()
    
    # Create and start the server
    server = MCPServer(app)
    
    logger.info(f"Starting DaVinci Resolve MCP server on {host}:{port}")
    logger.info(f"Debug mode: {'enabled' if debug else 'disabled'}")
    
    try:
        await server.serve(host=host, port=port)
    except asyncio.CancelledError:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        logger.exception("Server error details:")
        raise
    finally:
        # Ensure clean shutdown
        await shutdown_event()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="DaVinci Resolve MCP Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(start_server(host=args.host, port=args.port, debug=args.debug))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
