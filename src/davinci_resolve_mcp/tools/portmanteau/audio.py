"""
DaVinci Resolve Audio Portmanteau Tool.

Consolidates audio operations into a single tool.
"""
import logging
from typing import Any, Dict, List, Literal, Optional

logger = logging.getLogger(__name__)


def setup_audio_portmanteau(app):
    """Register the audio portmanteau tool."""

    @app.tool()
    async def resolve_audio(
        action: Literal["get_tracks", "add_effect", "adjust_levels", "normalize"],
        timeline_name: Optional[str] = None,
        track_index: int = 1,
        effect_type: str = "eq",
        preset: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        volume: Optional[float] = None,
        pan: Optional[float] = None,
        mute: Optional[bool] = None,
        solo: Optional[bool] = None,
        target_level: float = -23.0,
        track_indices: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive audio processing for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates 4 audio tools into 1.

        SUPPORTED ACTIONS:
        - get_tracks: Get all audio track information
        - add_effect: Add audio effect to track (requires: track_index, effect_type)
        - adjust_levels: Adjust track levels (requires: track_index)
        - normalize: Normalize audio levels

        Args:
            action: Operation to perform (get_tracks, add_effect, adjust_levels, normalize)
            timeline_name: Target timeline. Optional.
            track_index: Track index (1-based). Default: 1
            effect_type: Effect type (eq, compressor, limiter, reverb, etc). Default: eq
            preset: Effect preset name. Optional.
            parameters: Effect parameters dict. Optional.
            volume: Volume level (0.0-1.0). Used by: adjust_levels
            pan: Pan position (-1.0 to 1.0). Used by: adjust_levels
            mute: Mute track. Used by: adjust_levels
            solo: Solo track. Used by: adjust_levels
            target_level: Target LUFS level. Used by: normalize. Default: -23.0
            track_indices: Specific tracks to normalize. Used by: normalize

        Returns:
            Dict with operation results

        Examples:
            # Get audio tracks
            resolve_audio("get_tracks")

            # Add EQ effect
            resolve_audio("add_effect", track_index=1, effect_type="eq")

            # Adjust levels
            resolve_audio("adjust_levels", track_index=1, volume=0.8, pan=-0.5)

            # Normalize all tracks
            resolve_audio("normalize", target_level=-23.0)

            # Normalize specific tracks
            resolve_audio("normalize", track_indices=[1, 2, 3])
        """
        from ..audio_tools import (
            get_audio_tracks_impl as get_audio_tracks,
            add_audio_effect_impl as add_audio_effect,
            adjust_audio_levels_impl as adjust_audio_levels,
            normalize_audio_impl as normalize_audio,
            AudioEffectType,
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

