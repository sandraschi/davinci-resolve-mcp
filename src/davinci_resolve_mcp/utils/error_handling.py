"""
Error Handling Utilities for DaVinci Resolve MCP.

This module provides standardized error handling and response formatting
for the FastMCP server.
"""
import logging
import traceback
from functools import wraps
from typing import Any, Dict, Optional, Type, TypeVar, Callable, Awaitable, cast

from fastmcp import FastMCP
from fastmcp.tools import Tool

from .exceptions import (
    DaVinciResolveMCPError,
    ResolveConnectionError,
    ResolveOperationError,
    ResolveAPIError,
    ResolveNotRunningError
)
from ..types import ErrorResponse, SuccessResponse, F

# Alias for backward compatibility
ResolveError = DaVinciResolveMCPError

logger = logging.getLogger(__name__)


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


def create_tool(func: F, **tool_kwargs) -> F:
    """
    Decorator to create a FastMCP tool with error handling.

    Args:
        func: The function to wrap with error handling
        **tool_kwargs: Additional keyword arguments (currently unused)

    Returns:
        The wrapped function with error handling
    """
    # Wrap the function with error handling
    wrapped_func = handle_errors(func)

    # Store original function attributes
    wrapped_func.__name__ = func.__name__
    wrapped_func.__doc__ = func.__doc__
    wrapped_func.__annotations__ = func.__annotations__

    return wrapped_func


def register_error_handlers(app: FastMCP) -> None:
    """
    Register error handlers with the FastMCP application.

    Note: FastMCP handles errors differently than FastAPI.
    Error handling is done at the tool level using the handle_errors decorator.

    Args:
        app: The FastMCP application instance
    """
    # Error handling is now done at the tool level with handle_errors decorator
    # FastMCP doesn't have FastAPI-style exception handlers
    pass
