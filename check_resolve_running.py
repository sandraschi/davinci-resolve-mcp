"""
Check if DaVinci Resolve is running and try to connect to it.
"""
import os
import sys
import time
import logging
import psutil
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_resolve_running() -> bool:
    """Check if DaVinci Resolve is currently running."""
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'resolve' in proc.info['name'].lower():
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking if Resolve is running: {e}")
        return False

def main():
    """Main function to check Resolve status and attempt connection."""
    print("🔍 Checking DaVinci Resolve status...")
    
    # Check if Resolve is running
    if is_resolve_running():
        print("✅ DaVinci Resolve is running")
        
        # Try to connect using the default Python module
        print("\nAttempting to connect using Python module...")
        try:
            import DaVinciResolveScript as dvr_script
            resolve = dvr_script.scriptapp("Resolve")
            if resolve:
                print("✅ Successfully connected using Python module")
                print(f"DaVinci Resolve Version: {resolve.GetVersion()}")
                return
        except ImportError:
            print("❌ DaVinciResolveScript module not found in Python path")
        except Exception as e:
            print(f"❌ Failed to connect using Python module: {e}")
        
        # Try to connect using COM
        print("\nAttempting to connect using COM...")
        try:
            import win32com.client
            resolve = win32com.client.Dispatch("Resolve.Application")
            if resolve:
                print("✅ Successfully connected using COM")
                print(f"DaVinci Resolve Version: {resolve.GetVersion()}")
                return
        except ImportError:
            print("❌ pywin32 module not installed. Install with: pip install pywin32")
        except Exception as e:
            print(f"❌ Failed to connect using COM: {e}")
        
        print("\n⚠️  Could not connect to DaVinci Resolve using any method")
        print("Please ensure that:")
        print("1. You're running this script with administrator privileges")
        print("2. The DaVinci Resolve Python module is in your PYTHONPATH")
        print("3. The DaVinci Resolve API is properly installed")
    else:
        print("❌ DaVinci Resolve is not running")
        print("Please start DaVinci Resolve and try again")

if __name__ == "__main__":
    main()
