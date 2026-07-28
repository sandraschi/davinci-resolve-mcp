"""
DaVinci Resolve Timeline Tools.

This module provides tools for managing timelines in DaVinci Resolve,
including creating, editing, and manipulating timelines and their contents.
"""

import logging
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from ..connection.manager import ResolveConnectionManager
from ..utils.exceptions import ResolveOperationError

logger = logging.getLogger(__name__)


class TrackType(StrEnum):
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
    source_path: str | None = Field(None, description="Source media path if applicable")


class TimelineTrack(BaseModel):
    """Model representing a track in a timeline."""

    track_type: TrackType = Field(..., description="Type of track")
    index: int = Field(..., description="Track index")
    is_muted: bool = Field(False, description="Whether the track is muted")
    is_locked: bool = Field(False, description="Whether the track is locked")
    items: list[TimelineItem] = Field(default_factory=list, description="Items in this track")


class TimelineInfo(BaseModel):
    """Model representing a timeline."""

    name: str = Field(..., description="Name of the timeline")
    frame_rate: float = Field(..., description="Timeline frame rate")
    start_frame: int = Field(0, description="Start frame number")
    end_frame: int = Field(0, description="End frame number")
    resolution_width: int = Field(1920, description="Timeline width in pixels")
    resolution_height: int = Field(1080, description="Timeline height in pixels")
    tracks: list[TimelineTrack] = Field(default_factory=list, description="Tracks in the timeline")


async def create_timeline(
    app,
    name: str,
    frame_rate: float = 24.0,
    width: int = 1920,
    height: int = 1080,
    start_frame: int = 0,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a new timeline in the current project.

    Args:
        app: FastMCP app instance
        name: Name for the new timeline
        frame_rate: Frame rate for the timeline
        width: Width in pixels
        height: Height in pixels
        start_frame: Starting frame number
        timeline_name: Optional name for the timeline

    Returns:
        Dict containing timeline creation result
    """
    return await create_timeline_impl(app, name, frame_rate, width, height, start_frame, timeline_name)


async def get_timeline_info(app, timeline_name: str | None = None) -> dict[str, Any]:
    """
    Get information about a timeline.

    Args:
        app: FastMCP app instance
        timeline_name: Name of timeline to get info for (uses current if None)

    Returns:
        Dict containing timeline information
    """
    return await get_timeline_info_impl(app, timeline_name)


async def add_clip_to_timeline(
    app,
    clip_path: str,
    track_index: int = 1,
    track_type: TrackType = TrackType.VIDEO,
    start_frame: int | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Add a clip to a timeline at the specified position.

    Args:
        app: FastMCP app instance
        clip_path: Path to the clip in media pool
        track_index: Track index to add to
        track_type: Type of track (video/audio)
        start_frame: Frame to insert at (uses current playhead if None)
        timeline_name: Name of timeline to add to (uses current if None)

    Returns:
        Dict containing clip addition result
    """
    return await add_clip_to_timeline_impl(app, clip_path, track_index, track_type, start_frame, timeline_name)


async def cut_clip(
    app,
    frame: int,
    track_index: int = 1,
    track_type: TrackType = TrackType.VIDEO,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Cut a clip at the specified frame.

    Args:
        app: FastMCP app instance
        frame: Frame number to cut at
        track_index: Track index containing the clip
        track_type: Type of track
        timeline_name: Name of timeline (uses current if None)

    Returns:
        Dict containing cut result
    """
    return await cut_clip_impl(app, frame, track_index, track_type, timeline_name)


async def set_timeline_playhead(app, frame: int, timeline_name: str | None = None) -> dict[str, Any]:
    """
    Set the playhead position in a timeline.

    Args:
        app: FastMCP app instance
        frame: Frame number to set playhead to
        timeline_name: Name of timeline (uses current if None)

    Returns:
        Dict containing playhead setting result
    """
    return await set_timeline_playhead_impl(app, frame, timeline_name)


async def create_timeline_impl(
    app,
    name: str,
    frame_rate: float = 24.0,
    width: int = 1920,
    height: int = 1080,
    start_frame: int = 0,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Implementation of timeline creation (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        # Create timeline
        timeline = project.AddTimeline(name, frame_rate, width, height, start_frame)
        if not timeline:
            raise ResolveOperationError(f"Failed to create timeline '{name}'")

        # Set timeline name if provided
        if timeline_name:
            timeline.SetName(timeline_name)

        return {
            "status": "success",
            "timeline": {
                "name": timeline.GetName(),
                "frame_rate": timeline.GetSetting("timelineFrameRate"),
                "duration": timeline.GetDuration(),
                "start_frame": timeline.GetStartFrame(),
            },
        }

    except Exception as e:
        logger.error(f"Error creating timeline: {e!s}")
        raise ResolveOperationError(f"Failed to create timeline: {e!s}") from e


async def get_timeline_info_impl(app, timeline_name: str | None = None) -> dict[str, Any]:
    """
    Implementation of timeline info retrieval (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
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

        # Get timeline tracks
        tracks = []
        for track_type in [TrackType.VIDEO, TrackType.AUDIO, TrackType.SUBTITLE]:
            track_count = timeline.GetTrackCount(track_type.value)
            for i in range(1, track_count + 1):
                track_name = timeline.GetTrackName(track_type.value, i)
                tracks.append(
                    {
                        "type": track_type.value,
                        "index": i,
                        "name": track_name,
                        "is_locked": timeline.GetIsTrackLocked(track_type.value, i),
                        "is_muted": timeline.GetIsTrackMuted(track_type.value, i),
                    }
                )

        return {
            "status": "success",
            "timeline": {
                "name": timeline.GetName(),
                "duration": timeline.GetDuration(),
                "frame_rate": timeline.GetSetting("timelineFrameRate"),
                "start_frame": timeline.GetStartFrame(),
                "end_frame": timeline.GetEndFrame(),
                "current_timecode": timeline.GetCurrentTimecode(),
                "tracks": tracks,
            },
        }

    except Exception as e:
        logger.error(f"Error getting timeline info: {e!s}")
        raise ResolveOperationError(f"Failed to get timeline info: {e!s}") from e


async def add_clip_to_timeline_impl(
    app,
    clip_path: str,
    track_index: int = 1,
    track_type: TrackType = TrackType.VIDEO,
    start_frame: int | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Implementation of clip addition to timeline (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        media_pool = project.GetMediaPool()
        if not media_pool:
            raise ResolveOperationError("Failed to access media pool")

        # Get the specified timeline or current timeline
        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        # Find the clip in media pool
        clip = None
        root_folder = media_pool.GetRootFolder()

        def find_clip(folder, path_parts):
            if not path_parts:
                return None
            clip_name = path_parts[-1]
            folder_path = path_parts[:-1]

            current_folder = folder
            for folder_name in folder_path:
                subfolders = media_pool.GetSubFolders(current_folder)
                if subfolders and folder_name in subfolders:
                    current_folder = subfolders[folder_name]
                else:
                    return None

            clips = media_pool.GetClipList(current_folder) or []
            for c in clips:
                if c.GetName() == clip_name:
                    return c
            return None

        path_parts = [p for p in clip_path.split("/") if p]
        clip = find_clip(root_folder, path_parts)

        if not clip:
            raise ResolveOperationError(f"Clip '{clip_path}' not found in media pool")

        # Insert at current position if no start_frame is specified
        if start_frame is None:
            start_frame = timeline.GetCurrentTimecode()

        # Insert the clip
        result = timeline.InsertClipTimeline(
            {"mediaPoolItem": clip, "trackIndex": track_index, "recordFrame": start_frame},
            start_frame,
        )

        if not result:
            raise ResolveOperationError("Failed to add clip to timeline")

        return {
            "status": "success",
            "clip_path": clip_path,
            "timeline_name": timeline.GetName(),
            "track_index": track_index,
            "track_type": track_type.value,
            "start_frame": start_frame,
        }

    except Exception as e:
        logger.error(f"Error adding clip to timeline: {e!s}")
        raise ResolveOperationError(f"Failed to add clip to timeline: {e!s}") from e


async def cut_clip_impl(
    app,
    frame: int,
    track_index: int = 1,
    track_type: TrackType = TrackType.VIDEO,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Implementation of clip cutting (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
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

        # Cut the clip at the specified frame
        result = timeline.CutClipAtPlayhead(frame, track_index)
        if not result:
            raise ResolveOperationError(f"Failed to cut clip at frame {frame}")

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "frame": frame,
            "track_index": track_index,
            "track_type": track_type.value,
        }

    except Exception as e:
        logger.error(f"Error cutting clip: {e!s}")
        raise ResolveOperationError(f"Failed to cut clip: {e!s}") from e


async def set_timeline_playhead_impl(app, frame: int, timeline_name: str | None = None) -> dict[str, Any]:
    """
    Implementation of playhead setting (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
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

        # Set the playhead
        result = timeline.SetCurrentTimecode(frame)
        if not result:
            raise ResolveOperationError(f"Failed to set playhead to frame {frame}")

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "frame": frame,
            "timecode": timeline.GetCurrentTimecode(),
        }

    except Exception as e:
        logger.error(f"Error setting playhead: {e!s}")
        raise ResolveOperationError(f"Failed to set playhead: {e!s}") from e


# ── Marker Operations ──────────────────────────────────────────────


async def add_marker_impl(
    app,
    frame: int,
    color: str = "Blue",
    name: str = "",
    note: str = "",
    duration: int = 1,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Implementation of marker addition (shared between individual and portmanteau tools)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        valid_colors = {
            "Blue",
            "Cyan",
            "Green",
            "Yellow",
            "Red",
            "Pink",
            "Purple",
            "Fuchsia",
            "Rose",
            "Lavender",
            "Sky",
            "Mint",
            "Lemon",
            "Sand",
            "Cocoa",
            "Cream",
        }
        if color not in valid_colors:
            logger.warning(f"Unknown marker color '{color}', defaulting to Blue")
            color = "Blue"

        if hasattr(timeline, "AddMarker"):
            timeline.AddMarker(frame, color, name, note, duration)
        else:
            raise ResolveOperationError("Timeline does not support AddMarker (API version too old)")

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "frame": frame,
            "color": color,
            "name": name,
            "note": note,
            "duration": duration,
            "message": f"Added {color} marker at frame {frame}" + (f": {name}" if name else ""),
        }

    except Exception as e:
        logger.error(f"Error adding marker: {e!s}")
        raise ResolveOperationError(f"Failed to add marker: {e!s}") from e


async def get_markers_impl(
    app,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Implementation of markers retrieval (shared between individual and portmanteau tools)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        markers = {}
        if hasattr(timeline, "GetMarkers"):
            markers = timeline.GetMarkers() or {}

        marker_list = []
        for frame, marker_info in markers.items():
            marker_list.append(
                {
                    "frame": frame,
                    "color": marker_info.get("color", ""),
                    "name": marker_info.get("name", ""),
                    "note": marker_info.get("note", ""),
                    "duration": marker_info.get("duration", 1),
                    "customData": marker_info.get("customData", ""),
                }
            )

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "markers": marker_list,
            "count": len(marker_list),
        }

    except Exception as e:
        logger.error(f"Error getting markers: {e!s}")
        raise ResolveOperationError(f"Failed to get markers: {e!s}") from e


async def delete_marker_impl(
    app,
    frame: int,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Implementation of marker deletion (shared between individual and portmanteau tools)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        if hasattr(timeline, "DeleteMarkerAtFrame"):
            timeline.DeleteMarkerAtFrame(frame)
        else:
            raise ResolveOperationError("Timeline does not support DeleteMarkerAtFrame")

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "frame": frame,
            "message": f"Deleted marker at frame {frame}",
        }

    except Exception as e:
        logger.error(f"Error deleting marker: {e!s}")
        raise ResolveOperationError(f"Failed to delete marker: {e!s}") from e


# ── Keyframe Operations ────────────────────────────────────────────


async def add_keyframe_impl(
    app,
    clip_path: str,
    property_name: str,
    frame: int,
    value: float,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Implementation of keyframe addition (shared between individual and portmanteau tools)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        current_clip = timeline.GetCurrentVideoItem()
        if not current_clip:
            raise ResolveOperationError("No clip is currently selected")

        if hasattr(current_clip, "AddKeyframe"):
            current_clip.AddKeyframe(property_name, frame, value)
        else:
            raise ResolveOperationError("Clip does not support AddKeyframe (API version too old)")

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": current_clip.GetName(),
            "property": property_name,
            "frame": frame,
            "value": value,
            "message": f"Added keyframe for '{property_name}' at frame {frame} = {value}",
        }

    except Exception as e:
        logger.error(f"Error adding keyframe: {e!s}")
        raise ResolveOperationError(f"Failed to add keyframe: {e!s}") from e


async def get_keyframes_impl(
    app,
    property_name: str,
    clip_path: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Implementation of keyframe retrieval (shared between individual and portmanteau tools)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        current_clip = timeline.GetCurrentVideoItem()
        if not current_clip:
            raise ResolveOperationError("No clip is currently selected")

        keyframes = {}
        if hasattr(current_clip, "GetKeyframeList"):
            keyframes = current_clip.GetKeyframeList(property_name) or {}

        kf_list = []
        for kf_frame, kf_value in keyframes.items():
            kf_list.append({"frame": kf_frame, "value": kf_value})

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": current_clip.GetName(),
            "property": property_name,
            "keyframes": kf_list,
            "count": len(kf_list),
        }

    except Exception as e:
        logger.error(f"Error getting keyframes: {e!s}")
        raise ResolveOperationError(f"Failed to get keyframes: {e!s}") from e


async def delete_keyframe_impl(
    app,
    property_name: str,
    frame: int,
    clip_path: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Implementation of keyframe deletion (shared between individual and portmanteau tools)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        current_clip = timeline.GetCurrentVideoItem()
        if not current_clip:
            raise ResolveOperationError("No clip is currently selected")

        if hasattr(current_clip, "DeleteKeyframe"):
            current_clip.DeleteKeyframe(property_name, frame)
        else:
            raise ResolveOperationError("Clip does not support DeleteKeyframe")

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": current_clip.GetName(),
            "property": property_name,
            "frame": frame,
            "message": f"Deleted keyframe for '{property_name}' at frame {frame}",
        }

    except Exception as e:
        logger.error(f"Error deleting keyframe: {e!s}")
        raise ResolveOperationError(f"Failed to delete keyframe: {e!s}") from e


def register_tools(app):
    """Register timeline management tools with the FastMCP app."""

    @app.tool()
    async def create_timeline(
        name: str,
        frame_rate: float = 24.0,
        width: int = 1920,
        height: int = 1080,
        start_frame: int = 0,
        project_name: str | None = None,
    ) -> dict[str, Any]:
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
                timeline.SetSetting("timelineFrameRate", str(frame_rate))
                timeline.SetSetting("timelineResolutionWidth", str(width))
                timeline.SetSetting("timelineResolutionHeight", str(height))
                timeline.SetSetting("timelineStartFrame", str(start_frame))

                # Save the project
                project_manager.SaveProject()

                return {
                    "status": "success",
                    "message": f"Timeline '{name}' created successfully",
                    "timeline": {
                        "name": name,
                        "frame_rate": frame_rate,
                        "resolution": f"{width}x{height}",
                        "start_frame": start_frame,
                    },
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to create timeline: {e!s}") from e

    @app.tool()
    async def get_timeline_info(timeline_name: str | None = None) -> dict[str, Any]:
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
                frame_rate = float(timeline.GetSetting("timelineFrameRate") or "24.0")
                width = int(timeline.GetSetting("timelineResolutionWidth") or "1920")
                height = int(timeline.GetSetting("timelineResolutionHeight") or "1080")
                start_frame = int(timeline.GetSetting("timelineStartFrame") or "0")
                end_frame = int(timeline.GetEndFrame() or "0")

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
                            "items": [],
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
                        "tracks": tracks,
                    },
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to get timeline info: {e!s}") from e

    @app.tool()
    async def add_clip_to_timeline(
        clip_path: str,
        track_index: int = 1,
        track_type: TrackType = TrackType.VIDEO,
        start_frame: int | None = None,
        timeline_name: str | None = None,
    ) -> dict[str, Any]:
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
                insert_info = [
                    {
                        "mediaPoolItem": clips[0],
                        "trackIndex": track_index - 1,  # Convert to 0-based
                        "startFrame": 0,
                    }
                ]

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
                        "start_frame": start_frame,
                    },
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to add clip to timeline: {e!s}") from e

    @app.tool()
    async def cut_clip(
        frame: int,
        track_index: int,
        track_type: TrackType = TrackType.VIDEO,
        timeline_name: str | None = None,
    ) -> dict[str, Any]:
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
                    "message": f"Cut performed at frame {frame} on {track_type_str} track {track_index}",
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to cut clip: {e!s}") from e

    @app.tool()
    async def set_timeline_playhead(frame: int, timeline_name: str | None = None) -> dict[str, Any]:
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
                    "frame": frame,
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to set playhead position: {e!s}") from e

    @app.tool()
    async def add_timeline_marker(
        frame: int,
        color: str = "Blue",
        name: str = "",
        note: str = "",
        duration: int = 1,
        timeline_name: str | None = None,
    ) -> dict[str, Any]:
        """Add a marker at a specific frame in the timeline."""
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                valid_colors = {
                    "Blue",
                    "Cyan",
                    "Green",
                    "Yellow",
                    "Red",
                    "Pink",
                    "Purple",
                    "Fuchsia",
                    "Rose",
                    "Lavender",
                    "Sky",
                    "Mint",
                    "Lemon",
                    "Sand",
                    "Cocoa",
                    "Cream",
                }
                if color not in valid_colors:
                    color = "Blue"
                if hasattr(timeline, "AddMarker"):
                    timeline.AddMarker(frame, color, name, note, duration)
                else:
                    raise ResolveOperationError("AddMarker not available in this API version")
                return {
                    "status": "success",
                    "timeline_name": timeline.GetName(),
                    "frame": frame,
                    "color": color,
                    "name": name,
                    "message": f"Added {color} marker at frame {frame}" + (f": {name}" if name else ""),
                }
        except Exception as e:
            raise ResolveOperationError(f"Failed to add marker: {e!s}") from e

    @app.tool()
    async def get_timeline_markers(timeline_name: str | None = None) -> dict[str, Any]:
        """Get all markers in the timeline."""
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                markers = timeline.GetMarkers() if hasattr(timeline, "GetMarkers") else {}
                marker_list = []
                for frame, info in (markers or {}).items():
                    marker_list.append(
                        {
                            "frame": frame,
                            "color": info.get("color", ""),
                            "name": info.get("name", ""),
                            "note": info.get("note", ""),
                            "duration": info.get("duration", 1),
                        }
                    )
                return {
                    "status": "success",
                    "timeline_name": timeline.GetName(),
                    "markers": marker_list,
                    "count": len(marker_list),
                }
        except Exception as e:
            raise ResolveOperationError(f"Failed to get markers: {e!s}") from e

    @app.tool()
    async def delete_timeline_marker(frame: int, timeline_name: str | None = None) -> dict[str, Any]:
        """Delete a marker at a specific frame in the timeline."""
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                if hasattr(timeline, "DeleteMarkerAtFrame"):
                    timeline.DeleteMarkerAtFrame(frame)
                else:
                    raise ResolveOperationError("DeleteMarkerAtFrame not available in this API version")
                return {
                    "status": "success",
                    "timeline_name": timeline.GetName(),
                    "frame": frame,
                    "message": f"Deleted marker at frame {frame}",
                }
        except Exception as e:
            raise ResolveOperationError(f"Failed to delete marker: {e!s}") from e

    # Add more timeline-related tools as needed
    # - Add transitions
    # - Apply effects
    # - Adjust clip properties
    # - Manage markers
    # - Etc.
