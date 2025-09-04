"""
Build script for creating the DaVinci Resolve MCP DXT package.

This script automates the process of creating a DXT package for the DaVinci Resolve MCP server.
It handles copying necessary files, validating the manifest, and creating the final package.
"""

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

def validate_manifest(manifest_path):
    """Validate the DXT manifest file."""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        print("✓ Manifest validation successful")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in manifest: {e}")
        return False
    except Exception as e:
        print(f"✗ Error validating manifest: {e}")
        return False

def ensure_directory(directory):
    """Ensure a directory exists, create it if it doesn't."""
    os.makedirs(directory, exist_ok=True)

def copy_source_files(source_dir, dest_dir):
    """Copy Python source files to the DXT package directory."""
    # Copy the entire src directory
    src_path = source_dir / "src"
    dest_src_path = dest_dir / "src"
    
    if dest_src_path.exists():
        shutil.rmtree(dest_src_path)
    
    # Copy all files and directories from src to dest_dir/src
    shutil.copytree(src_path, dest_src_path, dirs_exist_ok=True)
    
    # Also copy any top-level Python files
    for item in source_dir.glob("*.py"):
        if item.is_file() and item.name != "build_dxt.py":
            shutil.copy2(item, dest_dir / item.name)
    
    print(f"✓ Copied source files to {dest_dir}")

def copy_assets(source_dir, dest_dir):
    """Copy asset files to the DXT package directory."""
    assets_src = source_dir / "dxt" / "assets"
    assets_dest = dest_dir / "assets"
    
    if assets_src.exists():
        if assets_dest.exists():
            shutil.rmtree(assets_dest)
        shutil.copytree(assets_src, assets_dest)
        print(f"✓ Copied assets to {assets_dest}")
    else:
        print("ℹ No assets directory found, skipping")

def copy_license(source_dir, dest_dir):
    """Copy the LICENSE file to the DXT package directory."""
    license_src = source_dir / "LICENSE"
    if license_src.exists():
        shutil.copy2(license_src, dest_dir)
        print(f"✓ Copied LICENSE to {dest_dir}")
    else:
        print("ℹ No LICENSE file found, skipping")

def copy_readme(source_dir, dest_dir):
    """Copy the README.md file to the DXT package directory."""
    readme_src = source_dir / "README.md"
    if readme_src.exists():
        shutil.copy2(readme_src, dest_dir)
        print(f"✓ Copied README.md to {dest_dir}")
    else:
        print("ℹ No README.md file found, skipping")

def install_dependencies(dest_dir):
    """Install Python dependencies in the DXT package directory."""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("ℹ No requirements.txt found, skipping dependency installation")
        return False
    
    # Create lib directory if it doesn't exist
    lib_dir = dest_dir / "lib"
    ensure_directory(lib_dir)
    
    print("Installing Python dependencies...")
    try:
        # Install dependencies to a temporary directory first
        temp_dir = dest_dir / "_temp_deps"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        ensure_directory(temp_dir)
        
        # Install with --no-deps to prevent conflicts with system packages
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", 
             "-r", str(requirements_file),
             "--target", str(temp_dir),
             "--no-deps",
             "--no-compile"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Move the installed packages to the lib directory
        for item in temp_dir.iterdir():
            if item.name not in ["_temp_deps", "lib"]:
                dest_path = lib_dir / item.name
                if dest_path.exists():
                    if dest_path.is_dir():
                        shutil.rmtree(dest_path)
                    else:
                        dest_path.unlink()
                shutil.move(str(item), str(lib_dir))
        
        # Clean up
        shutil.rmtree(temp_dir)
        print("✓ Installed Python dependencies")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        return False
    except Exception as e:
        print(f"✗ Error during dependency installation: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def create_dxt_package(source_dir, output_dir):
    """Create the DXT package from the source files."""
    # Ensure output directory exists
    ensure_directory(output_dir)
    
    # Create a temporary build directory
    build_dir = source_dir / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    ensure_directory(build_dir)
    
    # Create a dxt directory inside build for package contents
    dxt_dir = build_dir / "dxt"
    ensure_directory(dxt_dir)
    
    try:
        # Copy manifest file
        manifest_src = source_dir / "dxt" / "manifest.json"
        if not manifest_src.exists():
            print("✗ Manifest file not found in dxt/manifest.json")
            return False
        
        # Copy manifest.json directly to the build directory (root of package)
        shutil.copy2(manifest_src, build_dir / "manifest.json")
        print("✓ Copied manifest to package root")
        
        # Validate the manifest
        manifest_path = build_dir / "manifest.json"
        if not validate_manifest(manifest_path):
            return False
        
        # Copy source files and assets to dxt directory
        copy_source_files(source_dir, dxt_dir)
        copy_assets(source_dir, dxt_dir)
        copy_license(source_dir, dxt_dir)
        copy_readme(source_dir, dxt_dir)
        
        # Install dependencies in the dxt/lib directory
        install_dependencies(dxt_dir)
        
        # Create the DXT package
        print("\nCreating DXT package...")
        try:
            # Ensure the output directory exists
            ensure_directory(output_dir)
            
            # Get the package name and version from the manifest
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            package_name = manifest.get('name', 'davinci-resolve-mcp')
            package_version = manifest.get('version', '0.1.0')
            output_file = output_dir / f"{package_name}-{package_version}.dxt"
            
            # Create a zip file with .dxt extension
            output_file_zip = output_file.with_suffix('.zip')
            
            # Create the zip file manually to ensure proper structure
            with zipfile.ZipFile(output_file_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files and directories from build_dir (root level)
                for root, dirs, files in os.walk(build_dir):
                    for file in files:
                        file_path = Path(root) / file
                        # Calculate the relative path for the zip file
                        arcname = file_path.relative_to(build_dir)
                        # Skip any __pycache__ directories
                        if "__pycache__" in str(arcname):
                            continue
                        zipf.write(file_path, arcname)
            
            # Rename .zip to .dxt
            if output_file_zip.exists():
                if output_file.exists():
                    output_file.unlink()  # Remove existing .dxt file if it exists
                output_file_zip.rename(output_file)
                print(f"✓ Created DXT package: {output_file}")
                
                # Verify the package was created correctly
                if output_file.exists():
                    print("✓ DXT package verification successful")
                    
                    # List contents of the package for verification
                    print("\nPackage contents:")
                    with zipfile.ZipFile(output_file, 'r') as zipf:
                        for file in zipf.namelist():
                            print(f"- {file}")
                    
                    return True
                else:
                    print("✗ Failed to create DXT package: Output file not found")
                    return False
            else:
                print("✗ Failed to create ZIP file for DXT package")
                return False
            
        except Exception as e:
            print(f"✗ Failed to create DXT package: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    finally:
        # Clean up the build directory
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print("✓ Cleaned up build directory")

def main():
    """Main function to build the DXT package."""
    print("\n=== Building DaVinci Resolve MCP DXT Package ===\n")
    
    # Set up paths
    repo_root = Path(__file__).parent.absolute()
    output_dir = repo_root / "dist"
    
    # Create the DXT package
    success = create_dxt_package(repo_root, output_dir)
    
    if success:
        print("\n✓ DXT package created successfully!")
    else:
        print("\n✗ Failed to create DXT package")
        sys.exit(1)

if __name__ == "__main__":
    main()
