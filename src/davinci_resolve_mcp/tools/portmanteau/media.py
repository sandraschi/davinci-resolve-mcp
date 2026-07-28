"""
DaVinci Resolve Media Portmanteau Tool.

Consolidates media pool operations into a single tool.
"""

import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)


_MUTATING = {}


def setup_media_portmanteau(app):
    """Register the media portmanteau tool."""

    @app.tool(annotations=_MUTATING)
    async def resolve_media(
        action: Literal["import", "list", "create_folder", "get_metadata"],
        paths: list[str] | None = None,
        folder_path: str = "",
        target_folder: str | None = None,
        as_sequence: bool = False,
        force_framerate: float | None = None,
        force_resolution: str | None = None,
        clip_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive media pool management for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates 4 media tools into 1.

        SUPPORTED ACTIONS:
        - import: Import media files (requires: paths)
        - list: List media in folder (optional: folder_path)
        - create_folder: Create folder in media pool (requires: folder_path)
        - get_metadata: Get clip metadata (requires: clip_path)

        Args:
            action: Operation to perform (import, list, create_folder, get_metadata)
            paths: File paths to import. Required for: import
            folder_path: Folder path in media pool. Used by: list, create_folder
            target_folder: Target folder for imports. Used by: import
            as_sequence: Treat as image sequence. Used by: import. Default: False
            force_framerate: Force frame rate. Used by: import
            force_resolution: Force resolution (WxH). Used by: import
            clip_path: Path to clip for metadata. Required for: get_metadata

        Returns:
            Dict with operation results

        Examples:
            # Import media files
            resolve_media("import", paths=["C:/Videos/clip1.mp4", "C:/Videos/clip2.mp4"])

            # Import to specific folder
            resolve_media("import", paths=["C:/Videos/raw.mp4"], target_folder="Raw Footage")

            # List media in folder
            resolve_media("list", folder_path="Raw Footage")

            # Create folder
            resolve_media("create_folder", folder_path="Assets/Music")

            # Get metadata
            resolve_media("get_metadata", clip_path="C:/Videos/clip1.mp4")
        """
        from ..media_tools import (
            create_folder_impl as create_folder,
        )
        from ..media_tools import (
            get_media_metadata_impl as get_media_metadata,
        )
        from ..media_tools import (
            import_media_impl as import_media,
        )
        from ..media_tools import (
            list_media_impl as list_media,
        )

        if action == "import":
            if not paths:
                return {"status": "error", "message": "paths is required for import action"}
            return await import_media(app, paths, target_folder, as_sequence, force_framerate, force_resolution)

        elif action == "list":
            return await list_media(app, folder_path)

        elif action == "create_folder":
            if not folder_path:
                return {
                    "status": "error",
                    "message": "folder_path is required for create_folder action",
                }
            return await create_folder(app, folder_path)

        elif action == "get_metadata":
            if not clip_path:
                return {
                    "status": "error",
                    "message": "clip_path is required for get_metadata action",
                }
            return await get_media_metadata(app, clip_path)

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_media portmanteau tool")
