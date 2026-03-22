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
        action: Literal["create", "info", "add_clip", "cut", "set_playhead"],
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
    ) -> dict[str, Any]:
        """
        Comprehensive timeline editing for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates 5 timeline tools into 1.

        SUPPORTED ACTIONS:
        - create: Create new timeline (requires: name)
        - info: Get timeline information (optional: timeline_name)
        - add_clip: Add clip to timeline (requires: clip_path)
        - cut: Cut clip at frame (requires: frame, track_index)
        - set_playhead: Set playhead position (requires: frame)

        Args:
            action: Operation to perform (create, info, add_clip, cut, set_playhead)
            name: Timeline name. Required for: create
            timeline_name: Target timeline name. Optional for most actions.
            frame_rate: Frame rate. Used by: create. Default: 24.0
            width: Width in pixels. Used by: create. Default: 1920
            height: Height in pixels. Used by: create. Default: 1080
            start_frame: Starting frame. Used by: create, add_clip. Default: 0
            clip_path: Path to clip. Required for: add_clip
            track_index: Track index (1-based). Used by: add_clip, cut. Default: 1
            track_type: Track type (video/audio). Used by: add_clip, cut. Default: video
            frame: Frame number. Required for: cut, set_playhead

        Returns:
            Dict with operation results

        Examples:
            # Create 4K timeline
            resolve_timeline("create", name="Main Edit", width=3840, height=2160)

            # Get timeline info
            resolve_timeline("info")

            # Add clip to timeline
            resolve_timeline("add_clip", clip_path="C:/Videos/scene1.mp4", track_index=1)

            # Cut clip at frame 100
            resolve_timeline("cut", frame=100, track_index=1)

            # Set playhead
            resolve_timeline("set_playhead", frame=500)
        """
        from ..timeline_tools import (
            TrackType,
        )
        from ..timeline_tools import (
            add_clip_to_timeline_impl as add_clip_to_timeline,
        )
        from ..timeline_tools import (
            create_timeline_impl as create_timeline,
        )
        from ..timeline_tools import (
            cut_clip_impl as cut_clip,
        )
        from ..timeline_tools import (
            get_timeline_info_impl as get_timeline_info,
        )
        from ..timeline_tools import (
            set_timeline_playhead_impl as set_timeline_playhead,
        )

        # Map track_type string to enum
        track_type_enum = TrackType.VIDEO if track_type.lower() == "video" else TrackType.AUDIO

        if action == "create":
            if not name:
                return {"status": "error", "message": "name is required for create action"}
            return await create_timeline(
                app, name, frame_rate, width, height, start_frame, timeline_name
            )

        elif action == "info":
            return await get_timeline_info(app, timeline_name)

        elif action == "add_clip":
            if not clip_path:
                return {"status": "error", "message": "clip_path is required for add_clip action"}
            return await add_clip_to_timeline(
                app, clip_path, track_index, track_type_enum, start_frame, timeline_name
            )

        elif action == "cut":
            if frame is None:
                return {"status": "error", "message": "frame is required for cut action"}
            return await cut_clip(app, frame, track_index, track_type_enum, timeline_name)

        elif action == "set_playhead":
            if frame is None:
                return {"status": "error", "message": "frame is required for set_playhead action"}
            return await set_timeline_playhead(app, frame, timeline_name)

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_timeline portmanteau tool")
