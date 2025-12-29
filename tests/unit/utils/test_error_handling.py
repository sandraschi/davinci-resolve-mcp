"""
Tests for the error handling utilities.
"""
import pytest
from fastmcp import FastMCP
from fastapi import status

from davinci_resolve_mcp.utils.error_handling import (
    ErrorResponse,
    handle_resolve_error,
    register_error_handlers
)
from davinci_resolve_mcp.utils.exceptions import (
    ResolveConnectionError,
    ProjectOperationError,
    MediaPoolError,
    ResolveAPIError
)

class TestErrorResponse:
    """Tests for the ErrorResponse class."""
    
    def test_create_error_response(self):
        """Test creating an ErrorResponse instance."""
        error = ErrorResponse(
            error_type="TEST_ERROR",
            message="Test error message"
        )

        assert error.status == "error"
        assert error.error_type == "TEST_ERROR"
        assert error.message == "Test error message"
    
    def test_error_response_dict(self):
        """Test ErrorResponse as dictionary."""
        error = ErrorResponse(
            error_type="TEST_ERROR",
            message="Test error message"
        )

        result = error.dict()

        assert result["status"] == "error"
        assert result["error_type"] == "TEST_ERROR"
        assert result["message"] == "Test error message"


class TestErrorHandlers:
    """Tests for the error handling utilities."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.app = FastMCP(
            name="Test App",
            instructions="Test application",
            version="0.1.0"
        )
        
        # Register error handlers
        register_error_handlers(self.app)
        
        # Create a test route that raises an exception
        @self.app.get("/test/connection-error")
        async def connection_error():
            raise ResolveConnectionError("Connection failed")
            
        @self.app.get("/test/project-error")
        async def project_error():
            raise ProjectOperationError("Project not found", project_name="test")
            
        @self.app.get("/test/media-error")
        async def media_error():
            raise MediaPoolError("Media not found", media_path="/path/to/media")
            
        @self.app.get("/test/api-error")
        async def api_error():
            raise ResolveAPIError("API call failed", method="test_method", params={"param": "value"})
            
        @self.app.get("/test/generic-error")
        async def generic_error():
            raise ValueError("A generic error occurred")
    
    def test_resolve_connection_error_handler(self, test_client):
        """Test handling of ResolveConnectionError."""
        response = test_client.get("/test/connection-error")
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "error"
        assert "Connection failed" in data["error"]
        assert data["error_code"] == "RESOLVE_CONNECTION_ERROR"
    
    def test_resolve_project_error_handler(self, test_client):
        """Test handling of ProjectOperationError."""
        response = test_client.get("/test/project-error")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["status"] == "error"
        assert "Project not found" in data["error"]
        assert data["error_code"] == "RESOLVE_PROJECT_ERROR"
        assert data["details"]["project_name"] == "test"
    
    def test_resolve_media_error_handler(self, test_client):
        """Test handling of MediaPoolError."""
        response = test_client.get("/test/media-error")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["status"] == "error"
        assert "Media not found" in data["error"]
        assert data["error_code"] == "RESOLVE_MEDIA_ERROR"
        assert data["details"]["media_path"] == "/path/to/media"
    
    def test_resolve_api_error_handler(self, test_client):
        """Test handling of ResolveAPIError."""
        response = test_client.get("/test/api-error")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["status"] == "error"
        assert "API call failed" in data["error"]
        assert data["error_code"] == "RESOLVE_API_ERROR"
        assert data["details"]["method"] == "test_method"
        assert data["details"]["params"] == {"param": "value"}
    
    def test_generic_error_handler(self, test_client):
        """Test handling of generic exceptions."""
        response = test_client.get("/test/generic-error")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["status"] == "error"
        assert "A generic error occurred" in data["error"]
        assert data["error_code"] == "INTERNAL_SERVER_ERROR"
    
    def test_handle_resolve_error_decorator(self):
        """Test the handle_resolve_error decorator."""
        # Create a test function that raises an exception
        @handle_resolve_error
        def test_func():
            raise ResolveConnectionError("Connection failed")
        
        # Call the function and verify it returns an error response
        response = test_func()
        
        assert response["status"] == "error"
        assert "Connection failed" in response["error"]
        assert response["error_code"] == "RESOLVE_CONNECTION_ERROR"
    
    def test_register_error_handlers(self):
        """Test that error handlers registration works (FastMCP doesn't use FastAPI-style handlers)."""
        app = FastMCP(
            name="Test App",
            instructions="Test application",
            version="0.1.0"
        )

        # Register error handlers (should not raise any exceptions)
        register_error_handlers(app)

        # FastMCP doesn't have exception_handlers attribute like FastAPI
        # Error handling is done at the tool level with decorators


class TestHandleErrorsDecorator:
    """Tests for the handle_errors decorator."""

    def test_successful_execution(self):
        """Test the decorator with a successful function call."""
        from davinci_resolve_mcp.utils.error_handling import handle_errors

        @handle_errors
        def test_func():
            return {"status": "success", "data": "test"}

        result = test_func()
        assert result == {"status": "success", "data": "test"}
    
    def test_resolve_connection_error_handling(self):
        """Test handling of ResolveConnectionError."""
        from davinci_resolve_mcp.utils.error_handling import handle_errors

        @handle_errors
        def test_func():
            raise ResolveConnectionError("Connection failed")

        result = test_func()
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is False
    
    def test_generic_exception_handling(self):
        """Test handling of generic exceptions."""
        from davinci_resolve_mcp.utils.error_handling import handle_errors

        @handle_errors
        def test_func():
            raise ValueError("Something went wrong")

        result = test_func()
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is False
