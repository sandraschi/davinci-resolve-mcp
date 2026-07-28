"""
DaVinci Resolve Connection Manager.

This module handles connection management to the DaVinci Resolve API,
including connection establishment, monitoring, and recovery.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any

from ..types import ConnectionState
from ..utils.exceptions import ResolveAPIError, ResolveConnectionError, ResolveNotRunningError
from .environment import ResolveEnvironment

if TYPE_CHECKING:
    from ..config import DaVinciResolveConfig

logger = logging.getLogger(__name__)


def _add_resolve_to_path() -> None:
    """Add DaVinci Resolve Scripting module to sys.path.
    Must be called after setup_environment_variables() so RESOLVE_SCRIPT_API is set.
    """
    import os
    import sys

    api = os.environ.get("RESOLVE_SCRIPT_API", "")
    if not api:
        return
    modules = os.path.join(api, "Modules")
    if modules and modules not in sys.path:
        sys.path.insert(0, modules)


class ResolveConnectionManager:
    """
    Manages connections to DaVinci Resolve API.

    This class handles the complexity of connecting to DaVinci Resolve,
    including error handling, retry logic, and connection monitoring.
    """

    def __init__(self, config: DaVinciResolveConfig | None = None) -> None:
        """
        Initialize the connection manager.

        Args:
            config: DaVinci Resolve configuration (optional; loaded from defaults if omitted)
        """
        if config is None:
            from ..config import load_default

            config = load_default()
        self.config = config
        self.environment = ResolveEnvironment()

        # Connection state
        self.resolve: Any | None = None
        self.project_manager: Any | None = None
        self.current_project: Any | None = None
        self.connection_status: str = ConnectionState.DISCONNECTED
        self.last_connection_check: float = 0.0
        self._lock = asyncio.Lock()

        # Setup environment — add Resolve scripting module to sys.path
        self.environment.setup_environment_variables()
        _add_resolve_to_path()

    async def connect(self, max_retries: int = 3, retry_delay: float = 1.0) -> bool:
        """
        Establish connection to DaVinci Resolve with retry logic.
        """
        async with self._lock:
            if self.connection_status == ConnectionState.CONNECTED:
                return True

            last_error = None

            for attempt in range(1, max_retries + 1):
                try:
                    if not self.environment.check_resolve_running():
                        raise ResolveNotRunningError("DaVinci Resolve is not running")

                    import DaVinciResolveScript as dvr_script

                    self.resolve = dvr_script.scriptapp("Resolve")
                    if not self.resolve:
                        raise ResolveConnectionError(
                            "scriptapp returned None — Resolve is running but the scripting "
                            "bridge is not responding. Open a project and check Resolve > "
                            "Preferences > System > General > External Scripting 'Always'."
                        )

                    self.project_manager = self.resolve.GetProjectManager()
                    self.connection_status = ConnectionState.CONNECTED
                    self.last_connection_check = time.time()
                    logger.info("Connected to DaVinci Resolve")
                    return True

                except ResolveNotRunningError:
                    self.connection_status = ConnectionState.ERROR
                    raise
                except Exception as e:
                    last_error = e
                    self.connection_status = ConnectionState.ERROR
                    if attempt < max_retries:
                        logger.warning(f"Connect attempt {attempt}: {e}")
                        await asyncio.sleep(retry_delay)

            raise ResolveConnectionError(f"Failed to connect: {last_error}" if last_error else "Failed to connect")

    async def ensure_connection(self) -> bool:
        """
        Ensure connection to DaVinci Resolve is active.
        """
        try:
            current_time = time.time()
            if (current_time - self.last_connection_check) < self.config.connection.connection_check_interval:
                if self.connection_status == ConnectionState.CONNECTED:
                    return True

            if self.resolve and self._test_connection():
                self.last_connection_check = current_time
                return True

            logger.warning("Connection lost, attempting to reconnect...")
            await self.connect()
            return True

        except Exception as e:
            logger.error(f"Failed to ensure connection: {e}")
            return False

    def _test_connection(self) -> bool:
        """Test if the current connection is still valid."""
        try:
            if not self.resolve:
                return False

            # Prefer GetVersion(); fall back to GetVersionString() for API variants.
            if hasattr(self.resolve, "GetVersion"):
                version = self.resolve.GetVersion()
                return version is not None
            if hasattr(self.resolve, "GetVersionString"):
                return bool(self.resolve.GetVersionString())
            return True

        except Exception:
            return False

    async def execute_with_retry(self, operation, *args, **kwargs):
        """
        Execute an operation with retry logic.

        Args:
            operation: Function to execute
            *args: Arguments to pass to operation
            **kwargs: Keyword arguments to pass to operation

        Returns:
            Result of the operation

        Raises:
            ResolveAPIError: If operation fails after all retries
        """
        last_exception = None

        for attempt in range(self.config.connection.retry_attempts):
            try:
                # Ensure connection is active
                if not await self.ensure_connection():
                    raise ResolveConnectionError("Cannot establish connection to DaVinci Resolve")

                # Execute operation
                result = operation(*args, **kwargs)
                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"Operation failed (attempt {attempt + 1}/{self.config.connection.retry_attempts}): {e}")

                if attempt < self.config.connection.retry_attempts - 1:
                    # Wait before retry
                    await asyncio.sleep(self.config.connection.retry_delay)

                    # Try to reconnect
                    try:
                        await self.connect()
                    except Exception:
                        logger.warning("Reconnect attempt failed, will retry")

        # All retries failed
        raise ResolveAPIError(
            f"Operation failed after {self.config.connection.retry_attempts} attempts: {last_exception}"
        )

    def get_connection(self) -> Any:
        """
        Return the Resolve application object from DaVinciResolveScript.

        Raises:
            ResolveConnectionError: If there is no active connection yet.
        """
        if not self.resolve:
            raise ResolveConnectionError(
                "Not connected to DaVinci Resolve. Ensure Resolve is running and the "
                "connection has been established (ensure_connection / connect)."
            )
        return self.resolve

    def get_status(self) -> dict[str, Any]:
        """Summary status for MCP tools and the web API (mirrors connection info)."""
        return self.get_connection_info()

    def get_current_project(self):
        """
        Get the currently active project.

        Returns:
            Current project object or None if no project is active
        """
        try:
            if not self.project_manager:
                return None

            return self.project_manager.GetCurrentProject()

        except Exception as e:
            logger.error(f"Failed to get current project: {e}")
            return None

    def set_current_project(self, project) -> bool:
        """
        Set the current project.

        Args:
            project: Project object to set as current

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.current_project = project
            return True

        except Exception as e:
            logger.error(f"Failed to set current project: {e}")
            return False

    def get_connection_info(self) -> dict[str, Any]:
        """
        Get current connection information.

        Returns:
            Dict[str, Any]: Connection status and information
        """
        try:
            info = {
                "status": self.connection_status,
                "last_check": self.last_connection_check,
                "resolve_running": self.environment.check_resolve_running(),
                "api_available": self.environment.validate_api_access(),
            }

            if self.resolve:
                try:
                    info["resolve_version"] = self.resolve.GetVersion()
                    info["product_name"] = self.resolve.GetProductName()
                except Exception:
                    logger.warning("Could not read Resolve version info", exc_info=True)

            if self.current_project:
                try:
                    info["current_project"] = self.current_project.GetName()
                except Exception:
                    logger.warning("Could not read current project name", exc_info=True)

            return info

        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"status": "error", "error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Dict[str, Any]: Health check results
        """
        health = {
            "overall_status": "unknown",
            "resolve_installation": False,
            "resolve_running": False,
            "api_connection": False,
            "project_access": False,
            "environment_setup": False,
            "details": {},
        }

        try:
            # Check environment
            env_status = self.environment.get_environment_status()
            health["details"]["environment"] = env_status
            health["environment_setup"] = env_status.get("api_available", False)

            # Check installation
            health["resolve_installation"] = env_status.get("resolve_installation") is not None

            # Check if running
            health["resolve_running"] = self.environment.check_resolve_running()

            # Check API connection
            try:
                if await self.ensure_connection():
                    health["api_connection"] = True

                    # Check project access
                    current_project = self.get_current_project()
                    health["project_access"] = current_project is not None
                    if current_project:
                        health["details"]["current_project"] = current_project.GetName()

            except Exception as e:
                health["details"]["connection_error"] = str(e)

            # Determine overall status
            if health["api_connection"] and health["project_access"]:
                health["overall_status"] = "healthy"
            elif health["api_connection"]:
                health["overall_status"] = "connected"
            elif health["resolve_running"]:
                health["overall_status"] = "resolve_running"
            elif health["resolve_installation"]:
                health["overall_status"] = "installed"
            else:
                health["overall_status"] = "not_available"

            return health

        except Exception as e:
            health["overall_status"] = "error"
            health["details"]["health_check_error"] = str(e)
            return health


class ResolveConnectionPool:
    """
    Connection pool for managing multiple DaVinci Resolve connections.

    This is useful for advanced scenarios where multiple projects
    or operations need to be handled concurrently.
    """

    def __init__(self, config: DaVinciResolveConfig, max_connections: int = 3):
        """
        Initialize connection pool.

        Args:
            config: DaVinci Resolve configuration
            max_connections: Maximum number of concurrent connections
        """
        self.config = config
        self.max_connections = max_connections
        self.connections: dict[str, ResolveConnectionManager] = {}
        self.connection_queue = asyncio.Queue()

    async def get_connection(self, connection_id: str = "default") -> ResolveConnectionManager:
        """
        Get a connection from the pool.

        Args:
            connection_id: Identifier for the connection

        Returns:
            ResolveConnectionManager: Connection manager instance
        """
        if connection_id not in self.connections:
            if len(self.connections) >= self.max_connections:
                # Wait for a connection to become available
                await self.connection_queue.get()

            # Create new connection
            self.connections[connection_id] = ResolveConnectionManager(self.config)

        return self.connections[connection_id]

    async def release_connection(self, connection_id: str) -> None:
        """
        Release a connection back to the pool.

        Args:
            connection_id: Identifier for the connection to release
        """
        if connection_id in self.connections:
            await self.connection_queue.put(connection_id)

    async def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        for connection in self.connections.values():
            await connection.disconnect()
        self.connections.clear()

    async def close(self) -> None:
        """Release all pooled connection managers."""
        await self.close_all_connections()
