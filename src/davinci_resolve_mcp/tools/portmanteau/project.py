"""
DaVinci Resolve Project Portmanteau Tool.

Consolidates project management operations into a single tool.
"""
import logging
from typing import Any, Dict, Literal, Optional

logger = logging.getLogger(__name__)


def setup_project_portmanteau(app):
    """Register the project portmanteau tool."""

    @app.tool()
    async def resolve_project(
        action: Literal["create", "open", "list", "get_settings", "update_settings"],
        name: Optional[str] = None,
        frame_rate: float = 24.0,
        width: int = 1920,
        height: int = 1080,
        template: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive project management for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates 5 project tools into 1.

        SUPPORTED ACTIONS:
        - create: Create new project (requires: name)
        - open: Open existing project (requires: name)
        - list: List all available projects
        - get_settings: Get current project settings
        - update_settings: Update project settings (requires: settings dict)

        Args:
            action: Operation to perform (create, open, list, get_settings, update_settings)
            name: Project name. Required for: create, open
            frame_rate: Frame rate for new project. Used by: create. Default: 24.0
            width: Width in pixels. Used by: create. Default: 1920
            height: Height in pixels. Used by: create. Default: 1080
            template: Template name. Used by: create. Optional.
            settings: Settings dict. Required for: update_settings

        Returns:
            Dict with operation results

        Examples:
            # Create 4K project
            resolve_project("create", name="My Film", width=3840, height=2160)

            # Open existing project
            resolve_project("open", name="Client Video")

            # List all projects
            resolve_project("list")

            # Get current settings
            resolve_project("get_settings")

            # Update settings
            resolve_project("update_settings", settings={"timelineFrameRate": "30"})
        """
        from ..project_tools import (
            create_project,
            open_project,
            list_projects,
            get_project_settings,
            update_project_settings,
        )

        if action == "create":
            if not name:
                return {"status": "error", "message": "name is required for create action"}
            return await create_project(name, frame_rate, width, height, template)

        elif action == "open":
            if not name:
                return {"status": "error", "message": "name is required for open action"}
            return await open_project(name)

        elif action == "list":
            return await list_projects()

        elif action == "get_settings":
            return await get_project_settings()

        elif action == "update_settings":
            if not settings:
                return {"status": "error", "message": "settings dict is required for update_settings action"}
            return await update_project_settings(settings)

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_project portmanteau tool")

