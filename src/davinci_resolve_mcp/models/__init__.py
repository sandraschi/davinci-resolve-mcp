"""
DaVinci Resolve MCP - Data Models

This package contains all data models used by the DaVinci Resolve MCP (Media Control Protocol) interface.
These models provide a structured way to interact with DaVinci Resolve's functionality.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

# Re-export all public classes and enums from submodules
from .common import (
    ResolveObject,
    TimeCode,
    Resolution,
    FrameRate,
    ColorSpace,
    FileFormat,
    MediaType,
    LogLevel,
    ErrorCode,
    Result,
    Error,
    Success,
    Failure,
    ValidationError,
    NotFoundError,
    PermissionError,
    ConnectionError,
    TimeoutError,
    ServerError,
    NotSupportedError,
    InvalidOperationError,
    AlreadyExistsError,
    ResourceExhaustedError,
    UnauthorizedError,
    ForbiddenError,
    RateLimitError,
    ConflictError,
    PreconditionFailedError,
    PayloadTooLargeError,
    UnprocessableEntityError,
    LockedError,
    TooManyRequestsError,
    RequestHeaderFieldsTooLargeError,
    UnavailableForLegalReasonsError,
    InternalServerError,
    NotImplementedError,
    BadGatewayError,
    ServiceUnavailableError,
    GatewayTimeoutError,
    HTTPVersionNotSupportedError,
    VariantAlsoNegotiatesError,
    InsufficientStorageError,
    LoopDetectedError,
    NotExtendedError,
    NetworkAuthenticationRequiredError,
    NetworkConnectTimeoutError,
    NetworkReadTimeoutError,
    NetworkSendTimeoutError,
    ProcessingError,
    EarlyHintsError,
    CheckpointError,
    MisdirectedRequestError,
    UnassignedError,
    InvalidTokenError,
    LoginRequiredError,
    InvalidRequestError,
    UnknownError,
)

from .project import (
    ProjectSettings,
    ProjectDatabase,
    ProjectInfo,
    ProjectTemplate,
    ProjectBackup,
    ProjectCollaboration,
    ProjectRenderPreset,
)

from .media import (
    MediaMetadata,
    MediaItem,
    ImportSettings,
    MediaPoolBin,
    SmartBin,
    MediaPool,
)

from .timeline import (
    TrackType,
    Track,
    TimelineItem,
    TimelineMarker,
    Timeline,
    EditOperation,
)

from .render import (
    RenderFormat,
    RenderCodec,
    RenderPreset,
    RenderJob,
    RenderQueue,
)

from .color import (
    ColorNodeType,
    ColorNode,
    ColorGrade,
    LUTInfo,
    ColorWheels,
    ColorSpaceTransform,
    ScopesSettings,
)

from .audio import (
    AudioTrackType,
    AudioChannelLayout,
    AudioSampleRate,
    AudioBitDepth,
    AudioClip,
    AudioEffectType,
    AudioEffect,
    AudioTrack,
    AudioBus,
    AudioMixer,
)

# Define __all__ for explicit exports
__all__ = [
    # Common
    'ResolveObject',
    'TimeCode',
    'Resolution',
    'FrameRate',
    'ColorSpace',
    'FileFormat',
    'MediaType',
    'LogLevel',
    'ErrorCode',
    'Result',
    'Error',
    'Success',
    'Failure',
    'ValidationError',
    'NotFoundError',
    'PermissionError',
    'ConnectionError',
    'TimeoutError',
    'ServerError',
    'NotSupportedError',
    'InvalidOperationError',
    'AlreadyExistsError',
    'ResourceExhaustedError',
    'UnauthorizedError',
    'ForbiddenError',
    'RateLimitError',
    'ConflictError',
    'PreconditionFailedError',
    'PayloadTooLargeError',
    'UnprocessableEntityError',
    'LockedError',
    'TooManyRequestsError',
    'RequestHeaderFieldsTooLargeError',
    'UnavailableForLegalReasonsError',
    'InternalServerError',
    'NotImplementedError',
    'BadGatewayError',
    'ServiceUnavailableError',
    'GatewayTimeoutError',
    'HTTPVersionNotSupportedError',
    'VariantAlsoNegotiatesError',
    'InsufficientStorageError',
    'LoopDetectedError',
    'NotExtendedError',
    'NetworkAuthenticationRequiredError',
    'NetworkConnectTimeoutError',
    'NetworkReadTimeoutError',
    'NetworkSendTimeoutError',
    'ProcessingError',
    'EarlyHintsError',
    'CheckpointError',
    'MisdirectedRequestError',
    'UnassignedError',
    'InvalidTokenError',
    'LoginRequiredError',
    'InvalidRequestError',
    'UnknownError',
    
    # Project
    'ProjectSettings',
    'ProjectDatabase',
    'ProjectInfo',
    'ProjectTemplate',
    'ProjectBackup',
    'ProjectCollaboration',
    'ProjectRenderPreset',
    
    # Media
    'MediaMetadata',
    'MediaItem',
    'ImportSettings',
    'MediaPoolBin',
    'SmartBin',
    'MediaPool',
    
    # Timeline
    'TrackType',
    'Track',
    'TimelineItem',
    'TimelineMarker',
    'Timeline',
    'EditOperation',
    
    # Render
    'RenderFormat',
    'RenderCodec',
    'RenderPreset',
    'RenderJob',
    'RenderQueue',
    
    # Color
    'ColorNodeType',
    'ColorNode',
    'ColorGrade',
    'LUTInfo',
    'ColorWheels',
    'ColorSpaceTransform',
    'ScopesSettings',
    
    # Audio
    'AudioTrackType',
    'AudioChannelLayout',
    'AudioSampleRate',
    'AudioBitDepth',
    'AudioClip',
    'AudioEffectType',
    'AudioEffect',
    'AudioTrack',
    'AudioBus',
    'AudioMixer',
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

def get_available_models() -> List[str]:
    """
    Get a list of all available model class names in the package.
    
    Returns:
        List[str]: A list of model class names
    """
    return [
        # Common
        'ResolveObject',
        'TimeCode',
        'Resolution',
        'FrameRate',
        'ColorSpace',
        'FileFormat',
        'MediaType',
        'LogLevel',
        'ErrorCode',
        'Result',
        'Error',
        'Success',
        'Failure',
        
        # Project
        'ProjectSettings',
        'ProjectDatabase',
        'ProjectInfo',
        'ProjectTemplate',
        'ProjectBackup',
        'ProjectCollaboration',
        'ProjectRenderPreset',
        
        # Media
        'MediaMetadata',
        'MediaItem',
        'ImportSettings',
        'MediaPoolBin',
        'SmartBin',
        'MediaPool',
        
        # Timeline
        'TrackType',
        'Track',
        'TimelineItem',
        'TimelineMarker',
        'Timeline',
        'EditOperation',
        
        # Render
        'RenderFormat',
        'RenderCodec',
        'RenderPreset',
        'RenderJob',
        'RenderQueue',
        
        # Color
        'ColorNodeType',
        'ColorNode',
        'ColorGrade',
        'LUTInfo',
        'ColorWheels',
        'ColorSpaceTransform',
        'ScopesSettings',
        
        # Audio
        'AudioTrackType',
        'AudioChannelLayout',
        'AudioSampleRate',
        'AudioBitDepth',
        'AudioClip',
        'AudioEffectType',
        'AudioEffect',
        'AudioTrack',
        'AudioBus',
        'AudioMixer',
    ]

def get_model_dependencies(model_name: str) -> List[str]:
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
        'ResolveObject': [],
        'TimeCode': [],
        'Resolution': [],
        'FrameRate': [],
        
        # Project models
        'ProjectSettings': ['ResolveObject'],
        'ProjectDatabase': ['ResolveObject'],
        'ProjectInfo': ['ResolveObject', 'ProjectSettings'],
        'ProjectTemplate': ['ResolveObject', 'ProjectSettings'],
        'ProjectBackup': ['ResolveObject', 'ProjectInfo'],
        'ProjectCollaboration': ['ResolveObject'],
        'ProjectRenderPreset': ['ResolveObject'],
        
        # Media models
        'MediaMetadata': ['ResolveObject'],
        'MediaItem': ['ResolveObject', 'MediaMetadata'],
        'ImportSettings': ['ResolveObject'],
        'MediaPoolBin': ['ResolveObject'],
        'SmartBin': ['ResolveObject', 'MediaPoolBin'],
        'MediaPool': ['ResolveObject', 'MediaItem', 'MediaPoolBin', 'SmartBin'],
        
        # Timeline models
        'TrackType': [],
        'Track': ['ResolveObject', 'TrackType'],
        'TimelineItem': ['ResolveObject', 'MediaItem'],
        'TimelineMarker': ['ResolveObject', 'TimeCode'],
        'Timeline': ['ResolveObject', 'Track', 'TimelineItem', 'TimelineMarker'],
        'EditOperation': ['ResolveObject', 'Timeline', 'TimeCode'],
        
        # Render models
        'RenderFormat': [],
        'RenderCodec': [],
        'RenderPreset': ['ResolveObject', 'RenderFormat', 'RenderCodec'],
        'RenderJob': ['ResolveObject', 'RenderPreset', 'TimeCode'],
        'RenderQueue': ['ResolveObject', 'RenderJob'],
        
        # Color models
        'ColorNodeType': [],
        'ColorNode': ['ResolveObject', 'ColorNodeType'],
        'ColorGrade': ['ResolveObject', 'ColorNode'],
        'LUTInfo': ['ResolveObject', 'ColorSpace'],
        'ColorWheels': ['ResolveObject'],
        'ColorSpaceTransform': ['ResolveObject', 'ColorSpace'],
        'ScopesSettings': ['ResolveObject'],
        
        # Audio models
        'AudioTrackType': [],
        'AudioChannelLayout': [],
        'AudioSampleRate': [],
        'AudioBitDepth': [],
        'AudioClip': ['ResolveObject', 'TimeCode', 'AudioSampleRate', 'AudioBitDepth'],
        'AudioEffectType': [],
        'AudioEffect': ['ResolveObject', 'AudioEffectType'],
        'AudioTrack': ['ResolveObject', 'AudioTrackType', 'AudioClip', 'AudioEffect'],
        'AudioBus': ['ResolveObject', 'AudioTrackType', 'AudioEffect'],
        'AudioMixer': ['ResolveObject', 'AudioBus', 'AudioTrack'],
    }
    
    if model_name not in dependencies:
        raise ValueError(f"Model '{model_name}' not found")
        
    return dependencies[model_name]
