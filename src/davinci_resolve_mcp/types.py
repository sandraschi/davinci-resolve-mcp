"""
Shared type definitions for DaVinci Resolve MCP.

This module contains common type definitions used across the application
to prevent circular imports and improve code organization.
"""

from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel

# Type variables for generic function typing
F = TypeVar("F", bound=Callable[..., Any])


# Common response types
class SuccessResponse(BaseModel):
    """Standard success response format."""

    status: str = "success"
    data: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Standard error response format."""

    status: str = "error"
    error_type: str
    message: str
    details: dict[str, Any] | None = None


# Connection related types
class ConnectionState:
    """Connection state constants."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


# Configuration related types
class ResolveConfig(BaseModel):
    """Base configuration model for DaVinci Resolve."""

    host: str = "localhost"
    port: int = 8080
    timeout: float = 30.0
    debug: bool = False
    log_level: str = "info"
    max_workers: int = 4
