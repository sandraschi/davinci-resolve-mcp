"""
DaVinci Resolve Render Portmanteau Tool.

Consolidates rendering operations into a single tool.
"""

import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)


_MUTATING = {}

def setup_render_portmanteau(app):
    """Register the render portmanteau tool."""

    @app.tool(annotations=_MUTATING)
    async def resolve_render(
        action: Literal["timeline", "presets", "with_preset", "job_status"],
        output_path: str | None = None,
        format: str = "mp4",
        codec: str | None = None,
        resolution: str | None = None,
        frame_rate: float | None = None,
        timeline_name: str | None = None,
        use_timeline_name: bool = True,
        custom_name: str | None = None,
        overwrite: bool = False,
        preset_name: str | None = None,
        job_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive rendering and export for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates 4 render tools into 1.

        SUPPORTED ACTIONS:
        - timeline: Render timeline with settings (requires: output_path)
        - presets: Get available render presets
        - with_preset: Render using preset (requires: preset_name, output_path)
        - job_status: Get render job status (requires: job_id)

        Args:
            action: Operation to perform (timeline, presets, with_preset, job_status)
            output_path: Output directory. Required for: timeline, with_preset
            format: Output format (mp4, mov, mxf, dnxhd, prores, etc). Default: mp4
            codec: Video codec. Optional.
            resolution: Output resolution (WxH). Optional.
            frame_rate: Output frame rate. Optional.
            timeline_name: Timeline to render. Optional.
            use_timeline_name: Include timeline name in filename. Default: True
            custom_name: Custom output filename. Optional.
            overwrite: Overwrite existing files. Default: False
            preset_name: Render preset name. Required for: with_preset
            job_id: Render job ID. Required for: job_status

        Returns:
            Dict with operation results

        Examples:
            # Render timeline to MP4
            resolve_render("timeline", output_path="C:/Output", format="mp4")

            # Render 4K ProRes
            resolve_render("timeline", output_path="C:/Output", format="prores",
                          resolution="3840x2160", codec="prores_422_hq")

            # List presets
            resolve_render("presets")

            # Render with preset
            resolve_render("with_preset", preset_name="YouTube 4K", output_path="C:/Output")

            # Check job status
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
                app, output_path, format_enum, codec_enum, preset_name, custom_name, timeline_name
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
