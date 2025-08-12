"""
Error Handling Utilities for DaVinci Resolve MCP.

This module provides standardized error handling and response formatting
for the FastMCP server.
"""
import logging
import traceback
from typing import Any, Dict, Optional, Type, TypeVar, Callable, Awaitable
from functools import wraps

from fastmcp import FastMCP
from fastmcp.tools import Tool
from pydantic import BaseModel

from .exceptions import (
    DaVinciResolveMCPError,
    ResolveConnectionError,
    ResolveOperationError,
    ResolveAPIError,
    ResolveNotRunningError
)

# Alias for backward compatibility
ResolveError = DaVinciResolveMCPError

logger = logging.getLogger(__name__)

# Type variable for generic function typing
F = TypeVar('F', bound=Callable[..., Awaitable[Any]])


class ErrorResponse(BaseModel):
    """Standard error response format."""
    status: str = "error"
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel):
    """Standard success response format."""
    status: str = "success"
    data: Dict[str, Any]


def handle_errors(func: F) -> Callable[..., Any]:
    """
    Decorator to handle and standardize error responses.
    
    This decorator catches exceptions and wraps them in a standardized
    error response format using the handle_resolve_error function.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # Call the original function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
                
            # If the function returns a response, ensure it has the right format
            if isinstance(result, dict):
                if "status" not in result:
                    return SuccessResponse(data=result).dict()
            
            return result
            
        except Exception as e:
            # Log the full exception with traceback
            logger.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            
            # Handle the error using the centralized error handler
            return handle_resolve_error(e)
    
    return wrapper  # type: ignore


def handle_resolve_error(exc: Exception) -> dict:
    """
    Handle a ResolveError and return an error response.
    
    Args:
        exc: The exception that was raised
        
    Returns:
        dict: A dictionary containing the error response
    """
    if isinstance(exc, ResolveConnectionError):
        return ErrorResponse(
            error_type="connection_error",
            message=str(exc) or "Failed to connect to DaVinci Resolve",
            details={"original_error": str(exc)}
        ).dict()
    elif isinstance(exc, ResolveOperationError):
        return ErrorResponse(
            error_type="operation_error",
            message=str(exc) or "Operation failed in DaVinci Resolve",
            details={"original_error": str(exc)}
        ).dict()
    elif isinstance(exc, ResolveAPIError):
        return ErrorResponse(
            error_type="api_error",
            message="DaVinci Resolve API returned an error",
            details={"original_error": str(exc)}
        ).dict()
    elif isinstance(exc, ResolveNotRunningError):
        return ErrorResponse(
            error_type="not_running",
            message="DaVinci Resolve is not running",
            details={"original_error": str(exc)}
        ).dict()
    elif isinstance(exc, ResolveError):
        return ErrorResponse(
            error_type="resolve_error",
            message="An error occurred in DaVinci Resolve",
            details={"original_error": str(exc)}
        ).dict()
    else:
        logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
        return ErrorResponse(
            error_type="unexpected_error",
            message="An unexpected error occurred",
            details={
                "error": str(exc),
                "type": type(exc).__name__,
                "traceback": traceback.format_exc()
            }
        ).dict()


def create_tool(func: F, **tool_kwargs) -> Tool:
    """
    Create a FastMCP tool with error handling.
    
    This is a convenience function that wraps a function with error handling
    and creates a FastMCP tool from it.
    """
    # Apply error handling decorator
    wrapped_func = handle_errors(func)
    
    # Create the tool with the wrapped function
    return Tool(wrapped_func, **tool_kwargs)
