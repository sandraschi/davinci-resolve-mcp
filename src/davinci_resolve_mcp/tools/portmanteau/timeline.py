"""
DaVinci Resolve Timeline Portmanteau Tool.

Consolidates timeline editing operations into a single tool.
"""

import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)


def setup_timeline_portmanteau(app):
    """Register the timeline portmanteau tool."""

    @app.tool()
    async def resolve_timeline(
        action: Literal[
            "create", "info", "add_clip", "cut", "set_playhead",
            "add_marker", "get_markers", "delete_marker",
            "add_keyframe", "get_keyframes", "delete_keyframe",
            "set_clip_property",
        ],
        name: str | None = None,
        timeline_name: str | None = None,
        frame_rate: float = 24.0,
        width: int = 1920,
        height: int = 1080,
        start_frame: int = 0,
        clip_path: str | None = None,
        track_index: int = 1,
        track_type: str = "video",
        frame: int | None = None,
        # Marker params
        color: str = "Blue",
        note: str = "",
        duration: int = 1,
        # Keyframe params
        property_name: str | None = None,
        value: float | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive timeline editing for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates timeline tools into 1.

        SUPPORTED ACTIONS:
        - create: Create new timeline (requires: name)
        - info: Get timeline information
        - add_clip: Add clip to timeline (requires: clip_path)
        - cut: Cut clip at frame (requires: frame, track_index)
        - set_playhead: Set playhead position (requires: frame)
        - add_marker: Add marker at frame (requires: frame)
        - get_markers: Get all timeline markers
        - delete_marker: Delete marker at frame (requires: frame)
        - add_keyframe: Add keyframe to clip (requires: property_name, frame, value)
        - get_keyframes: Get keyframes for property (requires: property_name)
        - delete_keyframe: Delete keyframe (requires: property_name, frame)
        - set_clip_property: Set clip property like Speed, Zoom, etc. (requires: property_name, value)

        ## Return Format
        {"status": "success", ...}

        ## Examples
        resolve_timeline("create", name="Main Edit", width=3840, height=2160)
        resolve_timeline("add_marker", frame=120, color="Red", name="VFX cue")
        resolve_timeline("add_keyframe", property_name="Zoom", frame=0, value=1.0)
        resolve_timeline("set_clip_property", property_name="Speed", value=2.0)
        """
        from ..timeline_tools import TrackType
        from ..timeline_tools import (
            add_clip_to_timeline_impl as add_clip_to_timeline,
        )
        from ..timeline_tools import (
            add_keyframe_impl as add_keyframe,
        )
        from ..timeline_tools import (
            add_marker_impl as add_marker,
        )
        from ..timeline_tools import (
            create_timeline_impl as create_timeline,
        )
        from ..timeline_tools import (
            cut_clip_impl as cut_clip,
        )
        from ..timeline_tools import (
            delete_keyframe_impl as delete_keyframe,
        )
        from ..timeline_tools import (
            delete_marker_impl as delete_marker,
        )
        from ..timeline_tools import (
            get_keyframes_impl as get_keyframes,
        )
        from ..timeline_tools import (
            get_markers_impl as get_markers,
        )
        from ..timeline_tools import (
            get_timeline_info_impl as get_timeline_info,
        )
        from ..timeline_tools import (
            set_timeline_playhead_impl as set_timeline_playhead,
        )

        track_type_enum = TrackType.VIDEO if track_type.lower() == "video" else TrackType.AUDIO

        if action == "create":
            if not name:
                return {"status": "error", "message": "name is required for create action"}
            return await create_timeline(app, name, frame_rate, width, height, start_frame, timeline_name)

        elif action == "info":
            return await get_timeline_info(app, timeline_name)

        elif action == "add_clip":
            if not clip_path:
                return {"status": "error", "message": "clip_path is required for add_clip action"}
            return await add_clip_to_timeline(app, clip_path, track_index, track_type_enum, start_frame, timeline_name)

        elif action == "cut":
            if frame is None:
                return {"status": "error", "message": "frame is required for cut action"}
            return await cut_clip(app, frame, track_index, track_type_enum, timeline_name)

        elif action == "set_playhead":
            if frame is None:
                return {"status": "error", "message": "frame is required for set_playhead action"}
            return await set_timeline_playhead(app, frame, timeline_name)

        elif action == "add_marker":
            if frame is None:
                return {"status": "error", "message": "frame is required for add_marker action"}
            return await add_marker(app, frame, color, name or "", note, duration, timeline_name)

        elif action == "get_markers":
            return await get_markers(app, timeline_name)

        elif action == "delete_marker":
            if frame is None:
                return {"status": "error", "message": "frame is required for delete_marker action"}
            return await delete_marker(app, frame, timeline_name)

        elif action == "add_keyframe":
            if not property_name or frame is None or value is None:
                return {"status": "error", "message": "property_name, frame, and value are required for add_keyframe"}
            return await add_keyframe(app, clip_path or "", property_name, frame, value, timeline_name)

        elif action == "get_keyframes":
            if not property_name:
                return {"status": "error", "message": "property_name is required for get_keyframes"}
            return await get_keyframes(app, property_name, clip_path, timeline_name)

        elif action == "delete_keyframe":
            if not property_name or frame is None:
                return {"status": "error", "message": "property_name and frame are required for delete_keyframe"}
            return await delete_keyframe(app, property_name, frame, clip_path, timeline_name)

        elif action == "set_clip_property":
            if not property_name or value is None:
                return {"status": "error", "message": "property_name and value are required for set_clip_property"}
            from ..timeline_tools import ResolveConnectionManager
            try:
                with ResolveConnectionManager() as resolve:
                    project = resolve.GetProjectManager().GetCurrentProject()
                    if not project:
                        return {"status": "error", "message": "No project is currently open"}
                    if timeline_name:
                        timeline = project.GetTimelineByName(timeline_name)
                    else:
                        timeline = project.GetCurrentTimeline()
                    if not timeline:
                        return {"status": "error", "message": "No timeline is currently open"}
                    clip = timeline.GetCurrentVideoItem()
                    if not clip:
                        return {"status": "error", "message": "No clip is currently selected"}
                    clip.SetClipProperty(property_name, str(value))
                    return {"status": "success", "property": property_name, "value": value, "message": f"Set {property_name}={value}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_timeline portmanteau tool")
