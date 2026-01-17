"""
Pre-commit hooks installation script.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Install pre-commit hooks."""
    try:
        # Check if pre-commit is installed
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "pre-commit"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("📦 Installing pre-commit...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "pre-commit"
            ], check=True)

        # Install the pre-commit hooks
        print("🔧 Installing pre-commit hooks...")
        subprocess.run(["pre-commit", "install"], check=True)

        # Install the pre-commit hooks for commit-msg if configured
        hooks_config = Path(".pre-commit-config.yaml")
        if hooks_config.exists():
            with open(hooks_config, 'r') as f:
                content = f.read()
                if "commit-msg" in content:
                    print("🔧 Installing commit-msg hooks...")
                    subprocess.run(["pre-commit", "install", "--hook-type", "commit-msg"], check=True)

        print("✅ Pre-commit hooks installed successfully!")
        print("\n📋 Next steps:")
        print("  1. Run 'pre-commit run --all-files' to check all files")
        print("  2. Commit changes to trigger automatic checks")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install pre-commit hooks: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
