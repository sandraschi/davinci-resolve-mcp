"""
Build script for creating the DaVinci Resolve MCPB package.

This script automates the process of creating a MCPB package for the DaVinci Resolve MCP server.
IMPORTANT: MCPB packages contain NO dependencies - handled by MCPB runtime.
"""

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

def validate_manifest(manifest_path):
    """Validate the MCPB manifest file."""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        print("[OK] Manifest validation successful")
        return True
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in manifest: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error validating manifest: {e}")
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
        if item.is_file() and item.name != "build_mcpb.py":
            shutil.copy2(item, dest_dir / item.name)
    
    print(f"[OK] Copied source files to {dest_dir}")

def copy_assets(source_dir, dest_dir):
    """Copy asset files to the DXT package directory."""
    assets_src = source_dir / "dxt" / "assets"
    assets_dest = dest_dir / "assets"
    
    if assets_src.exists():
        if assets_dest.exists():
            shutil.rmtree(assets_dest)
        shutil.copytree(assets_src, assets_dest)
        print(f"[OK] Copied assets to {assets_dest}")
    else:
        print("[INFO] No assets directory found, skipping")

def copy_license(source_dir, dest_dir):
    """Copy the LICENSE file to the DXT package directory."""
    license_src = source_dir / "LICENSE"
    if license_src.exists():
        shutil.copy2(license_src, dest_dir)
        print(f"[OK] Copied LICENSE to {dest_dir}")
    else:
        print("[INFO] No LICENSE file found, skipping")

def copy_readme(source_dir, dest_dir):
    """Copy the README.md file to the DXT package directory."""
    readme_src = source_dir / "README.md"
    if readme_src.exists():
        shutil.copy2(readme_src, dest_dir)
        print(f"[OK] Copied README.md to {dest_dir}")
    else:
        print("[INFO] No README.md file found, skipping")

# REMOVED: install_dependencies() - MCPB packages contain NO dependencies!
# Dependencies are handled by the MCPB runtime system.

def create_mcpb_package(source_dir, output_dir):
    """Create the MCPB package - MINIMAL approach with NO dependencies."""
    # Ensure output directory exists
    ensure_directory(output_dir)

    # Get manifest info
    manifest_src = source_dir / "mcpb" / "manifest.json"
    if not manifest_src.exists():
        print("[ERROR] Manifest file not found in mcpb/manifest.json")
        return False

    try:
        # Read manifest to get package info
        with open(manifest_src, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        package_name = manifest.get('name', 'davinci-resolve-mcp')
        package_version = manifest.get('version', '0.1.0')
        output_file = output_dir / f"{package_name}-{package_version}.mcpb"

        # Create the MCPB package with MINIMAL contents
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Write the CORRECT manifest file (manifest.json)
            zipf.writestr("manifest.json", json.dumps(manifest, indent=2))

            # Add the main server file ONLY (NO dependencies, NO assets, NO extras)
            server_path = source_dir / "src" / "davinci_resolve_mcp" / "server.py"
            if server_path.exists():
                zipf.write(str(server_path), "src/davinci_resolve_mcp/server.py")
            else:
                print("[WARNING] Main server file not found, package may not work")

        print(f"[SUCCESS] Created minimal MCPB package: {output_file}")
        print(f"[WARNING] IMPORTANT: This MCPB package contains NO dependencies!")
        print(f"   The MCPB runtime handles all Python package dependencies.\n")

        # List contents for verification
        print("Package contents:")
        with zipfile.ZipFile(output_file, 'r') as zipf:
            for file in zipf.namelist():
                print(f"- {file}")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to create MCPB package: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to build the MCPB package."""
    print("\n=== Building DaVinci Resolve MCPB Package (NO dependencies) ===\n")

    # Set up paths
    repo_root = Path(__file__).parent.absolute()
    output_dir = repo_root / "dist"

    # Create the MCPB package
    success = create_mcpb_package(repo_root, output_dir)

    if success:
        print("\n[SUCCESS] MCPB package created successfully!")
    else:
        print("\n[ERROR] Failed to create MCPB package")
        sys.exit(1)

if __name__ == "__main__":
    main()
