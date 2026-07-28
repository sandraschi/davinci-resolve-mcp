"""
Project-related data models for DaVinci Resolve.

This module contains data models for managing DaVinci Resolve projects,
including project settings, metadata, and database information.
"""

from datetime import datetime
from typing import Any

from pydantic import Field

from .common import ColorSpace, FrameRate, Resolution, ResolveObject, TimeCode


class ProjectSettings(ResolveObject):
    """Project settings and metadata."""

    name: str = Field(..., description="Project name")
    description: str | None = Field(default=None, description="Project description")
    resolution: Resolution = Field(..., description="Project resolution")
    frame_rate: FrameRate = Field(..., description="Project frame rate")
    color_space: ColorSpace = Field(default=ColorSpace.REC709, description="Color space")
    audio_channels: int = Field(default=2, ge=1, le=16, description="Audio channels")
    audio_sample_rate: int = Field(default=48000, description="Sample rate in Hz")
    start_timecode: TimeCode = Field(
        default_factory=lambda: TimeCode(hours=1, minutes=0, seconds=0, frames=0),
        description="Starting timecode",
    )
    working_folder: str | None = Field(default=None, description="Working folder path")
    auto_save: bool = Field(default=True, description="Auto-save enabled")
    auto_save_interval: int = Field(default=10, ge=1, le=60, description="Auto-save interval (minutes)")
    project_type: str = Field(default="feature_film", description="Project type")
    tags: list[str] = Field(default_factory=list, description="Project tags")


class ProjectDatabase(ResolveObject):
    """Database settings and information."""

    name: str = Field(..., description="Database name")
    server: str | None = Field(default=None, description="Server address")
    port: int | None = Field(default=None, ge=1, le=65535, description="Server port")
    is_cloud: bool = Field(default=False, description="Cloud database flag")
    is_local: bool = Field(default=True, description="Local database flag")
    last_backup: datetime | None = Field(default=None, description="Last backup time")
    max_size_gb: float | None = Field(default=None, ge=0.1, description="Max size in GB")
    used_size_gb: float | None = Field(default=None, ge=0, description="Used size in GB")
    version: str | None = Field(default=None, description="Database version")
    is_connected: bool = Field(default=False, description="Connection status")


class ProjectInfo(ResolveObject):
    """Information about a DaVinci Resolve project."""

    name: str = Field(..., description="Project name")
    path: str | None = Field(default=None, description="Filesystem path")
    is_loaded: bool = Field(default=False, description="Project loaded status")
    is_modified: bool = Field(default=False, description="Unsaved changes status")
    last_saved: datetime | None = Field(default=None, description="Last save time")
    duration: TimeCode | None = Field(default=None, description="Project duration")
    timeline_count: int = Field(default=0, description="Number of timelines")
    media_pool_item_count: int = Field(default=0, description="Media pool items count")
    render_status: str = Field(default="idle", description="Current render status")
    render_progress: float = Field(default=0.0, ge=0, le=100, description="Render progress %")
    render_output_path: str | None = Field(default=None, description="Render output path")
    is_archived: bool = Field(default=False, description="Archived status")
    archive_path: str | None = Field(default=None, description="Archive file path")
    thumbnail_path: str | None = Field(default=None, description="Thumbnail path")
    settings: ProjectSettings = Field(default_factory=ProjectSettings, description="Project settings")
    database: ProjectDatabase | None = Field(default=None, description="Database info")


class ProjectTemplate(ResolveObject):
    """Project template settings."""

    name: str = Field(..., description="Template name")
    description: str | None = Field(default=None, description="Template description")
    settings: ProjectSettings = Field(default_factory=ProjectSettings, description="Template settings")
    is_system: bool = Field(default=False, description="System template flag")
    preview_path: str | None = Field(default=None, description="Preview image path")
    category: str | None = Field(default=None, description="Template category")


class ProjectBackup(ResolveObject):
    """Project backup information."""

    timestamp: datetime = Field(..., description="Backup timestamp")
    path: str = Field(..., description="Backup file path")
    size_bytes: int = Field(..., ge=0, description="Backup size in bytes")
    version: str = Field(..., description="DaVinci Resolve version")
    comment: str | None = Field(default=None, description="Backup comment")
    is_auto: bool = Field(default=True, description="Auto-backup flag")


class ProjectCollaboration(ResolveObject):
    """Project collaboration settings."""

    is_enabled: bool = Field(default=False, description="Collaboration enabled")
    server_url: str | None = Field(default=None, description="Collaboration server URL")
    last_sync: datetime | None = Field(default=None, description="Last sync time")
    sync_status: str = Field(default="idle", description="Sync status")
    conflict_count: int = Field(default=0, description="Number of sync conflicts")
    last_error: str | None = Field(default=None, description="Last sync error")


class ProjectRenderPreset(ResolveObject):
    """Render preset for projects."""

    name: str = Field(..., description="Preset name")
    format: str = Field(default="mp4", description="Output format")
    codec: str | None = Field(default=None, description="Codec name")
    resolution: Resolution | None = Field(default=None, description="Output resolution")
    frame_rate: FrameRate | None = Field(default=None, description="Output frame rate")
    bitrate: int | None = Field(default=None, description="Bitrate in kbps")
    is_default: bool = Field(default=False, description="Default preset flag")
    custom_settings: dict[str, Any] = Field(default_factory=dict, description="Custom settings")
