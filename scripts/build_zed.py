"""
Build script for Zed extension packaging.
"""

import shutil
import zipfile
from pathlib import Path


def main():
    """Build the Zed extension package."""
    repo_root = Path(__file__).parent.parent
    extension_dir = repo_root / "zed-extension"
    dist_dir = repo_root / "dist"

    dist_dir.mkdir(exist_ok=True)

    # Create extension zip
    zip_path = dist_dir / "davinci-resolve-mcp-zed-extension.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add extension files
        for file_path in extension_dir.rglob("*"):
            if file_path.is_file():
                arc_path = file_path.relative_to(extension_dir)
                zipf.write(file_path, f"davinci-resolve-mcp/{arc_path}")

        # Add core source files needed for the extension
        src_dir = repo_root / "src"
        for file_path in src_dir.rglob("*.py"):
            arc_path = Path("davinci-resolve-mcp") / file_path.relative_to(repo_root)
            zipf.write(file_path, arc_path)

    print(f"✅ Zed extension built: {zip_path}")


if __name__ == "__main__":
    main()
