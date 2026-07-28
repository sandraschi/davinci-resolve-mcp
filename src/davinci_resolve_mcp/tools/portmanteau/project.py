"""
DaVinci Resolve Project Portmanteau Tool.

Consolidates project management operations into a single tool with conversational returns.
"""

import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)


_MUTATING = {}


def setup_project_portmanteau(app):
    """Register the project portmanteau tool with conversational capabilities."""

    @app.tool(annotations=_MUTATING)
    async def resolve_project(
        action: Literal["create", "open", "list", "get_settings", "update_settings"],
        name: str | None = None,
        frame_rate: float = 24.0,
        width: int = 1920,
        height: int = 1080,
        template: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive project management for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates 5 project tools into 1 with conversational responses.

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
            Dict with conversational response and operation results

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
            create_project_impl as create_project,
        )
        from ..project_tools import (
            get_project_settings_impl as get_project_settings,
        )
        from ..project_tools import (
            list_projects_impl as list_projects,
        )
        from ..project_tools import (
            open_project_impl as open_project,
        )
        from ..project_tools import (
            update_project_settings_impl as update_project_settings,
        )

        if action == "create":
            if not name:
                return {
                    "success": False,
                    "error": "name parameter is required for create action",
                    "message": "Please provide a project name to create a new project.",
                }

            result = await create_project(app, name, frame_rate, width, height, template)
            if result.get("status") == "success":
                resolution = f"{width}x{height}"
                message = f"Created new project '{name}' with {resolution} resolution at {frame_rate}fps"
                if template:
                    message += f" using '{template}' template"
                return {
                    "success": True,
                    "operation": "project_create",
                    "message": message,
                    "project_name": name,
                    "resolution": resolution,
                    "frame_rate": frame_rate,
                    "template": template,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "message": f"Failed to create project '{name}': {result.get('message', 'Unknown error')}",
                }

        elif action == "open":
            if not name:
                return {
                    "success": False,
                    "error": "name parameter is required for open action",
                    "message": "Please provide a project name to open.",
                }

            result = await open_project(app, name)
            if result.get("status") == "success":
                return {
                    "success": True,
                    "operation": "project_open",
                    "message": f"Opened project '{name}' successfully",
                    "project_name": name,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "message": f"Failed to open project '{name}': {result.get('message', 'Unknown error')}",
                }

        elif action == "list":
            result = await list_projects(app)
            if result.get("status") == "success":
                projects = result.get("projects", [])
                count = len(projects)
                message = f"Found {count} project{'s' if count != 1 else ''}"
                if count > 0:
                    message += f": {', '.join(projects[:5])}{'...' if count > 5 else ''}"

                return {
                    "success": True,
                    "operation": "project_list",
                    "message": message,
                    "project_count": count,
                    "projects": projects,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "message": f"Failed to list projects: {result.get('message', 'Unknown error')}",
                }

        elif action == "get_settings":
            result = await get_project_settings(app)
            if result.get("status") == "success":
                settings_data = result.get("settings", {})
                message = "Retrieved current project settings"
                if settings_data:
                    timeline_fps = settings_data.get("timelineFrameRate")
                    if timeline_fps:
                        message += f" (timeline: {timeline_fps}fps)"

                return {
                    "success": True,
                    "operation": "project_get_settings",
                    "message": message,
                    "settings": settings_data,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "message": f"Failed to get project settings: {result.get('message', 'Unknown error')}",
                }

        elif action == "update_settings":
            if not settings:
                return {
                    "success": False,
                    "error": "settings parameter is required for update_settings action",
                    "message": "Please provide a settings dictionary to update project settings.",
                }

            result = await update_project_settings(app, settings)
            if result.get("status") == "success":
                setting_keys = list(settings.keys())
                message = f"Updated project settings: {', '.join(setting_keys)}"

                return {
                    "success": True,
                    "operation": "project_update_settings",
                    "message": message,
                    "updated_settings": setting_keys,
                    "settings": settings,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "message": f"Failed to update project settings: {result.get('message', 'Unknown error')}",
                }

        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "message": f"Unsupported action '{action}'. Supported actions: create, open, list, get_settings, update_settings",
            }

    logger.info("Registered resolve_project portmanteau tool with conversational returns")
