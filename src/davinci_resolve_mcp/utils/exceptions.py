"""
Custom exceptions for DaVinci Resolve MCP Server.

This module defines custom exception classes for handling various
error conditions in the DaVinci Resolve MCP server.
"""


class DaVinciResolveMCPError(Exception):
    """Base exception for all DaVinci Resolve MCP errors."""

    def __init__(self, message: str, recovery_action: str = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            recovery_action: Suggested recovery action
        """
        super().__init__(message)
        self.recovery_action = recovery_action


class ResolveConnectionError(DaVinciResolveMCPError):
    """Exception raised when connection to DaVinci Resolve fails."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="ensure_resolve_running")


class ResolveNotRunningError(ResolveConnectionError):
    """Exception raised when DaVinci Resolve is not running."""

    def __init__(self, message: str = "DaVinci Resolve is not running"):
        super().__init__(message)
        self.recovery_action = "start_resolve"


class ResolveAPIError(DaVinciResolveMCPError):
    """Exception raised when DaVinci Resolve API operation fails."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="check_api_compatibility")


class ResolveOperationError(DaVinciResolveMCPError):
    """
    Base exception for operation-related errors in DaVinci Resolve.

    This exception is raised when a general operation in DaVinci Resolve fails.
    """

    def __init__(self, message: str, recovery_action: str = "retry_operation"):
        """
        Initialize the exception.

        Args:
            message: Error message describing the operation failure
            recovery_action: Suggested recovery action (default: "retry_operation")
        """
        super().__init__(message, recovery_action)


class ProjectNotFoundError(DaVinciResolveMCPError):
    """Exception raised when specified project doesn't exist."""

    def __init__(self, project_name: str):
        super().__init__(
            f"Project '{project_name}' not found", recovery_action="list_available_projects"
        )


class ProjectOperationError(DaVinciResolveMCPError):
    """Exception raised when project operation fails."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="check_project_state")


class MediaPoolError(DaVinciResolveMCPError):
    """Exception raised when media pool operation fails."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="check_media_pool_state")


class MediaImportError(MediaPoolError):
    """Exception raised when media import fails."""

    def __init__(self, file_path: str, reason: str = None):
        message = f"Failed to import media: {file_path}"
        if reason:
            message += f" - {reason}"
        super().__init__(message)
        self.recovery_action = "check_file_format"


class TimelineError(DaVinciResolveMCPError):
    """Exception raised when timeline operation fails."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="verify_timeline_state")


class TimelineNotFoundError(TimelineError):
    """Exception raised when specified timeline doesn't exist."""

    def __init__(self, timeline_name: str):
        super().__init__(
            f"Timeline '{timeline_name}' not found", recovery_action="list_available_timelines"
        )


class ColorGradingError(DaVinciResolveMCPError):
    """Exception raised when color grading operation fails."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="check_color_page_state")


class RenderError(DaVinciResolveMCPError):
    """Exception raised when rendering operation fails."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="check_render_settings")


class RenderQueueError(RenderError):
    """Exception raised when render queue operation fails."""

    def __init__(self, message: str):
        super().__init__(
            f"Render queue error: {message}", recovery_action="check_render_queue_state"
        )


class AudioProcessingError(DaVinciResolveMCPError):
    """Exception raised when audio processing operation fails."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="check_audio_settings")


class ConfigurationError(DaVinciResolveMCPError):
    """Exception raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="check_configuration")


class EnvironmentError(DaVinciResolveMCPError):
    """Exception raised when environment setup fails."""

    def __init__(self, message: str):
        super().__init__(message, recovery_action="setup_environment")


class ValidationError(DaVinciResolveMCPError):
    """Exception raised when input validation fails."""

    def __init__(self, field: str, value: any, reason: str = None):
        message = f"Invalid value for {field}: {value}"
        if reason:
            message += f" - {reason}"
        super().__init__(message, recovery_action="check_input_parameters")


class OperationTimeoutError(DaVinciResolveMCPError):
    """Exception raised when operation times out."""

    def __init__(self, operation: str, timeout: float):
        super().__init__(
            f"Operation '{operation}' timed out after {timeout} seconds",
            recovery_action="increase_timeout_or_check_system",
        )


class InsufficientPermissionsError(DaVinciResolveMCPError):
    """Exception raised when insufficient permissions for operation."""

    def __init__(self, operation: str):
        super().__init__(
            f"Insufficient permissions for operation: {operation}",
            recovery_action="check_file_permissions",
        )


class UnsupportedFormatError(DaVinciResolveMCPError):
    """Exception raised when file format is not supported."""

    def __init__(self, file_path: str, format_type: str = None):
        message = f"Unsupported format: {file_path}"
        if format_type:
            message += f" (detected as {format_type})"
        super().__init__(message, recovery_action="convert_to_supported_format")


class ResourceNotAvailableError(DaVinciResolveMCPError):
    """Exception raised when required resource is not available."""

    def __init__(self, resource: str):
        super().__init__(
            f"Resource not available: {resource}", recovery_action="check_resource_availability"
        )
