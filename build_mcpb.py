"""
MCPB Build Script for DaVinci Resolve MCP

Creates optimized MCPB packages with FastMCP 2.14.3 conversational and sampling capabilities.
Follows MCPB specification for professional distribution.
"""

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional


class MCPBPackager:
    """Professional MCPB package creator with validation and optimization."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.mcpb_dir = repo_root / "mcpb"
        self.dist_dir = repo_root / "dist"
        self.src_dir = repo_root / "src"

    def validate_manifest(self) -> bool:
        """Validate MCPB manifest with comprehensive checks."""
        manifest_path = self.mcpb_dir / "manifest.json"

        if not manifest_path.exists():
            print("❌ Manifest file not found at mcpb/manifest.json")
            return False

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            # Required fields validation
            required_fields = ["manifest_version", "name", "version", "server"]
            missing_fields = [field for field in required_fields if field not in manifest]

            if missing_fields:
                print(f"❌ Missing required manifest fields: {', '.join(missing_fields)}")
                return False

            # Version validation
            if manifest.get("manifest_version") != "0.2":
                print("❌ Unsupported manifest version. Expected: 0.2")
                return False

            # FastMCP version validation
            deps = manifest.get("dependencies", {})
            fastmcp_version = deps.get("fastmcp", "")
            if not fastmcp_version or "2.14.3" not in fastmcp_version:
                print("⚠️  Warning: FastMCP 2.14.3 not specified in dependencies")

            print("✅ Manifest validation successful")
            return True

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in manifest: {e}")
            return False
        except Exception as e:
            print(f"❌ Error validating manifest: {e}")
            return False

    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.dist_dir.mkdir(exist_ok=True)
        print(f"✅ Output directory ready: {self.dist_dir}")

    def collect_package_files(self) -> Dict[str, Path]:
        """Collect all files to include in the MCPB package."""
        files_to_package = {}

        # Core server files
        server_files = [
            "server.py",
            "agentic.py",
            "config.py",
            "types.py"
        ]

        for file in server_files:
            src_path = self.src_dir / "davinci_resolve_mcp" / file
            if src_path.exists():
                files_to_package[f"src/davinci_resolve_mcp/{file}"] = src_path
            else:
                print(f"⚠️  Warning: Core file not found: {file}")

        # Tools directory
        tools_dir = self.src_dir / "davinci_resolve_mcp" / "tools"
        if tools_dir.exists():
            for file_path in tools_dir.rglob("*.py"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.src_dir)
                    files_to_package[f"src/{rel_path}"] = file_path

        # Utils directory
        utils_dir = self.src_dir / "davinci_resolve_mcp" / "utils"
        if utils_dir.exists():
            for file_path in utils_dir.rglob("*.py"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.src_dir)
                    files_to_package[f"src/{rel_path}"] = file_path

        # Connection directory
        conn_dir = self.src_dir / "davinci_resolve_mcp" / "connection"
        if conn_dir.exists():
            for file_path in conn_dir.rglob("*.py"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.src_dir)
                    files_to_package[f"src/{rel_path}"] = file_path

        # Models directory
        models_dir = self.src_dir / "davinci_resolve_mcp" / "models"
        if models_dir.exists():
            for file_path in models_dir.rglob("*.py"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.src_dir)
                    files_to_package[f"src/{rel_path}"] = file_path

        # Main __init__.py
        init_file = self.src_dir / "davinci_resolve_mcp" / "__init__.py"
        if init_file.exists():
            files_to_package["src/davinci_resolve_mcp/__init__.py"] = init_file

        print(f"📦 Collected {len(files_to_package)} files for packaging")
        return files_to_package

    def create_package(self, files_to_package: Dict[str, Path]) -> bool:
        """Create the MCPB package with optimized compression."""
        manifest_path = self.mcpb_dir / "manifest.json"

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            package_name = manifest.get('name', 'davinci-resolve-mcp')
            package_version = manifest.get('version', '0.1.0')
            output_file = self.dist_dir / f"{package_name}-{package_version}.mcpb"

            print(f"🏗️  Building MCPB package: {output_file.name}")

            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                # Add manifest
                zipf.writestr("manifest.json", json.dumps(manifest, indent=2))

                # Add all collected files
                for archive_path, source_path in files_to_package.items():
                    zipf.write(str(source_path), archive_path)
                    print(f"  ➕ {archive_path}")

            # Verify package
            with zipfile.ZipFile(output_file, 'r') as zipf:
                package_files = zipf.namelist()

            print("
📋 Package contents:"            for file in sorted(package_files):
                print(f"  • {file}")

            file_size = output_file.stat().st_size
            print("
📊 Package statistics:"            print(f"  • Files: {len(package_files)}")
            print(f"  • Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print(f"  • Location: {output_file}")

            return True

        except Exception as e:
            print(f"❌ Failed to create MCPB package: {e}")
            import traceback
            traceback.print_exc()
            return False

    def validate_package(self, package_path: Path) -> bool:
        """Validate the created MCPB package."""
        try:
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # Check for required files
                required_files = [
                    "manifest.json",
                    "src/davinci_resolve_mcp/server.py"
                ]

                package_files = zipf.namelist()
                missing_files = [f for f in required_files if f not in package_files]

                if missing_files:
                    print(f"❌ Missing required files in package: {', '.join(missing_files)}")
                    return False

                # Validate manifest
                with zipf.open("manifest.json") as f:
                    manifest = json.loads(f.read().decode('utf-8'))

                if manifest.get("name") != "davinci-resolve-mcp":
                    print("❌ Package name mismatch in manifest")
                    return False

                print("✅ Package validation successful")
                return True

        except Exception as e:
            print(f"❌ Package validation failed: {e}")
            return False


def main():
    """Main MCPB packaging function."""
    print("\n🚀 DaVinci Resolve MCP - MCPB Package Builder")
    print("=" * 50)

    repo_root = Path(__file__).parent.absolute()
    packager = MCPBPackager(repo_root)

    # Validation phase
    print("\n1️⃣  Validation Phase")
    if not packager.validate_manifest():
        print("\n❌ Validation failed. Aborting build.")
        sys.exit(1)

    # Preparation phase
    print("\n2️⃣  Preparation Phase")
    packager.ensure_directories()

    # Collection phase
    print("\n3️⃣  File Collection Phase")
    files_to_package = packager.collect_package_files()

    if not files_to_package:
        print("\n❌ No files collected for packaging. Aborting.")
        sys.exit(1)

    # Build phase
    print("\n4️⃣  Build Phase")
    success = packager.create_package(files_to_package)

    if not success:
        print("\n❌ Build failed.")
        sys.exit(1)

    # Validation phase
    print("\n5️⃣  Validation Phase")
    manifest_path = packager.mcpb_dir / "manifest.json"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    package_name = manifest.get('name', 'davinci-resolve-mcp')
    package_version = manifest.get('version', '0.1.0')
    package_path = packager.dist_dir / f"{package_name}-{package_version}.mcpb"

    if not packager.validate_package(package_path):
        print("\n❌ Package validation failed.")
        sys.exit(1)

    print("\n🎉 MCPB Package Build Complete!"    print(f"📦 Package: {package_path}")
    print("\n✨ Features included:"    print("  • FastMCP 2.14.3 conversational tools")
    print("  • SEP-1577 sampling capabilities")
    print("  • Agentic workflow orchestration")
    print("  • Portmanteau tool design")
    print("  • Professional video editing automation")

    print("\n📋 Next steps:"    print("  1. Test the package in your MCP environment")
    print("  2. Distribute via MCP registry or direct download")
    print("  3. Check compatibility with target DaVinci Resolve versions")


if __name__ == "__main__":
    main()
