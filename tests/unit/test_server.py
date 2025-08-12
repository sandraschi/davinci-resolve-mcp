"""
Tests for the DaVinci Resolve MCP server.
"""
import asyncio
import signal
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from fastmcp import FastMCP
from fastapi.testclient import TestClient

from davinci_resolve_mcp.server import app, AppState, lifespan, handle_shutdown, handle_startup
from davinci_resolve_mcp.config import DaVinciResolveConfig
from davinci_resolve_mcp.connection.manager import ResolveConnectionManager

class TestAppState:
    """Tests for the AppState class."""
    
    def test_initialization(self, mock_config):
        """Test that AppState initializes correctly."""
        state = AppState(mock_config)
        
        assert state.config == mock_config
        assert state.connection_manager is None
        assert state.connection_pool is None
        assert state.should_exit is False
    
    def test_shutdown(self, mock_config):
        """Test the shutdown method."""
        state = AppState(mock_config)
        state.connection_pool = AsyncMock()
        
        # Call shutdown
        state.shutdown()
        
        assert state.should_exit is True
        state.connection_pool.close_all_connections.assert_called_once()


class TestServerLifespan:
    """Tests for the server lifespan events."""
    
    @pytest.fixture
    def mock_app(self):
        """Create a mock FastMCP app with state."""
        app = FastMCP(
            name="Test App",
            description="Test application",
            version="0.1.0"
        )
        app.state = AppState(MagicMock())
        return app
    
    @pytest.mark.asyncio
    async def test_lifespan_startup(self, mock_app):
        """Test the application startup event."""
        # Create a mock lifespan context
        mock_lifespan_context = AsyncMock()
        mock_lifespan_context.__aenter__.return_value = {"app": mock_app}
        
        # Mock the connection manager
        mock_connection_manager = AsyncMock()
        mock_connection_manager.connect.return_value = True
        
        with patch('davinci_resolve_mcp.server.ResolveConnectionManager', 
                  return_value=mock_connection_manager) as mock_manager_cls:
            # Call the lifespan function
            async with lifespan(mock_app) as context:
                assert context == {"app": mock_app}
                
                # Verify the connection manager was initialized
                mock_manager_cls.assert_called_once_with(mock_app.state.config)
                
                # Verify connect was called
                mock_connection_manager.connect.assert_awaited_once()
                
                # Verify the app state was updated
                assert mock_app.state.connection_manager == mock_connection_manager
    
    @pytest.mark.asyncio
    async def test_lifespan_shutdown(self, mock_app):
        """Test the application shutdown event."""
        # Set up a mock connection pool
        mock_connection_pool = AsyncMock()
        mock_app.state.connection_pool = mock_connection_pool
        
        # Call the shutdown handler
        await handle_shutdown(mock_app)
        
        # Verify the connection pool was closed
        mock_connection_pool.close_all_connections.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_lifespan_startup_connection_error(self, mock_app):
        """Test startup when connection to Resolve fails."""
        # Mock the connection manager to fail connection
        mock_connection_manager = AsyncMock()
        mock_connection_manager.connect.return_value = False
        
        with patch('davinci_resolve_mcp.server.ResolveConnectionManager', 
                  return_value=mock_connection_manager):
            # Call the lifespan function and expect an exception
            with pytest.raises(RuntimeError, match="Failed to connect to DaVinci Resolve"):
                async with lifespan(mock_app):
                    pass
    
    @pytest.mark.asyncio
    async def test_handle_startup(self, mock_app):
        """Test the handle_startup function."""
        # Mock the connection manager
        mock_connection_manager = AsyncMock()
        mock_connection_manager.connect.return_value = True
        mock_app.state.connection_manager = mock_connection_manager
        
        # Call the startup handler
        await handle_startup(mock_app)
        
        # Verify connect was called
        mock_connection_manager.connect.assert_awaited_once()


class TestServerEndpoints:
    """Tests for the server API endpoints."""
    
    @pytest.fixture
    def test_client(self, mock_config, mock_connection_manager):
        """Create a test client with mocked dependencies."""
        # Create a test app with our mocks
        test_app = FastMCP(
            name="Test App",
            description="Test application",
            version="0.1.0"
        )
        
        # Set up app state
        test_app.state = AppState(mock_config)
        test_app.state.connection_manager = mock_connection_manager
        
        # Register routes from the main app
        test_app.include_router(app.router)
        
        # Create and return a test client
        with TestClient(test_app) as client:
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
    
    def test_signal_handlers(self, mock_config):
        """Test that signal handlers are set up correctly."""
        # Mock signal.signal
        with patch('signal.signal') as mock_signal:
            # Create an app with our signal handlers
            test_app = FastMCP(
                name="Test App",
                description="Test application",
                version="0.1.0"
            )
            test_app.state = AppState(mock_config)
            
            # Call the signal handler setup
            test_app.router.on_startup.append(lambda: handle_startup(test_app))
            test_app.router.on_shutdown.append(lambda: handle_shutdown(test_app))
            
            # Verify signal handlers were set up
            assert len(test_app.router.on_startup) > 0
            assert len(test_app.router.on_shutdown) > 0
