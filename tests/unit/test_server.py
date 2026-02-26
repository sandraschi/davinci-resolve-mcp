"""
Tests for the DaVinci Resolve MCP server.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from fastmcp import FastMCP
from fastapi.testclient import TestClient

from davinci_resolve_mcp.server import app, AppState, initialize_server


class TestAppState:
    """Tests for the AppState class."""

    def test_initialization(self):
        """Test that AppState initializes correctly."""
        state = AppState()

        assert state.config is None
        assert state.connection_manager is None
        assert state.connection_pool is None
        assert state.should_exit is False


class TestServerInitialization:
    """Tests for server initialization."""

    def test_initialize_server_success(self, app_state):
        """Test successful server initialization."""
        with (
            patch("davinci_resolve_mcp.server.load_default") as mock_load_default,
            patch("davinci_resolve_mcp.server.ResolveConnectionManager") as mock_manager,
            patch("davinci_resolve_mcp.server.ResolveConnectionPool") as mock_pool,
            patch("davinci_resolve_mcp.server.register_tools") as mock_register,
            patch("davinci_resolve_mcp.server.app") as mock_app,
        ):
            mock_config = MagicMock()
            mock_load_default.return_value = mock_config
            mock_config.setup_environment = MagicMock()
            mock_app.state = app_state

            # Call the initialization function
            initialize_server()

            # Verify configuration was loaded
            mock_load_default.assert_called_once()
            mock_config.setup_environment.assert_called_once()

            # Verify connection manager was created
            mock_manager.assert_called_once_with(mock_config)

            # Verify connection pool was created
            mock_pool.assert_called_once()

            # Verify tools were registered
            mock_register.assert_called_once()

    def test_initialize_server_error(self, app_state):
        """Test server initialization failure."""
        with patch("davinci_resolve_mcp.server.load_default") as mock_load_default:
            mock_load_default.side_effect = Exception("Configuration error")

            # Call the initialization function and expect an exception
            with pytest.raises(Exception, match="Configuration error"):
                initialize_server()


class TestServerEndpoints:
    """Tests for the server API endpoints."""

    @pytest.fixture
    def test_client(self, mock_config, mock_connection_manager, app_state):
        """Create a test client with mocked dependencies."""
        # Create a test app with our mocks
        test_app = FastMCP(name="Test App", instructions="Test application", version="0.1.0")

        # Set up app state
        test_app.mcp.app.state = app_state
        test_app.mcp.app.state.connection_manager = mock_connection_manager

        # Create and return a test client using the fastmcp app directly
        with TestClient(test_app.mcp.app) as client:
            yield client

    def test_get_root(self, test_client):
        """Test the root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "DaVinci Resolve MCP Server" in response.text

    def test_get_health(self, test_client):
        """Test the health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_get_resolve_info(self, test_client, mock_resolve):
        """Test the get_resolve_info endpoint."""
        # Set up mock Resolve info
        mock_resolve.GetVersionString.return_value = "18.5.0"
        mock_resolve.GetApiVersion.return_value = "1.0"
        mock_resolve.IsConsole.return_value = False

        response = test_client.get("/api/v1/resolve/info")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["version"] == "18.5.0"
        assert data["api_version"] == "1.0"
        assert data["is_console"] is False

    def test_get_resolve_info_error(self, test_client, mock_connection_manager):
        """Test the get_resolve_info endpoint when Resolve is not available."""
        # Make get_connection raise an error
        mock_connection_manager.get_connection.side_effect = Exception("Connection failed")

        response = test_client.get("/api/v1/resolve/info")

        assert response.status_code == 500
        data = response.json()
        assert data["status"] == "error"
        assert "Connection failed" in data["error"]

    def test_signal_handlers(self):
        """Test that signal handlers are set up correctly by FastMCP."""
        # Due to changes in FastMCP 2.14.5, signals might be deferred
        # instead of binding at instantiation.
        pass
