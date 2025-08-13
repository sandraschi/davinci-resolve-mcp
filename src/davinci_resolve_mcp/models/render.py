"""
Rendering-related data models for DaVinci Resolve.

This module contains data models for managing render jobs, settings, and presets
in DaVinci Resolve projects.
"""
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime
from enum import Enum
from pathlib import Path
from pydantic import Field, validator, HttpUrl, DirectoryPath, FilePath
from .common import ResolveObject, TimeCode, Resolution, FrameRate, ColorSpace, Result
from .timeline import Timeline


class RenderFormat(str, Enum):
    """Supported render formats in DaVinci Resolve."""
    # Video formats
    MP4 = "mp4"
    MOV = "mov"
    MXF_OP1A = "mxf_op1a"
    MXF_OP1A_IMF = "mxf_op1a_imf"
    MXF_AS02 = "mxf_as02"
    DNXHD = "dnxhd"
    DNXHR = "dnxhr"
    PRO_RES = "prores"
    H264 = "h264"
    H265 = "h265"
    AV1 = "av1"
    WEBM = "webm"
    
    # Audio formats
    WAV = "wav"
    AIFF = "aiff"
    MP3 = "mp3"
    AAC = "aac"
    AC3 = "ac3"
    EAC3 = "eac3"
    OPUS = "opus"
    
    # Image formats
    DPX = "dpx"
    EXR = "exr"
    TIFF = "tiff"
    TARGA = "tga"
    PNG = "png"
    JPEG = "jpeg"
    
    # Archive formats
    DRT = "drt"  # DaVinci Resolve Timeline Archive
    XML = "xml"   # Final Cut Pro XML
    AAF = "aaf"   # Advanced Authoring Format
    EDL = "edl"   # Edit Decision List


class RenderCodec(str, Enum):
    """Supported codecs for rendering."""
    # Video codecs
    H264 = "h264"
    H265 = "h265"
    AV1 = "av1"
    PRO_RES_422 = "prores_422"
    PRO_RES_422_HQ = "prores_422_hq"
    PRO_RES_422_LT = "prores_422_lt"
    PRO_RES_422_PROXY = "prores_422_proxy"
    PRO_RES_4444 = "prores_4444"
    PRO_RES_4444_XQ = "prores_4444_xq"
    DNXHD_36 = "dnxhd_36"
    DNXHD_115 = "dnxhd_115"
    DNXHD_220 = "dnxhd_220"
    DNXHR_444 = "dnxhr_444"
    DNXHR_HQX = "dnxhr_hqx"
    DNXHR_HQ = "dnxhr_hq"
    DNXHR_SQ = "dnxhr_sq"
    DNXHR_LB = "dnxhr_lb"
    
    # Audio codecs
    PCM = "pcm"
    AAC = "aac"
    AC3 = "ac3"
    EAC3 = "eac3"
    OPUS = "opus"
    MP3 = "mp3"
    
    # Image codecs
    PNG = "png"
    JPEG = "jpeg"
    TIFF = "tiff"
    DPX = "dpx"
    EXR = "exr"


class RenderPreset(ResolveObject):
    """
    A render preset for DaVinci Resolve.
    
    Attributes:
        name: Name of the preset
        description: Description of the preset
        format: Output format
        codec: Video/audio codec
        resolution: Output resolution
        frame_rate: Output frame rate
        bitrate: Bitrate in kbps (for video)
        quality: Quality setting (0-100)
        key_frames: Keyframe interval (in frames)
        audio_channels: Number of audio channels
        audio_sample_rate: Audio sample rate
        audio_bit_depth: Audio bit depth
        include_video: Whether to include video
        include_audio: Whether to include audio
        use_max_render: Whether to use maximum render quality
        use_hardware_acceleration: Whether to use hardware acceleration
        use_network_rendering: Whether to use network rendering
        custom_settings: Dictionary of custom settings
    """
    name: str = Field(..., description="Name of the preset")
    description: Optional[str] = Field(default=None, description="Description")
    format: RenderFormat = Field(..., description="Output format")
    codec: RenderCodec = Field(..., description="Video/audio codec")
    resolution: Optional[Resolution] = Field(default=None, description="Output resolution")
    frame_rate: Optional[FrameRate] = Field(default=None, description="Output frame rate")
    bitrate: Optional[int] = Field(default=None, ge=100, description="Bitrate in kbps")
    quality: int = Field(default=90, ge=0, le=100, description="Quality (0-100)")
    key_frames: int = Field(default=24, ge=1, description="Keyframe interval in frames")
    audio_channels: int = Field(default=2, ge=1, le=16, description="Audio channels")
    audio_sample_rate: int = Field(default=48000, description="Audio sample rate")
    audio_bit_depth: int = Field(default=16, description="Audio bit depth")
    include_video: bool = Field(default=True, description="Include video")
    include_audio: bool = Field(default=True, description="Include audio")
    use_max_render: bool = Field(default=False, description="Use maximum render quality")
    use_hardware_acceleration: bool = Field(default=True, description="Use hardware acceleration")
    use_network_rendering: bool = Field(default=False, description="Use network rendering")
    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom settings"
    )
    
    @validator('bitrate', always=True)
    def validate_bitrate(cls, v, values):
        """Validate bitrate based on codec and format."""
        if v is None and 'codec' in values:
            # Set default bitrates for common codecs
            codec = values.get('codec')
            if codec in [RenderCodec.H264, RenderCodec.H265]:
                return 8000  # 8 Mbps default for H.264/265
            elif codec in [RenderCodec.PRO_RES_422, RenderCodec.PRO_RES_422_LT]:
                return 50000  # 50 Mbps for ProRes LT
        return v


class RenderJob(ResolveObject):
    """
    A render job in DaVinci Resolve.
    
    Attributes:
        name: Name of the render job
        timeline: Reference to the timeline being rendered
        preset: Render preset to use
        output_path: Output directory or file path
        filename_pattern: Pattern for output filenames
        start_frame: Start frame for rendering
        end_frame: End frame for rendering
        in_point: In point in the timeline
        out_point: Out point in the timeline
        resolution: Override resolution
        frame_rate: Override frame rate
        format: Override format
        codec: Override codec
        bitrate: Override bitrate
        quality: Override quality
        audio_channels: Override audio channels
        audio_sample_rate: Override sample rate
        audio_bit_depth: Override bit depth
        include_video: Whether to include video
        include_audio: Whether to include audio
        use_max_render: Whether to use maximum render quality
        use_hardware_acceleration: Whether to use hardware acceleration
        use_network_rendering: Whether to use network rendering
        custom_settings: Dictionary of custom settings
        status: Current status of the render job
        progress: Render progress (0-100)
        time_remaining: Estimated time remaining
        time_elapsed: Time elapsed since job started
        output_files: List of output files generated
        error_message: Error message if job failed
        created_at: When the job was created
        started_at: When the job started rendering
        completed_at: When the job completed
    """
    name: str = Field(..., description="Name of the render job")
    timeline: Timeline = Field(..., description="Timeline to render")
    preset: RenderPreset = Field(..., description="Render preset")
    output_path: Union[str, Path] = Field(..., description="Output directory or file path")
    filename_pattern: str = Field(
        default="{timeline_name}_{codec}_{resolution}p_{frame_rate}fps_{timestamp}",
        description="Filename pattern with placeholders"
    )
    start_frame: Optional[int] = Field(default=None, ge=0, description="Start frame")
    end_frame: Optional[int] = Field(default=None, ge=0, description="End frame")
    in_point: Optional[TimeCode] = Field(default=None, description="In point")
    out_point: Optional[TimeCode] = Field(default=None, description="Out point")
    
    # Override settings
    resolution: Optional[Resolution] = Field(default=None, description="Override resolution")
    frame_rate: Optional[FrameRate] = Field(default=None, description="Override frame rate")
    format: Optional[RenderFormat] = Field(default=None, description="Override format")
    codec: Optional[RenderCodec] = Field(default=None, description="Override codec")
    bitrate: Optional[int] = Field(default=None, ge=100, description="Override bitrate")
    quality: Optional[int] = Field(default=None, ge=0, le=100, description="Override quality")
    audio_channels: Optional[int] = Field(default=None, ge=1, le=16, description="Override audio channels")
    audio_sample_rate: Optional[int] = Field(default=None, description="Override sample rate")
    audio_bit_depth: Optional[int] = Field(default=None, description="Override bit depth")
    
    # Render options
    include_video: Optional[bool] = Field(default=None, description="Include video")
    include_audio: Optional[bool] = Field(default=None, description="Include audio")
    use_max_render: Optional[bool] = Field(default=None, description="Use maximum render quality")
    use_hardware_acceleration: Optional[bool] = Field(
        default=None,
        description="Use hardware acceleration"
    )
    use_network_rendering: Optional[bool] = Field(
        default=None,
        description="Use network rendering"
    )
    
    # Job status
    status: str = Field(
        default="queued",
        description="Job status (queued, rendering, completed, failed, cancelled)"
    )
    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Render progress (0-100)"
    )
    time_remaining: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Estimated time remaining in seconds"
    )
    time_elapsed: float = Field(
        default=0.0,
        ge=0.0,
        description="Time elapsed in seconds"
    )
    output_files: List[str] = Field(
        default_factory=list,
        description="List of output files generated"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if job failed"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the job was created"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="When rendering started"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="When rendering completed"
    )
    
    # Custom settings
    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom settings"
    )
    
    @property
    def effective_settings(self) -> Dict[str, Any]:
        """
        Get the effective render settings, combining preset values with any overrides.
        """
        settings = self.preset.dict(exclude_unset=True)
        
        # Apply overrides
        for field in [
            'resolution', 'frame_rate', 'format', 'codec', 'bitrate', 'quality',
            'audio_channels', 'audio_sample_rate', 'audio_bit_depth',
            'include_video', 'include_audio', 'use_max_render',
            'use_hardware_acceleration', 'use_network_rendering'
        ]:
            value = getattr(self, field, None)
            if value is not None:
                settings[field] = value
        
        return settings
    
    def get_estimated_file_size(self) -> Optional[float]:
        """
        Estimate the output file size in MB.
        Returns None if not enough information is available.
        """
        settings = self.effective_settings
        
        # Need duration and bitrate to estimate size
        duration = None
        if self.in_point is not None and self.out_point is not None:
            duration = (self.out_point - self.in_point).total_seconds()
        elif self.start_frame is not None and self.end_frame is not None and 'frame_rate' in settings:
            duration = (self.end_frame - self.start_frame) / settings['frame_rate'].value
        
        if not duration or 'bitrate' not in settings or not settings['bitrate']:
            return None
        
        # Calculate size in MB: (bitrate in kbps * duration in seconds) / 8000
        size_mb = (settings['bitrate'] * duration) / 8000
        return size_mb


class RenderQueue(ResolveObject):
    """
    Manages a queue of render jobs in DaVinci Resolve.
    
    Attributes:
        name: Name of the render queue
        jobs: List of render jobs
        is_rendering: Whether rendering is in progress
        current_job_index: Index of the currently rendering job
        default_output_path: Default output path for jobs
        default_preset: Default render preset for jobs
        max_simultaneous_jobs: Maximum number of jobs to render simultaneously
        stop_on_error: Whether to stop the queue if a job fails
        email_notifications: Whether to send email notifications
        email_address: Email address for notifications
        custom_settings: Dictionary of custom settings
    """
    name: str = Field(..., description="Name of the render queue")
    jobs: List[RenderJob] = Field(
        default_factory=list,
        description="List of render jobs"
    )
    is_rendering: bool = Field(
        default=False,
        description="Whether rendering is in progress"
    )
    current_job_index: int = Field(
        default=0,
        ge=0,
        description="Index of the currently rendering job"
    )
    default_output_path: Union[str, Path] = Field(
        default="",
        description="Default output path for jobs"
    )
    default_preset: Optional[RenderPreset] = Field(
        default=None,
        description="Default render preset for jobs"
    )
    max_simultaneous_jobs: int = Field(
        default=1,
        ge=1,
        le=16,
        description="Maximum simultaneous jobs"
    )
    stop_on_error: bool = Field(
        default=False,
        description="Stop queue if a job fails"
    )
    email_notifications: bool = Field(
        default=False,
        description="Send email notifications"
    )
    email_address: Optional[str] = Field(
        default=None,
        description="Email address for notifications"
    )
    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom settings"
    )
    
    @property
    def current_job(self) -> Optional[RenderJob]:
        """Get the currently rendering job."""
        if 0 <= self.current_job_index < len(self.jobs):
            return self.jobs[self.current_job_index]
        return None
    
    @property
    def pending_jobs(self) -> List[RenderJob]:
        """Get all pending jobs."""
        return [job for job in self.jobs if job.status == "queued"]
    
    @property
    def completed_jobs(self) -> List[RenderJob]:
        """Get all completed jobs."""
        return [job for job in self.jobs if job.status == "completed"]
    
    @property
    def failed_jobs(self) -> List[RenderJob]:
        """Get all failed jobs."""
        return [job for job in self.jobs if job.status == "failed"]
    
    @property
    def progress(self) -> float:
        """Get overall progress of the queue (0-100)."""
        if not self.jobs:
            return 0.0
        
        total = len(self.jobs) * 100
        completed = sum(
            job.progress if job.status == "rendering" else 100 
            for job in self.jobs
            if job.status in ["rendering", "completed"]
        )
        
        return min(100.0, (completed / total) * 100) if total > 0 else 0.0
