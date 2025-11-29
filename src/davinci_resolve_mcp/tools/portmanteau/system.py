"""
DaVinci Resolve System Portmanteau Tool.

Consolidates system/utility operations into a single tool.
"""
import logging
from typing import Any, Dict, Literal, Optional

logger = logging.getLogger(__name__)


def setup_system_portmanteau(app):
    """Register the system portmanteau tool."""

    @app.tool()
    async def resolve_system(
        action: Literal["info", "status", "health", "help"],
        topic: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        System information and utilities for DaVinci Resolve MCP.

        PORTMANTEAU PATTERN: Consolidates system tools into 1.

        SUPPORTED ACTIONS:
        - info: Get DaVinci Resolve version and connection info
        - status: Get current server and connection status
        - health: Perform comprehensive health check
        - help: Get help on topics (optional: topic, level)

        Args:
            action: Operation to perform (info, status, health, help)
            topic: Help topic. Used by: help. Optional.
            level: User level (beginner, intermediate, advanced, developer). Used by: help.

        Returns:
            Dict with operation results

        Examples:
            # Get Resolve info
            resolve_system("info")

            # Get status
            resolve_system("status")

            # Health check
            resolve_system("health")

            # Get help
            resolve_system("help", topic="color_grading", level="beginner")
        """
        # Import from server module - these are the core functions
        from ..help_tool import get_help

        if action == "info":
            # Get Resolve info from app state
            try:
                from ...server import app as server_app
                if server_app.state.connection_manager:
                    resolve = server_app.state.connection_manager.get_connection()
                    project_manager = resolve.GetProjectManager()
                    current_project = project_manager.GetCurrentProject()

                    return {
                        "status": "success",
                        "data": {
                            "version": resolve.GetVersionString(),
                            "api_version": getattr(resolve, 'GetApiVersion', lambda: "N/A")(),
                            "is_rendering": getattr(resolve, 'IsRenderingInProgress', lambda: False)(),
                            "project_name": current_project.GetName() if current_project else None,
                        }
                    }
                else:
                    return {"status": "error", "message": "Connection manager not initialized"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif action == "status":
            try:
                from ...server import app as server_app
                if server_app.state.connection_manager:
                    return {
                        "status": "success",
                        "data": server_app.state.connection_manager.get_status()
                    }
                else:
                    return {"status": "error", "message": "Connection manager not initialized"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif action == "health":
            try:
                from ...server import app as server_app
                if server_app.state.connection_manager:
                    result = await server_app.state.connection_manager.health_check()
                    return {"status": "success", "data": result}
                else:
                    return {"status": "error", "message": "Connection manager not initialized"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif action == "help":
            help_text = get_help(topic, level)
            return {"status": "success", "help": help_text}

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_system portmanteau tool")

