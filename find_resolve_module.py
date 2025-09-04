"""
Script to locate the DaVinci Resolve Python module.
"""
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_resolve_module():
    """Find the DaVinci Resolve Python module."""
    # Common paths where DaVinci Resolve might be installed
    common_paths = [
        # Windows
        r"C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\fusionscript.dll",
        r"C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules\\fusionscript.py",
        
        # macOS
        "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so",
        "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Resources/Developer/Scripting/Modules/fusionscript.py",
        
        # Linux
        "/opt/resolve/libs/Fusion/fusionscript.so",
        "/opt/resolve/Developer/Scripting/Modules/fusionscript.py",
    ]
    
    logger.info("Searching for DaVinci Resolve Python module...")
    
    # Check common paths
    for path in common_paths:
        if os.path.exists(path):
            logger.info(f"Found DaVinci Resolve module at: {path}")
            return path
    
    # Check Python path
    for path in sys.path:
        if os.path.exists(os.path.join(path, 'DaVinciResolveScript.pyd')) or \
           os.path.exists(os.path.join(path, 'fusionscript.py')):
            logger.info(f"Found DaVinci Resolve module in Python path: {path}")
            return path
    
    logger.error("Could not find DaVinci Resolve Python module in common locations or Python path")
    return None

if __name__ == "__main__":
    logger.info("Python executable: %s", sys.executable)
    logger.info("Python version: %s", sys.version)
    logger.info("Python path:\n  %s", "\n  ".join(sys.path))
    
    resolve_path = find_resolve_module()
    if resolve_path:
        logger.info("✅ Found DaVinci Resolve module at: %s", resolve_path)
        
        # Try to import the module
        try:
            import DaVinciResolveScript as dvr_script
            logger.info("✅ Successfully imported DaVinciResolveScript")
            
            # Test getting Resolve instance
            resolve = dvr_script.scriptapp("Resolve")
            if resolve:
                logger.info("✅ Successfully connected to DaVinci Resolve")
                logger.info(f"DaVinci Resolve Version: {resolve.GetVersion()}")
            else:
                logger.warning("⚠️  Could not get Resolve instance. Is DaVinci Resolve running?")
                
        except Exception as e:
            logger.error(f"❌ Failed to import DaVinciResolveScript: {e}")
    else:
        logger.error("❌ Could not find DaVinci Resolve Python module")
