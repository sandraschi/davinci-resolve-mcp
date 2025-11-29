"""
DaVinci Resolve Timeline Portmanteau Tool.

Consolidates timeline editing operations into a single tool.
"""
import logging
from typing import Any, Dict, Literal, Optional

logger = logging.getLogger(__name__)


def setup_timeline_portmanteau(app):
    """Register the timeline portmanteau tool."""

    @app.tool()
    async def resolve_timeline(
        action: Literal["create", "info", "add_clip", "cut", "set_playhead"],
        name: Optional[str] = None,
        timeline_name: Optional[str] = None,
        frame_rate: float = 24.0,
        width: int = 1920,
        height: int = 1080,
        start_frame: int = 0,
        clip_path: Optional[str] = None,
        track_index: int = 1,
        track_type: str = "video",
        frame: Optional[int] = None,
    ) -> Dict[str, Any]:
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
            create_timeline,
            get_timeline_info,
            add_clip_to_timeline,
            cut_clip,
            set_timeline_playhead,
            TrackType,
        )

        # Map track_type string to enum
        track_type_enum = TrackType.VIDEO if track_type.lower() == "video" else TrackType.AUDIO

        if action == "create":
            if not name:
                return {"status": "error", "message": "name is required for create action"}
            return await create_timeline(name, frame_rate, width, height, start_frame, timeline_name)

        elif action == "info":
            return await get_timeline_info(timeline_name)

        elif action == "add_clip":
            if not clip_path:
                return {"status": "error", "message": "clip_path is required for add_clip action"}
            return await add_clip_to_timeline(clip_path, track_index, track_type_enum, start_frame if start_frame else None, timeline_name)

        elif action == "cut":
            if frame is None:
                return {"status": "error", "message": "frame is required for cut action"}
            return await cut_clip(frame, track_index, track_type_enum, timeline_name)

        elif action == "set_playhead":
            if frame is None:
                return {"status": "error", "message": "frame is required for set_playhead action"}
            return await set_timeline_playhead(frame, timeline_name)

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_timeline portmanteau tool")

