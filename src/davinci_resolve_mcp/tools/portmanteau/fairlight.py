"""
DaVinci Resolve Fairlight Portmanteau Tool.

Consolidates Fairlight (DAW) operations: open page, tracks, mute, solo, volume, EQ, sends, buses, automation.
"""

import logging
from typing import Annotated, Any, Literal

from fastmcp.tools.tool import ToolAnnotations
from pydantic import Field

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


_MUTATING = ToolAnnotations(readOnlyHint=False, destructiveHint=False)


def setup_fairlight_portmanteau(app):
    """Register the Fairlight portmanteau tool."""

    @app.tool(annotations=_MUTATING)
    async def resolve_fairlight(
        operation: Annotated[
            Literal[
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
            Field(description="Operation to perform"),
        ],
        timeline_name: Annotated[str | None, Field(description="Target timeline. Optional")] = None,
        track_index: Annotated[int, Field(description="1-based track index")] = 1,
        mute: Annotated[bool, Field(description="Mute state. Used by: set_mute")] = False,
        solo: Annotated[bool, Field(description="Solo state. Used by: set_solo")] = False,
        volume: Annotated[float | None, Field(description="Volume (0.0-1.0). Required for: set_volume")] = None,
        # EQ params
        eq_band: Annotated[int | None, Field(description="EQ band number. Used by: track_eq")] = None,
        eq_frequency: Annotated[float | None, Field(description="EQ frequency Hz. Used by: track_eq")] = None,
        eq_gain_db: Annotated[float | None, Field(description="EQ gain dB. Used by: track_eq")] = None,
        eq_q_factor: Annotated[float | None, Field(description="EQ Q factor. Used by: track_eq")] = None,
        eq_band_type: Annotated[str | None, Field(description="EQ band type. Used by: track_eq")] = None,
        eq_enabled: Annotated[bool | None, Field(description="EQ enabled flag. Used by: track_eq")] = None,
        # Send params
        bus_index: Annotated[int, Field(description="Target bus index. Used by: track_send")] = 1,
        send_level: Annotated[float | None, Field(description="Send level. Used by: track_send")] = None,
        send_pre_fader: Annotated[bool | None, Field(description="Pre-fader send. Used by: track_send")] = None,
        send_enabled: Annotated[bool | None, Field(description="Send enabled. Used by: track_send")] = None,
        # Automation params
        automation_param: Annotated[
            str, Field(description="Automation parameter. Used by: track_automation")
        ] = "volume",
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

        ## Return Format
        {"status": "success", "message": "Human-readable result", ...}
        {"status": "error", "message": "Human-readable failure reason"}

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
                app,
                track_index,
                eq_band,
                eq_frequency,
                eq_gain_db,
                eq_q_factor,
                eq_band_type,
                eq_enabled,
                timeline_name,
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
