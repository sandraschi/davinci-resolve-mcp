"""
Check Python environment and paths.
"""
import os
import platform
import site
import sys


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"{title}".center(80))
    print("=" * 80)

def main():
    """Main function to check the environment."""
    # Basic Python info
    print_section("Python Environment")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")

    # Path information
    print_section("Python Path")
    for i, path in enumerate(sys.path, 1):
        print(f"{i:2d}. {path}")

    # Site packages
    print_section("Site Packages")
    try:
        for path in site.getsitepackages():
            print(f"- {path}")
    except Exception as e:
        print(f"Could not get site packages: {e}")

    # Environment variables
    print_section("Environment Variables")
    env_vars = [
        "PYTHONPATH",
        "PATH",
        "PYTHONHOME",
        "VIRTUAL_ENV",
        "CONDA_PREFIX"
    ]

    for var in env_vars:
        value = os.environ.get(var, "[Not Set]")
        print(f"{var}: {value}")

    # Check for DaVinci Resolve
    print_section("DaVinci Resolve Check")
    resolve_path = r"C:\Program Files\Blackmagic Design\DaVinci Resolve"
    if os.path.exists(resolve_path):
        print(f"✅ DaVinci Resolve found at: {resolve_path}")

        # Check for Python modules
        modules_path = os.path.join(resolve_path, "fusionscript.dll")
        if os.path.exists(modules_path):
            print(f"✅ Found fusionscript.dll at: {modules_path}")
        else:
            print(f"❌ fusionscript.dll not found at: {modules_path}")

        # Check for Python modules directory
        modules_dir = os.path.join(resolve_path, "Support", "Developer", "Scripting", "Modules")
        if os.path.exists(modules_dir):
            print(f"✅ Found Python modules at: {modules_dir}")

            # List Python files in the modules directory
            try:
                print("\nPython modules in DaVinci Resolve directory:")
                for f in os.listdir(modules_dir):
                    if f.endswith(('.py', '.pyd')):
                        print(f"- {f}")
            except Exception as e:
                print(f"  Could not list directory contents: {e}")
        else:
            print(f"❌ Python modules directory not found at: {modules_dir}")
    else:
        print(f"❌ DaVinci Resolve not found at: {resolve_path}")

    print("\n" + "=" * 80)
    print("Environment check complete".center(80))
    print("=" * 80)

if __name__ == "__main__":
    main()
