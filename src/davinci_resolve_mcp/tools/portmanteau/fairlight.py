"""
DaVinci Resolve Fairlight Portmanteau Tool.

Consolidates Fairlight (DAW) operations: open page, get tracks, mute, solo, volume.
"""

import logging
from typing import Any, Literal

from ..fairlight_tools import (
    fairlight_get_timeline_tracks_impl,
    fairlight_open_page_impl,
    fairlight_set_track_mute_impl,
    fairlight_set_track_solo_impl,
    fairlight_set_track_volume_impl,
)

logger = logging.getLogger(__name__)


def setup_fairlight_portmanteau(app):
    """Register the Fairlight portmanteau tool."""

    @app.tool()
    async def resolve_fairlight(
        operation: Literal[
            "open_page",
            "get_tracks",
            "set_mute",
            "set_solo",
            "set_volume",
        ],
        timeline_name: str | None = None,
        track_index: int = 1,
        mute: bool = False,
        solo: bool = False,
        volume: float | None = None,
    ) -> dict[str, Any]:
        """
        Fairlight (DAW) operations in DaVinci Resolve.

        PORTMANTEAU: Single tool for Fairlight page and timeline audio.

        OPERATIONS:
        - open_page: Switch Resolve UI to the Fairlight page.
        - get_tracks: Get audio track list for current (or named) timeline.
        - set_mute: Mute/unmute a track (track_index, mute=True/False).
        - set_solo: Solo/unsolo a track (track_index, solo=True/False).
        - set_volume: Set track volume 0.0-2.0 (track_index, volume).

        Args:
            operation: open_page | get_tracks | set_mute | set_solo | set_volume
            timeline_name: Optional timeline name (default: current).
            track_index: 1-based track index for set_mute/set_solo/set_volume.
            mute: Mute state for set_mute.
            solo: Solo state for set_solo.
            volume: Volume level (0.0-2.0) for set_volume.

        Returns:
            Dict with status and operation result.
        """
        if operation == "open_page":
            return await fairlight_open_page_impl(app)
        if operation == "get_tracks":
            return await fairlight_get_timeline_tracks_impl(app, timeline_name)
        if operation == "set_mute":
            return await fairlight_set_track_mute_impl(app, track_index, mute, timeline_name)
        if operation == "set_solo":
            return await fairlight_set_track_solo_impl(app, track_index, solo, timeline_name)
        if operation == "set_volume":
            if volume is None:
                return {"status": "error", "message": "set_volume requires volume"}
            return await fairlight_set_track_volume_impl(app, track_index, volume, timeline_name)
        return {"status": "error", "message": f"Unknown operation: {operation}"}

    logger.info("Registered resolve_fairlight portmanteau tool")
