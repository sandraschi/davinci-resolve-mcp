"""
DaVinci Resolve Fairlight Tools.

Fairlight is the DAW/audio page inside Resolve. Uses the same Resolve Scripting API
(OpenPage("fairlight"), timeline audio track APIs). Operations for Fairlight page,
timeline audio tracks, mute/solo, and level control.
"""

import logging
from typing import Any

from ..utils.exceptions import ResolveOperationError

logger = logging.getLogger(__name__)


async def _ensure_resolve(app) -> None:
    """
    Ensure the Resolve connection manager has an active Scripting API session.

    Raises:
        ResolveOperationError: If the manager is missing or connection fails.
    """
    connection = app.state.connection_manager
    if not connection:
        raise ResolveOperationError("Connection manager not initialized")
    if not await connection.ensure_connection():
        raise ResolveOperationError("Not connected to DaVinci Resolve")


async def fairlight_open_page_impl(app) -> dict[str, Any]:
    """Switch Resolve UI to the Fairlight page."""
    try:
        await _ensure_resolve(app)
        connection = app.state.connection_manager
        resolve = connection.get_connection()
        if hasattr(resolve, "OpenPage"):
            resolve.OpenPage("fairlight")
            return {"status": "success", "message": "Switched to Fairlight page"}
        return {"status": "success", "message": "OpenPage not available in this API version"}
    except Exception as e:
        logger.exception("fairlight_open_page failed")
        raise ResolveOperationError(str(e)) from e


async def fairlight_get_timeline_tracks_impl(
    app, timeline_name: str | None = None
) -> dict[str, Any]:
    """Get audio track list for current or named timeline (Fairlight context)."""
    try:
        await _ensure_resolve(app)
        connection = app.state.connection_manager
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
            name = (
                timeline.GetTrackName("audio", i)
                if hasattr(timeline, "GetTrackName")
                else f"Audio {i}"
            )
            tracks.append(
                {
                    "index": i,
                    "name": name or f"Audio {i}",
                    "muted": timeline.GetIsTrackMuted("audio", i)
                    if hasattr(timeline, "GetIsTrackMuted")
                    else False,
                    "solo": timeline.GetIsTrackSolo("audio", i)
                    if hasattr(timeline, "GetIsTrackSolo")
                    else False,
                    "locked": timeline.GetIsTrackLocked("audio", i)
                    if hasattr(timeline, "GetIsTrackLocked")
                    else False,
                }
            )
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
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Set mute state for an audio track."""
    try:
        await _ensure_resolve(app)
        connection = app.state.connection_manager
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = (
            project.GetTimelineByName(timeline_name)
            if timeline_name
            else project.GetCurrentTimeline()
        )
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
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Set solo state for an audio track."""
    try:
        await _ensure_resolve(app)
        connection = app.state.connection_manager
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = (
            project.GetTimelineByName(timeline_name)
            if timeline_name
            else project.GetCurrentTimeline()
        )
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
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Set volume for an audio track (0.0 to 2.0)."""
    try:
        await _ensure_resolve(app)
        connection = app.state.connection_manager
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = (
            project.GetTimelineByName(timeline_name)
            if timeline_name
            else project.GetCurrentTimeline()
        )
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


# ── Fairlight Depth: EQ, Sends, Buses, Automation ────────────────────


async def fairlight_track_eq_impl(
    app,
    track_index: int,
    band: int | None = None,
    frequency: float | None = None,
    gain_db: float | None = None,
    q_factor: float | None = None,
    band_type: str | None = None,
    enabled: bool | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Get or set EQ parameters on an audio track via Fusion AudioEQ tool."""
    try:
        await _ensure_resolve(app)
        connection = app.state.connection_manager
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = project.GetTimelineByName(timeline_name) if timeline_name else project.GetCurrentTimeline()
        if not timeline:
            raise ResolveOperationError("No timeline is currently open")

        resolve = connection.get_connection()
        fusion = resolve.Fusion() if hasattr(resolve, "Fusion") else None
        if not fusion:
            raise ResolveOperationError("Could not access Fusion interface")

        comp = fusion.GetCurrentComp()
        if not comp:
            raise ResolveOperationError("Could not access current composition")

        eq_node = comp.FindTool("AudioEQ")
        if not eq_node:
            eq_node = comp.AddTool("AudioEQ", -1, -1)
            if not eq_node:
                raise ResolveOperationError("Failed to create AudioEQ node")

        if band is not None and any(p is not None for p in [frequency, gain_db, q_factor, band_type, enabled]):
            changes = {}
            if frequency is not None and hasattr(eq_node, f"Band{band}Frequency"):
                setattr(eq_node, f"Band{band}Frequency", frequency)
                changes["frequency"] = frequency
            if gain_db is not None and hasattr(eq_node, f"Band{band}Gain"):
                setattr(eq_node, f"Band{band}Gain", gain_db)
                changes["gain_db"] = gain_db
            if q_factor is not None and hasattr(eq_node, f"Band{band}Q"):
                setattr(eq_node, f"Band{band}Q", q_factor)
                changes["q_factor"] = q_factor
            if band_type is not None and hasattr(eq_node, f"Band{band}Type"):
                setattr(eq_node, f"Band{band}Type", band_type)
                changes["band_type"] = band_type
            if enabled is not None and hasattr(eq_node, f"Band{band}Enabled"):
                setattr(eq_node, f"Band{band}Enabled", enabled)
                changes["enabled"] = enabled
            return {"status": "success", "track_index": track_index, "band": band, "changes": changes, "message": f"EQ band {band} updated"}
        else:
            bands = []
            for b in range(1, 7):
                b_info = {"band": b}
                for prop in ["Frequency", "Gain", "Q", "Type", "Enabled"]:
                    attr = f"Band{b}{prop}"
                    if hasattr(eq_node, attr):
                        b_info[prop.lower()] = getattr(eq_node, attr)
                bands.append(b_info)
            return {"status": "success", "track_index": track_index, "eq_bands": bands, "message": f"EQ read from track {track_index}"}

    except Exception as e:
        logger.exception("fairlight_track_eq failed")
        raise ResolveOperationError(str(e)) from e


async def fairlight_track_send_impl(
    app,
    track_index: int,
    bus_index: int = 1,
    level: float | None = None,
    pre_fader: bool | None = None,
    enabled: bool | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Get or set send level from an audio track to a bus."""
    try:
        await _ensure_resolve(app)
        connection = app.state.connection_manager
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = project.GetTimelineByName(timeline_name) if timeline_name else project.GetCurrentTimeline()
        if not timeline:
            raise ResolveOperationError("No timeline is currently open")

        changes = {}
        if level is not None:
            send_prop = f"send{track_index}Level{bus_index}"
            if hasattr(timeline, "SetTrackProperty"):
                timeline.SetTrackProperty(send_prop, "audio", str(level))
                changes["level"] = level
        if enabled is not None:
            send_prop = f"send{track_index}Enable{bus_index}"
            if hasattr(timeline, "SetTrackProperty"):
                timeline.SetTrackProperty(send_prop, "audio", "1" if enabled else "0")
                changes["enabled"] = enabled
        if pre_fader is not None:
            send_prop = f"send{track_index}Pre{bus_index}"
            if hasattr(timeline, "SetTrackProperty"):
                timeline.SetTrackProperty(send_prop, "audio", "1" if pre_fader else "0")
                changes["pre_fader"] = pre_fader

        return {"status": "success", "track_index": track_index, "bus_index": bus_index, "changes": changes, "message": f"Send {track_index}->Bus{bus_index} updated"}

    except Exception as e:
        logger.exception("fairlight_track_send failed")
        raise ResolveOperationError(str(e)) from e


async def fairlight_get_buses_impl(
    app,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Get bus/master channel configuration for the timeline."""
    try:
        await _ensure_resolve(app)
        connection = app.state.connection_manager
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = project.GetTimelineByName(timeline_name) if timeline_name else project.GetCurrentTimeline()
        if not timeline:
            raise ResolveOperationError("No timeline is currently open")

        buses = []
        for bus_type in ["Main", "Sub", "Aux", "Master"]:
            try:
                bus_count_prop = f"bus{bus_type}Count"
                if hasattr(timeline, "GetSetting"):
                    count = int(timeline.GetSetting(bus_count_prop) or "0")
                else:
                    count = 0
                for i in range(1, count + 1):
                    buses.append({"index": i, "type": bus_type, "name": f"{bus_type} {i}"})
            except Exception:
                pass

        if not buses:
            buses.append({"index": 1, "type": "Master", "name": "Master"})

        return {"status": "success", "timeline_name": timeline.GetName(), "buses": buses, "count": len(buses)}

    except Exception as e:
        logger.exception("fairlight_get_buses failed")
        raise ResolveOperationError(str(e)) from e


async def fairlight_track_automation_impl(
    app,
    track_index: int,
    parameter: str = "volume",
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Get automation data for an audio track parameter."""
    try:
        await _ensure_resolve(app)
        connection = app.state.connection_manager
        project = connection.get_current_project()
        if not project:
            raise ResolveOperationError("No project is currently open")
        timeline = project.GetTimelineByName(timeline_name) if timeline_name else project.GetCurrentTimeline()
        if not timeline:
            raise ResolveOperationError("No timeline is currently open")

        resolve = connection.get_connection()
        fusion = resolve.Fusion() if hasattr(resolve, "Fusion") else None
        if not fusion:
            return {"status": "success", "track_index": track_index, "parameter": parameter, "keyframes": [], "message": "Fusion automation not available"}

        comp = fusion.GetCurrentComp()
        if not comp:
            return {"status": "success", "track_index": track_index, "parameter": parameter, "keyframes": [], "message": "No composition"}

        param_map = {
            "volume": "AudioVolume",
            "pan": "AudioPan",
            "mute": "AudioMute",
            "eq_band1_gain": "AudioEQBand1Gain",
        }

        tool_name = param_map.get(parameter.lower(), "AudioVolume")
        tool = comp.FindTool(tool_name)
        if not tool:
            return {"status": "success", "track_index": track_index, "parameter": parameter, "keyframes": [], "message": f"No automation tool found for '{parameter}'"}

        keyframes = {}
        if hasattr(tool, "GetKeyframeList"):
            keyframes = tool.GetKeyframeList("Value") or {}

        kf_list = [{"frame": k, "value": v} for k, v in keyframes.items()]

        return {"status": "success", "track_index": track_index, "parameter": parameter, "keyframes": kf_list, "count": len(kf_list)}

    except Exception as e:
        logger.exception("fairlight_track_automation failed")
        raise ResolveOperationError(str(e)) from e
