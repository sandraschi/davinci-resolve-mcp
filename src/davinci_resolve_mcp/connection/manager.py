"""
DaVinci Resolve Connection Manager.

This module handles connection management to the DaVinci Resolve API,
including connection establishment, monitoring, and recovery.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Dict, Optional, Any, Type, TYPE_CHECKING, cast

from ..types import ConnectionState
from ..utils.exceptions import (
    ResolveConnectionError,
    ResolveNotRunningError,
    ResolveAPIError,
    ResolveOperationError
)
from .environment import ResolveEnvironment

if TYPE_CHECKING:
    from ..config import DaVinciResolveConfig
    import DaVinciResolveScript as DVR_script  # type: ignore

logger = logging.getLogger(__name__)


class ResolveConnectionManager:
    """
    Manages connections to DaVinci Resolve API.
    
    This class handles the complexity of connecting to DaVinci Resolve,
    including error handling, retry logic, and connection monitoring.
    """
    
    def __init__(self, config: 'DaVinciResolveConfig') -> None:
        """
        Initialize the connection manager.
        
        Args:
            config: DaVinci Resolve configuration
        """
        self.config = config
        self.environment = ResolveEnvironment()
        
        # Connection state
        self.resolve: Optional[Any] = None
        self.project_manager: Optional[Any] = None
        self.current_project: Optional[Any] = None
        self.connection_status: str = ConnectionState.DISCONNECTED
        self.last_connection_check: float = 0.0
        self._lock = asyncio.Lock()
        
        # Setup environment
        self.environment.setup_environment_variables()
        
    async def connect(self, max_retries: int = 3, retry_delay: float = 1.0) -> bool:
        """
        Establish connection to DaVinci Resolve with retry logic.
        
        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Delay between retry attempts in seconds
            
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            ResolveNotRunningError: If DaVinci Resolve is not running
            ResolveConnectionError: If connection fails after all retries
        """
        async with self._lock:
            if self.connection_status == ConnectionState.CONNECTED:
                return True
                
            last_error = None
            
            for attempt in range(1, max_retries + 1):
                try:
                    # Check if Resolve is running
                    if not self.environment.check_resolve_running():
                        raise ResolveNotRunningError("DaVinci Resolve is not running")
                    
                    # Import DaVinci Resolve script module
                    try:
                        import DaVinciResolveScript as dvr_script  # type: ignore
                    except ImportError as e:
                        raise ResolveConnectionError(
                            f"Cannot import DaVinciResolveScript: {e}. "
                            "Make sure DaVinci Resolve is installed and the script module is available."
                        ) from e
                    
                    # Establish connection
                    self.resolve = dvr_script.scriptapp("Resolve")
                    if not self.resolve:
                        raise ResolveConnectionError(
                            "Failed to connect to DaVinci Resolve: scriptapp returned None"
                        )
                    
                    # Get project manager
                    self.project_manager = self.resolve.GetProjectManager()
                    if not self.project_manager:
                        raise ResolveConnectionError(
                            "Failed to get project manager from DaVinci Resolve"
                        )
                    
                    self.connection_status = ConnectionState.CONNECTED
                    self.last_connection_check = time.time()
                    
                    logger.info("Successfully connected to DaVinci Resolve")
                    return True
                    
                except ResolveNotRunningError:
                    self.connection_status = ConnectionState.ERROR
                    logger.error("DaVinci Resolve is not running")
                    raise
                    
                except Exception as e:
                    last_error = e
                    self.connection_status = ConnectionState.ERROR
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Connection attempt {attempt} failed: {e}. "
                            f"Retrying in {retry_delay} seconds..."
                        )
                        await asyncio.sleep(retry_delay)
                    else:
                        error_msg = (
                            f"Failed to connect to DaVinci Resolve after {max_retries} attempts. "
                            f"Last error: {e}"
                        )
                        logger.error(error_msg)
                        raise ResolveConnectionError(error_msg) from e
            
            # This should theoretically never be reached due to the raise in the loop
            raise ResolveConnectionError(
                f"Failed to connect to DaVinci Resolve: {last_error}"
            ) if last_error else ResolveConnectionError("Failed to connect to DaVinci Resolve")
    
    async def disconnect(self) -> None:
        """Disconnect from DaVinci Resolve."""
        try:
            if self.current_project:
                # Save current project if needed
                self.current_project = None
                
            self.project_manager = None
            self.resolve = None
            self.connection_status = "disconnected"
            
            logger.info("Disconnected from DaVinci Resolve")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def ensure_connection(self) -> bool:
        """
        Ensure connection to DaVinci Resolve is active.
        
        Returns:
            bool: True if connection is active or restored, False otherwise
        """
        try:
            # Check if we need to verify connection
            current_time = time.time()
            if (current_time - self.last_connection_check) < self.config.connection.connection_check_interval:
                if self.connection_status == "connected":
                    return True
            
            # Quick connection test
            if self.resolve and self._test_connection():
                self.last_connection_check = current_time
                return True
            
            # Connection lost, try to reconnect
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
                
            # Simple API call to test connection
            version = self.resolve.GetVersion()
            return version is not None
            
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
                        pass  # Will try again on next attempt
        
        # All retries failed
        raise ResolveAPIError(f"Operation failed after {self.config.connection.retry_attempts} attempts: {last_exception}")
    
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
    
    def get_connection_info(self) -> Dict[str, Any]:
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
                    pass
            
            if self.current_project:
                try:
                    info["current_project"] = self.current_project.GetName()
                except Exception:
                    pass
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"status": "error", "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
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
            "details": {}
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
        self.connections: Dict[str, ResolveConnectionManager] = {}
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
