"""
Audio-related data models for DaVinci Resolve.

This module contains data models for managing audio tracks, effects, mixing,
and other audio-related functionality in DaVinci Resolve.
"""

from enum import Enum, StrEnum
from typing import Any

from pydantic import Field

from .common import ResolveObject, TimeCode


class AudioTrackType(StrEnum):
    """Types of audio tracks in DaVinci Resolve."""

    MONO = "mono"
    STEREO = "stereo"
    SURROUND_5_1 = "surround_5_1"
    SURROUND_7_1 = "surround_7_1"
    AMBISONIC = "ambisonic"
    ADAPTIVE = "adaptive"


class AudioChannelLayout(StrEnum):
    """Standard audio channel layouts."""

    MONO = "mono"
    STEREO = "stereo"
    STEREO_LFE = "stereo_lfe"
    SURROUND_5_1 = "5.1"
    SURROUND_7_1 = "7.1"
    AMBISONIC_FIRST_ORDER = "ambisonic_1st"
    AMBISONIC_SECOND_ORDER = "ambisonic_2nd"
    AMBISONIC_THIRD_ORDER = "ambisonic_3rd"


class AudioSampleRate(int, Enum):
    """Standard audio sample rates."""

    KHZ_44_1 = 44100
    KHZ_48 = 48000
    KHZ_88_2 = 88200
    KHZ_96 = 96000
    KHZ_176_4 = 176400
    KHZ_192 = 192000


class AudioBitDepth(int, Enum):
    """Standard audio bit depths."""

    BIT_16 = 16
    BIT_24 = 24
    BIT_32 = 32
    FLOAT_32 = 32
    FLOAT_64 = 64


class AudioClip(ResolveObject):
    """
    Represents an audio clip in DaVinci Resolve.

    Attributes:
        name: Name of the audio clip
        file_path: Path to the audio file
        sample_rate: Sample rate in Hz
        bit_depth: Bit depth
        channel_count: Number of audio channels
        channel_layout: Channel layout
        duration: Duration in seconds
        start_timecode: Start timecode
        end_timecode: End timecode
        is_offline: Whether the audio file is offline
        is_online: Whether the audio file is online
        is_muted: Whether the clip is muted
        is_soloed: Whether the clip is soloed
        is_locked: Whether the clip is locked
        volume: Volume level in dB (0.0 = unity, -inf = muted)
        pan: Pan position (-1.0 = full left, 0.0 = center, 1.0 = full right)
        is_music: Whether this is a music track
        is_dialogue: Whether this is a dialogue track
        is_sfx: Whether this is a sound effects track
        is_ambience: Whether this is an ambience track
        is_foley: Whether this is a foley track
        metadata: Additional metadata
    """

    name: str = Field(..., description="Name of the audio clip")
    file_path: str = Field(..., description="Path to the audio file")
    sample_rate: AudioSampleRate = Field(default=AudioSampleRate.KHZ_48, description="Sample rate in Hz")
    bit_depth: AudioBitDepth = Field(default=AudioBitDepth.BIT_24, description="Bit depth")
    channel_count: int = Field(default=2, ge=1, le=64, description="Number of audio channels")
    channel_layout: AudioChannelLayout = Field(default=AudioChannelLayout.STEREO, description="Channel layout")
    duration: float = Field(default=0.0, ge=0.0, description="Duration in seconds")
    start_timecode: TimeCode | None = Field(default=None, description="Start timecode")
    end_timecode: TimeCode | None = Field(default=None, description="End timecode")
    is_offline: bool = Field(default=False, description="Offline status")
    is_online: bool = Field(default=True, description="Online status")
    is_muted: bool = Field(default=False, description="Muted status")
    is_soloed: bool = Field(default=False, description="Soloed status")
    is_locked: bool = Field(default=False, description="Locked status")
    volume: float = Field(default=0.0, description="Volume in dB (0.0 = unity, -inf = muted)")
    pan: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Pan position (-1.0 = left, 0.0 = center, 1.0 = right)",
    )
    is_music: bool = Field(default=False, description="Music track flag")
    is_dialogue: bool = Field(default=False, description="Dialogue track flag")
    is_sfx: bool = Field(default=False, description="Sound effects track flag")
    is_ambience: bool = Field(default=False, description="Ambience track flag")
    is_foley: bool = Field(default=False, description="Foley track flag")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AudioEffectType(StrEnum):
    """Types of audio effects in DaVinci Resolve."""

    # Basic effects
    EQUALIZER = "equalizer"
    COMPRESSOR = "compressor"
    LIMITER = "limiter"
    EXPANDER = "expander"
    NOISE_GATE = "noise_gate"
    REVERB = "reverb"
    DELAY = "delay"
    CHORUS = "chorus"
    FLANGER = "flanger"
    PHASER = "phaser"
    TREMOLO = "tremolo"
    VIBRATO = "vibrato"
    PITCH_SHIFT = "pitch_shift"
    TIME_STRETCH = "time_stretch"
    NORMALIZE = "normalize"
    INVERT_PHASE = "invert_phase"
    GAIN = "gain"
    PAN = "pan"

    # Advanced effects
    DE_ESSER = "de_esser"
    DE_NOISER = "de_noiser"
    DE_CLIPPER = "de_clipper"
    DE_POPPER = "de_popper"
    DE_HUM = "de_hum"
    DE_ESSER_MULTIBAND = "de_esser_multiband"

    # Specialized
    LOUDNESS_METER = "loudness_meter"
    SPECTRAL_ANALYZER = "spectral_analyzer"
    PHASE_SCOPE = "phase_scope"
    GONIOMETER = "goniometer"
    CORRELATION_METER = "correlation_meter"

    # Fairlight specific
    FAIRLIGHT_FIXED = "fairlight_fixed"
    FAIRLIGHT_DYNAMICS = "fairlight_dynamics"
    FAIRLIGHT_EQ = "fairlight_eq"
    FAIRLIGHT_REVERB = "fairlight_reverb"
    FAIRLIGHT_DELAY = "fairlight_delay"


class AudioEffect(ResolveObject):
    """
    Represents an audio effect in DaVinci Resolve.

    Attributes:
        effect_type: Type of audio effect
        name: Name of the effect
        is_active: Whether the effect is active
        is_bypassed: Whether the effect is bypassed
        preset_name: Name of the preset (if any)
        parameters: Dictionary of effect parameters
        metadata: Additional metadata
    """

    effect_type: AudioEffectType = Field(..., description="Type of audio effect")
    name: str = Field(..., description="Name of the effect")
    is_active: bool = Field(default=True, description="Active status")
    is_bypassed: bool = Field(default=False, description="Bypass status")
    preset_name: str | None = Field(default=None, description="Name of the preset (if any)")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Effect parameters")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def set_parameter(self, name: str, value: Any) -> None:
        """Set an effect parameter."""
        self.parameters[name] = value

    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get an effect parameter."""
        return self.parameters.get(name, default)


class AudioTrack(ResolveObject):
    """
    Represents an audio track in DaVinci Resolve.

    Attributes:
        name: Name of the track
        track_type: Type of audio track
        index: Track index (1-based)
        is_muted: Whether the track is muted
        is_soloed: Whether the track is soloed
        is_locked: Whether the track is locked
        is_visible: Whether the track is visible
        volume: Volume level in dB (0.0 = unity, -inf = muted)
        pan: Pan position (-1.0 = full left, 0.0 = center, 1.0 = full right)
        clips: List of audio clips on this track
        effects: List of audio effects on this track
        automation_enabled: Whether automation is enabled
        automation_mode: Automation mode (read, touch, latch, write)
        is_folded: Whether the track is folded in the UI
        color: Track color
        metadata: Additional metadata
    """

    name: str = Field(..., description="Name of the track")
    track_type: AudioTrackType = Field(default=AudioTrackType.STEREO, description="Type of audio track")
    index: int = Field(..., ge=1, description="Track index (1-based)")
    is_muted: bool = Field(default=False, description="Muted status")
    is_soloed: bool = Field(default=False, description="Soloed status")
    is_locked: bool = Field(default=False, description="Locked status")
    is_visible: bool = Field(default=True, description="Visibility status")
    volume: float = Field(default=0.0, description="Volume in dB (0.0 = unity, -inf = muted)")
    pan: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Pan position (-1.0 = left, 0.0 = center, 1.0 = right)",
    )
    clips: list[AudioClip] = Field(default_factory=list, description="List of audio clips")
    effects: list[AudioEffect] = Field(default_factory=list, description="List of audio effects")
    automation_enabled: bool = Field(default=True, description="Automation enabled status")
    automation_mode: str = Field(default="read", description="Automation mode (read, touch, latch, write)")
    is_folded: bool = Field(default=False, description="Folded status in UI")
    color: str = Field(default="None", description="Track color")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def add_effect(self, effect: AudioEffect) -> None:
        """Add an effect to the track."""
        self.effects.append(effect)

    def remove_effect(self, effect_name: str) -> bool:
        """Remove an effect from the track by name."""
        for i, effect in enumerate(self.effects):
            if effect.name == effect_name:
                self.effects.pop(i)
                return True
        return False

    def get_effect(self, effect_name: str) -> AudioEffect | None:
        """Get an effect by name."""
        for effect in self.effects:
            if effect.name == effect_name:
                return effect
        return None


class AudioBus(ResolveObject):
    """
    Represents an audio bus in DaVinci Resolve.

    Attributes:
        name: Name of the bus
        bus_type: Type of audio bus
        is_master: Whether this is the master bus
        is_solo_safe: Whether solo safe is enabled
        is_muted: Whether the bus is muted
        is_soloed: Whether the bus is soloed
        volume: Volume level in dB (0.0 = unity, -inf = muted)
        pan: Pan position (-1.0 = full left, 0.0 = center, 1.0 = full right)
        effects: List of audio effects on this bus
        input_count: Number of input channels
        output_count: Number of output channels
        input_routing: Input routing configuration
        output_routing: Output routing configuration
        metadata: Additional metadata
    """

    name: str = Field(..., description="Name of the bus")
    bus_type: AudioTrackType = Field(default=AudioTrackType.STEREO, description="Type of audio bus")
    is_master: bool = Field(default=False, description="Master bus status")
    is_solo_safe: bool = Field(default=False, description="Solo safe status")
    is_muted: bool = Field(default=False, description="Muted status")
    is_soloed: bool = Field(default=False, description="Soloed status")
    volume: float = Field(default=0.0, description="Volume in dB (0.0 = unity, -inf = muted)")
    pan: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Pan position (-1.0 = left, 0.0 = center, 1.0 = right)",
    )
    effects: list[AudioEffect] = Field(default_factory=list, description="List of audio effects")
    input_count: int = Field(default=2, ge=1, le=64, description="Number of input channels")
    output_count: int = Field(default=2, ge=1, le=64, description="Number of output channels")
    input_routing: dict[str, Any] = Field(default_factory=dict, description="Input routing configuration")
    output_routing: dict[str, Any] = Field(default_factory=dict, description="Output routing configuration")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AudioMixer(ResolveObject):
    """
    Represents the audio mixer in DaVinci Resolve.

    Attributes:
        name: Name of the mixer
        sample_rate: Sample rate in Hz
        bit_depth: Bit depth
        master_bus: Master audio bus
        audio_buses: Dictionary of audio buses by name
        audio_tracks: List of audio tracks
        is_audio_metering_enabled: Whether audio metering is enabled
        is_automation_enabled: Whether automation is enabled
        is_snapping_enabled: Whether snapping is enabled
        is_loop_playback_enabled: Whether loop playback is enabled
        is_solo_in_place_enabled: Whether solo in place is enabled
        is_track_solo_isolate_enabled: Whether track solo isolate is enabled
        is_auto_ducking_enabled: Whether auto ducking is enabled
        is_loudness_normalization_enabled: Whether loudness normalization is enabled
        loudness_normalization_target: Loudness normalization target in LUFS
        is_dialog_intelligence_enabled: Whether dialog intelligence is enabled
        is_audio_detection_enabled: Whether audio detection is enabled
        is_audio_waveform_enabled: Whether audio waveform display is enabled
        is_audio_spectrum_enabled: Whether audio spectrum display is enabled
        is_audio_phase_scope_enabled: Whether audio phase scope is enabled
        is_audio_goniometer_enabled: Whether audio goniometer is enabled
        is_audio_correlation_meter_enabled: Whether audio correlation meter is enabled
        metadata: Additional metadata
    """

    name: str = Field(default="Audio Mixer", description="Name of the mixer")
    sample_rate: AudioSampleRate = Field(default=AudioSampleRate.KHZ_48, description="Sample rate in Hz")
    bit_depth: AudioBitDepth = Field(default=AudioBitDepth.BIT_24, description="Bit depth")
    master_bus: AudioBus = Field(
        default_factory=lambda: AudioBus(
            name="Master",
            is_master=True,
            bus_type=AudioTrackType.STEREO,
            input_count=2,
            output_count=2,
        ),
        description="Master audio bus",
    )
    audio_buses: dict[str, AudioBus] = Field(default_factory=dict, description="Dictionary of audio buses by name")
    audio_tracks: list[AudioTrack] = Field(default_factory=list, description="List of audio tracks")
    is_audio_metering_enabled: bool = Field(default=True, description="Audio metering status")
    is_automation_enabled: bool = Field(default=True, description="Automation status")
    is_snapping_enabled: bool = Field(default=True, description="Snapping status")
    is_loop_playback_enabled: bool = Field(default=False, description="Loop playback status")
    is_solo_in_place_enabled: bool = Field(default=False, description="Solo in place status")
    is_track_solo_isolate_enabled: bool = Field(default=False, description="Track solo isolate status")
    is_auto_ducking_enabled: bool = Field(default=False, description="Auto ducking status")
    is_loudness_normalization_enabled: bool = Field(default=False, description="Loudness normalization status")
    loudness_normalization_target: float = Field(default=-23.0, description="Loudness normalization target in LUFS")
    is_dialog_intelligence_enabled: bool = Field(default=False, description="Dialog intelligence status")
    is_audio_detection_enabled: bool = Field(default=True, description="Audio detection status")
    is_audio_waveform_enabled: bool = Field(default=True, description="Audio waveform display status")
    is_audio_spectrum_enabled: bool = Field(default=False, description="Audio spectrum display status")
    is_audio_phase_scope_enabled: bool = Field(default=False, description="Audio phase scope status")
    is_audio_goniometer_enabled: bool = Field(default=False, description="Audio goniometer status")
    is_audio_correlation_meter_enabled: bool = Field(default=False, description="Audio correlation meter status")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def add_audio_bus(self, bus: AudioBus) -> None:
        """Add an audio bus to the mixer."""
        if bus.name in self.audio_buses:
            raise ValueError(f"Audio bus '{bus.name}' already exists")
        self.audio_buses[bus.name] = bus

    def remove_audio_bus(self, bus_name: str) -> bool:
        """Remove an audio bus by name."""
        if bus_name in self.audio_buses:
            del self.audio_buses[bus_name]
            return True
        return False

    def get_audio_bus(self, bus_name: str) -> AudioBus | None:
        """Get an audio bus by name."""
        return self.audio_buses.get(bus_name)

    def add_audio_track(self, track: AudioTrack) -> None:
        """Add an audio track to the mixer."""
        self.audio_tracks.append(track)

    def remove_audio_track(self, track_index: int) -> bool:
        """Remove an audio track by index."""
        if 0 <= track_index < len(self.audio_tracks):
            self.audio_tracks.pop(track_index)
            return True
        return False

    def get_audio_track(self, track_index: int) -> AudioTrack | None:
        """Get an audio track by index."""
        if 0 <= track_index < len(self.audio_tracks):
            return self.audio_tracks[track_index]
        return None
