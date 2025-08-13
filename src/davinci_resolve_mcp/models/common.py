"""
Common types and enums used across all DaVinci Resolve operations.

This module contains the fundamental data types and base classes that are used throughout
the DaVinci Resolve MCP system. These types provide the foundation for all other models.
"""
from typing import Dict, Any, Optional, Union, List, Literal
from enum import Enum
from pydantic import BaseModel, Field, validator, conint, confloat
from datetime import datetime
from typing_extensions import Annotated

class ResolveObject(BaseModel):
    """
    Base class for all DaVinci Resolve objects.
    
    Attributes:
        id: Unique identifier for the object
        name: Human-readable name of the object
        created_at: Timestamp when the object was created
        modified_at: Timestamp when the object was last modified
    """
    id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the object"
    )
    name: Optional[str] = Field(
        default=None,
        description="Human-readable name of the object"
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the object was created"
    )
    modified_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the object was last modified"
    )
    
    class Config:
        extra = "allow"
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        allow_population_by_field_name = True
        validate_assignment = True


class TimeCode(BaseModel):
    """
    Represents a timecode in DaVinci Resolve.
    
    Attributes:
        hours: Hours component (0-23)
        minutes: Minutes component (0-59)
        seconds: Seconds component (0-59)
        frames: Frames component (0-29, depends on frame rate)
        drop_frame: Whether this is a drop-frame timecode (for 29.97, 59.94, etc.)
    """
    hours: int = Field(
        default=0,
        ge=0,
        le=23,
        description="Hours component (0-23)"
    )
    minutes: int = Field(
        default=0,
        ge=0,
        le=59,
        description="Minutes component (0-59)"
    )
    seconds: int = Field(
        default=0,
        ge=0,
        le=59,
        description="Seconds component (0-59)"
    )
    frames: int = Field(
        default=0,
        ge=0,
        le=29,
        description="Frames component (0-29, depends on frame rate)"
    )
    drop_frame: bool = Field(
        default=False,
        description="Whether this is a drop-frame timecode (for 29.97, 59.94, etc.)"
    )
    
    def __str__(self) -> str:
        """Return timecode as string in format HH:MM:SS:FF."""
        sep = ";" if self.drop_frame else ":"
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}{sep}{self.frames:02d}"
    
    @classmethod
    def from_string(cls, timecode_str: str) -> 'TimeCode':
        """Create a TimeCode from a string in format HH:MM:SS:FF or HH:MM:SS;FF (for drop frame)."""
        drop_frame = ";" in timecode_str
        parts = timecode_str.replace(';', ':').split(':')
        
        if len(parts) != 4:
            raise ValueError("Timecode string must be in format HH:MM:SS:FF or HH:MM:SS;FF")
            
        return cls(
            hours=int(parts[0]),
            minutes=int(parts[1]),
            seconds=int(parts[2]),
            frames=int(parts[3]),
            drop_frame=drop_frame
        )
    
    def to_frames(self, frame_rate: float) -> int:
        """Convert timecode to total number of frames."""
        total_seconds = (self.hours * 3600) + (self.minutes * 60) + self.seconds
        frames = int(round(total_seconds * frame_rate)) + self.frames
        
        if self.drop_frame and frame_rate in [29.97, 59.94]:
            # Drop frame calculation for 29.97 or 59.94 fps
            total_minutes = (self.hours * 60) + self.minutes
            drop_frames = 2 * (total_minutes - (total_minutes // 10))
            frames -= drop_frames
            
        return frames


class Resolution(BaseModel):
    """
    Video resolution settings.
    
    Attributes:
        width: Width in pixels (must be > 0)
        height: Height in pixels (must be > 0)
        pixel_aspect_ratio: Pixel aspect ratio (default: 1.0 for square pixels)
    """
    width: int = Field(
        gt=0,
        description="Width in pixels"
    )
    height: int = Field(
        gt=0,
        description="Height in pixels"
    )
    pixel_aspect_ratio: float = Field(
        default=1.0,
        gt=0,
        description="Pixel aspect ratio (default: 1.0 for square pixels)"
    )
    
    @property
    def aspect_ratio(self) -> float:
        """Return the display aspect ratio (width/height * pixel_aspect_ratio)."""
        return (self.width / self.height) * self.pixel_aspect_ratio
    
    @classmethod
    def from_string(cls, resolution_str: str) -> 'Resolution':
        """Create a Resolution from a string in format WxH or WxH@PAR."""
        if '@' in resolution_str:
            res_part, par_part = resolution_str.split('@')
            par = float(par_part)
        else:
            res_part = resolution_str
            par = 1.0
            
        width, height = map(int, res_part.lower().split('x'))
        return cls(width=width, height=height, pixel_aspect_ratio=par)
    
    def __str__(self) -> str:
        """Return resolution as string in format WxH@PAR."""
        if self.pixel_aspect_ratio == 1.0:
            return f"{self.width}x{self.height}"
        return f"{self.width}x{self.height}@{self.pixel_aspect_ratio}"


class FrameRate(BaseModel):
    """
    Frame rate representation with support for various timebases.
    
    Attributes:
        value: Frame rate value
        timebase: Timebase (e.g., 24, 25, 29.97, 30, 50, 59.94, 60)
        drop_frame: Whether this is a drop-frame rate (for 29.97, 59.94)
    """
    value: float = Field(
        gt=0,
        description="Frame rate value"
    )
    timebase: Optional[float] = Field(
        default=None,
        description="Timebase (e.g., 24, 25, 29.97, 30, 50, 59.94, 60)"
    )
    drop_frame: bool = Field(
        default=False,
        description="Whether this is a drop-frame rate (for 29.97, 59.94)"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        # If timebase not provided, use the value as timebase
        if self.timebase is None:
            self.timebase = self.value
    
    def __str__(self) -> str:
        """Return frame rate as string."""
        if self.drop_frame:
            return f"{self.value} DF"
        return f"{self.value}"
    
    @classmethod
    def from_string(cls, rate_str: str) -> 'FrameRate':
        """Create a FrameRate from a string like '24', '29.97', '59.94 DF', etc."""
        drop_frame = 'DF' in rate_str.upper()
        value = float(rate_str.upper().replace('DF', '').strip())
        return cls(value=value, drop_frame=drop_frame)


class ColorSpace(str, Enum):
    """Standard color spaces used in DaVinci Resolve."""
    REC709 = "Rec.709"
    REC2020 = "Rec.2020"
    REC2100_PQ = "Rec.2100 PQ"
    REC2100_HLG = "Rec.2100 HLG"
    DCI_P3 = "DCI-P3"
    ARRI_LOGC3 = "ARRI LogC3"
    SONY_SLOG3 = "Sony S-Log3"
    PANASONIC_VLOG = "Panasonic V-Log"
    CANON_LOG3 = "Canon Log 3"
    ACES_AP0 = "ACES AP0"
    ACES_AP1 = "ACES AP1"
    LINEAR = "Linear"
    SRGB = "sRGB"


class FileFormat(str, Enum):
    """Common file formats for media and projects."""
    # Video/Audio Formats
    MP4 = "mp4"
    MOV = "mov"
    MXF = "mxf"
    AVI = "avi"
    MKV = "mkv"
    WEBM = "webm"
    
    # Image Sequences
    DPX = "dpx"
    EXR = "exr"
    TIFF = "tiff"
    TARGA = "tga"
    PNG = "png"
    JPEG = "jpeg"
    
    # Audio Only
    WAV = "wav"
    AIFF = "aiff"
    MP3 = "mp3"
    
    # Project Files
    DRP = "drp"  # DaVinci Resolve Project
    XML = "xml"   # Final Cut Pro XML
    AAF = "aaf"   # Advanced Authoring Format
    EDL = "edl"   # Edit Decision List


class MediaType(str, Enum):
    """Types of media in DaVinci Resolve."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    IMAGE_SEQUENCE = "image_sequence"
    FUSION_COMPOSITION = "fusion_composition"
    GENERATOR = "generator"
    FUSION_TITLE = "fusion_title"
    ADOBE_AFTER_EFFECTS = "after_effects"
    UNKNOWN = "unknown"


class ChannelLayout(str, Enum):
    """Audio channel layouts."""
    MONO = "mono"
    STEREO = "stereo"
    FIVE_ONE = "5.1"
    SEVEN_ONE = "7.1"
    AMBISONIC_FIRST_ORDER = "ambisonic_1st"
    AMBISONIC_SECOND_ORDER = "ambisonic_2nd"
    AMBISONIC_THIRD_ORDER = "ambisonic_3rd"
    OTHER = "other"


class FieldOrder(str, Enum):
    """Video field order for interlaced footage."""
    PROGRESSIVE = "progressive"
    UPPER_FIRST = "upper_first"
    LOWER_FIRST = "lower_first"


class PixelFormat(str, Enum):
    """Pixel formats for video data."""
    U8 = "8-bit"
    U10 = "10-bit"
    U12 = "12-bit"
    U16 = "16-bit"
    F16 = "16-bit float"
    F32 = "32-bit float"
    RGB_8 = "8-bit RGB"
    RGB_10 = "10-bit RGB"
    RGB_12 = "12-bit RGB"
    RGB_16 = "16-bit RGB"
    RGB_FLOAT = "Float RGB"
    RGBA_8 = "8-bit RGBA"
    RGBA_10 = "10-bit RGBA"
    RGBA_12 = "12-bit RGBA"
    RGBA_16 = "16-bit RGBA"
    RGBA_FLOAT = "Float RGBA"
    YUV_422_8 = "8-bit YUV 4:2:2"
    YUV_422_10 = "10-bit YUV 4:2:2"
    YUV_444_10 = "10-bit YUV 4:4:4"
    YUV_444_12 = "12-bit YUV 4:4:4"
    YUV_444_16 = "16-bit YUV 4:4:4"


class TimecodeDisplayFormat(str, Enum):
    """Timecode display formats."""
    FRAMES = "frames"
    SECONDS = "seconds"
    TIME = "time"
    FEET_AND_FRAMES_16MM = "16mm"
    FEET_AND_FRAMES_35MM = "35mm"


class ProjectType(str, Enum):
    """Types of DaVinci Resolve projects."""
    FEATURE_FILM = "feature_film"
    EPISODIC = "episodic"
    COMMERCIAL = "commercial"
    MUSIC_VIDEO = "music_video"
    DOCUMENTARY = "documentary"
    CORPORATE = "corporate"
    SHORT_FILM = "short_film"
    TRAILER = "trailer"
    SOCIAL_MEDIA = "social_media"
    OTHER = "other"


class VersionControlStatus(str, Enum):
    """Version control status for project files."""
    CURRENT = "current"
    OUTDATED = "outdated"
    MODIFIED = "modified"
    CONFLICT = "conflict"
    LOCKED = "locked"
    UNTRACKED = "untracked"


class MediaStorageType(str, Enum):
    """Types of media storage locations."""
    LOCAL = "local"
    NETWORK = "network"
    CLOUD = "cloud"
    ARCHIVE = "archive"
    OFFLINE = "offline"


class ErrorSeverity(str, Enum):
    """Severity levels for error reporting."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogLevel(str, Enum):
    """Logging levels for the application."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Result(BaseModel):
    """Standardized response for operations.
    
    Attributes:
        success: Whether the operation was successful
        message: Human-readable message about the result
        data: Optional data returned by the operation
        error: Error details if the operation failed
        warnings: List of warning messages
    """
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message about the result")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional data returned by the operation"
    )
    error: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Error details if the operation failed"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warning messages"
    )
    
    @classmethod
    def success_result(
        cls,
        message: str = "Operation completed successfully",
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None
    ) -> 'Result':
        """Create a successful result."""
        return cls(
            success=True,
            message=message,
            data=data or {},
            warnings=warnings or []
        )
    
    @classmethod
    def error_result(
        cls,
        message: str,
        error_code: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None
    ) -> 'Result':
        """Create an error result."""
        error = {
            "code": error_code or "unknown_error",
            "message": message,
            "details": error_details or {}
        }
        return cls(
            success=False,
            message=message,
            error=error,
            data=data or {},
            warnings=warnings or []
        )
