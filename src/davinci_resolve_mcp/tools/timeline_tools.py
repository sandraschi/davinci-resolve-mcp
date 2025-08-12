"""
DaVinci Resolve Timeline Tools.

This module provides tools for managing timelines in DaVinci Resolve,
including creating, editing, and manipulating timelines and their contents.
"""
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator

from ..connection.manager import ResolveConnectionManager
from ..utils.exceptions import ResolveConnectionError, ResolveOperationError

logger = logging.getLogger(__name__)


class TrackType(str, Enum):
    """Types of tracks in a timeline."""
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"


class TimelineItem(BaseModel):
    """Model representing an item in a timeline track."""
    name: str = Field(..., description="Name of the timeline item")
    start_frame: int = Field(..., description="Start frame in the timeline")
    end_frame: int = Field(..., description="End frame in the timeline")
    media_type: str = Field(..., description="Type of media (video, audio, etc.)")
    track_index: int = Field(..., description="Index of the track containing this item")
    track_type: TrackType = Field(..., description="Type of track")
    source_path: Optional[str] = Field(None, description="Source media path if applicable")


class TimelineTrack(BaseModel):
    """Model representing a track in a timeline."""
    track_type: TrackType = Field(..., description="Type of track")
    index: int = Field(..., description="Track index")
    is_muted: bool = Field(False, description="Whether the track is muted")
    is_locked: bool = Field(False, description="Whether the track is locked")
    items: List[TimelineItem] = Field(default_factory=list, description="Items in this track")


class TimelineInfo(BaseModel):
    """Model representing a timeline."""
    name: str = Field(..., description="Name of the timeline")
    frame_rate: float = Field(..., description="Timeline frame rate")
    start_frame: int = Field(0, description="Start frame number")
    end_frame: int = Field(0, description="End frame number")
    resolution_width: int = Field(1920, description="Timeline width in pixels")
    resolution_height: int = Field(1080, description="Timeline height in pixels")
    tracks: List[TimelineTrack] = Field(default_factory=list, description="Tracks in the timeline")


def register_tools(app):
    """Register timeline management tools with the FastMCP app."""
    
    @app.tool()
    async def create_timeline(
        name: str,
        frame_rate: float = 24.0,
        width: int = 1920,
        height: int = 1080,
        start_frame: int = 0,
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new timeline in the current or specified project.
        
        Args:
            name: Name for the new timeline
            frame_rate: Frame rate for the timeline (default: 24.0)
            width: Width in pixels (default: 1920)
            height: Height in pixels (default: 1080)
            start_frame: Starting frame number (default: 0)
            project_name: Optional name of the project to create the timeline in
            
        Returns:
            Dictionary with timeline creation status and details
        """
        try:
            with ResolveConnectionManager() as resolve:
                # Get the project
                project_manager = resolve.GetProjectManager()
                if project_name:
                    project = project_manager.LoadProject(project_name)
                    if not project:
                        project = project_manager.CreateProject(project_name)
                else:
                    project = project_manager.GetCurrentProject()
                
                if not project:
                    raise ResolveOperationError("No project available")
                
                # Create a new timeline
                timeline = project.CreateTimeline(name)
                if not timeline:
                    raise ResolveOperationError(f"Failed to create timeline '{name}'")
                
                # Set timeline settings
                timeline.SetSetting('timelineFrameRate', str(frame_rate))
                timeline.SetSetting('timelineResolutionWidth', str(width))
                timeline.SetSetting('timelineResolutionHeight', str(height))
                timeline.SetSetting('timelineStartFrame', str(start_frame))
                
                # Save the project
                project_manager.SaveProject()
                
                return {
                    "status": "success",
                    "message": f"Timeline '{name}' created successfully",
                    "timeline": {
                        "name": name,
                        "frame_rate": frame_rate,
                        "resolution": f"{width}x{height}",
                        "start_frame": start_frame
                    }
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to create timeline: {str(e)}")

    @app.tool()
    async def get_timeline_info(timeline_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about the current or specified timeline.
        
        Args:
            timeline_name: Optional name of the timeline to get info for
            
        Returns:
            Dictionary with timeline information
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Get timeline settings
                frame_rate = float(timeline.GetSetting('timelineFrameRate') or '24.0')
                width = int(timeline.GetSetting('timelineResolutionWidth') or '1920')
                height = int(timeline.GetSetting('timelineResolutionHeight') or '1080')
                start_frame = int(timeline.GetSetting('timelineStartFrame') or '0')
                end_frame = int(timeline.GetEndFrame() or '0')
                
                # Get tracks
                tracks = []
                for track_type in ["video", "audio"]:
                    track_count = timeline.GetTrackCount(track_type)
                    for i in range(1, track_count + 1):
                        is_muted = timeline.GetTrackProperty(f"showTrackMute{i}", track_type) == "1"
                        is_locked = timeline.GetTrackProperty(f"showTrackLock{i}", track_type) == "1"
                        
                        track = {
                            "track_type": track_type,
                            "index": i,
                            "is_muted": is_muted,
                            "is_locked": is_locked,
                            "items": []
                        }
                        tracks.append(track)
                
                return {
                    "status": "success",
                    "timeline": {
                        "name": timeline.GetName(),
                        "frame_rate": frame_rate,
                        "resolution_width": width,
                        "resolution_height": height,
                        "start_frame": start_frame,
                        "end_frame": end_frame,
                        "tracks": tracks
                    }
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to get timeline info: {str(e)}")

    @app.tool()
    async def add_clip_to_timeline(
        clip_path: str,
        track_index: int = 1,
        track_type: TrackType = TrackType.VIDEO,
        start_frame: Optional[int] = None,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a clip to the specified timeline track.
        
        Args:
            clip_path: Path to the media file to add
            track_index: Index of the track to add to (1-based)
            track_type: Type of track (video/audio/subtitle)
            start_frame: Frame to start the clip at (None for current playhead position)
            timeline_name: Optional name of the timeline to add to
            
        Returns:
            Dictionary with operation status and clip details
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Import the media into the media pool
                media_pool = project.GetMediaPool()
                if not media_pool:
                    raise ResolveOperationError("Could not access media pool")
                
                # Add the clip to the media pool
                clips = media_pool.ImportMedia([clip_path])
                if not clips:
                    raise ResolveOperationError(f"Failed to import media: {clip_path}")
                
                # Add the clip to the timeline
                track_type_str = track_type.value.lower()
                if track_type_str not in ["video", "audio"]:
                    track_type_str = "video"  # Default to video for unsupported types
                
                # Prepare the insert options
                insert_info = [{
                    "mediaPoolItem": clips[0],
                    "trackIndex": track_index - 1,  # Convert to 0-based
                    "startFrame": 0
                }]
                
                # Insert at current position if no start_frame is specified
                if start_frame is None:
                    start_frame = timeline.GetCurrentTimecode()
                
                # Insert the clip
                result = timeline.InsertClipTimeline(insert_info, start_frame)
                if not result:
                    raise ResolveOperationError("Failed to add clip to timeline")
                
                # Save the project
                resolve.GetProjectManager().SaveProject()
                
                return {
                    "status": "success",
                    "message": f"Added clip to {track_type_str} track {track_index}",
                    "clip": {
                        "path": clip_path,
                        "track_type": track_type_str,
                        "track_index": track_index,
                        "start_frame": start_frame
                    }
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to add clip to timeline: {str(e)}")

    @app.tool()
    async def cut_clip(
        frame: int,
        track_index: int,
        track_type: TrackType = TrackType.VIDEO,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cut a clip at the specified frame.
        
        Args:
            frame: Frame number to make the cut
            track_index: Index of the track containing the clip
            track_type: Type of track (video/audio/subtitle)
            timeline_name: Optional name of the timeline
            
        Returns:
            Dictionary with operation status
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Set the playhead to the cut position
                timeline.SetCurrentTimecode(frame)
                
                # Perform the cut
                track_type_str = track_type.value.lower()
                if track_type_str not in ["video", "audio"]:
                    track_type_str = "video"  # Default to video for unsupported types
                
                # Razor cut at the current position
                result = timeline.RazorCut(track_index - 1, track_type_str, frame, frame, False)
                
                if not result:
                    raise ResolveOperationError("Failed to perform cut")
                
                # Save the project
                resolve.GetProjectManager().SaveProject()
                
                return {
                    "status": "success",
                    "message": f"Cut performed at frame {frame} on {track_type_str} track {track_index}"
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to cut clip: {str(e)}")

    @app.tool()
    async def set_timeline_playhead(
        frame: int,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set the playhead position in the timeline.
        
        Args:
            frame: Frame number to move the playhead to
            timeline_name: Optional name of the timeline
            
        Returns:
            Dictionary with operation status
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Set the playhead position
                timeline.SetCurrentTimecode(frame)
                
                return {
                    "status": "success",
                    "message": f"Playhead set to frame {frame}",
                    "frame": frame
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to set playhead position: {str(e)}")

    # Add more timeline-related tools as needed
    # - Add transitions
    # - Apply effects
    # - Adjust clip properties
    # - Manage markers
    # - Etc.

    return app
