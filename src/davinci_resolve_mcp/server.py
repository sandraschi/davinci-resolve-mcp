"""
DaVinci Resolve MCP — FastMCP 3.1+ server.

Implements the MCP server for DaVinci Resolve. Fleet standards: MCP Central Docs
(`standards/AGENT_PROTOCOLS.md`, `standards/SOTA_REQUIREMENTS.md`).
"""

import collections
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from fastmcp.server import create_proxy
from pydantic import BaseModel, Field

from .config import DaVinciResolveConfig, load_default
from .connection.manager import ResolveConnectionManager, ResolveConnectionPool
from .utils.exceptions import ResolveConnectionError

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
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# In-memory log ring buffer for System Logs page (max 500 entries)
_LOG_BUFFER_SIZE = 500
_log_buffer: collections.deque = collections.deque(maxlen=_LOG_BUFFER_SIZE)
_log_seq = 0


class _LogRingHandler(logging.Handler):
    """Capture log records into _log_buffer for GET /api/v1/logs."""

    _LEVEL_MAP = {
        logging.DEBUG: "debug",
        logging.INFO: "info",
        logging.WARNING: "warn",
        logging.ERROR: "error",
        logging.CRITICAL: "error",
    }

    def emit(self, record: logging.LogRecord) -> None:
        global _log_seq
        try:
            _log_seq += 1
            _log_buffer.append(
                {
                    "id": f"{int(record.created * 1000)}-{_log_seq}",
                    "ts": time.strftime("%H:%M:%S", time.localtime(record.created)),
                    "level": self._LEVEL_MAP.get(record.levelno, "info"),
                    "name": record.name,
                    "message": record.getMessage(),
                    "exc": record.exc_text if record.exc_text else None,
                }
            )
        except Exception:
            logger.warning("Log ring handler emit failed", exc_info=True)


_ring_handler = _LogRingHandler()
_ring_handler.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger().addHandler(_ring_handler)


def get_log_buffer() -> list[dict[str, Any]]:
    """Return recent log entries for the API (newest last)."""
    return list(_log_buffer)


# Global application state
class AppState:
    """Global application state."""

    def __init__(self):
        self.config: DaVinciResolveConfig | None = None
        self.connection_manager: ResolveConnectionManager | None = None
        self.connection_pool: ResolveConnectionPool | None = None
        self.should_exit = False


# Server lifespan for startup/shutdown lifecycle
@asynccontextmanager
async def server_lifespan(app: FastMCP):
    """Server lifespan context manager for FastMCP 3.1+."""
    # Startup
    logger.info("Starting DaVinci Resolve MCP Server", version="0.1.0", fastmcp_version="3.1+")
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down DaVinci Resolve MCP Server")


# Initialize the FastMCP 3.1+ app (see MCP Central Docs: standards/SOTA_REQUIREMENTS.md)
app = FastMCP(
    "DaVinci Resolve MCP",
    instructions="""You are DaVinci Resolve MCP, a FastMCP 3.1+ server for DaVinci Resolve automation via the Model Context Protocol.

FASTMCP 3.1+ (fleet 2026 alignment):
- Tools: portmanteau resolve_* tools with operation parameters; structured dict responses
- Sampling: use Context.sample() / agentic tools when the host supports MCP sampling (see SOTA_REQUIREMENTS.md §2)
- Prompts & skills: register when exposed; clients may list MCP prompts and skill:// resources per WEBAPP_STANDARDS / packaging docs

CORE CAPABILITIES:
- Project: create, open, list projects
- Media: import, folders, media pool search
- Timeline: timelines, clips, edits
- Color: LUTs, primaries/secondaries, nodes
- Render: queue jobs, monitor, export
- Audio: levels, effects, sync
- Fairlight: resolve_fairlight(operation=open_page|get_tracks|set_mute|set_solo|set_volume, ...)
- Subtitles: resolve_subtitle(action=add|get|edit|delete|import_srt|export_srt, ...)
- System: resolve_system, health, help

RESPONSE FORMAT:
- Prefer dicts with success, message, and task-specific fields; errors include error when applicable

PORTMANTEAU DESIGN:
Eight consolidated tools (resolve_project, resolve_media, resolve_timeline, resolve_color, resolve_render, resolve_audio, resolve_system, resolve_fairlight, resolve_subtitle; plus resolve_help where registered). Each uses an operation (or action) parameter.

TOOL MODES:
- Portmanteau (default): RESOLVE_TOOL_MODE=portmanteau
- Individual: RESOLVE_TOOL_MODE=individual (legacy 26-tool surface)

RESOLUTION / COLOR:
- 4K/8K/HDR and common color spaces (Rec.709, Rec.2020, P3) where Resolve exposes them""",
    lifespan=server_lifespan,
)

# MCP Bridge: proxy upstream servers via MCP_BRIDGE_URLS (comma-separated)
_bridge_proxies = []
bridge_urls = os.getenv("MCP_BRIDGE_URLS", "")
if bridge_urls:
    for url in bridge_urls.split(","):
        url = url.strip()
        if url:
            try:
                app.add_provider(create_proxy(url))
                _bridge_proxies.append(url)
            except Exception:
                logger.warning("Failed to add bridge proxy: %s", url, exc_info=True)

# Initialize application state
app.state = AppState()

# HTTP routes: must load after FastMCP `app` exists (routes import `app`). `api_app` is built after `initialize_server`.
from .api.routes import router as api_router

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
            config=app.state.config, max_connections=app.state.config.max_workers
        )

        # Register all tools
        register_tools()

        logger.info("DaVinci Resolve MCP server initialized successfully")

    except Exception as e:
        logger.error("Failed to initialize server", error=str(e))
        raise


@asynccontextmanager
async def api_lifespan(_http: FastAPI):
    """Initialize shared MCP state in the ASGI process.

    Uvicorn ``--reload`` (DEBUG) and some workers import ``api_app`` without re-running
    ``run_api``'s ``__main__`` block, so ``initialize_server()`` never ran — connection
    manager stayed None and the dashboard always showed disconnected.
    """
    if app.state.connection_manager is None:
        try:
            initialize_server()
        except Exception as e:
            logger.warning(
                "api_lifespan: initialize_server skipped or failed (Resolve may be unavailable)",
                error=str(e),
            )
    yield


api_app = FastAPI(
    title="DaVinci Resolve MCP API",
    description="HTTP API for the DaVinci Resolve MCP web dashboard (FastMCP 3.1+ stack).",
    version="1.0.0",
    lifespan=api_lifespan,
)

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:10842",
        "http://127.0.0.1:10842",
        "tauri://localhost",
        "http://tauri.localhost",
        "https://tauri.localhost",
    ],
    allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_app.include_router(api_router, prefix="/api/v1")


# Note: Server initialization is handled in main.py and the MCP command


@app.tool()
async def get_resolve_info() -> dict[str, Any]:
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

    if not await app.state.connection_manager.ensure_connection():
        raise ResolveConnectionError("Could not connect to DaVinci Resolve")

    resolve = app.state.connection_manager.get_connection()
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()

    return {
        "version": resolve.GetVersionString(),
        "api_version": resolve.GetApiVersion() if hasattr(resolve, "GetApiVersion") else "N/A",
        "is_console": resolve.IsConsole() if hasattr(resolve, "IsConsole") else False,
        "is_rendering": resolve.IsRenderingInProgress() if hasattr(resolve, "IsRenderingInProgress") else False,
        "project_name": current_project.GetName() if current_project else None,
    }


@app.tool()
async def list_projects() -> dict[str, Any]:
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

    if not await app.state.connection_manager.ensure_connection():
        raise ResolveConnectionError("Could not connect to DaVinci Resolve")

    resolve = app.state.connection_manager.get_connection()
    project_manager = resolve.GetProjectManager()

    current_project = project_manager.GetCurrentProject()
    current_project_name = current_project.GetName() if current_project else None

    projects = project_manager.GetProjectListInCurrentFolder() or []

    return {"current_project": current_project_name, "projects": projects}


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
            logger.info("Registered portmanteau tools", count=9)
        else:
            # Legacy: register individual tools (26 tools)
            from .tools.help_tool import get_help

            @app.tool()
            async def help(topic: str | None = None, level: str | None = None) -> str:
                """Get help and documentation for DaVinci Resolve MCP tools."""
                return get_help(topic, level)

            @app.tool()
            async def get_status() -> dict[str, Any]:
                """Get the current status of DaVinci Resolve and MCP server."""
                if not app.state.connection_manager:
                    return {"status": "error", "message": "Connection manager not initialized"}
                return app.state.connection_manager.get_status()

            @app.tool()
            async def health_check() -> dict[str, Any]:
                """Perform a comprehensive health check of the system."""
                if not app.state.connection_manager:
                    return {"status": "error", "message": "Connection manager not initialized"}
                return await app.state.connection_manager.health_check()

            from .tools.audio_tools import register_tools as register_audio_tools
            from .tools.color_tools import register_tools as register_color_tools
            from .tools.media_tools import register_tools as register_media_tools
            from .tools.project_tools import register_tools as register_project_tools
            from .tools.render_tools import register_tools as register_render_tools
            from .tools.subtitle_tools import register_tools as register_subtitle_tools
            from .tools.timeline_tools import register_tools as register_timeline_tools

            # Call each registration function (they return app but we ignore the return value)
            _ = register_project_tools(app)
            _ = register_media_tools(app)
            _ = register_timeline_tools(app)
            _ = register_render_tools(app)
            _ = register_audio_tools(app)
            _ = register_color_tools(app)
            _ = register_subtitle_tools(app)
            logger.info("Registered individual tools", count=32)

        # Register agentic workflow tools (always, regardless of tool mode)
        from .agentic import register_agentic_tools

        register_agentic_tools()
        logger.info("Registered agentic workflow tools", count=3)

        # Register shutdown tool
        @app.tool()
        async def davinci_resolve_shutdown(confirm: bool = False) -> dict:
            """Shut down the DaVinci Resolve MCP server gracefully.

            Requires confirm=True to prevent accidental termination.

            ## Return Format
            {"success": bool, "message": str}
            """
            if not confirm:
                return {"success": False, "message": "Set confirm=True to shut down the server"}
            logger.warning("Server shutdown requested via MCP tool")
            app.state.should_exit = True
            import os

            os._exit(0)

        logger.info("All tools registered successfully")

    except Exception as e:
        logger.error("Failed to register tools", error=str(e))
        raise


def start_server(host: str | None = None, port: int | None = None, debug: bool | None = None) -> None:
    """
    Start the HTTP API server (api_app) for the web dashboard.

    Args:
        host: Host to bind the server to (default: from config or "0.0.0.0")
        port: Port to run the server on (default: from config or 8000)
        debug: Enable debug mode with verbose logging (default: from config or False)
    """
    import uvicorn

    host = host or os.getenv("HOST", "0.0.0.0")
    port = port or int(os.getenv("PORT", "8000"))
    debug = debug if debug is not None else os.getenv("DEBUG", "false").lower() == "true"

    logger.info("Starting DaVinci Resolve MCP API on %s:%s (debug: %s)", host, port, debug)

    uvicorn.run(
        api_app,
        host=host,
        port=port,
        log_level="debug" if debug else "info",
        reload=debug,
    )


if __name__ == "__main__":
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description="DaVinci Resolve MCP API server for webapp")
    parser.add_argument("--host", type=str, help="Host to bind to (overrides HOST env var)")
    parser.add_argument("--port", type=int, help="Port to listen on (overrides PORT env var)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (overrides DEBUG env var)")
    parser.add_argument("--config", type=str, help="Path to configuration file")

    args = parser.parse_args()

    if args.host:
        os.environ["HOST"] = args.host
    if args.port:
        os.environ["PORT"] = str(args.port)
    if args.debug:
        os.environ["DEBUG"] = "true"
    if args.config:
        os.environ["CONFIG_PATH"] = args.config

    try:
        initialize_server()
    except Exception as e:
        logger.warning("Server init warning (Resolve may be unavailable): %s", e)

    try:
        start_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error: %s", str(e))
        sys.exit(1)
