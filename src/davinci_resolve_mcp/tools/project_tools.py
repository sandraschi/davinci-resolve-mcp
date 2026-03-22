"""
DaVinci Resolve Project Tools.

This module provides tools for managing DaVinci Resolve projects,
including creation, opening, listing, and project settings management.
"""

import logging
from typing import Any

from pydantic import BaseModel, Field

from ..utils.exceptions import ResolveConnectionError, ResolveOperationError

logger = logging.getLogger(__name__)


class ProjectInfo(BaseModel):
    """Model representing a DaVinci Resolve project."""

    name: str = Field(..., description="Name of the project")
    path: str | None = Field(None, description="File path of the project")
    frame_rate: float | None = Field(None, description="Project frame rate")
    resolution: str | None = Field(None, description="Project resolution (WxH)")
    is_active: bool = Field(False, description="Whether this is the active project")


class ProjectSettings(BaseModel):
    """Model for project settings that can be modified."""

    frame_rate: float | None = Field(None, ge=1.0, le=120.0, description="Frames per second")
    resolution_width: int | None = Field(None, ge=640, le=7680, description="Width in pixels")
    resolution_height: int | None = Field(None, ge=360, le=4320, description="Height in pixels")
    pixel_aspect_ratio: float | None = Field(None, ge=0.1, le=2.0, description="Pixel aspect ratio")
    playback_framerate: float | None = Field(None, description="Playback frame rate")
    timeline_format: str | None = Field(None, description="Timeline format preset")


async def create_project(
    app,
    name: str,
    frame_rate: float = 24.0,
    width: int = 1920,
    height: int = 1080,
    template: str | None = None,
) -> dict[str, Any]:
    """
    Create a new DaVinci Resolve project.

    Args:
        app: FastMCP app instance
        name: Name for the new project
        frame_rate: Frame rate for the project (default: 24.0)
        width: Width in pixels (default: 1920)
        height: Height in pixels (default: 1080)
        template: Optional template to use for the project

    Returns:
        Dict containing project information
    """
    return await create_project_impl(app, name, frame_rate, width, height, template)


async def open_project(app, name: str) -> dict[str, Any]:
    """
    Open an existing DaVinci Resolve project.

    Args:
        app: FastMCP app instance
        name: Name of the project to open

    Returns:
        Dict containing project information
    """
    return await open_project_impl(app, name)


async def list_projects(app) -> dict[str, Any]:
    """
    List all available DaVinci Resolve projects.

    Args:
        app: FastMCP app instance

    Returns:
        Dict containing project list
    """
    return await list_projects_impl(app)


async def get_project_settings(app) -> dict[str, Any]:
    """
    Get settings for the current DaVinci Resolve project.

    Args:
        app: FastMCP app instance

    Returns:
        Dict containing project settings
    """
    return await get_project_settings_impl(app)


async def update_project_settings(app, settings: dict[str, Any]) -> dict[str, Any]:
    """
    Update settings for the current DaVinci Resolve project.

    Args:
        app: FastMCP app instance
        settings: Dict of settings to update

    Returns:
        Dict containing update results
    """
    return await update_project_settings_impl(app, settings)


async def create_project_impl(
    app,
    name: str,
    frame_rate: float = 24.0,
    width: int = 1920,
    height: int = 1080,
    template: str | None = None,
) -> dict[str, Any]:
    """
    Implementation of project creation (shared between individual and portmanteau tools).
    """
    try:
        # Get connection to Resolve
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        project_manager = connection.project_manager
        if not project_manager:
            raise ResolveConnectionError("Failed to get project manager")

        # Create new project
        project = project_manager.CreateProject(name)
        if not project:
            raise ResolveOperationError(f"Failed to create project '{name}'")

        # Set project settings
        project.SetSetting("timelineFrameRate", str(frame_rate))
        project.SetSetting("timelineResolutionWidth", str(width))
        project.SetSetting("timelineResolutionHeight", str(height))

        # Save the project
        if not project.SaveProject():
            logger.warning(f"Created project '{name}' but failed to save it")

        return {
            "status": "success",
            "project": {
                "name": name,
                "frame_rate": frame_rate,
                "resolution": f"{width}x{height}",
                "path": project.GetName(),  # Get the full project path
            },
        }

    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise ResolveOperationError(f"Failed to create project: {str(e)}")


async def open_project_impl(app, name: str) -> dict[str, Any]:
    """
    Implementation of project opening (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        project_manager = connection.project_manager
        if not project_manager:
            raise ResolveConnectionError("Failed to get project manager")

        # Try to open the project
        project = project_manager.LoadProject(name)
        if not project:
            # Try to find the project in the current folder
            projects = project_manager.GetProjectListInCurrentFolder()
            if name in projects:
                project = project_manager.LoadProject(name)

            if not project:
                raise ResolveOperationError(f"Project '{name}' not found")

        # Update connection's current project
        connection.current_project = project

        # Get project settings
        settings = {}
        for setting in ["timelineFrameRate", "timelineResolutionWidth", "timelineResolutionHeight"]:
            value = project.GetSetting(setting)
            if value is not None:
                settings[setting] = value

        return {
            "status": "success",
            "project": {
                "name": project.GetName(),
                "path": project.GetProjectPath() or "",
                "settings": settings,
            },
        }

    except Exception as e:
        logger.error(f"Error opening project: {str(e)}")
        raise ResolveOperationError(f"Failed to open project: {str(e)}")


async def list_projects_impl(app) -> dict[str, Any]:
    """
    Implementation of project listing (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        project_manager = connection.project_manager
        if not project_manager:
            raise ResolveConnectionError("Failed to get project manager")

        # Get projects in current folder
        projects = project_manager.GetProjectListInCurrentFolder()
        if not projects:
            projects = []

        # Get current project
        current_project = project_manager.GetCurrentProject()
        current_name = current_project.GetName() if current_project else None

        project_list = []
        for project_name in projects:
            project_list.append(
                {
                    "name": project_name,
                    "is_active": project_name == current_name,
                    "path": "",  # Could be enhanced to get full paths
                }
            )

        return {"status": "success", "projects": project_list, "current_project": current_name}

    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise ResolveOperationError(f"Failed to list projects: {str(e)}")


async def get_project_settings_impl(app) -> dict[str, Any]:
    """
    Implementation of project settings retrieval (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        project_manager = connection.project_manager
        if not project_manager:
            raise ResolveConnectionError("Failed to get project manager")

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            raise ResolveOperationError("No active project")

        # Get common project settings
        settings = {}
        setting_keys = [
            "timelineFrameRate",
            "timelineResolutionWidth",
            "timelineResolutionHeight",
            "timelinePixelAspectRatio",
            "timelinePlaybackFrameRate",
            "timelineFormat",
        ]

        for key in setting_keys:
            value = current_project.GetSetting(key)
            if value is not None:
                settings[key] = value

        return {
            "status": "success",
            "project_name": current_project.GetName(),
            "settings": settings,
        }

    except Exception as e:
        logger.error(f"Error getting project settings: {str(e)}")
        raise ResolveOperationError(f"Failed to get project settings: {str(e)}")


async def update_project_settings_impl(app, settings: dict[str, Any]) -> dict[str, Any]:
    """
    Implementation of project settings update (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        project_manager = connection.project_manager
        if not project_manager:
            raise ResolveConnectionError("Failed to get project manager")

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            raise ResolveOperationError("No active project")

        updated = {}
        for key, value in settings.items():
            if value is not None:
                if current_project.SetSetting(key, str(value)):
                    updated[key] = value

        # Save project if any settings were updated
        if updated:
            if not current_project.SaveProject():
                logger.warning("Updated settings but failed to save project")

        return {
            "status": "success",
            "updated_settings": updated,
            "project_name": current_project.GetName(),
        }

    except Exception as e:
        logger.error(f"Error updating project settings: {str(e)}")
        raise ResolveOperationError(f"Failed to update project settings: {str(e)}")


def register_tools(app):
    """Register project management tools with the FastMCP app."""

    @app.tool()
    async def create_project(
        name: str,
        frame_rate: float = 24.0,
        width: int = 1920,
        height: int = 1080,
        template: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new DaVinci Resolve project.

        Args:
            name: Name for the new project
            frame_rate: Frame rate for the project (default: 24.0)
            width: Width in pixels (default: 1920)
            height: Height in pixels (default: 1080)
            template: Optional template to use for the project

        Returns:
            Dict containing project information

        Raises:
            ResolveOperationError: If project creation fails
        """
        try:
            # Get connection to Resolve
            connection = app.state.connection_manager
            if not connection or not connection.resolve:
                raise ResolveConnectionError("Not connected to DaVinci Resolve")

            project_manager = connection.project_manager
            if not project_manager:
                raise ResolveConnectionError("Failed to get project manager")

            # Create new project
            project = project_manager.CreateProject(name)
            if not project:
                raise ResolveOperationError(f"Failed to create project '{name}'")

            # Set project settings
            project.SetSetting("timelineFrameRate", str(frame_rate))
            project.SetSetting("timelineResolutionWidth", str(width))
            project.SetSetting("timelineResolutionHeight", str(height))

            # Save the project
            if not project.SaveProject():
                logger.warning(f"Created project '{name}' but failed to save it")

            return {
                "status": "success",
                "project": {
                    "name": name,
                    "frame_rate": frame_rate,
                    "resolution": f"{width}x{height}",
                    "path": project.GetName(),  # Get the full project path
                },
            }

        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise ResolveOperationError(f"Failed to create project: {str(e)}")

    @app.tool()
    async def open_project(name: str) -> dict[str, Any]:
        """
        Open an existing DaVinci Resolve project.

        Args:
            name: Name of the project to open

        Returns:
            Dict containing project information

        Raises:
            ResolveOperationError: If project cannot be opened
        """
        try:
            connection = app.state.connection_manager
            if not connection or not connection.resolve:
                raise ResolveConnectionError("Not connected to DaVinci Resolve")

            project_manager = connection.project_manager
            if not project_manager:
                raise ResolveConnectionError("Failed to get project manager")

            # Try to open the project
            project = project_manager.LoadProject(name)
            if not project:
                # Try to find the project in the current folder
                projects = project_manager.GetProjectListInCurrentFolder()
                if name in projects:
                    project = project_manager.LoadProject(name)

                if not project:
                    raise ResolveOperationError(f"Project '{name}' not found")

            # Update connection's current project
            connection.current_project = project

            # Get project settings
            frame_rate = float(project.GetSetting("timelineFrameRate") or "0")
            width = int(project.GetSetting("timelineResolutionWidth") or "0")
            height = int(project.GetSetting("timelineResolutionHeight") or "0")

            return {
                "status": "success",
                "project": {
                    "name": project.GetName(),
                    "frame_rate": frame_rate,
                    "resolution": f"{width}x{height}",
                    "path": project.GetName(),
                },
            }

        except Exception as e:
            logger.error(f"Error opening project: {str(e)}")
            raise ResolveOperationError(f"Failed to open project: {str(e)}")

    @app.tool()
    async def list_projects() -> dict[str, Any]:
        """
        List all available projects in DaVinci Resolve.

        Returns:
            Dict containing list of projects and current project info

        Raises:
            ResolveOperationError: If project listing fails
        """
        try:
            connection = app.state.connection_manager
            if not connection or not connection.resolve:
                raise ResolveConnectionError("Not connected to DaVinci Resolve")

            project_manager = connection.project_manager
            if not project_manager:
                raise ResolveConnectionError("Failed to get project manager")

            # Get current project
            current_project = project_manager.GetCurrentProject()
            current_project_name = current_project.GetName() if current_project else None

            # Get all projects in current folder
            projects = project_manager.GetProjectListInCurrentFolder() or []

            # Get project details
            project_list = []
            for project_name in projects:
                project = project_manager.LoadProject(project_name)
                if project:
                    frame_rate = project.GetSetting("timelineFrameRate") or "N/A"
                    width = project.GetSetting("timelineResolutionWidth") or "N/A"
                    height = project.GetSetting("timelineResolutionHeight") or "N/A"

                    project_list.append(
                        {
                            "name": project_name,
                            "frame_rate": frame_rate,
                            "resolution": f"{width}x{height}",
                            "is_active": project_name == current_project_name,
                        }
                    )

            return {
                "status": "success",
                "current_project": current_project_name,
                "projects": project_list,
            }

        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            raise ResolveOperationError(f"Failed to list projects: {str(e)}")

    @app.tool()
    async def get_project_settings() -> dict[str, Any]:
        """
        Get settings for the current project.

        Returns:
            Dict containing project settings

        Raises:
            ResolveOperationError: If no project is open or settings cannot be retrieved
        """
        try:
            connection = app.state.connection_manager
            if not connection or not connection.resolve:
                raise ResolveConnectionError("Not connected to DaVinci Resolve")

            project = connection.current_project
            if not project:
                raise ResolveOperationError("No project is currently open")

            # Get all project settings
            settings = {}
            setting_names = [
                "timelineFrameRate",
                "timelineResolutionWidth",
                "timelineResolutionHeight",
                "pixelAspectRatio",
                "playbackFrameRate",
                "timelineFormat",
            ]

            for setting in setting_names:
                settings[setting] = project.GetSetting(setting)

            return {"status": "success", "project_name": project.GetName(), "settings": settings}

        except Exception as e:
            logger.error(f"Error getting project settings: {str(e)}")
            raise ResolveOperationError(f"Failed to get project settings: {str(e)}")

    @app.tool()
    async def update_project_settings(settings: dict[str, Any]) -> dict[str, Any]:
        """
        Update settings for the current project.

        Args:
            settings: Dictionary of settings to update

        Returns:
            Dict containing status and updated settings

        Raises:
            ResolveOperationError: If settings cannot be updated
        """
        try:
            connection = app.state.connection_manager
            if not connection or not connection.resolve:
                raise ResolveConnectionError("Not connected to DaVinci Resolve")

            project = connection.current_project
            if not project:
                raise ResolveOperationError("No project is currently open")

            # Apply settings
            updated = {}
            for key, value in settings.items():
                if value is not None:
                    if project.SetSetting(key, str(value)):
                        updated[key] = value

            # Save project if any settings were updated
            if updated:
                if not project.SaveProject():
                    logger.warning("Updated settings but failed to save project")

            return {
                "status": "success",
                "updated_settings": updated,
                "project_name": project.GetName(),
            }

        except Exception as e:
            logger.error(f"Error updating project settings: {str(e)}")
            raise ResolveOperationError(f"Failed to update project settings: {str(e)}")

    logger.info("Registered project management tools")
