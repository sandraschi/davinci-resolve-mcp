"""
DaVinci Resolve Audio Portmanteau Tool.

Consolidates audio operations into a single tool.
"""

import logging
from typing import Annotated, Any, Literal

# fastmcp.tools.tool resolves via vendored mcp.server.fastmcp at runtime (shadowed by tool() fn)
from fastmcp.tools.tool import ToolAnnotations  # pyright: ignore[reportMissingImports]
from pydantic import Field

logger = logging.getLogger(__name__)


_MUTATING = ToolAnnotations(readOnlyHint=False, destructiveHint=False)


def setup_audio_portmanteau(app):
    """Register the audio portmanteau tool."""

    @app.tool(annotations=_MUTATING, output_schema={"type": "object"})
    async def resolve_audio(
        action: Annotated[
            Literal["get_tracks", "add_effect", "adjust_levels", "normalize"], Field(description="Operation to perform")
        ],
        timeline_name: Annotated[str | None, Field(description="Target timeline. Optional")] = None,
        track_index: Annotated[int, Field(description="1-based track index. Used by: add_effect, adjust_levels")] = 1,
        effect_type: Annotated[
            str, Field(description="Effect type (eq, compressor, limiter, reverb, ...). Used by: add_effect")
        ] = "eq",
        preset: Annotated[str | None, Field(description="Effect preset name. Used by: add_effect. Optional")] = None,
        parameters: Annotated[
            dict[str, Any] | None, Field(description="Effect parameters dict. Used by: add_effect. Optional")
        ] = None,
        volume: Annotated[float | None, Field(description="Volume level (0.0-1.0). Used by: adjust_levels")] = None,
        pan: Annotated[float | None, Field(description="Pan position (-1.0 to 1.0). Used by: adjust_levels")] = None,
        mute: Annotated[bool | None, Field(description="Mute track. Used by: adjust_levels")] = None,
        solo: Annotated[bool | None, Field(description="Solo track. Used by: adjust_levels")] = None,
        target_level: Annotated[float, Field(description="Target LUFS level. Used by: normalize")] = -23.0,
        track_indices: Annotated[
            list[int] | None, Field(description="Specific tracks to normalize. Used by: normalize")
        ] = None,
    ) -> dict[str, Any]:
        """
        Comprehensive audio processing for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates 4 audio tools into 1.

        SUPPORTED ACTIONS:
        - get_tracks: Get all audio track information
        - add_effect: Add audio effect to track (requires: track_index, effect_type)
        - adjust_levels: Adjust track levels (requires: track_index)
        - normalize: Normalize audio levels

        ## Return Format
        {"status": "success", "message": "Human-readable result", ...}
        {"status": "error", "message": "Human-readable failure reason"}

        ## Examples
        resolve_audio("get_tracks")
        resolve_audio("add_effect", track_index=1, effect_type="eq")
        resolve_audio("adjust_levels", track_index=1, volume=0.8, pan=-0.5)
        resolve_audio("normalize", target_level=-23.0)
        resolve_audio("normalize", track_indices=[1, 2, 3])
        """
        from ..audio_tools import (
            AudioEffectType,
        )
        from ..audio_tools import (
            add_audio_effect_impl as add_audio_effect,
        )
        from ..audio_tools import (
            adjust_audio_levels_impl as adjust_audio_levels,
        )
        from ..audio_tools import (
            get_audio_tracks_impl as get_audio_tracks,
        )
        from ..audio_tools import (
            normalize_audio_impl as normalize_audio,
        )

        # Map effect_type string to enum
        effect_map = {
            "eq": AudioEffectType.EQ,
            "equalizer": AudioEffectType.EQ,
            "compressor": AudioEffectType.COMPRESSOR,
            "limiter": AudioEffectType.LIMITER,
            "expander": AudioEffectType.EXPANDER,
            "gate": AudioEffectType.GATE,
            "reverb": AudioEffectType.REVERB,
            "delay": AudioEffectType.DELAY,
            "pitch_shift": AudioEffectType.PITCH_SHIFT,
            "noise_reduction": AudioEffectType.NOISE_REDUCTION,
            "normalize": AudioEffectType.NORMALIZE,
            "loudness": AudioEffectType.LOUDNESS,
        }

        if action == "get_tracks":
            return await get_audio_tracks(app, timeline_name)

        elif action == "add_effect":
            effect_enum = effect_map.get(effect_type.lower(), AudioEffectType.EQ)
            return await add_audio_effect(app, effect_enum, track_index, parameters, timeline_name)

        elif action == "adjust_levels":
            return await adjust_audio_levels(app, track_index, volume, pan, mute, timeline_name)

        elif action == "normalize":
            return await normalize_audio(app, track_indices, target_level, timeline_name)

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_audio portmanteau tool")
