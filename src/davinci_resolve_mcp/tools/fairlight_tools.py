"""
DaVinci Resolve Fairlight Tools.

Fairlight is the DAW/audio page inside Resolve. Uses the same Resolve Scripting API
(OpenPage("fairlight"), timeline audio track APIs). Operations for Fairlight page,
timeline audio tracks, mute/solo, and level control.
"""
import logging
from typing import Any, Dict, List, Optional

from ..utils.exceptions import ResolveOperationError

logger = logging.getLogger(__name__)


async def fairlight_open_page_impl(app) -> Dict[str, Any]:
    """Switch Resolve UI to the Fairlight page."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")
        resolve = connection.get_connection()
        if hasattr(resolve, "OpenPage"):
            resolve.OpenPage("fairlight")
            return {"status": "success", "message": "Switched to Fairlight page"}
        return {"status": "success", "message": "OpenPage not available in this API version"}
    except Exception as e:
        logger.exception("fairlight_open_page failed")
        raise ResolveOperationError(str(e)) from e


async def fairlight_get_timeline_tracks_impl(
    app, timeline_name: Optional[str] = None
) -> Dict[str, Any]:
    """Get audio track list for current or named timeline (Fairlight context)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
        else:
            timeline = project.GetCurrentTimeline()
        if not timeline:
            raise ResolveOperationError("No timeline is currently open")
        audio_count = timeline.GetTrackCount("audio")
        tracks = []
        for i in range(1, audio_count + 1):
            name = timeline.GetTrackName("audio", i) if hasattr(timeline, "GetTrackName") else f"Audio {i}"
            tracks.append({
                "index": i,
                "name": name or f"Audio {i}",
                "muted": timeline.GetIsTrackMuted("audio", i) if hasattr(timeline, "GetIsTrackMuted") else False,
                "solo": timeline.GetIsTrackSolo("audio", i) if hasattr(timeline, "GetIsTrackSolo") else False,
                "locked": timeline.GetIsTrackLocked("audio", i) if hasattr(timeline, "GetIsTrackLocked") else False,
            })
        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "track_count": len(tracks),
            "tracks": tracks,
        }
    except Exception as e:
        logger.exception("fairlight_get_timeline_tracks failed")
        raise ResolveOperationError(str(e)) from e


async def fairlight_set_track_mute_impl(
    app,
    track_index: int,
    mute: bool,
    timeline_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Set mute state for an audio track."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = project.GetTimelineByName(timeline_name) if timeline_name else project.GetCurrentTimeline()
        if not timeline:
            raise ResolveOperationError("No timeline is currently open")
        if hasattr(timeline, "SetTrackMute"):
            timeline.SetTrackMute("audio", track_index, mute)
            return {"status": "success", "track_index": track_index, "mute": mute}
        return {"status": "error", "message": "SetTrackMute not available"}
    except Exception as e:
        logger.exception("fairlight_set_track_mute failed")
        raise ResolveOperationError(str(e)) from e


async def fairlight_set_track_solo_impl(
    app,
    track_index: int,
    solo: bool,
    timeline_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Set solo state for an audio track."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = project.GetTimelineByName(timeline_name) if timeline_name else project.GetCurrentTimeline()
        if not timeline:
            raise ResolveOperationError("No timeline is currently open")
        if hasattr(timeline, "SetTrackSolo"):
            timeline.SetTrackSolo("audio", track_index, solo)
            return {"status": "success", "track_index": track_index, "solo": solo}
        return {"status": "error", "message": "SetTrackSolo not available"}
    except Exception as e:
        logger.exception("fairlight_set_track_solo failed")
        raise ResolveOperationError(str(e)) from e


async def fairlight_set_track_volume_impl(
    app,
    track_index: int,
    volume: float,
    timeline_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Set volume for an audio track (0.0 to 2.0)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = project.GetTimelineByName(timeline_name) if timeline_name else project.GetCurrentTimeline()
        if not timeline:
            raise ResolveOperationError("No timeline is currently open")
        volume = max(0.0, min(2.0, float(volume)))
        if hasattr(timeline, "SetTrackVolume"):
            timeline.SetTrackVolume("audio", track_index, volume)
            return {"status": "success", "track_index": track_index, "volume": volume}
        return {"status": "error", "message": "SetTrackVolume not available"}
    except Exception as e:
        logger.exception("fairlight_set_track_volume failed")
        raise ResolveOperationError(str(e)) from e
