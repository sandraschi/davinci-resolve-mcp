"""
Timeline-related data models for DaVinci Resolve.

This module contains data models for managing timelines, tracks, clips, and edits
in DaVinci Resolve projects.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from .common import FrameRate, Resolution, ResolveObject, TimeCode
from .media import MediaItem


class TrackType(str, Enum):
    """Types of tracks in a timeline."""

    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    FUSION = "fusion"
    FUSION_COMPOUND = "fusion_compound"
    FUSION_TITLE = "fusion_title"
    FUSION_TEXT = "fusion_text"
    FUSION_STILL = "fusion_still"
    FUSION_MOVIE = "fusion_movie"
    FUSION_TRANSITION = "fusion_transition"
    FUSION_MASK = "fusion_mask"
    FUSION_MODIFIER = "fusion_modifier"
    FUSION_MATTE = "fusion_matte"
    FUSION_3D = "fusion_3d"
    FUSION_3D_MESH = "fusion_3d_mesh"
    FUSION_3D_MODIFIER = "fusion_3d_modifier"
    FUSION_3D_PARTICLE = "fusion_3d_particle"
    FUSION_3D_REPLICATOR = "fusion_3d_replicator"
    FUSION_3D_TEXT = "fusion_3d_text"
    FUSION_3D_TRACKER = "fusion_3d_tracker"
    FUSION_3D_TRANSFORM = "fusion_3d_transform"
    FUSION_3D_VERTEX = "fusion_3d_vertex"


class Track(ResolveObject):
    """
    Represents a track in a DaVinci Resolve timeline.

    Attributes:
        name: Name of the track
        track_type: Type of track (video, audio, etc.)
        index: Track index (1-based)
        is_muted: Whether the track is muted
        is_locked: Whether the track is locked
        is_solo: Whether the track is soloed
        is_audio_track: Whether this is an audio track
        is_video_track: Whether this is a video track
        is_subtitle_track: Whether this is a subtitle track
        height: Height of the track in pixels
        items: List of timeline items on this track
        is_targeted: Whether the track is targeted for edits
        is_visible: Whether the track is visible
        is_audio_muted: Whether the track's audio is muted
        is_audio_solo: Whether the track's audio is soloed
        is_audio_mono: Whether the track is mono audio
        is_audio_stereo: Whether the track is stereo audio
        is_audio_51: Whether the track is 5.1 audio
        is_audio_71: Whether the track is 7.1 audio
        is_audio_ambisonic: Whether the track is ambisonic audio
    """

    name: str = Field(..., description="Name of the track")
    track_type: TrackType = Field(..., description="Type of track")
    index: int = Field(..., ge=1, description="Track index (1-based)")
    is_muted: bool = Field(default=False, description="Muted status")
    is_locked: bool = Field(default=False, description="Locked status")
    is_solo: bool = Field(default=False, description="Solo status")
    height: int = Field(default=50, ge=20, le=200, description="Track height in pixels")
    is_targeted: bool = Field(default=False, description="Targeted for edits")
    is_visible: bool = Field(default=True, description="Track visibility")

    @property
    def is_audio_track(self) -> bool:
        """Check if this is an audio track."""
        return self.track_type == TrackType.AUDIO

    @property
    def is_video_track(self) -> bool:
        """Check if this is a video track."""
        return self.track_type == TrackType.VIDEO

    @property
    def is_subtitle_track(self) -> bool:
        """Check if this is a subtitle track."""
        return self.track_type == TrackType.SUBTITLE

    @property
    def is_fusion_track(self) -> bool:
        """Check if this is a Fusion track."""
        return self.track_type.value.startswith("fusion_")


class TimelineItem(ResolveObject):
    """
    Represents an item on a timeline track in DaVinci Resolve.

    Attributes:
        name: Name of the timeline item
        media_item: Reference to the source media item
        track_index: Index of the track this item is on
        start_frame: Start frame in the timeline
        end_frame: End frame in the timeline
        in_point: In point in the source media
        out_point: Out point in the source media
        speed: Playback speed (1.0 = normal, 2.0 = 2x, etc.)
        is_reversed: Whether the clip is reversed
        is_nesting: Whether this is a nested timeline
        is_audio: Whether this is an audio clip
        is_video: Whether this is a video clip
        is_compound: Whether this is a compound clip
        is_fusion: Whether this is a Fusion clip
        is_generator: Whether this is a generator
        is_transition: Whether this is a transition
        is_blank: Whether this is a blank space
        is_locked: Whether the item is locked
        is_muted: Whether the item is muted
        is_solo: Whether the item is soloed
        is_collapsed: Whether the item is collapsed
        is_selected: Whether the item is selected
        is_visible: Whether the item is visible
        is_audio_muted: Whether the item's audio is muted
        is_audio_solo: Whether the item's audio is soloed
        is_audio_mono: Whether the item's audio is mono
        is_audio_stereo: Whether the item's audio is stereo
        is_audio_51: Whether the item's audio is 5.1
        is_audio_71: Whether the item's audio is 7.1
        is_audio_ambisonic: Whether the item's audio is ambisonic
    """

    name: str = Field(..., description="Name of the timeline item")
    media_item: MediaItem | None = Field(default=None, description="Source media item")
    track_index: int = Field(..., ge=1, description="Track index (1-based)")
    start_frame: int = Field(..., ge=0, description="Start frame in timeline")
    end_frame: int = Field(..., ge=0, description="End frame in timeline")
    in_point: int = Field(default=0, ge=0, description="In point in source")
    out_point: int | None = Field(default=None, ge=0, description="Out point in source")
    speed: float = Field(default=1.0, gt=0, description="Playback speed")
    is_reversed: bool = Field(default=False, description="Reversed status")
    is_nesting: bool = Field(default=False, description="Nested timeline flag")
    is_audio: bool = Field(default=False, description="Audio clip flag")
    is_video: bool = Field(default=False, description="Video clip flag")
    is_compound: bool = Field(default=False, description="Compound clip flag")
    is_fusion: bool = Field(default=False, description="Fusion clip flag")
    is_generator: bool = Field(default=False, description="Generator flag")
    is_transition: bool = Field(default=False, description="Transition flag")
    is_blank: bool = Field(default=False, description="Blank space flag")
    is_locked: bool = Field(default=False, description="Locked status")
    is_muted: bool = Field(default=False, description="Muted status")
    is_solo: bool = Field(default=False, description="Solo status")
    is_selected: bool = Field(default=False, description="Selected status")
    is_visible: bool = Field(default=True, description="Visibility status")

    @property
    def duration_frames(self) -> int:
        """Duration of the item in frames."""
        return self.end_frame - self.start_frame

    @property
    def source_duration_frames(self) -> int | None:
        """Duration of the source media in frames."""
        if self.out_point is not None and self.in_point is not None:
            return self.out_point - self.in_point
        return None


class TimelineMarker(ResolveObject):
    """
    Represents a marker on a timeline in DaVinci Resolve.

    Attributes:
        name: Name of the marker
        frame: Frame number where the marker is placed
        duration: Duration of the marker in frames
        color: Color of the marker
        note: Optional note for the marker
        chapter: Whether this is a chapter marker
        is_selected: Whether the marker is selected
        is_visible: Whether the marker is visible
    """

    name: str = Field(..., description="Name of the marker")
    frame: int = Field(..., ge=0, description="Frame number")
    duration: int = Field(default=1, ge=1, description="Duration in frames")
    color: str = Field(default="Red", description="Marker color")
    note: str | None = Field(default=None, description="Marker note")
    chapter: bool = Field(default=False, description="Chapter marker flag")
    is_selected: bool = Field(default=False, description="Selected status")
    is_visible: bool = Field(default=True, description="Visibility status")


class Timeline(ResolveObject):
    """
    Represents a timeline in DaVinci Resolve.

    Attributes:
        name: Name of the timeline
        frame_rate: Frame rate of the timeline
        resolution: Resolution of the timeline
        start_timecode: Starting timecode
        duration: Duration of the timeline
        tracks: List of tracks in the timeline
        markers: List of markers in the timeline
        is_active: Whether this is the active timeline
        is_sequence: Whether this is a sequence timeline
        is_multicam: Whether this is a multicam timeline
        is_compound: Whether this is a compound clip timeline
        is_nested: Whether this is a nested timeline
        is_audio_muted: Whether the timeline's audio is muted
        is_audio_solo: Whether the timeline's audio is soloed
        is_audio_mono: Whether the timeline's audio is mono
        is_audio_stereo: Whether the timeline's audio is stereo
        is_audio_51: Whether the timeline's audio is 5.1
        is_audio_71: Whether the timeline's audio is 7.1
        is_audio_ambisonic: Whether the timeline's audio is ambisonic
    """

    name: str = Field(..., description="Name of the timeline")
    frame_rate: FrameRate = Field(..., description="Frame rate")
    resolution: Resolution = Field(..., description="Resolution")
    start_timecode: TimeCode = Field(..., description="Starting timecode")
    duration: TimeCode = Field(..., description="Duration")
    tracks: list[Track] = Field(default_factory=list, description="List of tracks")
    markers: list[TimelineMarker] = Field(default_factory=list, description="List of markers")
    is_active: bool = Field(default=False, description="Active timeline flag")
    is_sequence: bool = Field(default=True, description="Sequence timeline flag")
    is_multicam: bool = Field(default=False, description="Multicam timeline flag")
    is_compound: bool = Field(default=False, description="Compound clip flag")
    is_nested: bool = Field(default=False, description="Nested timeline flag")

    def get_track(self, track_type: TrackType, index: int) -> Track | None:
        """Get a track by type and index."""
        for track in self.tracks:
            if track.track_type == track_type and track.index == index:
                return track
        return None

    def get_tracks_by_type(self, track_type: TrackType) -> list[Track]:
        """Get all tracks of a specific type."""
        return [track for track in self.tracks if track.track_type == track_type]

    def get_markers_in_range(self, start_frame: int, end_frame: int) -> list[TimelineMarker]:
        """Get all markers within a frame range."""
        return [m for m in self.markers if start_frame <= m.frame <= end_frame]


class EditOperation(ResolveObject):
    """
    Represents an edit operation on a timeline.

    Attributes:
        operation_type: Type of edit operation
        timeline: Reference to the timeline being edited
        track_index: Index of the track being edited
        start_frame: Start frame of the edit
        end_frame: End frame of the edit
        in_point: In point in the source media
        out_point: Out point in the source media
        media_item: Reference to the source media item
        parameters: Additional parameters for the operation
        timestamp: When the operation was performed
        user: User who performed the operation
    """

    operation_type: str = Field(..., description="Type of edit operation")
    timeline: Timeline = Field(..., description="Target timeline")
    track_index: int = Field(..., ge=1, description="Target track index")
    start_frame: int = Field(..., ge=0, description="Start frame")
    end_frame: int = Field(..., ge=0, description="End frame")
    in_point: int | None = Field(default=None, ge=0, description="In point in source")
    out_point: int | None = Field(default=None, ge=0, description="Out point in source")
    media_item: MediaItem | None = Field(default=None, description="Source media item")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    timestamp: datetime = Field(default_factory=datetime.now, description="Operation timestamp")
    user: str | None = Field(default=None, description="User who performed the operation")
