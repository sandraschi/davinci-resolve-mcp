"""
Test script to verify connection to DaVinci Resolve using fusionscript.dll
"""
import os
import sys
import ctypes
import platform
from ctypes import wintypes

# Constants
RESOLVE_PATH = r"C:\Program Files\Blackmagic Design\DaVinci Resolve"
FUSION_SCRIPT_DLL = os.path.join(RESOLVE_PATH, "fusionscript.dll")

def test_resolve_connection():
    """Test connection to DaVinci Resolve using fusionscript.dll"""
    print(f"🔍 Testing connection to DaVinci Resolve at: {RESOLVE_PATH}")
    
    # Check if fusionscript.dll exists
    if not os.path.exists(FUSION_SCRIPT_DLL):
        print(f"❌ Error: Could not find fusionscript.dll at {FUSION_SCRIPT_DLL}")
        return False
    
    print(f"✅ Found fusionscript.dll at: {FUSION_SCRIPT_DLL}")
    
    try:
        # Load the DLL
        print("\n🔹 Loading fusionscript.dll...")
        fusionscript = ctypes.CDLL(FUSION_SCRIPT_DLL)
        
        # Define the function prototype for GetResolve()
        fusionscript.GetResolve.argtypes = []
        fusionscript.GetResolve.restype = ctypes.c_void_p
        
        # Try to get Resolve instance
        print("🔹 Attempting to get Resolve instance...")
        resolve_ptr = fusionscript.GetResolve()
        
        if resolve_ptr:
            print("✅ Successfully connected to DaVinci Resolve!")
            
            # Try to get version (this is a simplified example)
            try:
                # Note: This is a simplified example. The actual implementation would need
                # to properly define the Resolve COM interface
                print("ℹ️  Note: To get version and project info, we need to define the COM interface")
                print("     This requires more detailed implementation of the Resolve COM interface")
            except Exception as e:
                print(f"⚠️  Could not get version info: {e}")
            
            return True
        else:
            print("❌ Failed to get Resolve instance")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if "The specified module could not be found" in str(e):
            print("   This usually means a dependency is missing. Make sure all required")
            print("   Visual C++ Redistributable packages are installed.")
        return False

if __name__ == "__main__":
    print(f"Python {platform.python_version()} on {platform.system()} {platform.release()}")
    print(f"Current directory: {os.getcwd()}")
    
    # Add DaVinci Resolve to PATH if needed
    if RESOLVE_PATH not in os.environ["PATH"]:
        os.environ["PATH"] = RESOLVE_PATH + os.pathsep + os.environ["PATH"]
    
    # Test the connection
    if test_resolve_connection():
        print("\n✅ DaVinci Resolve connection test completed successfully!")
    else:
        print("\n❌ Failed to connect to DaVinci Resolve")
        print("\nTroubleshooting tips:")
        print("1. Make sure DaVinci Resolve is running")
        print("2. Run this script as Administrator")
        print("3. Check if all Visual C++ Redistributable packages are installed")
        print("4. Make sure your Python architecture (32/64-bit) matches DaVinci Resolve")
        print("5. Try running this script from within DaVinci Resolve's built-in Python console")
