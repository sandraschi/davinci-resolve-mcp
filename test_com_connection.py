"""
Test COM connection to DaVinci Resolve on Windows.
"""
import os
import sys
import logging
import win32com.client
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_resolve_instance() -> Optional[Any]:
    """Get a COM instance of DaVinci Resolve."""
    try:
        # Try to get the Resolve instance via COM
        resolve = win32com.client.Dispatch("Resolve.Application")
        return resolve
    except Exception as e:
        logger.error(f"Failed to get Resolve instance via COM: {e}")
        return None

def test_resolve_connection() -> Dict[str, Any]:
    """Test connection to DaVinci Resolve."""
    result = {
        "success": False,
        "version": None,
        "project_name": None,
        "error": None
    }
    
    try:
        logger.info("Attempting to connect to DaVinci Resolve via COM...")
        
        # Get Resolve instance
        resolve = get_resolve_instance()
        if not resolve:
            result["error"] = "Could not get Resolve instance. Is DaVinci Resolve running?"
            return result
        
        logger.info("Successfully connected to DaVinci Resolve via COM")
        
        # Get version
        try:
            version = resolve.GetVersion()
            result["version"] = version
            logger.info(f"DaVinci Resolve Version: {version}")
        except Exception as e:
            logger.warning(f"Could not get version: {e}")
        
        # Get project manager
        project_manager = resolve.GetProjectManager()
        if not project_manager:
            result["error"] = "Could not get Project Manager"
            return result
        
        # Get current project
        project = project_manager.GetCurrentProject()
        if project:
            try:
                project_name = project.GetName()
                result["project_name"] = project_name
                logger.info(f"Current Project: {project_name}")
            except Exception as e:
                logger.warning(f"Could not get project name: {e}")
        else:
            logger.info("No project is currently open")
        
        result["success"] = True
        return result
        
    except Exception as e:
        error_msg = f"Error connecting to DaVinci Resolve: {e}"
        logger.error(error_msg)
        result["error"] = str(e)
        return result

if __name__ == "__main__":
    logger.info("Testing connection to DaVinci Resolve...")
    
    # Add the DaVinci Resolve Python modules to the path
    resolve_path = r"C:\Program Files\Blackmagic Design\DaVinci Resolve"
    if os.path.exists(resolve_path):
        sys.path.append(resolve_path)
    
    # Test the connection
    connection_result = test_resolve_connection()
    
    if connection_result["success"]:
        logger.info("✅ Successfully connected to DaVinci Resolve")
        if connection_result["version"]:
            logger.info(f"Version: {connection_result['version']}")
        if connection_result["project_name"]:
            logger.info(f"Current Project: {connection_result['project_name']}")
        sys.exit(0)
    else:
        logger.error(f"❌ Failed to connect to DaVinci Resolve: {connection_result.get('error', 'Unknown error')}")
        sys.exit(1)
