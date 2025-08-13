"""
Project-related data models for DaVinci Resolve.

This module contains data models for managing DaVinci Resolve projects,
including project settings, metadata, and database information.
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import Field, validator, HttpUrl
from .common import ResolveObject, TimeCode, Resolution, FrameRate, ColorSpace, Result

class ProjectSettings(ResolveObject):
    """Project settings and metadata."""
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    resolution: Resolution = Field(..., description="Project resolution")
    frame_rate: FrameRate = Field(..., description="Project frame rate")
    color_space: ColorSpace = Field(default=ColorSpace.REC709, description="Color space")
    audio_channels: int = Field(default=2, ge=1, le=16, description="Audio channels")
    audio_sample_rate: int = Field(default=48000, description="Sample rate in Hz")
    start_timecode: TimeCode = Field(
        default_factory=lambda: TimeCode(hours=1, minutes=0, seconds=0, frames=0),
        description="Starting timecode"
    )
    working_folder: Optional[str] = Field(default=None, description="Working folder path")
    auto_save: bool = Field(default=True, description="Auto-save enabled")
    auto_save_interval: int = Field(default=10, ge=1, le=60, description="Auto-save interval (minutes)")
    project_type: str = Field(default="feature_film", description="Project type")
    tags: List[str] = Field(default_factory=list, description="Project tags")

class ProjectDatabase(ResolveObject):
    """Database settings and information."""
    name: str = Field(..., description="Database name")
    server: Optional[str] = Field(default=None, description="Server address")
    port: Optional[int] = Field(default=None, ge=1, le=65535, description="Server port")
    is_cloud: bool = Field(default=False, description="Cloud database flag")
    is_local: bool = Field(default=True, description="Local database flag")
    last_backup: Optional[datetime] = Field(default=None, description="Last backup time")
    max_size_gb: Optional[float] = Field(default=None, ge=0.1, description="Max size in GB")
    used_size_gb: Optional[float] = Field(default=None, ge=0, description="Used size in GB")
    version: Optional[str] = Field(default=None, description="Database version")
    is_connected: bool = Field(default=False, description="Connection status")

class ProjectInfo(ResolveObject):
    """Information about a DaVinci Resolve project."""
    name: str = Field(..., description="Project name")
    path: Optional[str] = Field(default=None, description="Filesystem path")
    is_loaded: bool = Field(default=False, description="Project loaded status")
    is_modified: bool = Field(default=False, description="Unsaved changes status")
    last_saved: Optional[datetime] = Field(default=None, description="Last save time")
    duration: Optional[TimeCode] = Field(default=None, description="Project duration")
    timeline_count: int = Field(default=0, description="Number of timelines")
    media_pool_item_count: int = Field(default=0, description="Media pool items count")
    render_status: str = Field(default="idle", description="Current render status")
    render_progress: float = Field(default=0.0, ge=0, le=100, description="Render progress %")
    render_output_path: Optional[str] = Field(default=None, description="Render output path")
    is_archived: bool = Field(default=False, description="Archived status")
    archive_path: Optional[str] = Field(default=None, description="Archive file path")
    thumbnail_path: Optional[str] = Field(default=None, description="Thumbnail path")
    settings: ProjectSettings = Field(default_factory=ProjectSettings, description="Project settings")
    database: Optional[ProjectDatabase] = Field(default=None, description="Database info")

class ProjectTemplate(ResolveObject):
    """Project template settings."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(default=None, description="Template description")
    settings: ProjectSettings = Field(default_factory=ProjectSettings, description="Template settings")
    is_system: bool = Field(default=False, description="System template flag")
    preview_path: Optional[str] = Field(default=None, description="Preview image path")
    category: Optional[str] = Field(default=None, description="Template category")

class ProjectBackup(ResolveObject):
    """Project backup information."""
    timestamp: datetime = Field(..., description="Backup timestamp")
    path: str = Field(..., description="Backup file path")
    size_bytes: int = Field(..., ge=0, description="Backup size in bytes")
    version: str = Field(..., description="DaVinci Resolve version")
    comment: Optional[str] = Field(default=None, description="Backup comment")
    is_auto: bool = Field(default=True, description="Auto-backup flag")

class ProjectCollaboration(ResolveObject):
    """Project collaboration settings."""
    is_enabled: bool = Field(default=False, description="Collaboration enabled")
    server_url: Optional[str] = Field(default=None, description="Collaboration server URL")
    last_sync: Optional[datetime] = Field(default=None, description="Last sync time")
    sync_status: str = Field(default="idle", description="Sync status")
    conflict_count: int = Field(default=0, description="Number of sync conflicts")
    last_error: Optional[str] = Field(default=None, description="Last sync error")

class ProjectRenderPreset(ResolveObject):
    """Render preset for projects."""
    name: str = Field(..., description="Preset name")
    format: str = Field(default="mp4", description="Output format")
    codec: Optional[str] = Field(default=None, description="Codec name")
    resolution: Optional[Resolution] = Field(default=None, description="Output resolution")
    frame_rate: Optional[FrameRate] = Field(default=None, description="Output frame rate")
    bitrate: Optional[int] = Field(default=None, description="Bitrate in kbps")
    is_default: bool = Field(default=False, description="Default preset flag")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")
