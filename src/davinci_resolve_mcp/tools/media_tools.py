"""
DaVinci Resolve Media Tools.

This module provides tools for managing media in DaVinci Resolve,
including importing media, organizing the media pool, and managing clips.
"""

import logging
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from ..utils.exceptions import ResolveConnectionError, ResolveOperationError

logger = logging.getLogger(__name__)


class MediaItem(BaseModel):
    """Model representing a media item in the media pool."""

    name: str = Field(..., description="Name of the media item")
    file_path: str = Field(..., description="File system path to the media")
    media_type: str = Field(..., description="Type of media (video, audio, image, etc.)")
    duration: float | None = Field(None, description="Duration in seconds")
    frame_rate: float | None = Field(None, description="Frame rate (for video)")
    resolution: str | None = Field(None, description="Resolution (e.g., '1920x1080')")
    channels: int | None = Field(None, description="Audio channels (for audio)")
    sample_rate: float | None = Field(None, description="Sample rate in Hz (for audio)")


class FolderInfo(BaseModel):
    """Model representing a folder in the media pool."""

    name: str = Field(..., description="Name of the folder")
    path: str = Field(..., description="Path of the folder in the media pool")
    item_count: int = Field(0, description="Number of items in the folder")
    subfolder_count: int = Field(0, description="Number of subfolders")


async def import_media(
    app,
    paths: list[str],
    target_folder: str | None = None,
    as_sequence: bool = False,
    force_framerate: float | None = None,
    force_resolution: str | None = None,
) -> dict[str, Any]:
    """
    Import media files into DaVinci Resolve's media pool.

    Args:
        app: FastMCP app instance
        paths: List of file paths to import
        target_folder: Optional folder path in media pool (creates if doesn't exist)
        as_sequence: Treat image sequences as a single clip
        force_framerate: Optional frame rate to force for the media
        force_resolution: Optional resolution to force (format: 'WxH')

    Returns:
        Dict containing import results
    """
    return await import_media_impl(
        app, paths, target_folder, as_sequence, force_framerate, force_resolution
    )


async def list_media(app, folder_path: str = "") -> dict[str, Any]:
    """
    List media in a specific folder or the current folder.

    Args:
        app: FastMCP app instance
        folder_path: Path to folder to list (empty string for current folder)

    Returns:
        Dict containing media list
    """
    return await list_media_impl(app, folder_path)


async def create_folder(app, folder_path: str) -> dict[str, Any]:
    """
    Create a folder in the media pool.

    Args:
        app: FastMCP app instance
        folder_path: Path of folder to create

    Returns:
        Dict containing creation result
    """
    return await create_folder_impl(app, folder_path)


async def get_media_metadata(app, clip_path: str) -> dict[str, Any]:
    """
    Get metadata for a specific media clip.

    Args:
        app: FastMCP app instance
        clip_path: Path to the clip in media pool

    Returns:
        Dict containing clip metadata
    """
    return await get_media_metadata_impl(app, clip_path)


async def import_media_impl(
    app,
    paths: list[str],
    target_folder: str | None = None,
    as_sequence: bool = False,
    force_framerate: float | None = None,
    force_resolution: str | None = None,
) -> dict[str, Any]:
    """
    Implementation of media import (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        media_pool = project.GetMediaPool()
        if not media_pool:
            raise ResolveOperationError("Failed to access media pool")

        # Get or create target folder
        current_folder = media_pool.GetCurrentFolder()

        if target_folder:
            # Split path into components
            folder_parts = [p for p in target_folder.split("/") if p]
            if not folder_parts:
                raise ResolveOperationError("No folder name specified")

            # Start at root folder
            current_folder = media_pool.GetRootFolder()
            created_path = []

            # Navigate through path, creating folders as needed
            for folder_name in folder_parts:
                subfolders = media_pool.GetSubFolders(current_folder)
                found = False

                if subfolders:
                    for name, folder in subfolders.items():
                        if name == folder_name:
                            current_folder = folder
                            created_path.append(name)
                            found = True
                            break

                if not found:
                    # Create the folder
                    new_folder = media_pool.AddSubFolder(current_folder, folder_name)
                    if not new_folder:
                        raise ResolveOperationError(f"Failed to create folder '{folder_name}'")
                    current_folder = new_folder
                    created_path.append(folder_name)


        # Import media files
        import_results = []
        for path in paths:
            if not os.path.exists(path):
                import_results.append(
                    {"path": path, "status": "error", "message": "File does not exist"}
                )
                continue

            # Create media storage object
            media_storage = {"media": path, "startFrame": 0, "endFrame": 0}

            # Add optional parameters
            if force_framerate is not None:
                media_storage["frameRate"] = force_framerate

            if force_resolution:
                try:
                    width, height = map(int, force_resolution.split("x"))
                    media_storage["resolutionWidth"] = width
                    media_storage["resolutionHeight"] = height
                except ValueError:
                    logger.warning(f"Invalid resolution format: {force_resolution}")

            if as_sequence:
                media_storage["isSequence"] = True

            # Import the media
            result = media_pool.ImportMedia([media_storage])
            if result:
                import_results.append(
                    {"path": path, "status": "success", "clips_created": len(result)}
                )
            else:
                import_results.append({"path": path, "status": "error", "message": "Import failed"})

        return {
            "status": "success",
            "target_folder": target_folder,
            "results": import_results,
            "total_imported": sum(1 for r in import_results if r["status"] == "success"),
        }

    except Exception as e:
        logger.error(f"Error importing media: {e!s}")
        raise ResolveOperationError(f"Failed to import media: {e!s}")


async def list_media_impl(app, folder_path: str = "") -> dict[str, Any]:
    """
    Implementation of media listing (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        media_pool = project.GetMediaPool()
        if not media_pool:
            raise ResolveOperationError("Failed to access media pool")

        # Navigate to target folder
        target_folder = media_pool.GetCurrentFolder()
        if folder_path:
            folder_parts = [p for p in folder_path.split("/") if p]
            current_folder = media_pool.GetRootFolder()

            for folder_name in folder_parts:
                subfolders = media_pool.GetSubFolders(current_folder)
                found = False

                if subfolders:
                    for name, folder in subfolders.items():
                        if name == folder_name:
                            current_folder = folder
                            found = True
                            break

                if not found:
                    raise ResolveOperationError(f"Folder '{folder_name}' not found")

            target_folder = current_folder

        # Get clips in folder
        clips = media_pool.GetClipList(target_folder) or []
        clip_info = []

        for clip in clips:
            clip_info.append(
                {
                    "name": clip.GetName(),
                    "type": clip.GetClipProperty("Type") or "Unknown",
                    "duration": clip.GetClipProperty("Duration") or 0,
                    "frame_rate": clip.GetClipProperty("Frame Rate") or 0,
                    "resolution": f"{clip.GetClipProperty('Resolution Width') or 0}x{clip.GetClipProperty('Resolution Height') or 0}",
                }
            )

        # Get subfolders
        subfolders = media_pool.GetSubFolders(target_folder) or {}
        folder_info = []

        for name, folder in subfolders.items():
            folder_info.append(
                {
                    "name": name,
                    "item_count": len(media_pool.GetClipList(folder) or []),
                    "subfolder_count": len(media_pool.GetSubFolders(folder) or {}),
                }
            )

        return {
            "status": "success",
            "folder_path": folder_path,
            "clips": clip_info,
            "folders": folder_info,
            "total_clips": len(clip_info),
            "total_folders": len(folder_info),
        }

    except Exception as e:
        logger.error(f"Error listing media: {e!s}")
        raise ResolveOperationError(f"Failed to list media: {e!s}")


async def create_folder_impl(app, folder_path: str) -> dict[str, Any]:
    """
    Implementation of folder creation (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        media_pool = project.GetMediaPool()
        if not media_pool:
            raise ResolveOperationError("Failed to access media pool")

        # Split path into components
        folder_parts = [p for p in folder_path.split("/") if p]
        if not folder_parts:
            raise ResolveOperationError("No folder name specified")

        # Start at root folder
        current_folder = media_pool.GetRootFolder()
        created_path = []

        # Navigate through path, creating folders as needed
        for folder_name in folder_parts:
            subfolders = media_pool.GetSubFolders(current_folder)
            found = False

            if subfolders:
                for name, folder in subfolders.items():
                    if name == folder_name:
                        current_folder = folder
                        created_path.append(name)
                        found = True
                        break

            if not found:
                # Create the folder
                new_folder = media_pool.AddSubFolder(current_folder, folder_name)
                if not new_folder:
                    raise ResolveOperationError(f"Failed to create folder '{folder_name}'")
                current_folder = new_folder
                created_path.append(folder_name)

        return {
            "status": "success",
            "folder_path": folder_path,
            "created_path": "/".join(created_path),
        }

    except Exception as e:
        logger.error(f"Error creating folder: {e!s}")
        raise ResolveOperationError(f"Failed to create folder: {e!s}")


async def get_media_metadata_impl(app, clip_path: str) -> dict[str, Any]:
    """
    Implementation of media metadata retrieval (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveConnectionError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        media_pool = project.GetMediaPool()
        if not media_pool:
            raise ResolveOperationError("Failed to access media pool")

        # Navigate to clip location
        path_parts = clip_path.split("/")
        clip_name = path_parts[-1]
        folder_path = "/".join(path_parts[:-1]) if len(path_parts) > 1 else ""

        # Navigate to folder
        current_folder = media_pool.GetRootFolder()
        if folder_path:
            folder_parts = [p for p in folder_path.split("/") if p]

            for folder_name in folder_parts:
                subfolders = media_pool.GetSubFolders(current_folder)
                found = False

                if subfolders:
                    for name, folder in subfolders.items():
                        if name == folder_name:
                            current_folder = folder
                            found = True
                            break

                if not found:
                    raise ResolveOperationError(f"Folder '{folder_name}' not found")

        # Find the clip
        clips = media_pool.GetClipList(current_folder) or []
        target_clip = None

        for clip in clips:
            if clip.GetName() == clip_name:
                target_clip = clip
                break

        if not target_clip:
            raise ResolveOperationError(f"Clip '{clip_name}' not found")

        # Get clip properties
        properties = [
            "Type",
            "Duration",
            "Frame Rate",
            "Resolution Width",
            "Resolution Height",
            "PAR",
            "DAR",
            "Audio Channels",
            "Audio Sample Rate",
            "Bit Depth",
            "Codec",
            "File Path",
            "File Size",
            "Date Created",
            "Date Modified",
        ]

        metadata = {}
        for prop in properties:
            value = target_clip.GetClipProperty(prop)
            if value is not None:
                # Convert property name to lowercase with underscores
                key = prop.lower().replace(" ", "_")
                metadata[key] = value

        # Add any additional properties
        for key, value in properties.items():
            if key not in metadata:
                metadata[key.lower().replace(" ", "_")] = value

        return {"status": "success", "clip_path": clip_path, "metadata": metadata}

    except Exception as e:
        logger.error(f"Error getting media metadata: {e!s}")
        raise ResolveOperationError(f"Failed to get media metadata: {e!s}")


def register_tools(app):
    """Register media management tools with the FastMCP app."""

    @app.tool()
    async def import_media(
        paths: list[str],
        target_folder: str | None = None,
        as_sequence: bool = False,
        force_framerate: float | None = None,
        force_resolution: str | None = None,
    ) -> dict[str, Any]:
        """
        Import media files into DaVinci Resolve's media pool.

        Args:
            paths: List of file paths to import
            target_folder: Optional folder path in media pool (creates if doesn't exist)
            as_sequence: Treat image sequences as a single clip
            force_framerate: Optional frame rate to force for the media
            force_resolution: Optional resolution to force (format: 'WxH')

        Returns:
            Dict containing import results

        Raises:
            ResolveOperationError: If import fails
        """
        try:
            connection = app.state.connection_manager
            if not connection or not connection.resolve:
                raise ResolveConnectionError("Not connected to DaVinci Resolve")

            project = connection.current_project
            if not project:
                raise ResolveOperationError("No project is currently open")

            media_pool = project.GetMediaPool()
            if not media_pool:
                raise ResolveOperationError("Failed to access media pool")

            # Get or create target folder
            current_folder = media_pool.GetCurrentFolder()
            target_folder_obj = None

            if target_folder:
                # Split path into components
                folder_parts = [p for p in target_folder.split("/") if p]

                # Navigate to or create each folder in the path
                for folder_name in folder_parts:
                    subfolders = media_pool.GetSubFolders(current_folder)
                    found = False

                    if subfolders:
                        for name, folder in subfolders.items():
                            if name == folder_name:
                                current_folder = folder
                                target_folder_obj = folder
                                found = True
                                break

                    if not found:
                        # Create the folder if it doesn't exist
                        result = media_pool.AddSubFolder(current_folder, folder_name)
                        if not result:
                            raise ResolveOperationError(f"Failed to create folder: {folder_name}")
                        current_folder = result
                        target_folder_obj = result

            # Set current folder to target
            if target_folder_obj:
                media_pool.SetCurrentFolder(target_folder_obj)
            else:
                media_pool.SetCurrentFolder(media_pool.GetRootFolder())

            # Import each file
            imported_items = []
            failed_imports = []

            for path in paths:
                try:
                    # Expand user path and resolve to absolute path
                    expanded_path = str(Path(path).expanduser().resolve())

                    # Check if file exists
                    if not os.path.exists(expanded_path):
                        logger.warning(f"File not found: {expanded_path}")
                        failed_imports.append({"path": expanded_path, "error": "File not found"})
                        continue

                    # Import options
                    import_options = {
                        "importAsNumberedStills": as_sequence,
                    }

                    if force_framerate:
                        import_options["frameRate"] = force_framerate

                    if force_resolution:
                        try:
                            width, height = map(int, force_resolution.lower().split("x"))
                            import_options["width"] = width
                            import_options["height"] = height
                        except (ValueError, AttributeError):
                            logger.warning(f"Invalid resolution format: {force_resolution}")

                    # Import the media
                    result = media_pool.ImportMedia(expanded_path, import_options)

                    if result:
                        imported_items.append(expanded_path)
                    else:
                        failed_imports.append({"path": expanded_path, "error": "Import failed"})

                except Exception as e:
                    logger.error(f"Error importing {path}: {e!s}")
                    failed_imports.append({"path": path, "error": str(e)})

            return {
                "status": "partial"
                if failed_imports and imported_items
                else "success"
                if imported_items
                else "failed",
                "imported_count": len(imported_items),
                "failed_count": len(failed_imports),
                "imported_items": imported_items,
                "failed_imports": failed_imports,
            }

        except Exception as e:
            logger.error(f"Error in import_media: {e!s}")
            raise ResolveOperationError(f"Failed to import media: {e!s}")

    @app.tool()
    async def list_media(folder_path: str = "") -> dict[str, Any]:
        """
        List media items in the specified folder of the media pool.

        Args:
            folder_path: Path to the folder in media pool (empty for current folder)

        Returns:
            Dict containing folder contents

        Raises:
            ResolveOperationError: If operation fails
        """
        try:
            connection = app.state.connection_manager
            if not connection or not connection.resolve:
                raise ResolveConnectionError("Not connected to DaVinci Resolve")

            project = connection.current_project
            if not project:
                raise ResolveOperationError("No project is currently open")

            media_pool = project.GetMediaPool()
            if not media_pool:
                raise ResolveOperationError("Failed to access media pool")

            # Navigate to target folder if specified
            current_folder = media_pool.GetRootFolder()

            if folder_path:
                folder_parts = [p for p in folder_path.split("/") if p]

                for folder_name in folder_parts:
                    subfolders = media_pool.GetSubFolders(current_folder)
                    found = False

                    if subfolders:
                        for name, folder in subfolders.items():
                            if name == folder_name:
                                current_folder = folder
                                found = True
                                break

                    if not found:
                        raise ResolveOperationError(f"Folder not found: {folder_path}")

            # Get contents of current folder
            media_pool.SetCurrentFolder(current_folder)

            # Get subfolders
            subfolders = []
            folder_items = media_pool.GetSubFolders(current_folder)
            if folder_items:
                for name, folder in folder_items.items():
                    subfolders.append(
                        {
                            "name": name,
                            "path": f"{folder_path}/{name}" if folder_path else name,
                            "type": "folder",
                        }
                    )

            # Get media items
            media_items = []
            clips = media_pool.GetClipsInFolder(current_folder) or {}

            for clip_id, clip in clips.items():
                try:
                    clip_info = {
                        "id": clip_id,
                        "name": clip.GetName(),
                        "type": "clip",
                        "path": clip.GetMediaPath(),
                        "duration": clip.GetClipProperty("Duration"),
                        "frame_rate": clip.GetClipProperty("FPS"),
                        "resolution": f"{clip.GetClipProperty('Width')}x{clip.GetClipProperty('Height')}",
                        "has_video": clip.GetClipProperty("Has Video") == "1",
                        "has_audio": clip.GetClipProperty("Has Audio") == "1",
                    }
                    media_items.append(clip_info)
                except Exception as e:
                    logger.warning(f"Error getting clip info: {e!s}")

            return {
                "status": "success",
                "current_folder": folder_path or "/",
                "subfolders": subfolders,
                "media_items": media_items,
            }

        except Exception as e:
            logger.error(f"Error listing media: {e!s}")
            raise ResolveOperationError(f"Failed to list media: {e!s}")

    @app.tool()
    async def create_folder(path: str) -> dict[str, Any]:
        """
        Create a new folder in the media pool.

        Args:
            path: Path of the folder to create (e.g., "Assets/Videos")

        Returns:
            Dict containing operation status

        Raises:
            ResolveOperationError: If folder creation fails
        """
        try:
            connection = app.state.connection_manager
            if not connection or not connection.resolve:
                raise ResolveConnectionError("Not connected to DaVinci Resolve")

            project = connection.current_project
            if not project:
                raise ResolveOperationError("No project is currently open")

            media_pool = project.GetMediaPool()
            if not media_pool:
                raise ResolveOperationError("Failed to access media pool")

            # Split path into components
            folder_parts = [p for p in path.split("/") if p]
            if not folder_parts:
                raise ResolveOperationError("No folder name specified")

            # Start at root folder
            current_folder = media_pool.GetRootFolder()
            created_path = []

            # Navigate through path, creating folders as needed
            for folder_name in folder_parts:
                subfolders = media_pool.GetSubFolders(current_folder)
                found = False

                if subfolders:
                    for name, folder in subfolders.items():
                        if name == folder_name:
                            current_folder = folder
                            created_path.append(name)
                            found = True
                            break

                if not found:
                    # Create the folder
                    result = media_pool.AddSubFolder(current_folder, folder_name)
                    if not result:
                        raise ResolveOperationError(f"Failed to create folder: {folder_name}")

                    current_folder = result
                    created_path.append(folder_name)

            return {
                "status": "success",
                "path": "/".join(created_path),
                "message": f"Folder created: {'/'.join(created_path)}",
            }

        except Exception as e:
            logger.error(f"Error creating folder: {e!s}")
            raise ResolveOperationError(f"Failed to create folder: {e!s}")

    @app.tool()
    async def get_media_metadata(clip_path: str) -> dict[str, Any]:
        """
        Get detailed metadata for a media item.

        Args:
            clip_path: Path to the media item in the media pool

        Returns:
            Dict containing media metadata

        Raises:
            ResolveOperationError: If metadata cannot be retrieved
        """
        try:
            connection = app.state.connection_manager
            if not connection or not connection.resolve:
                raise ResolveConnectionError("Not connected to DaVinci Resolve")

            project = connection.current_project
            if not project:
                raise ResolveOperationError("No project is currently open")

            media_pool = project.GetMediaPool()
            if not media_pool:
                raise ResolveOperationError("Failed to access media pool")

            # Find the clip by path
            clip = None
            clips = media_pool.GetClipsInFolder(media_pool.GetRootFolder()) or {}

            for _clip_id, c in clips.items():
                if c.GetMediaPath() == clip_path:
                    clip = c
                    break

            if not clip:
                raise ResolveOperationError(f"Media not found: {clip_path}")

            # Get clip properties
            properties = clip.GetClipProperty()

            # Extract relevant metadata
            metadata = {
                "name": clip.GetName(),
                "path": clip.GetMediaPath(),
                "type": "video" if clip.GetClipProperty("Has Video") == "1" else "audio",
                "duration": clip.GetClipProperty("Duration"),
                "frame_rate": clip.GetClipProperty("FPS"),
                "resolution": f"{clip.GetClipProperty('Width')}x{clip.GetClipProperty('Height')}",
                "start_frame": clip.GetClipProperty("Start"),
                "end_frame": clip.GetClipProperty("End"),
                "has_audio": clip.GetClipProperty("Has Audio") == "1",
                "audio_channels": clip.GetClipProperty("Audio Channels"),
                "audio_sample_rate": clip.GetClipProperty("Sample Rate"),
                "codec": clip.GetClipProperty("Codec"),
                "file_size": clip.GetClipProperty("File Size"),
                "date_created": clip.GetClipProperty("Date Created"),
                "date_modified": clip.GetClipProperty("Date Modified"),
            }

            # Add any additional properties
            for key, value in properties.items():
                if key not in metadata:
                    metadata[key.lower().replace(" ", "_")] = value

            return {"status": "success", "metadata": metadata}

        except Exception as e:
            logger.error(f"Error getting media metadata: {e!s}")
            raise ResolveOperationError(f"Failed to get media metadata: {e!s}")

    logger.info("Registered media management tools")
