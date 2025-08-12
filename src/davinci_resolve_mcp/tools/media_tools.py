"""
DaVinci Resolve Media Tools.

This module provides tools for managing media in DaVinci Resolve,
including importing media, organizing the media pool, and managing clips.
"""
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from ..connection.manager import ResolveConnectionManager
from ..utils.exceptions import ResolveConnectionError, ResolveOperationError

logger = logging.getLogger(__name__)


class MediaItem(BaseModel):
    """Model representing a media item in the media pool."""
    name: str = Field(..., description="Name of the media item")
    file_path: str = Field(..., description="File system path to the media")
    media_type: str = Field(..., description="Type of media (video, audio, image, etc.)")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    frame_rate: Optional[float] = Field(None, description="Frame rate (for video)")
    resolution: Optional[str] = Field(None, description="Resolution (e.g., '1920x1080')")
    channels: Optional[int] = Field(None, description="Audio channels (for audio)")
    sample_rate: Optional[float] = Field(None, description="Sample rate in Hz (for audio)")


class FolderInfo(BaseModel):
    """Model representing a folder in the media pool."""
    name: str = Field(..., description="Name of the folder")
    path: str = Field(..., description="Path of the folder in the media pool")
    item_count: int = Field(0, description="Number of items in the folder")
    subfolder_count: int = Field(0, description="Number of subfolders")


def register_tools(app):
    """Register media management tools with the FastMCP app."""
    
    @app.tool()
    async def import_media(
        paths: List[str],
        target_folder: Optional[str] = None,
        as_sequence: bool = False,
        force_framerate: Optional[float] = None,
        force_resolution: Optional[str] = None
    ) -> Dict[str, Any]:
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
                folder_parts = [p for p in target_folder.split('/') if p]
                
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
                        'importAsNumberedStills': as_sequence,
                    }
                    
                    if force_framerate:
                        import_options['frameRate'] = force_framerate
                    
                    if force_resolution:
                        try:
                            width, height = map(int, force_resolution.lower().split('x'))
                            import_options['width'] = width
                            import_options['height'] = height
                        except (ValueError, AttributeError):
                            logger.warning(f"Invalid resolution format: {force_resolution}")
                    
                    # Import the media
                    result = media_pool.ImportMedia(expanded_path, import_options)
                    
                    if result:
                        imported_items.append(expanded_path)
                    else:
                        failed_imports.append({"path": expanded_path, "error": "Import failed"})
                        
                except Exception as e:
                    logger.error(f"Error importing {path}: {str(e)}")
                    failed_imports.append({"path": path, "error": str(e)})
            
            return {
                "status": "partial" if failed_imports and imported_items else "success" if imported_items else "failed",
                "imported_count": len(imported_items),
                "failed_count": len(failed_imports),
                "imported_items": imported_items,
                "failed_imports": failed_imports
            }
            
        except Exception as e:
            logger.error(f"Error in import_media: {str(e)}")
            raise ResolveOperationError(f"Failed to import media: {str(e)}")
    
    @app.tool()
    async def list_media(folder_path: str = "") -> Dict[str, Any]:
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
                folder_parts = [p for p in folder_path.split('/') if p]
                
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
                    subfolders.append({
                        "name": name,
                        "path": f"{folder_path}/{name}" if folder_path else name,
                        "type": "folder"
                    })
            
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
                        "has_audio": clip.GetClipProperty("Has Audio") == "1"
                    }
                    media_items.append(clip_info)
                except Exception as e:
                    logger.warning(f"Error getting clip info: {str(e)}")
            
            return {
                "status": "success",
                "current_folder": folder_path or "/",
                "subfolders": subfolders,
                "media_items": media_items
            }
            
        except Exception as e:
            logger.error(f"Error listing media: {str(e)}")
            raise ResolveOperationError(f"Failed to list media: {str(e)}")
    
    @app.tool()
    async def create_folder(path: str) -> Dict[str, Any]:
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
            folder_parts = [p for p in path.split('/') if p]
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
                "message": f"Folder created: {'/'.join(created_path)}"
            }
            
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            raise ResolveOperationError(f"Failed to create folder: {str(e)}")
    
    @app.tool()
    async def get_media_metadata(clip_path: str) -> Dict[str, Any]:
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
            
            for clip_id, c in clips.items():
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
                "date_modified": clip.GetClipProperty("Date Modified")
            }
            
            # Add any additional properties
            for key, value in properties.items():
                if key not in metadata:
                    metadata[key.lower().replace(' ', '_')] = value
            
            return {
                "status": "success",
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting media metadata: {str(e)}")
            raise ResolveOperationError(f"Failed to get media metadata: {str(e)}")
    
    logger.info("Registered media management tools")
    return app
