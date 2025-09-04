"""
Simple script to test connection to DaVinci Resolve.
"""
import sys
import os
import logging
import pythoncom
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_resolve_connection():
    """Test connection to DaVinci Resolve."""
    try:
        # Try to import the DaVinci Resolve API
        try:
            import DaVinciResolveScript as dvr_script
            logger.info("Successfully imported DaVinciResolveScript")
        except ImportError as e:
            logger.error("Failed to import DaVinciResolveScript. Make sure DaVinci Resolve is installed.")
            logger.error(f"Error: {e}")
            return False
        
        # Initialize COM for Windows
        try:
            pythoncom.CoInitialize()
            logger.info("Initialized COM")
        except Exception as e:
            logger.error(f"Failed to initialize COM: {e}")
            return False
        
        # Get Resolve instance
        try:
            resolve = dvr_script.scriptapp("Resolve")
            if not resolve:
                logger.error("Failed to get Resolve instance. Is DaVinci Resolve running?")
                return False
            
            logger.info("Successfully connected to DaVinci Resolve")
            
            # Get Resolve version
            version = resolve.GetVersion()
            logger.info(f"DaVinci Resolve Version: {version}")
            
            # Get project manager
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                logger.warning("Failed to get Project Manager")
            else:
                # Get current project
                project = project_manager.GetCurrentProject()
                if project:
                    logger.info(f"Current Project: {project.GetName()}")
                else:
                    logger.info("No project is currently open")
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to DaVinci Resolve: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        # Clean up COM
        try:
            pythoncom.CoUninitialize()
        except:
            pass

if __name__ == "__main__":
    logger.info("Testing connection to DaVinci Resolve...")
    success = test_resolve_connection()
    if success:
        logger.info("✅ Successfully connected to DaVinci Resolve")
    else:
        logger.error("❌ Failed to connect to DaVinci Resolve")
        sys.exit(1)
