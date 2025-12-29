"""
Helper functions for DaVinci Resolve MCP Server.

This module contains utility functions for file handling, validation,
and common operations used throughout the server.
"""

import os
import re
import tempfile
from pathlib import Path
from typing import List, Tuple, Union

from .exceptions import ValidationError


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    Validate and normalize file path.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Path: Normalized path object
        
    Raises:
        ValidationError: If path is invalid or doesn't exist
    """
    if not file_path:
        raise ValidationError("file_path", file_path, "Path cannot be empty")
    
    path = Path(file_path)
    
    if not path.exists():
        raise ValidationError("file_path", file_path, "File does not exist")
    
    if not path.is_file():
        raise ValidationError("file_path", file_path, "Path is not a file")
    
    return path.resolve()


def validate_resolution(resolution: str) -> Tuple[int, int]:
    """
    Validate and parse resolution string.
    
    Args:
        resolution: Resolution in format "WIDTHxHEIGHT" (e.g., "1920x1080")
        
    Returns:
        Tuple[int, int]: Width and height
        
    Raises:
        ValidationError: If resolution format is invalid
    """
    if not resolution:
        raise ValidationError("resolution", resolution, "Resolution cannot be empty")
    
    pattern = r'^(\d+)x(\d+)$'
    match = re.match(pattern, resolution)
    
    if not match:
        raise ValidationError("resolution", resolution, "Format must be WIDTHxHEIGHT (e.g., 1920x1080)")
    
    width, height = int(match.group(1)), int(match.group(2))
    
    # Basic validation ranges
    if width < 320 or width > 7680:
        raise ValidationError("resolution", resolution, "Width must be between 320 and 7680")
    
    if height < 240 or height > 4320:
        raise ValidationError("resolution", resolution, "Height must be between 240 and 4320")
    
    return width, height


def validate_frame_rate(frame_rate: float) -> float:
    """
    Validate frame rate value.
    
    Args:
        frame_rate: Frame rate to validate
        
    Returns:
        float: Validated frame rate
        
    Raises:
        ValidationError: If frame rate is invalid
    """
    if frame_rate <= 0:
        raise ValidationError("frame_rate", frame_rate, "Frame rate must be positive")
    
    if frame_rate > 120:
        raise ValidationError("frame_rate", frame_rate, "Frame rate cannot exceed 120 fps")
    
    # Common frame rates
    common_rates = [23.976, 24, 25, 29.97, 30, 50, 59.94, 60, 120]
    
    # Allow small tolerance for floating point comparison
    tolerance = 0.001
    for rate in common_rates:
        if abs(frame_rate - rate) < tolerance:
            return rate
    
    # If not a common rate, validate it's reasonable
    if frame_rate < 1:
        raise ValidationError("frame_rate", frame_rate, "Frame rate too low (minimum 1 fps)")
    
    return frame_rate


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration (e.g., "01:23:45.67")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get file extension from path.
    
    Args:
        file_path: Path to file
        
    Returns:
        str: File extension (lowercase, without dot)
    """
    return Path(file_path).suffix.lower().lstrip('.')


def is_supported_video_format(file_path: Union[str, Path]) -> bool:
    """
    Check if file format is supported for video operations.
    
    Args:
        file_path: Path to check
        
    Returns:
        bool: True if format is supported
    """
    supported_extensions = {
        # Common video formats
        'mp4', 'mov', 'avi', 'mkv', 'mxf', 'prores',
        # Professional formats
        'dpx', 'exr', 'tiff', 'tif', 'jpg', 'jpeg', 'png',
        # Raw formats
        'r3d', 'braw', 'ari', 'dng',
        # Other formats
        'wmv', 'webm', 'flv', 'm4v', '3gp',
    }
    
    extension = get_file_extension(file_path)
    return extension in supported_extensions


def is_supported_audio_format(file_path: Union[str, Path]) -> bool:
    """
    Check if file format is supported for audio operations.
    
    Args:
        file_path: Path to check
        
    Returns:
        bool: True if format is supported
    """
    supported_extensions = {
        # Common audio formats
        'wav', 'aif', 'aiff', 'mp3', 'aac', 'flac',
        # Professional formats
        'bwf', 'rf64', 'caf',
        # Other formats
        'ogg', 'wma', 'm4a', 'opus',
    }
    
    extension = get_file_extension(file_path)
    return extension in supported_extensions


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for cross-platform compatibility.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure filename isn't empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    # Limit length (keep extension)
    name_part, ext_part = os.path.splitext(sanitized)
    max_name_length = 200 - len(ext_part)
    
    if len(name_part) > max_name_length:
        name_part = name_part[:max_name_length]
    
    return name_part + ext_part


def create_temp_file(suffix: str = None, prefix: str = "resolve_mcp_") -> Path:
    """
    Create a temporary file.
    
    Args:
        suffix: File suffix (extension)
        prefix: File prefix
        
    Returns:
        Path: Path to temporary file
    """
    fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)  # Close file descriptor, keep file
    return Path(temp_path)


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        Path: Resolved directory path
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path.resolve()


def parse_timecode(timecode: str) -> float:
    """
    Parse timecode string to seconds.
    
    Args:
        timecode: Timecode in format "HH:MM:SS:FF" or "HH:MM:SS.fff"
        
    Returns:
        float: Time in seconds
        
    Raises:
        ValidationError: If timecode format is invalid
    """
    if not timecode:
        raise ValidationError("timecode", timecode, "Timecode cannot be empty")
    
    # Try HH:MM:SS.fff format first
    pattern1 = r'^(\d{1,2}):(\d{2}):(\d{2})\.(\d{1,3})$'
    match = re.match(pattern1, timecode)
    
    if match:
        hours, minutes, seconds, milliseconds = match.groups()
        total_seconds = (
            int(hours) * 3600 +
            int(minutes) * 60 +
            int(seconds) +
            int(milliseconds.ljust(3, '0')) / 1000
        )
        return total_seconds
    
    # Try HH:MM:SS:FF format (assuming 24fps)
    pattern2 = r'^(\d{1,2}):(\d{2}):(\d{2}):(\d{2})$'
    match = re.match(pattern2, timecode)
    
    if match:
        hours, minutes, seconds, frames = match.groups()
        total_seconds = (
            int(hours) * 3600 +
            int(minutes) * 60 +
            int(seconds) +
            int(frames) / 24.0  # Assume 24fps
        )
        return total_seconds
    
    raise ValidationError("timecode", timecode, "Invalid timecode format (use HH:MM:SS.fff or HH:MM:SS:FF)")


def format_timecode(seconds: float, frame_rate: float = 24.0) -> str:
    """
    Format seconds to timecode string.
    
    Args:
        seconds: Time in seconds
        frame_rate: Frame rate for frame calculation
        
    Returns:
        str: Timecode in HH:MM:SS:FF format
    """
    total_frames = int(seconds * frame_rate)
    
    hours = total_frames // (3600 * frame_rate)
    remaining_frames = total_frames % (3600 * frame_rate)
    
    minutes = remaining_frames // (60 * frame_rate)
    remaining_frames = remaining_frames % (60 * frame_rate)
    
    secs = remaining_frames // frame_rate
    frames = remaining_frames % frame_rate
    
    return f"{int(hours):02d}:{int(minutes):02d}:{int(secs):02d}:{int(frames):02d}"


def validate_color_value(value: float, name: str = "color") -> float:
    """
    Validate color adjustment value.
    
    Args:
        value: Color value to validate
        name: Name of the color parameter
        
    Returns:
        float: Validated color value
        
    Raises:
        ValidationError: If value is out of range
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(name, value, "Value must be a number")
    
    # Most color values are in range -1.0 to 1.0
    if value < -1.0 or value > 1.0:
        raise ValidationError(name, value, "Value must be between -1.0 and 1.0")
    
    return float(value)


def get_supported_render_formats() -> List[str]:
    """
    Get list of supported render formats.
    
    Returns:
        List[str]: List of supported format names
    """
    return [
        "QuickTime",
        "MP4", 
        "AVI",
        "MXF",
        "AVCHD",
        "H.264",
        "H.265",
        "Apple ProRes",
        "DNxHD",
        "DNxHR",
        "Cineform",
        "Uncompressed",
        "TIFF",
        "DPX",
        "EXR",
        "JPEG",
        "PNG",
    ]


def get_supported_audio_codecs() -> List[str]:
    """
    Get list of supported audio codecs.
    
    Returns:
        List[str]: List of supported audio codec names
    """
    return [
        "Linear PCM",
        "AAC",
        "MP3",
        "AC-3",
        "FLAC",
        "Vorbis",
    ]
