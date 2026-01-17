"""
DaVinci Resolve MCP - FastMCP 2.14.3 Server

This module implements the FastMCP server for DaVinci Resolve integration.

Status: Production Ready - Actively maintained, SOTA features
"""
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

import structlog
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .connection.manager import ResolveConnectionManager, ResolveConnectionPool
from .config import DaVinciResolveConfig, load_default
from .utils.error_handling import (
    create_tool
)
from .utils.exceptions import (
    ResolveConnectionError
)

# Configure structured logging (JSON to stderr only)
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global application state
class AppState:
    """Global application state."""
    def __init__(self):
        self.config: Optional[DaVinciResolveConfig] = None
        self.connection_manager: Optional[ResolveConnectionManager] = None
        self.connection_pool: Optional[ResolveConnectionPool] = None
        self.should_exit = False

# Server lifespan for startup/shutdown lifecycle
@asynccontextmanager
async def server_lifespan(app: FastMCP):
    """Server lifespan context manager for FastMCP 2.14.3+."""
    # Startup
    logger.info("Starting DaVinci Resolve MCP Server", version="0.1.0", fastmcp_version="2.14.3")
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down DaVinci Resolve MCP Server")

# Initialize the FastMCP 2.14.3 app with conversational features
app = FastMCP(
    "DaVinci Resolve MCP",
    instructions="""You are DaVinci Resolve MCP, a comprehensive FastMCP 2.14.3 server for professional video editing automation using DaVinci Resolve.

FASTMCP 2.14.3 FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling capabilities for agentic workflows and complex video editing operations
- Portmanteau design preventing tool explosion while maintaining full functionality

CORE CAPABILITIES:
- Project Management: Create, open, list projects with professional settings
- Media Operations: Import media, organize folders, search and manage media pool
- Timeline Editing: Create timelines, add clips, perform cuts and edits
- Color Grading: Apply LUTs, adjust primary/secondary corrections, create color nodes
- Rendering: Queue render jobs, batch render, monitor progress, export timelines
- Audio Processing: Adjust levels, apply effects, sync audio, export audio tracks
- System Utilities: Get system info, health checks, help system

CONVERSATIONAL FEATURES:
- Tools return natural language responses alongside structured data
- Sampling allows autonomous orchestration of complex editing workflows
- Agentic capabilities for intelligent video production pipelines

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean and 'message' for conversational responses
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields and natural language summaries

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.

USAGE PATTERNS:
1. Project Setup: Use resolve_project(operation="create") to create projects, resolve_project(operation="open") to open existing ones
2. Media Management: Use resolve_media(operation="import") to import files, resolve_media(operation="list") to browse media pool
3. Timeline Editing: Use resolve_timeline(operation="create") to create timelines, resolve_timeline(operation="add_clip") to add clips
4. Color Grading: Use resolve_color(operation="apply_lut") for LUTs, resolve_color(operation="adjust_primary") for corrections
5. Rendering: Use resolve_render(operation="timeline") to queue renders, resolve_render(operation="job_status") to check progress
6. Audio: Use resolve_audio(operation="adjust_levels") for mixing, resolve_audio(operation="add_effect") for processing

ERROR HANDLING:
- Connection errors provide DaVinci Resolve startup instructions
- Operation errors specify what failed and how to fix it
- API errors include troubleshooting steps
- Direct communication: Clear, actionable feedback

TOOL MODES:
- Portmanteau mode (default): 7 consolidated tools with operation parameters
- Individual mode: 26 individual tools (set RESOLVE_TOOL_MODE=individual)

PROFESSIONAL WORKFLOWS:
- Supports 4K, 8K, HDR workflows
- Professional color spaces (Rec.709, Rec.2020, P3)
- Frame-accurate editing and color grading
- Batch processing for efficiency
- Multi-format rendering and export""",
    lifespan=server_lifespan
)

# Initialize application state
app.state = AppState()
Status: Beta - Actively developed, API may change
"""
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

import structlog
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .connection.manager import ResolveConnectionManager, ResolveConnectionPool
from .config import DaVinciResolveConfig, load_default
from .utils.error_handling import (
    create_tool
)
from .utils.exceptions import (
    ResolveConnectionError
)

# Configure structured logging (JSON to stderr only)
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global application state
class AppState:
    """Global application state."""
    def __init__(self):
        self.config: Optional[DaVinciResolveConfig] = None
        self.connection_manager: Optional[ResolveConnectionManager] = None
        self.connection_pool: Optional[ResolveConnectionPool] = None
        self.should_exit = False

# Server lifespan for startup/shutdown lifecycle
@asynccontextmanager
async def server_lifespan(app: FastMCP):
    """Server lifespan context manager for FastMCP 2.14.1+."""
    # Startup
    logger.info("Starting DaVinci Resolve MCP Server", version="0.1.0", fastmcp_version="2.14.1")
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down DaVinci Resolve MCP Server")

# Initialize the FastMCP 2.14.3 app with conversational features
app = FastMCP(
    "DaVinci Resolve MCP",
    instructions="""You are DaVinci Resolve MCP, a comprehensive FastMCP 2.14.3 server for professional video editing automation using DaVinci Resolve.

FASTMCP 2.14.3 FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling capabilities for agentic workflows and complex video editing operations
- Portmanteau design preventing tool explosion while maintaining full functionality

CORE CAPABILITIES:
- Project Management: Create, open, list projects with professional settings
- Media Operations: Import media, organize folders, search and manage media pool
- Timeline Editing: Create timelines, add clips, perform cuts and edits
- Color Grading: Apply LUTs, adjust color wheels, create color nodes, copy grades
- Rendering: Queue render jobs, batch render, monitor progress, export timelines
- Audio Processing: Adjust levels, apply effects, sync audio, export audio tracks
- System Utilities: Get system info, health checks, help system

CONVERSATIONAL FEATURES:
- Tools return natural language responses alongside structured data
- Sampling allows autonomous orchestration of complex editing workflows
- Agentic capabilities for intelligent video production pipelines

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean and 'message' for conversational responses
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields and natural language summaries

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.

USAGE PATTERNS:
1. Project Setup: Use resolve_project(operation="create") to create projects, resolve_project(operation="open") to open existing ones
2. Media Management: Use resolve_media(operation="import") to import files, resolve_media(operation="list") to browse media pool
3. Timeline Editing: Use resolve_timeline(operation="create") to create timelines, resolve_timeline(operation="add_clip") to add clips
4. Color Grading: Use resolve_color(operation="apply_lut") for LUTs, resolve_color(operation="adjust_wheels") for color correction
5. Rendering: Use resolve_render(operation="timeline") to queue renders, resolve_render(operation="job_status") to check progress
6. Audio: Use resolve_audio(operation="adjust_levels") for mixing, resolve_audio(operation="add_effect") for processing

ERROR HANDLING:
- Connection errors provide DaVinci Resolve startup instructions
- Operation errors specify what failed and how to fix it
- API errors include troubleshooting steps
- Direct communication: Clear, actionable feedback

TOOL MODES:
- Portmanteau mode (default): 7 consolidated tools with operation parameters
- Individual mode: 26 individual tools (set RESOLVE_TOOL_MODE=individual)

PROFESSIONAL WORKFLOWS:
- Supports 4K, 8K, HDR workflows
- Professional color spaces (Rec.709, Rec.2020, P3)
- Frame-accurate editing and color grading
- Batch processing for efficiency
- Multi-format rendering and export""",
    lifespan=server_lifespan
)

# Initialize application state
app.state = AppState()

# Note: FastMCP handles exceptions differently than FastAPI
# Error handling is done at the tool level using the handle_errors decorator

# Note: FastMCP handles HTTP serving and lifecycle differently
# Signal handlers and middleware are not applicable

class ConnectionParams(BaseModel):
    """Parameters for connecting to DaVinci Resolve."""
    host: str = Field("localhost", description="Hostname or IP address of the DaVinci Resolve API")
    port: int = Field(8080, description="Port number of the DaVinci Resolve API")
    timeout: int = Field(30, description="Connection timeout in seconds")


# Note: FastMCP handles lifecycle through the lifespan parameter or run() method
# For now, we'll initialize resources when the module is imported
def initialize_server():
    """Initialize server resources."""
    try:
        logger.info("Initializing DaVinci Resolve MCP server")

        # Load configuration
        config_path = os.getenv("CONFIG_PATH")
        if config_path and os.path.exists(config_path):
            app.state.config = DaVinciResolveConfig.load_from_file(config_path)
        else:
            app.state.config = load_default()

        logger.info("Configuration loaded", config_path=config_path or "default")

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
        logger.error("Failed to initialize server", error=str(e))
        raise

# Note: Server initialization is handled in main.py and the MCP command


@app.tool()
async def get_resolve_info() -> Dict[str, Any]:
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


@app.tool()
async def list_projects() -> Dict[str, Any]:
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
    import os
    tool_mode = os.getenv("RESOLVE_TOOL_MODE", "portmanteau").lower()

    try:
        logger.info("Registering tools", tool_mode=tool_mode)

        # Core server tools are registered via decorators

        if tool_mode == "portmanteau":
            # Use consolidated portmanteau tools (7 tools)
            from .tools.portmanteau import setup_all_portmanteau_tools
            setup_all_portmanteau_tools(app)
            logger.info("Registered portmanteau tools", count=7)
        else:
            # Legacy: register individual tools (26 tools)
            from .tools.help_tool import get_help
            @app.tool()
            async def help(topic: Optional[str] = None, level: Optional[str] = None) -> str:
                """Get help and documentation for DaVinci Resolve MCP tools."""
                return get_help(topic, level)

            @app.tool()
            async def get_status() -> Dict[str, Any]:
                """Get the current status of DaVinci Resolve and MCP server."""
                if not app.state.connection_manager:
                    return {"status": "error", "message": "Connection manager not initialized"}
                return app.state.connection_manager.get_status()

            @app.tool()
            async def health_check() -> Dict[str, Any]:
                """Perform a comprehensive health check of the system."""
                if not app.state.connection_manager:
                    return {"status": "error", "message": "Connection manager not initialized"}
                return await app.state.connection_manager.health_check()

            from .tools.project_tools import register_tools as register_project_tools
            from .tools.media_tools import register_tools as register_media_tools
            from .tools.timeline_tools import register_tools as register_timeline_tools
            from .tools.render_tools import register_tools as register_render_tools
            from .tools.audio_tools import register_tools as register_audio_tools
            from .tools.color_tools import register_tools as register_color_tools

            # Call each registration function (they return app but we ignore the return value)
            _ = register_project_tools(app)
            _ = register_media_tools(app)
            _ = register_timeline_tools(app)
            _ = register_render_tools(app)
            _ = register_audio_tools(app)
            _ = register_color_tools(app)
            logger.info("Registered individual tools", count=26)

        if tool_mode == "portmanteau":
            # Use consolidated portmanteau tools (7 tools)
            from .tools.portmanteau import setup_all_portmanteau_tools
            setup_all_portmanteau_tools(app)
            logger.info("Registered portmanteau tools", count=7)
        else:
            # Legacy: register individual tools (26 tools)
            from .tools.help_tool import get_help
            @app.tool()
            async def help(topic: Optional[str] = None, level: Optional[str] = None) -> str:
                """Get help and documentation for DaVinci Resolve MCP tools."""
                return get_help(topic, level)

            @app.tool()
            async def get_status() -> Dict[str, Any]:
                """Get the current status of DaVinci Resolve and MCP server."""
                if not app.state.connection_manager:
                    return {"status": "error", "message": "Connection manager not initialized"}
                return app.state.connection_manager.get_status()

            @app.tool()
            async def health_check() -> Dict[str, Any]:
                """Perform a comprehensive health check of the system."""
                if not app.state.connection_manager:
                    return {"status": "error", "message": "Connection manager not initialized"}
                return await app.state.connection_manager.health_check()

            from .tools.project_tools import register_tools as register_project_tools
            from .tools.media_tools import register_tools as register_media_tools
            from .tools.timeline_tools import register_tools as register_timeline_tools
            from .tools.render_tools import register_tools as register_render_tools
            from .tools.audio_tools import register_tools as register_audio_tools
            from .tools.color_tools import register_tools as register_color_tools

            # Call each registration function (they return app but we ignore the return value)
            _ = register_project_tools(app)
            _ = register_media_tools(app)
            _ = register_timeline_tools(app)
            _ = register_render_tools(app)
            _ = register_audio_tools(app)
            _ = register_color_tools(app)
            logger.info("Registered individual tools", count=26)

        # Register agentic workflow tools (always, regardless of tool mode)
        from .agentic import register_agentic_tools
        register_agentic_tools()
        logger.info("Registered agentic workflow tools", count=3)

        logger.info("All tools registered successfully")

    except Exception as e:
        logger.error("Failed to register tools", error=str(e))
        raise


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
