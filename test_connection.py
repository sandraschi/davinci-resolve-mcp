"""
Test script to verify connection to DaVinci Resolve.
"""
import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.insert(0, project_root)

from src.davinci_resolve_mcp.connection.manager import ResolveConnectionManager
from src.davinci_resolve_mcp.config import load_default

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test connection to DaVinci Resolve."""
    try:
        # Load default configuration
        config = load_default()
        
        # Create connection manager
        connection_manager = ResolveConnectionManager(config)
        
        # Test connection
        logger.info("Testing connection to DaVinci Resolve...")
        
        # Get connection info
        connection_info = connection_manager.get_connection_info()
        logger.info("Connection Info: %s", connection_info)
        
        # Get Resolve instance
        resolve = connection_manager.resolve
        if not resolve:
            logger.error("Failed to get Resolve instance")
            return False
        
        # Get Resolve version
        try:
            version = resolve.GetVersion()
            logger.info("DaVinci Resolve Version: %s", version)
            
            # Get project manager
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                logger.error("Failed to get Project Manager")
                return False
            
            # Get current project
            project = project_manager.GetCurrentProject()
            if project:
                logger.info("Current Project: %s", project.GetName())
            else:
                logger.info("No project is currently open")
            
            return True
            
        except Exception as e:
            logger.error("Failed to get Resolve version: %s", str(e))
            return False
            
    except Exception as e:
        logger.exception("Error testing connection:")
        return False
    finally:
        # Clean up
        if 'connection_manager' in locals():
            connection_manager.disconnect()

if __name__ == "__main__":
    success = test_connection()
    if success:
        logger.info("✅ Successfully connected to DaVinci Resolve")
    else:
        logger.error("❌ Failed to connect to DaVinci Resolve")
        sys.exit(1)
