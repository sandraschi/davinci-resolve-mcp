"""
DaVinci Resolve MCP - Data Models

This package contains all data models used by the DaVinci Resolve MCP (Media Control Protocol) interface.
These models provide a structured way to interact with DaVinci Resolve's functionality.
"""

from __future__ import annotations

from .audio import (
    AudioBitDepth,
    AudioBus,
    AudioChannelLayout,
    AudioClip,
    AudioEffect,
    AudioEffectType,
    AudioMixer,
    AudioSampleRate,
    AudioTrack,
    AudioTrackType,
)
from .color import (
    ColorGrade,
    ColorNode,
    ColorNodeType,
    ColorSpaceTransform,
    ColorWheels,
    LUTInfo,
    ScopesSettings,
)

# Re-export all public classes and enums from submodules
from .common import (
    AlreadyExistsError,
    BadGatewayError,
    CheckpointError,
    ColorSpace,
    ConflictError,
    ConnectionError,
    EarlyHintsError,
    Error,
    ErrorCode,
    Failure,
    FileFormat,
    ForbiddenError,
    FrameRate,
    GatewayTimeoutError,
    HTTPVersionNotSupportedError,
    InsufficientStorageError,
    InternalServerError,
    InvalidOperationError,
    InvalidRequestError,
    InvalidTokenError,
    LockedError,
    LoginRequiredError,
    LogLevel,
    LoopDetectedError,
    MediaType,
    MisdirectedRequestError,
    NetworkAuthenticationRequiredError,
    NetworkConnectTimeoutError,
    NetworkReadTimeoutError,
    NetworkSendTimeoutError,
    NotExtendedError,
    NotFoundError,
    NotImplementedError,
    NotSupportedError,
    PayloadTooLargeError,
    PermissionError,
    PreconditionFailedError,
    ProcessingError,
    RateLimitError,
    RequestHeaderFieldsTooLargeError,
    Resolution,
    ResolveObject,
    ResourceExhaustedError,
    Result,
    ServerError,
    ServiceUnavailableError,
    Success,
    TimeCode,
    TimeoutError,
    TooManyRequestsError,
    UnassignedError,
    UnauthorizedError,
    UnavailableForLegalReasonsError,
    UnknownError,
    UnprocessableEntityError,
    ValidationError,
    VariantAlsoNegotiatesError,
)
from .media import (
    ImportSettings,
    MediaItem,
    MediaMetadata,
    MediaPool,
    MediaPoolBin,
    SmartBin,
)
from .project import (
    ProjectBackup,
    ProjectCollaboration,
    ProjectDatabase,
    ProjectInfo,
    ProjectRenderPreset,
    ProjectSettings,
    ProjectTemplate,
)
from .render import (
    RenderCodec,
    RenderFormat,
    RenderJob,
    RenderPreset,
    RenderQueue,
)
from .timeline import (
    EditOperation,
    Timeline,
    TimelineItem,
    TimelineMarker,
    Track,
    TrackType,
)

# Define __all__ for explicit exports
__all__ = [
    "AlreadyExistsError",
    "AudioBitDepth",
    "AudioBus",
    "AudioChannelLayout",
    "AudioClip",
    "AudioEffect",
    "AudioEffectType",
    "AudioMixer",
    "AudioSampleRate",
    "AudioTrack",
    # Audio
    "AudioTrackType",
    "BadGatewayError",
    "CheckpointError",
    "ColorGrade",
    "ColorNode",
    # Color
    "ColorNodeType",
    "ColorSpace",
    "ColorSpaceTransform",
    "ColorWheels",
    "ConflictError",
    "ConnectionError",
    "EarlyHintsError",
    "EditOperation",
    "Error",
    "ErrorCode",
    "Failure",
    "FileFormat",
    "ForbiddenError",
    "FrameRate",
    "GatewayTimeoutError",
    "HTTPVersionNotSupportedError",
    "ImportSettings",
    "InsufficientStorageError",
    "InternalServerError",
    "InvalidOperationError",
    "InvalidRequestError",
    "InvalidTokenError",
    "LUTInfo",
    "LockedError",
    "LogLevel",
    "LoginRequiredError",
    "LoopDetectedError",
    "MediaItem",
    # Media
    "MediaMetadata",
    "MediaPool",
    "MediaPoolBin",
    "MediaType",
    "MisdirectedRequestError",
    "NetworkAuthenticationRequiredError",
    "NetworkConnectTimeoutError",
    "NetworkReadTimeoutError",
    "NetworkSendTimeoutError",
    "NotExtendedError",
    "NotFoundError",
    "NotImplementedError",
    "NotSupportedError",
    "PayloadTooLargeError",
    "PermissionError",
    "PreconditionFailedError",
    "ProcessingError",
    "ProjectBackup",
    "ProjectCollaboration",
    "ProjectDatabase",
    "ProjectInfo",
    "ProjectRenderPreset",
    # Project
    "ProjectSettings",
    "ProjectTemplate",
    "RateLimitError",
    "RenderCodec",
    # Render
    "RenderFormat",
    "RenderJob",
    "RenderPreset",
    "RenderQueue",
    "RequestHeaderFieldsTooLargeError",
    "Resolution",
    # Common
    "ResolveObject",
    "ResourceExhaustedError",
    "Result",
    "ScopesSettings",
    "ServerError",
    "ServiceUnavailableError",
    "SmartBin",
    "Success",
    "TimeCode",
    "Timeline",
    "TimelineItem",
    "TimelineMarker",
    "TimeoutError",
    "TooManyRequestsError",
    "Track",
    # Timeline
    "TrackType",
    "UnassignedError",
    "UnauthorizedError",
    "UnavailableForLegalReasonsError",
    "UnknownError",
    "UnprocessableEntityError",
    "ValidationError",
    "VariantAlsoNegotiatesError",
]

# Package version
__version__ = "0.1.0"


def get_version() -> str:
    """
    Get the current version of the DaVinci Resolve MCP models package.

    Returns:
        str: The current version string (e.g., "0.1.0")
    """
    return __version__


def get_available_models() -> list[str]:
    """
    Get a list of all available model class names in the package.

    Returns:
        List[str]: A list of model class names
    """
    return [
        # Common
        "ResolveObject",
        "TimeCode",
        "Resolution",
        "FrameRate",
        "ColorSpace",
        "FileFormat",
        "MediaType",
        "LogLevel",
        "ErrorCode",
        "Result",
        "Error",
        "Success",
        "Failure",
        # Project
        "ProjectSettings",
        "ProjectDatabase",
        "ProjectInfo",
        "ProjectTemplate",
        "ProjectBackup",
        "ProjectCollaboration",
        "ProjectRenderPreset",
        # Media
        "MediaMetadata",
        "MediaItem",
        "ImportSettings",
        "MediaPoolBin",
        "SmartBin",
        "MediaPool",
        # Timeline
        "TrackType",
        "Track",
        "TimelineItem",
        "TimelineMarker",
        "Timeline",
        "EditOperation",
        # Render
        "RenderFormat",
        "RenderCodec",
        "RenderPreset",
        "RenderJob",
        "RenderQueue",
        # Color
        "ColorNodeType",
        "ColorNode",
        "ColorGrade",
        "LUTInfo",
        "ColorWheels",
        "ColorSpaceTransform",
        "ScopesSettings",
        # Audio
        "AudioTrackType",
        "AudioChannelLayout",
        "AudioSampleRate",
        "AudioBitDepth",
        "AudioClip",
        "AudioEffectType",
        "AudioEffect",
        "AudioTrack",
        "AudioBus",
        "AudioMixer",
    ]


def get_model_dependencies(model_name: str) -> list[str]:
    """
    Get a list of model names that the specified model depends on.

    Args:
        model_name: Name of the model to get dependencies for

    Returns:
        List[str]: List of model names that the specified model depends on

    Raises:
        ValueError: If the model name is not found
    """
    # Define dependencies for each model
    dependencies = {
        # Common
        "ResolveObject": [],
        "TimeCode": [],
        "Resolution": [],
        "FrameRate": [],
        # Project models
        "ProjectSettings": ["ResolveObject"],
        "ProjectDatabase": ["ResolveObject"],
        "ProjectInfo": ["ResolveObject", "ProjectSettings"],
        "ProjectTemplate": ["ResolveObject", "ProjectSettings"],
        "ProjectBackup": ["ResolveObject", "ProjectInfo"],
        "ProjectCollaboration": ["ResolveObject"],
        "ProjectRenderPreset": ["ResolveObject"],
        # Media models
        "MediaMetadata": ["ResolveObject"],
        "MediaItem": ["ResolveObject", "MediaMetadata"],
        "ImportSettings": ["ResolveObject"],
        "MediaPoolBin": ["ResolveObject"],
        "SmartBin": ["ResolveObject", "MediaPoolBin"],
        "MediaPool": ["ResolveObject", "MediaItem", "MediaPoolBin", "SmartBin"],
        # Timeline models
        "TrackType": [],
        "Track": ["ResolveObject", "TrackType"],
        "TimelineItem": ["ResolveObject", "MediaItem"],
        "TimelineMarker": ["ResolveObject", "TimeCode"],
        "Timeline": ["ResolveObject", "Track", "TimelineItem", "TimelineMarker"],
        "EditOperation": ["ResolveObject", "Timeline", "TimeCode"],
        # Render models
        "RenderFormat": [],
        "RenderCodec": [],
        "RenderPreset": ["ResolveObject", "RenderFormat", "RenderCodec"],
        "RenderJob": ["ResolveObject", "RenderPreset", "TimeCode"],
        "RenderQueue": ["ResolveObject", "RenderJob"],
        # Color models
        "ColorNodeType": [],
        "ColorNode": ["ResolveObject", "ColorNodeType"],
        "ColorGrade": ["ResolveObject", "ColorNode"],
        "LUTInfo": ["ResolveObject", "ColorSpace"],
        "ColorWheels": ["ResolveObject"],
        "ColorSpaceTransform": ["ResolveObject", "ColorSpace"],
        "ScopesSettings": ["ResolveObject"],
        # Audio models
        "AudioTrackType": [],
        "AudioChannelLayout": [],
        "AudioSampleRate": [],
        "AudioBitDepth": [],
        "AudioClip": ["ResolveObject", "TimeCode", "AudioSampleRate", "AudioBitDepth"],
        "AudioEffectType": [],
        "AudioEffect": ["ResolveObject", "AudioEffectType"],
        "AudioTrack": ["ResolveObject", "AudioTrackType", "AudioClip", "AudioEffect"],
        "AudioBus": ["ResolveObject", "AudioTrackType", "AudioEffect"],
        "AudioMixer": ["ResolveObject", "AudioBus", "AudioTrack"],
    }

    if model_name not in dependencies:
        raise ValueError(f"Model '{model_name}' not found")

    return dependencies[model_name]
