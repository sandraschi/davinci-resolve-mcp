"""
DaVinci Resolve Render Portmanteau Tool.

Consolidates rendering operations into a single tool.
"""

import logging
from typing import Annotated, Any, Literal

# fastmcp.tools.tool resolves via vendored mcp.server.fastmcp at runtime (shadowed by tool() fn)
from fastmcp.tools.tool import ToolAnnotations  # pyright: ignore[reportMissingImports]
from pydantic import Field

logger = logging.getLogger(__name__)


_MUTATING = ToolAnnotations(readOnlyHint=False, destructiveHint=False)


def setup_render_portmanteau(app):
    """Register the render portmanteau tool."""

    @app.tool(annotations=_MUTATING, output_schema={"type": "object"})
    async def resolve_render(
        action: Annotated[
            Literal["timeline", "presets", "with_preset", "job_status"], Field(description="Operation to perform")
        ],
        output_path: Annotated[
            str | None, Field(description="Output directory. Required for: timeline, with_preset")
        ] = None,
        format: Annotated[str, Field(description="Output format (mp4, mov, mxf, dnxhd, prores, ...)")] = "mp4",
        codec: Annotated[str | None, Field(description="Video codec. Optional")] = None,
        resolution: Annotated[str | None, Field(description="Output resolution (WxH). Optional")] = None,
        frame_rate: Annotated[float | None, Field(description="Output frame rate. Optional")] = None,
        timeline_name: Annotated[str | None, Field(description="Timeline to render. Optional")] = None,
        use_timeline_name: Annotated[bool, Field(description="Include timeline name in filename")] = True,
        custom_name: Annotated[str | None, Field(description="Custom output filename. Optional")] = None,
        overwrite: Annotated[bool, Field(description="Overwrite existing files")] = False,
        preset_name: Annotated[str | None, Field(description="Render preset name. Required for: with_preset")] = None,
        job_id: Annotated[int | None, Field(description="Render job ID. Required for: job_status")] = None,
    ) -> dict[str, Any]:
        """
        Comprehensive rendering and export for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates 4 render tools into 1.

        SUPPORTED ACTIONS:
        - timeline: Render timeline with settings (requires: output_path)
        - presets: Get available render presets
        - with_preset: Render using preset (requires: preset_name, output_path)
        - job_status: Get render job status (requires: job_id)

        ## Return Format
        {"status": "success", "message": "Human-readable result", ...}
        {"status": "error", "message": "Human-readable failure reason"}

        ## Examples
        resolve_render("timeline", output_path="C:/Output", format="mp4")
        resolve_render("timeline", output_path="C:/Output", format="prores", resolution="3840x2160", codec="prores_422_hq")
        resolve_render("presets")
        resolve_render("with_preset", preset_name="YouTube 4K", output_path="C:/Output")
        resolve_render("job_status", job_id=1)
        """
        from ..render_tools import (
            RenderCodec,
            RenderFormat,
        )
        from ..render_tools import (
            get_render_job_status_impl as get_render_job_status,
        )
        from ..render_tools import (
            get_render_presets_impl as get_render_presets,
        )
        from ..render_tools import (
            render_timeline_impl as render_timeline,
        )
        from ..render_tools import (
            render_with_preset_impl as render_with_preset,
        )

        # Map format string to enum
        format_map = {
            "mp4": RenderFormat.MP4,
            "mov": RenderFormat.MOV,
            "mxf": RenderFormat.MXF,
            "dnxhd": RenderFormat.DNXHD,
            "prores": RenderFormat.PRO_RES,
            "h264": RenderFormat.H264,
            "h265": RenderFormat.H265,
            "dpx": RenderFormat.DPX,
            "exr": RenderFormat.EXR,
            "tiff": RenderFormat.TIFF,
            "jpeg": RenderFormat.JPEG,
            "png": RenderFormat.PNG,
        }

        # Map codec string to enum if provided
        codec_enum = None
        if codec:
            codec_map = {
                "h264": RenderCodec.H264,
                "h265": RenderCodec.H265,
                "prores_422": RenderCodec.PRORES_422,
                "prores_422_hq": RenderCodec.PRORES_422_HQ,
                "prores_422_lt": RenderCodec.PRORES_422_LT,
                "prores_4444": RenderCodec.PRORES_4444,
                "dnxhd_220": RenderCodec.DNXHD_220,
                "dnxhr_hq": RenderCodec.DNXHR_HQ,
            }
            codec_enum = codec_map.get(codec.lower())

        if action == "timeline":
            if not output_path:
                return {"status": "error", "message": "output_path required for timeline render"}
            format_enum = format_map.get(format.lower(), RenderFormat.MP4)
            return await render_timeline(
                app, output_path, format_enum, codec_enum or RenderCodec.H264, preset_name, custom_name, timeline_name
            )

        elif action == "presets":
            return await get_render_presets(app)

        elif action == "with_preset":
            if not preset_name or not output_path:
                return {"status": "error", "message": "preset_name and output_path required"}
            return await render_with_preset(app, preset_name, output_path, timeline_name)

        elif action == "job_status":
            if job_id is None:
                return {"status": "error", "message": "job_id required for job_status"}
            return await get_render_job_status(app, str(job_id))

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_render portmanteau tool")
