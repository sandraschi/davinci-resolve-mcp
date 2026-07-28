"""
Tests for the DaVinci Resolve connection manager.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from davinci_resolve_mcp.connection.manager import ResolveConnectionManager, ResolveConnectionPool
from davinci_resolve_mcp.utils.exceptions import ResolveConnectionError, ResolveNotRunningError


class TestResolveConnectionManager:
    """Tests for the ResolveConnectionManager class."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_config):
        """Set up test environment."""
        self.config = mock_config
        self.manager = ResolveConnectionManager(self.config)

        # Mock DaVinciResolveScript module
        self.mock_dvr = MagicMock()
        self.mock_resolve = MagicMock()
        self.mock_dvr.scriptapp.return_value = self.mock_resolve

        # Mock project manager and project
        self.mock_project_manager = MagicMock()
        self.mock_project = MagicMock()
        self.mock_resolve.GetProjectManager.return_value = self.mock_project_manager
        self.mock_project_manager.GetCurrentProject.return_value = self.mock_project

        # Patch the DaVinciResolveScript import
        self.dvr_patcher = patch("davinci_resolve_mcp.connection.manager.import_module", return_value=self.mock_dvr)
        self.dvr_patcher.start()

        yield

        # Cleanup
        self.dvr_patcher.stop()

    def test_initialization(self):
        """Test that the connection manager initializes correctly."""
        assert self.manager.config == self.config
        assert self.manager.resolve is None
        assert self.manager.project_manager is None
        assert self.manager.current_project is None
        assert self.manager.connection_status == "disconnected"

    @patch("davinci_resolve_mcp.connection.manager.ResolveEnvironment.check_resolve_running", return_value=False)
    async def test_connect_resolve_not_running(self, mock_check_running):
        """Test connect() when DaVinci Resolve is not running."""
        with pytest.raises(ResolveNotRunningError):
            await self.manager.connect()

        assert self.manager.connection_status == "error"

    @patch("davinci_resolve_mcp.connection.manager.ResolveEnvironment.check_resolve_running", return_value=True)
    async def test_connect_success(self, mock_check_running):
        """Test successful connection to DaVinci Resolve."""
        result = await self.manager.connect()

        assert result is True
        assert self.manager.connection_status == "connected"
        assert self.manager.resolve == self.mock_resolve
        assert self.manager.project_manager == self.mock_project_manager
        assert self.manager.current_project == self.mock_project

        # Verify the scriptapp was called with the correct parameters
        self.mock_dvr.scriptapp.assert_called_once_with("Resolve")

    @patch("davinci_resolve_mcp.connection.manager.ResolveEnvironment.check_resolve_running", return_value=True)
    async def test_connect_import_error(self, mock_check_running, monkeypatch):
        """Test connection failure due to import error."""

        # Make the import fail
        def mock_import_error(*args, **kwargs):
            raise ImportError("Module not found")

        monkeypatch.setattr("davinci_resolve_mcp.connection.manager.import_module", mock_import_error)

        with pytest.raises(ResolveConnectionError) as exc_info:
            await self.manager.connect()

        assert "Cannot import DaVinciResolveScript" in str(exc_info.value)
        assert self.manager.connection_status == "error"

    @patch("davinci_resolve_mcp.connection.manager.ResolveEnvironment.check_resolve_running", return_value=True)
    async def test_connect_resolve_not_available(self, mock_check_running):
        """Test connection when Resolve API is not available."""
        self.mock_dvr.scriptapp.return_value = None

        with pytest.raises(ResolveConnectionError) as exc_info:
            await self.manager.connect()

        assert "Failed to connect to DaVinci Resolve" in str(exc_info.value)
        assert self.manager.connection_status == "error"

    @patch("davinci_resolve_mcp.connection.manager.ResolveEnvironment.check_resolve_running", return_value=True)
    async def test_connect_project_manager_error(self, mock_check_running):
        """Test connection when project manager cannot be accessed."""
        self.mock_resolve.GetProjectManager.return_value = None

        with pytest.raises(ResolveConnectionError) as exc_info:
            await self.manager.connect()

        assert "Failed to get project manager" in str(exc_info.value)
        assert self.manager.connection_status == "error"

    async def test_disconnect(self):
        """Test disconnecting from DaVinci Resolve."""
        # First connect
        self.manager.resolve = self.mock_resolve
        self.manager.project_manager = self.mock_project_manager
        self.manager.current_project = self.mock_project
        self.manager.connection_status = "connected"

        # Mock project save
        self.mock_project.SaveProject.return_value = True

        await self.manager.disconnect()

        # Verify project was saved
        self.mock_project.SaveProject.assert_called_once()

        # Verify state was reset
        assert self.manager.resolve is None
        assert self.manager.project_manager is None
        assert self.manager.current_project is None
        assert self.manager.connection_status == "disconnected"

    async def test_disconnect_no_connection(self):
        """Test disconnect when not connected."""
        # Should not raise an exception
        await self.manager.disconnect()


class TestResolveConnectionPool:
    """Tests for the ResolveConnectionPool class."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_config):
        """Set up test environment."""
        self.config = mock_config
        self.max_connections = 3
        self.pool = ResolveConnectionPool(self.config, self.max_connections)

        # Mock connection manager
        self.mock_connection = AsyncMock()
        self.mock_connection.connect.return_value = True

        # Patch the ResolveConnectionManager
        self.manager_patcher = patch(
            "davinci_resolve_mcp.connection.manager.ResolveConnectionManager", return_value=self.mock_connection
        )
        self.manager_patcher.start()

        yield

        # Cleanup
        self.manager_patcher.stop()

    def test_initialization(self):
        """Test that the connection pool initializes correctly."""
        assert self.pool.config == self.config
        assert self.pool.max_connections == self.max_connections
        assert len(self.pool.connections) == 0
        # Queue is filled lazily on release; starts empty
        assert self.pool.connection_queue.qsize() == 0

    async def test_get_connection(self):
        """Test getting a connection from the pool."""
        connection = await self.pool.get_connection("test-connection")

        # Should return our mock connection
        assert connection == self.mock_connection

        # Should have called connect on the connection
        self.mock_connection.connect.assert_awaited_once()

        # Should be in the connections dict
        assert "test-connection" in self.pool.connections

        # Queue size should be reduced
        assert self.pool.connection_queue.qsize() == self.max_connections - 1

    async def test_get_connection_pool_exhausted(self):
        """Test getting a connection when the pool is exhausted."""
        # Exhaust the pool
        for i in range(self.max_connections):
            await self.pool.get_connection(f"test-{i}")

        # Next get_connection should raise an exception
        with pytest.raises(ResolveConnectionError) as exc_info:
            await self.pool.get_connection("extra-connection")

        assert "Connection pool exhausted" in str(exc_info.value)

    async def test_release_connection(self):
        """Test releasing a connection back to the pool."""
        # Get a connection
        await self.pool.get_connection("test-connection")

        # Release it
        await self.pool.release_connection("test-connection")

        # Should be removed from connections
        assert "test-connection" not in self.pool.connections

        # Queue size should be back to max_connections
        assert self.pool.connection_queue.qsize() == self.max_connections

    async def test_release_nonexistent_connection(self):
        """Test releasing a connection that doesn't exist."""
        # Should not raise an exception
        await self.pool.release_connection("nonexistent-connection")

    async def test_close_all_connections(self):
        """Test closing all connections in the pool."""
        # Add some connections
        for i in range(2):
            await self.pool.get_connection(f"test-{i}")

        # Close all connections
        await self.pool.close_all_connections()

        # Should have called close on all connections
        assert self.mock_connection.close.await_count == 2

        # Connections dict should be empty
        assert len(self.pool.connections) == 0

        # Queue should be restored to max_connections
        assert self.pool.connection_queue.qsize() == self.max_connections
