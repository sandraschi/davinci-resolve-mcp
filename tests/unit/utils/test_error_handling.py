"""
Tests for the error handling utilities.
"""

import pytest
from fastmcp import FastMCP

from davinci_resolve_mcp.utils.error_handling import (
    ErrorResponse,
    handle_resolve_error,
    register_error_handlers,
)
from davinci_resolve_mcp.utils.exceptions import (
    MediaPoolError,
    ProjectOperationError,
    ResolveAPIError,
    ResolveConnectionError,
)


class TestErrorResponse:
    """Tests for the ErrorResponse class."""

    def test_create_error_response(self):
        """Test creating an ErrorResponse instance."""
        error = ErrorResponse(error_type="TEST_ERROR", message="Test error message")

        assert error.status == "error"
        assert error.error_type == "TEST_ERROR"
        assert error.message == "Test error message"

    def test_error_response_dict(self):
        """Test ErrorResponse as dictionary."""
        error = ErrorResponse(error_type="TEST_ERROR", message="Test error message")

        result = error.dict()

        assert result["status"] == "error"
        assert result["error_type"] == "TEST_ERROR"
        assert result["message"] == "Test error message"


class TestErrorHandlers:
    """Tests for the error handling utilities."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.app = FastMCP(name="Test App", instructions="Test application", version="0.1.0")
        register_error_handlers(self.app)
        self._connection_error = ResolveConnectionError("Connection failed")
        self._project_error = ProjectOperationError("Project not found")
        self._media_error = MediaPoolError("Media not found")
        self._api_error = ResolveAPIError("API call failed")
        self._generic_error = ValueError("A generic error occurred")

    def test_resolve_connection_error_handler(self):
        """Test handling of ResolveConnectionError."""
        result = handle_resolve_error(self._connection_error)
        assert result["status"] == "error"
        assert result["error_type"] == "connection_error"

    def test_resolve_project_error_handler(self):
        """Test handling of ProjectOperationError."""
        result = handle_resolve_error(self._project_error)
        assert result["status"] == "error"

    def test_resolve_media_error_handler(self):
        """Test handling of MediaPoolError."""
        result = handle_resolve_error(self._media_error)
        assert result["status"] == "error"

    def test_resolve_api_error_handler(self):
        """Test handling of ResolveAPIError."""
        result = handle_resolve_error(self._api_error)
        assert result["status"] == "error"

    def test_generic_error_handler(self):
        """Test handling of generic exceptions."""
        result = handle_resolve_error(self._generic_error)
        assert result["status"] == "error"
        assert result["error_type"] == "unexpected_error"

    def test_handle_resolve_error_function(self):
        """Test handle_resolve_error returns structured error dicts."""
        response = handle_resolve_error(ResolveConnectionError("Connection failed"))
        assert response["status"] == "error"
        assert "Connection failed" in response["message"]
        assert response["error_type"] == "connection_error"

    def test_register_error_handlers(self):
        """Test that error handlers registration works (FastMCP doesn't use FastAPI-style handlers)."""
        app = FastMCP(name="Test App", instructions="Test application", version="0.1.0")
        register_error_handlers(app)

class TestHandleErrorsDecorator:
    """Tests for the handle_errors decorator."""

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test the decorator with a successful function call."""
        from davinci_resolve_mcp.utils.error_handling import handle_errors

        @handle_errors
        def test_func():
            return {"status": "success", "data": "test"}

        result = await test_func()
        assert result == {"status": "success", "data": "test"}

    @pytest.mark.asyncio
    async def test_resolve_connection_error_handling(self):
        """Test handling of ResolveConnectionError."""
        from davinci_resolve_mcp.utils.error_handling import handle_errors

        @handle_errors
        def test_func():
            raise ResolveConnectionError("Connection failed")

        result = await test_func()
        assert isinstance(result, dict)
        assert result.get("status") == "error"
        assert result.get("error_type") == "connection_error"

    @pytest.mark.asyncio
    async def test_generic_exception_handling(self):
        """Test handling of generic exceptions."""
        from davinci_resolve_mcp.utils.error_handling import handle_errors

        @handle_errors
        def test_func():
            raise ValueError("Something went wrong")

        result = await test_func()
        assert isinstance(result, dict)
        assert result.get("status") == "error"
        assert result.get("error_type") == "unexpected_error"
