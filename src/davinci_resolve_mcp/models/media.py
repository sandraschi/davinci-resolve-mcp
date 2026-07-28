"""
Media-related data models for DaVinci Resolve.

This module contains data models for managing media files, metadata, and import settings
in DaVinci Resolve projects.
"""

from datetime import datetime
from pathlib import Path

from pydantic import Field

from .common import (
    ColorSpace,
    FileFormat,
    FrameRate,
    MediaType,
    Resolution,
    ResolveObject,
    TimeCode,
)


class MediaMetadata(ResolveObject):
    """Metadata for media files in DaVinci Resolve."""

    file_path: str = Field(..., description="Path to the media file")
    file_name: str = Field(..., description="Name of the file")
    file_extension: str = Field(..., description="File extension")
    file_format: FileFormat = Field(..., description="File format")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")
    created_date: datetime = Field(..., description="File creation date")
    modified_date: datetime = Field(..., description="File modification date")
    duration: TimeCode | None = Field(default=None, description="Duration of the media")
    start_timecode: TimeCode | None = Field(default=None, description="Starting timecode")
    has_alpha: bool = Field(default=False, description="Has alpha channel")
    has_audio: bool = Field(default=False, description="Contains audio")
    has_video: bool = Field(default=False, description="Contains video")
    color_space: ColorSpace | None = Field(default=None, description="Color space")
    resolution: Resolution | None = Field(default=None, description="Resolution")
    frame_rate: FrameRate | None = Field(default=None, description="Frame rate")


class MediaItem(ResolveObject):
    """Represents a media item in DaVinci Resolve's media pool."""

    name: str = Field(..., description="Display name of the media item")
    file_path: str = Field(..., description="Path to the source file")
    media_type: MediaType = Field(..., description="Type of media")
    metadata: MediaMetadata = Field(default_factory=MediaMetadata, description="Media metadata")
    in_point: TimeCode | None = Field(default=None, description="In point timecode")
    out_point: TimeCode | None = Field(default=None, description="Out point timecode")
    duration: TimeCode | None = Field(default=None, description="Duration")
    thumbnail_path: str | None = Field(default=None, description="Thumbnail path")
    is_offline: bool = Field(default=False, description="Offline status")
    proxy_path: str | None = Field(default=None, description="Proxy media path")
    is_proxy_attached: bool = Field(default=False, description="Proxy attached status")
    audio_channels: int = Field(default=0, description="Number of audio channels")
    sample_rate: int | None = Field(default=None, description="Audio sample rate")
    color_space: ColorSpace | None = Field(default=None, description="Color space")
    resolution: Resolution | None = Field(default=None, description="Resolution")
    frame_rate: FrameRate | None = Field(default=None, description="Frame rate")
    is_sequence: bool = Field(default=False, description="Image sequence flag")
    clip_color: str = Field(default="None", description="Clip color tag")
    tags: list[str] = Field(default_factory=list, description="List of tags")


class ImportSettings(ResolveObject):
    """Settings for importing media into DaVinci Resolve."""

    source_paths: list[str | Path] = Field(default_factory=list, description="Source file/folder paths")
    target_bin_path: str = Field(default="", description="Target bin path")
    import_audio: bool = Field(default=True, description="Import audio tracks")
    import_video: bool = Field(default=True, description="Import video tracks")
    import_alpha: bool = Field(default=True, description="Import alpha channels")
    auto_import_sequences: bool = Field(default=True, description="Auto-detect sequences")
    sequence_handling: str = Field(default="auto", description="Sequence handling mode")
    create_proxy: bool = Field(default=False, description="Create proxy media")
    proxy_format: str = Field(default="DNxHR_LB", description="Proxy format")
    copy_local: bool = Field(default=False, description="Copy media to project folder")
    organize_by_type: bool = Field(default=True, description="Organize by type in bins")


class MediaPoolBin(ResolveObject):
    """Represents a bin in the DaVinci Resolve Media Pool."""

    name: str = Field(..., description="Name of the bin")
    path: str = Field(..., description="Full path of the bin")
    is_root: bool = Field(default=False, description="Root bin flag")
    parent_path: str | None = Field(default=None, description="Parent bin path")
    clip_count: int = Field(default=0, description="Number of clips in the bin")
    color: str = Field(default="None", description="Color tag")


class SmartBin(MediaPoolBin):
    """Represents a smart bin in the DaVinci Resolve Media Pool."""

    search_query: str = Field(..., description="Search query")
    search_scope: str = Field(default="bin", description="Search scope")
    match_type: str = Field(default="all", description="Match type ('all', 'any')")
    auto_update: bool = Field(default=True, description="Update automatically")


class MediaPool(ResolveObject):
    """Represents the DaVinci Resolve Media Pool."""

    name: str = Field(..., description="Name of the media pool")
    bins: list[MediaPoolBin | SmartBin] = Field(default_factory=list, description="List of bins")
    selected_bin: str | None = Field(default=None, description="Selected bin path")
    current_folder: str = Field(default="", description="Current folder path")
    view_mode: str = Field(default="grid", description="Current view mode")
