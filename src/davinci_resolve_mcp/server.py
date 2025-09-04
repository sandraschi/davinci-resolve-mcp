"""
DaVinci Resolve MCP - FastMCP Server

This module implements the FastMCP server for DaVinci Resolve integration.
"""
import asyncio
import logging
import sys
import signal
import os
import uvicorn
from pathlib import Path
from typing import Dict, Any, Optional, List, Type, Callable, Awaitable, Union

from fastmcp import FastMCP, FastMCPConfig
from fastmcp.tools import Tool
from pydantic import BaseModel, Field, HttpUrl, validator
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse

from .connection.manager import ResolveConnectionManager, ResolveConnectionPool
from .config import DaVinciResolveConfig, load_default
from .utils.error_handling import (
    handle_errors,
    register_error_handlers,
    ErrorResponse,
    SuccessResponse,
    create_tool,
    handle_resolve_error
)
from .utils.exceptions import (
    ResolveError,
    ResolveConnectionError,
    ResolveOperationError,
    ResolveAPIError,
    ResolveNotRunningError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('davinci_resolve_mcp.log')
    ]
)
logger = logging.getLogger(__name__)

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
    version="0.1.0",
    description="MCP server for DaVinci Resolve integration",
    config=FastMCPConfig(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info"),
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )
)

# Initialize application state
app.state = AppState()

# Register error handlers
app.add_exception_handler(ResolveError, handle_resolve_error)
app.add_exception_handler(HTTPException, lambda request, exc: JSONResponse(
    status_code=exc.status_code,
    content={"detail": exc.detail}
))
app.add_exception_handler(Exception, lambda request, exc: JSONResponse(
    status_code=500,
    content={"detail": "Internal server error"}
))

# Register signal handlers for graceful shutdown
def handle_shutdown(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal, cleaning up...")
    app.state.should_exit = True
    
    # Close all connections
    if hasattr(app.state, 'connection_pool') and app.state.connection_pool:
        app.state.connection_pool.close_all_connections()
    
    # Close connection manager
    if hasattr(app.state, 'connection_manager') and app.state.connection_manager:
        asyncio.create_task(app.state.connection_manager.close())
    
    logger.info("Cleanup complete. Shutting down...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

class ConnectionParams(BaseModel):
    """Parameters for connecting to DaVinci Resolve."""
    host: str = Field("localhost", description="Hostname or IP address of the DaVinci Resolve API")
    port: int = Field(8080, description="Port number of the DaVinci Resolve API")
    timeout: int = Field(30, description="Connection timeout in seconds")


@app.on_event("startup")
async def startup_event():
    """Initialize resources when the server starts."""
    try:
        logger.info("Starting DaVinci Resolve MCP server...")
        
        # Load configuration
        config_path = os.getenv("CONFIG_PATH")
        if config_path and os.path.exists(config_path):
            app.state.config = DaVinciResolveConfig.load_from_file(config_path)
        else:
            app.state.config = load_default()
        
        logger.info(f"Loaded configuration: {app.state.config.dict()}")
        
        # Set up environment
        app.state.config.setup_environment()
        
        # Initialize connection manager
        app.state.connection_manager = ResolveConnectionManager(app.state.config)
        
        # Initialize connection pool
        app.state.connection_pool = ResolveConnectionPool(
            config=app.state.config,
            max_connections=app.state.config.max_workers
        )
        
        # Register all tools
        register_tools()
        
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
    try:
        logger.info("Registering tools...")
        
        # Import tool modules
        from .tools.project_tools import register_tools as register_project_tools
        from .tools.media_tools import register_tools as register_media_tools
        from .tools.timeline_tools import register_tools as register_timeline_tools
        from .tools.render_tools import register_tools as register_render_tools
        from .tools.audio_tools import register_tools as register_audio_tools
        from .tools.color_tools import register_tools as register_color_tools
        
        # Register tools from modules
        register_project_tools(app)
        register_media_tools(app)
        register_timeline_tools(app)
        register_render_tools(app)
        register_audio_tools(app)
        register_color_tools(app)
        
        logger.info("All tools registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register tools: {str(e)}")
        raise
    
    logger.info("All tools registered successfully")


async def start_server(host: str = None, port: int = None, debug: bool = None):
    """
    Start the FastMCP server.
    
    Args:
        host: Host to bind the server to (default: from config or "0.0.0.0")
        port: Port to run the server on (default: from config or 8000)
        debug: Enable debug mode with verbose logging (default: from config or False)
    """
    try:
        # Get configuration from environment or use defaults
        host = host or os.getenv("HOST", "0.0.0.0")
        port = port or int(os.getenv("PORT", "8000"))
        debug = debug if debug is not None else os.getenv("DEBUG", "false").lower() == "true"
        
        logger.info(f"Starting DaVinci Resolve MCP server on {host}:{port} (debug: {debug})")
        
        # Configure uvicorn
        uvicorn_config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="debug" if debug else "info",
            reload=debug,
            workers=1  # We manage our own concurrency
        )
        
        # Create and run the server
        server = uvicorn.Server(uvicorn_config)
        
        # Register signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(server.shutdown()))
        
        # Run the server
        loop.run_until_complete(server.serve())
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        logger.exception("Server error:")
        raise


if __name__ == "__main__":
    import argparse
    import uvicorn
    import asyncio
    import signal
    import logging
    import os
    import sys
    
    parser = argparse.ArgumentParser(description="DaVinci Resolve MCP Server")
    parser.add_argument("--host", type=str, help="Host to bind to (overrides HOST env var)")
    parser.add_argument("--port", type=int, help="Port to listen on (overrides PORT env var)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (overrides DEBUG env var)")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Set environment variables from command line args
    if args.host:
        os.environ["HOST"] = args.host
    if args.port:
        os.environ["PORT"] = str(args.port)
    if args.debug:
        os.environ["DEBUG"] = "true"
    if args.config:
        os.environ["CONFIG_PATH"] = args.config
    
    try:
        start_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
