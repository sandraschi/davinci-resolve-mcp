"""
DaVinci Resolve Fairlight Portmanteau Tool.

Consolidates Fairlight (DAW) operations: open page, tracks, mute, solo, volume, EQ, sends, buses, automation.
"""

import logging
from typing import Any, Literal

from ..fairlight_tools import (
    fairlight_get_buses_impl,
    fairlight_get_timeline_tracks_impl,
    fairlight_open_page_impl,
    fairlight_set_track_mute_impl,
    fairlight_set_track_solo_impl,
    fairlight_set_track_volume_impl,
    fairlight_track_automation_impl,
    fairlight_track_eq_impl,
    fairlight_track_send_impl,
)

logger = logging.getLogger(__name__)


_MUTATING = {}

def setup_fairlight_portmanteau(app):
    """Register the Fairlight portmanteau tool."""

    @app.tool(annotations=_MUTATING)
    async def resolve_fairlight(
        operation: Literal[
            "open_page",
            "get_tracks",
            "set_mute",
            "set_solo",
            "set_volume",
            "track_eq",
            "track_send",
            "get_buses",
            "track_automation",
        ],
        timeline_name: str | None = None,
        track_index: int = 1,
        mute: bool = False,
        solo: bool = False,
        volume: float | None = None,
        # EQ params
        eq_band: int | None = None,
        eq_frequency: float | None = None,
        eq_gain_db: float | None = None,
        eq_q_factor: float | None = None,
        eq_band_type: str | None = None,
        eq_enabled: bool | None = None,
        # Send params
        bus_index: int = 1,
        send_level: float | None = None,
        send_pre_fader: bool | None = None,
        send_enabled: bool | None = None,
        # Automation params
        automation_param: str = "volume",
    ) -> dict[str, Any]:
        """
        Fairlight (DAW) operations in DaVinci Resolve.

        OPERATIONS:
        - open_page: Switch Resolve UI to the Fairlight page.
        - get_tracks: Get audio track list.
        - set_mute / set_solo / set_volume: Basic track control.
        - track_eq: Read or set EQ bands (set with eq_band + eq_frequency/gain/q/type/enabled).
        - track_send: Set track send to bus (send_level, bus_index).
        - get_buses: Get bus configuration.
        - track_automation: Get automation keyframes for a parameter.

        ## Examples
        resolve_fairlight("track_eq", track_index=1, eq_band=1, eq_gain_db=-3.5)
        resolve_fairlight("track_send", track_index=1, bus_index=1, send_level=0.75)
        resolve_fairlight("get_buses")
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
        if operation == "track_eq":
            return await fairlight_track_eq_impl(
                app, track_index, eq_band, eq_frequency, eq_gain_db, eq_q_factor, eq_band_type, eq_enabled, timeline_name
            )
        if operation == "track_send":
            return await fairlight_track_send_impl(
                app, track_index, bus_index, send_level, send_pre_fader, send_enabled, timeline_name
            )
        if operation == "get_buses":
            return await fairlight_get_buses_impl(app, timeline_name)
        if operation == "track_automation":
            return await fairlight_track_automation_impl(app, track_index, automation_param, timeline_name)
        return {"status": "error", "message": f"Unknown operation: {operation}"}

    logger.info("Registered resolve_fairlight portmanteau tool")
