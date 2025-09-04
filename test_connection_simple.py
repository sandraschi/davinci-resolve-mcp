"""
Minimal script to test DaVinci Resolve connection.
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    print("🔍 Testing DaVinci Resolve connection...")
    
    # Add DaVinci Resolve's Python modules to the path
    resolve_path = r"C:\\Program Files\\Blackmagic Design\\DaVinci Resolve"
    if os.path.exists(resolve_path):
        sys.path.append(resolve_path)
    
    # Try to import the module
    try:
        print("\n🔹 Attempting to import DaVinciResolveScript...")
        import DaVinciResolveScript as dvr_script
        print("✅ Successfully imported DaVinciResolveScript")
        
        # Try to get Resolve instance
        print("\n🔹 Attempting to get Resolve instance...")
        resolve = dvr_script.scriptapp("Resolve")
        if resolve:
            print("✅ Successfully connected to DaVinci Resolve")
            
            # Get version
            try:
                version = resolve.GetVersion()
                print(f"📊 Version: {version}")
            except Exception as e:
                print(f"⚠️  Could not get version: {e}")
            
            # Get project manager
            project_manager = resolve.GetProjectManager()
            if project_manager:
                print("✅ Successfully got Project Manager")
                
                # Get current project
                project = project_manager.GetCurrentProject()
                if project:
                    try:
                        project_name = project.GetName()
                        print(f"📂 Current Project: {project_name}")
                    except Exception as e:
                        print(f"⚠️  Could not get project name: {e}")
                else:
                    print("ℹ️  No project is currently open")
            else:
                print("⚠️  Could not get Project Manager")
        else:
            print("❌ Could not get Resolve instance. Is DaVinci Resolve running?")
    
    except ImportError as e:
        print(f"\n❌ Failed to import DaVinciResolveScript: {e}")
        print("\nPossible solutions:")
        print("1. Make sure DaVinci Resolve is installed at 'C:\\Program Files\\Blackmagic Design\\DaVinci Resolve'")
        print("2. Make sure you're running this script with the same Python version as DaVinci Resolve's built-in Python")
        print("3. Try running this script from within DaVinci Resolve's built-in Python console")
    
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
