"""
DaVinci Resolve Subtitle Portmanteau Tool.

Consolidates subtitle operations into a single tool.
"""

import logging
from typing import Annotated, Any, Literal

from fastmcp.tools.tool import ToolAnnotations
from pydantic import Field

logger = logging.getLogger(__name__)


_MUTATING = ToolAnnotations(readOnlyHint=False, destructiveHint=False)


def setup_subtitle_portmanteau(app):
    """Register the subtitle portmanteau tool."""

    @app.tool(annotations=_MUTATING, output_schema={"type": "object"})
    async def resolve_subtitle(
        action: Annotated[
            Literal["add", "get", "edit", "delete", "import_srt", "export_srt"],
            Field(description="Operation to perform"),
        ],
        track_index: Annotated[int, Field(description="1-based subtitle track index")] = 1,
        subtitle_index: Annotated[int, Field(description="Subtitle index. Required for: edit, delete")] = 0,
        name: Annotated[str | None, Field(description="Subtitle name. Required for: add")] = None,
        text: Annotated[str, Field(description="Subtitle text. Used by: add, edit")] = "",
        start_frame: Annotated[int | None, Field(description="Start frame. Required for: add")] = None,
        end_frame: Annotated[int | None, Field(description="End frame. Required for: add")] = None,
        srt_path: Annotated[str | None, Field(description="SRT file path. Required for: import_srt")] = None,
        output_path: Annotated[str | None, Field(description="Output file path. Required for: export_srt")] = None,
        timeline_name: Annotated[str | None, Field(description="Target timeline. Optional")] = None,
    ) -> dict[str, Any]:
        """
        Manage subtitles in DaVinci Resolve timelines.

        SUPPORTED ACTIONS:
        - add: Add subtitle (requires: name, start_frame, end_frame)
        - get: Get all subtitles from a track
        - edit: Edit subtitle text/position (requires: subtitle_index)
        - delete: Delete subtitle (requires: subtitle_index)
        - import_srt: Import SRT file (requires: srt_path)
        - export_srt: Export to SRT file (requires: output_path)

        ## Return Format
        {"status": "success", "message": "...", ...}

        ## Examples
        resolve_subtitle("add", name="Sub1", start_frame=0, end_frame=48, text="Hello")
        resolve_subtitle("import_srt", srt_path="C:/captions.srt")
        resolve_subtitle("export_srt", output_path="C:/out.srt")
        """
        from ..subtitle_tools import (
            add_subtitle_impl as add_subtitle,
        )
        from ..subtitle_tools import (
            delete_subtitle_impl as delete_subtitle,
        )
        from ..subtitle_tools import (
            edit_subtitle_impl as edit_subtitle,
        )
        from ..subtitle_tools import (
            export_srt_impl as export_srt,
        )
        from ..subtitle_tools import (
            get_subtitles_impl as get_subtitles,
        )
        from ..subtitle_tools import (
            import_srt_impl as import_srt,
        )

        if action == "add":
            if not name or start_frame is None or end_frame is None:
                return {"status": "error", "message": "name, start_frame, and end_frame are required for add"}
            return await add_subtitle(app, track_index, name, start_frame, end_frame, text, timeline_name)

        elif action == "get":
            return await get_subtitles(app, track_index, timeline_name)

        elif action == "edit":
            return await edit_subtitle(
                app, track_index, subtitle_index, text or None, start_frame, end_frame, name, timeline_name
            )

        elif action == "delete":
            return await delete_subtitle(app, track_index, subtitle_index, timeline_name)

        elif action == "import_srt":
            if not srt_path:
                return {"status": "error", "message": "srt_path is required for import_srt"}
            return await import_srt(app, srt_path, track_index, timeline_name)

        elif action == "export_srt":
            if not output_path:
                return {"status": "error", "message": "output_path is required for export_srt"}
            return await export_srt(app, output_path, track_index, timeline_name)

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_subtitle portmanteau tool")
