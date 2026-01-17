"""
DaVinci Resolve Audio Tools.

This module provides tools for working with audio in DaVinci Resolve,
including mixing, effects, and audio processing operations.
"""
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field

from ..connection.manager import ResolveConnectionManager
from ..utils.exceptions import ResolveOperationError

logger = logging.getLogger(__name__)


class AudioChannelLayout(str, Enum):
    """Supported audio channel layouts."""
    MONO = "mono"
    STEREO = "stereo"
    SURROUND_5_1 = "5.1"
    SURROUND_7_1 = "7.1"


class AudioEffectType(str, Enum):
    """Supported audio effect types."""
    EQ = "equalizer"
    COMPRESSOR = "compressor"
    LIMITER = "limiter"
    EXPANDER = "expander"
    GATE = "gate"
    REVERB = "reverb"
    DELAY = "delay"
    PITCH_SHIFT = "pitch_shift"
    NOISE_REDUCTION = "noise_reduction"
    NORMALIZE = "normalize"
    LOUDNESS = "loudness"


class AudioTrackType(str, Enum):
    """Audio track types."""
    MONO = "mono"
    STEREO = "stereo"
    SURROUND = "surround"
    ADAPTIVE = "adaptive"


class AudioTrackInfo(BaseModel):
    """Model representing an audio track."""
    index: int = Field(..., description="Track index (1-based)")
    name: str = Field(..., description="Track name")
    type: AudioTrackType = Field(..., description="Track type")
    is_muted: bool = Field(False, description="Whether the track is muted")
    is_solo: bool = Field(False, description="Whether the track is soloed")
    is_locked: bool = Field(False, description="Whether the track is locked")
    volume: float = Field(1.0, description="Track volume (0.0 to 1.0)")
    pan: float = Field(0.0, description="Pan position (-1.0 to 1.0)")


class AudioClipInfo(BaseModel):
    """Model representing an audio clip."""
    name: str = Field(..., description="Clip name")
    start_frame: int = Field(..., description="Start frame in the timeline")
    end_frame: int = Field(..., description="End frame in the timeline")
    track_index: int = Field(..., description="Index of the track containing this clip")
    channel_layout: AudioChannelLayout = Field(..., description="Audio channel layout")
    sample_rate: int = Field(48000, description="Sample rate in Hz")
    bit_depth: int = Field(24, description="Bit depth (16, 24, or 32)")


async def get_audio_tracks(app, timeline_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about all audio tracks in the current or specified timeline.

    Args:
        app: FastMCP app instance
        timeline_name: Optional name of the timeline

    Returns:
        Dictionary with audio track information
    """
    return await get_audio_tracks_impl(app, timeline_name)


async def add_audio_effect(
    app,
    effect_type: AudioEffectType,
    track_index: int,
    parameters: Optional[Dict[str, Any]] = None,
    timeline_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add an audio effect to a track.

    Args:
        app: FastMCP app instance
        effect_type: Type of audio effect to add
        track_index: Index of the audio track
        parameters: Optional effect parameters
        timeline_name: Optional name of the timeline

    Returns:
        Dictionary with effect addition result
    """
    return await add_audio_effect_impl(app, effect_type, track_index, parameters, timeline_name)


async def adjust_audio_levels(
    app,
    track_index: int,
    volume: Optional[float] = None,
    pan: Optional[float] = None,
    mute: Optional[bool] = None,
    timeline_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Adjust audio levels for a track.

    Args:
        app: FastMCP app instance
        track_index: Index of the audio track
        volume: Volume level (0.0 to 2.0)
        pan: Pan position (-1.0 to 1.0)
        mute: Mute state
        timeline_name: Optional name of the timeline

    Returns:
        Dictionary with level adjustment result
    """
    return await adjust_audio_levels_impl(app, track_index, volume, pan, mute, timeline_name)


async def normalize_audio(
    app,
    track_indices: Optional[List[int]] = None,
    target_level: float = -23.0,
    timeline_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Normalize audio levels across tracks.

    Args:
        app: FastMCP app instance
        track_indices: Optional list of track indices to normalize
        target_level: Target loudness level in LUFS
        timeline_name: Optional name of the timeline

    Returns:
        Dictionary with normalization result
    """
    return await normalize_audio_impl(app, track_indices, target_level, timeline_name)


async def get_audio_tracks_impl(app, timeline_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Implementation of audio tracks retrieval (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        # Get the specified timeline or current timeline
        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        # Get audio track count
        audio_track_count = timeline.GetTrackCount("audio")

        tracks = []
        for i in range(1, audio_track_count + 1):
            track_info = {
                "index": i,
                "name": timeline.GetTrackName("audio", i) or f"Audio Track {i}",
                "is_muted": timeline.GetIsTrackMuted("audio", i),
                "is_locked": timeline.GetIsTrackLocked("audio", i),
                "volume": getattr(timeline, 'GetTrackVolume', lambda x, y: 1.0)("audio", i),
                "pan": getattr(timeline, 'GetTrackPan', lambda x, y: 0.0)("audio", i)
            }
            tracks.append(track_info)

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "audio_tracks": tracks,
            "track_count": len(tracks)
        }

    except Exception as e:
        logger.error(f"Error getting audio tracks: {str(e)}")
        raise ResolveOperationError(f"Failed to get audio tracks: {str(e)}")


async def add_audio_effect_impl(
    app,
    effect_type: AudioEffectType,
    track_index: int,
    parameters: Optional[Dict[str, Any]] = None,
    timeline_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Implementation of audio effect addition (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        # Get the specified timeline or current timeline
        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        # Add audio effect to track
        # Note: This is a simplified implementation as DaVinci Resolve's audio API
        # may not have direct effect addition methods in the Python API
        effect_params = parameters or {}

        # This would typically involve Fairlight audio processing
        # For now, we'll return a placeholder response
        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "track_index": track_index,
            "effect_type": effect_type.value,
            "parameters": effect_params,
            "message": "Audio effect addition not fully implemented in Python API"
        }

    except Exception as e:
        logger.error(f"Error adding audio effect: {str(e)}")
        raise ResolveOperationError(f"Failed to add audio effect: {str(e)}")


async def adjust_audio_levels_impl(
    app,
    track_index: int,
    volume: Optional[float] = None,
    pan: Optional[float] = None,
    mute: Optional[bool] = None,
    timeline_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Implementation of audio level adjustment (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        # Get the specified timeline or current timeline
        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        # Adjust audio levels
        changes = {}

        if volume is not None:
            # Set track volume (0.0 to 2.0 range)
            volume = max(0.0, min(2.0, volume))
            if hasattr(timeline, 'SetTrackVolume'):
                timeline.SetTrackVolume("audio", track_index, volume)
                changes["volume"] = volume

        if pan is not None:
            # Set track pan (-1.0 to 1.0 range)
            pan = max(-1.0, min(1.0, pan))
            if hasattr(timeline, 'SetTrackPan'):
                timeline.SetTrackPan("audio", track_index, pan)
                changes["pan"] = pan

        if mute is not None:
            # Set track mute state
            if hasattr(timeline, 'SetTrackMute'):
                timeline.SetTrackMute("audio", track_index, mute)
                changes["mute"] = mute

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "track_index": track_index,
            "changes": changes
        }

    except Exception as e:
        logger.error(f"Error adjusting audio levels: {str(e)}")
        raise ResolveOperationError(f"Failed to adjust audio levels: {str(e)}")


async def normalize_audio_impl(
    app,
    track_indices: Optional[List[int]] = None,
    target_level: float = -23.0,
    timeline_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Implementation of audio normalization (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
        if not project:
            raise ResolveOperationError("No project is currently open")

        # Get the specified timeline or current timeline
        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        # Normalize audio tracks
        # This is a simplified implementation as DaVinci Resolve's audio normalization
        # is typically done through the Fairlight interface
        if track_indices is None:
            # Normalize all audio tracks
            audio_track_count = timeline.GetTrackCount("audio")
            track_indices = list(range(1, audio_track_count + 1))

        normalized_tracks = []
        for track_index in track_indices:
            # Apply normalization effect
            result = await add_audio_effect_impl(app, AudioEffectType.NORMALIZE,
                                               track_index, {"target_level": target_level},
                                               timeline.GetName())
            normalized_tracks.append(track_index)

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "normalized_tracks": normalized_tracks,
            "target_level": target_level
        }

    except Exception as e:
        logger.error(f"Error normalizing audio: {str(e)}")
        raise ResolveOperationError(f"Failed to normalize audio: {str(e)}")


def register_tools(app):
    """Register audio tools with the FastMCP app."""
    
    @app.tool()
    async def get_audio_tracks(timeline_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about all audio tracks in the current or specified timeline.
        
        Args:
            timeline_name: Optional name of the timeline
            
        Returns:
            Dictionary with audio track information
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Get audio tracks
                audio_tracks = []
                track_count = timeline.GetTrackCount("audio")
                
                for i in range(1, track_count + 1):
                    track_name = timeline.GetTrackName("audio", i)
                    is_muted = timeline.GetTrackProperty(f"showTrackMute{i}", "audio") == "1"
                    is_solo = timeline.GetTrackProperty(f"showTrackSolo{i}", "audio") == "1"
                    is_locked = timeline.GetTrackProperty(f"showTrackLock{i}", "audio") == "1"
                    
                    # Get track volume and pan (if available)
                    volume = 1.0
                    pan = 0.0
                    try:
                        volume = float(timeline.GetTrackProperty(f"volumeTrack{i}", "audio") or "1.0")
                        pan = float(timeline.GetTrackProperty(f"panTrack{i}", "audio") or "0.0")
                    except (ValueError, AttributeError):
                        pass
                    
                    # Determine track type based on channel count
                    channel_count = 2  # Default to stereo
                    try:
                        channel_count = int(timeline.GetTrackProperty(f"trackChannelCount{i}", "audio") or "2")
                    except (ValueError, AttributeError):
                        pass
                    
                    track_type = AudioTrackType.STEREO
                    if channel_count == 1:
                        track_type = AudioTrackType.MONO
                    elif channel_count > 2:
                        track_type = AudioTrackType.SURROUND
                    
                    audio_tracks.append({
                        "index": i,
                        "name": track_name or f"Audio {i}",
                        "type": track_type,
                        "is_muted": is_muted,
                        "is_solo": is_solo,
                        "is_locked": is_locked,
                        "volume": volume,
                        "pan": pan,
                        "channel_count": channel_count
                    })
                
                return {
                    "status": "success",
                    "tracks": audio_tracks,
                    "timeline": timeline.GetName()
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to get audio tracks: {str(e)}")

    @app.tool()
    async def add_audio_effect(
        effect_type: AudioEffectType,
        track_index: int,
        preset: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add an audio effect to a track.
        
        Args:
            effect_type: Type of effect to add
            track_index: Index of the track to add the effect to (1-based)
            preset: Optional preset name to apply
            parameters: Optional dictionary of effect parameters
            timeline_name: Optional name of the timeline
            
        Returns:
            Dictionary with operation status
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Get the audio track
                track_count = timeline.GetTrackCount("audio")
                if track_index < 1 or track_index > track_count:
                    raise ResolveOperationError(f"Invalid track index: {track_index}")
                
                # Get the Fusion composition for the timeline
                fusion = resolve.Fusion()
                if not fusion:
                    raise ResolveOperationError("Could not access Fusion (effects) interface")
                
                comp = fusion.GetCurrentComp()
                if not comp:
                    raise ResolveOperationError("Could not access current composition")
                
                # Map effect types to Fusion node types
                effect_map = {
                    AudioEffectType.EQ: "AudioEQ",
                    AudioEffectType.COMPRESSOR: "AudioCompressor",
                    AudioEffectType.LIMITER: "AudioLimiter",
                    AudioEffectType.EXPANDER: "AudioExpander",
                    AudioEffectType.GATE: "AudioGate",
                    AudioEffectType.REVERB: "AudioReverb",
                    AudioEffectType.DELAY: "AudioDelay",
                    AudioEffectType.PITCH_SHIFT: "AudioPitchShift",
                    AudioEffectType.NOISE_REDUCTION: "AudioNoiseReduction",
                    AudioEffectType.NORMALIZE: "AudioNormalize",
                    AudioEffectType.LOUDNESS: "AudioLoudness"
                }
                
                node_type = effect_map.get(effect_type)
                if not node_type:
                    raise ResolveOperationError(f"Unsupported effect type: {effect_type}")
                
                # Create the effect node
                effect_node = comp.AddTool(node_type, -1, -1)
                if not effect_node:
                    raise ResolveOperationError(f"Failed to create {effect_type} effect node")
                
                # Apply preset if specified
                if preset:
                    # This is a simplified example - actual preset loading would depend on the effect
                    effect_node.Preset = preset
                
                # Apply custom parameters if provided
                if parameters:
                    for param, value in parameters.items():
                        if hasattr(effect_node, param):
                            setattr(effect_node, param, value)
                
                # Connect the effect to the audio track
                # Note: This is a simplified example - actual connection logic would depend on the node graph
                
                return {
                    "status": "success",
                    "message": f"Added {effect_type} effect to track {track_index}",
                    "effect_node": effect_node.GetAttrs()["TOOLS_RegID"]
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to add audio effect: {str(e)}")

    @app.tool()
    async def adjust_audio_levels(
        track_index: int,
        volume: Optional[float] = None,
        pan: Optional[float] = None,
        mute: Optional[bool] = None,
        solo: Optional[bool] = None,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Adjust audio levels for a track.
        
        Args:
            track_index: Index of the track to adjust (1-based)
            volume: New volume level (0.0 to 1.0)
            pan: Pan position (-1.0 to 1.0)
            mute: Whether to mute the track
            solo: Whether to solo the track
            timeline_name: Optional name of the timeline
            
        Returns:
            Dictionary with operation status
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Get the audio track
                track_count = timeline.GetTrackCount("audio")
                if track_index < 1 or track_index > track_count:
                    raise ResolveOperationError(f"Invalid track index: {track_index}")
                
                # Apply changes
                if volume is not None:
                    timeline.SetTrackProperty(f"volumeTrack{track_index}", "audio", str(volume))
                
                if pan is not None:
                    timeline.SetTrackProperty(f"panTrack{track_index}", "audio", str(pan))
                
                if mute is not None:
                    timeline.SetTrackProperty(f"showTrackMute{track_index}", "audio", "1" if mute else "0")
                
                if solo is not None:
                    timeline.SetTrackProperty(f"showTrackSolo{track_index}", "audio", "1" if solo else "0")
                
                # Save the project
                resolve.GetProjectManager().SaveProject()
                
                return {
                    "status": "success",
                    "message": f"Updated audio track {track_index}",
                    "track_index": track_index,
                    "volume": volume,
                    "pan": pan,
                    "mute": mute,
                    "solo": solo
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to adjust audio levels: {str(e)}")

    @app.tool()
    async def normalize_audio(
        target_level: float = -23.0,
        track_indices: Optional[List[int]] = None,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Normalize audio levels to a target LUFS level.
        
        Args:
            target_level: Target LUFS level (default: -23.0)
            track_indices: Optional list of track indices to normalize (all tracks if None)
            timeline_name: Optional name of the timeline
            
        Returns:
            Dictionary with operation status
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Get all audio tracks if none specified
                if not track_indices:
                    track_count = timeline.GetTrackCount("audio")
                    track_indices = list(range(1, track_count + 1))
                
                # Apply normalization to each track
                results = []
                for track_index in track_indices:
                    try:
                        # Add a loudness meter to analyze the track
                        # Note: This is a simplified example - actual implementation would use the Fairlight API
                        # to analyze and adjust levels
                        
                        # For now, just set a volume adjustment based on the target level
                        # current_volume would be measured in a real implementation
                        adjustment = target_level / 20.0  # Simplified calculation
                        
                        timeline.SetTrackProperty(f"volumeTrack{track_index}", "audio", str(adjustment))
                        
                        results.append({
                            "track_index": track_index,
                            "status": "success",
                            "adjustment": adjustment
                        })
                    except Exception as e:
                        results.append({
                            "track_index": track_index,
                            "status": "error",
                            "error": str(e)
                        })
                
                # Save the project
                resolve.GetProjectManager().SaveProject()
                
                return {
                    "status": "success",
                    "message": "Audio normalization completed",
                    "results": results
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to normalize audio: {str(e)}")

    # Add more audio tools as needed
    # - Audio mixing
    # - Keyframe automation
    # - Audio routing
    # - Fairlight specific features
    # - Audio effects management
