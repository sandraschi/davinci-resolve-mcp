"""
DaVinci Resolve Render Tools.

This module provides tools for rendering and exporting projects and timelines
in DaVinci Resolve, including render presets, format settings, and batch operations.
"""
import logging
import os
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field

from ..connection.manager import ResolveConnectionManager
from ..utils.exceptions import ResolveOperationError

logger = logging.getLogger(__name__)


class RenderFormat(str, Enum):
    """Supported render formats."""
    MP4 = "mp4"
    MOV = "mov"
    MXF = "mxf"
    DNXHD = "dnxhd"
    PRO_RES = "prores"
    H264 = "h264"
    H265 = "h265"
    DPX = "dpx"
    EXR = "exr"
    TIFF = "tiff"
    JPEG = "jpeg"
    PNG = "png"


class RenderCodec(str, Enum):
    """Supported codecs for rendering."""
    H264 = "h264"
    H265 = "h265"
    PRORES_422 = "prores_422"
    PRORES_422_HQ = "prores_422_hq"
    PRORES_422_LT = "prores_422_lt"
    PRORES_422_PROXY = "prores_422_proxy"
    PRORES_4444 = "prores_4444"
    PRORES_4444_XQ = "prores_4444_xq"
    DNXHD_36 = "dnxhd_36"
    DNXHD_115 = "dnxhd_115"
    DNXHD_220 = "dnxhd_220"
    DNXHR_444 = "dnxhr_444"
    DNXHR_HQX = "dnxhr_hqx"
    DNXHR_HQ = "dnxhr_hq"
    DNXHR_SQ = "dnxhr_sq"
    DNXHR_LB = "dnxhr_lb"
    UNCOMPRESSED = "uncompressed"


class RenderSettings(BaseModel):
    """Model for render settings."""
    format: RenderFormat = Field(..., description="Output format")
    codec: Optional[RenderCodec] = Field(None, description="Codec to use")
    resolution_width: Optional[int] = Field(None, description="Output width in pixels")
    resolution_height: Optional[int] = Field(None, description="Output height in pixels")
    frame_rate: Optional[float] = Field(None, description="Output frame rate")
    bit_depth: int = Field(8, description="Bit depth (8, 10, 12, 16, 32)")
    quality: int = Field(90, ge=0, le=100, description="Quality setting (0-100)")
    output_path: str = Field("./output", description="Output directory or file path")
    use_timeline_name: bool = Field(True, description="Use timeline name in output filename")
    custom_name: Optional[str] = Field(None, description="Custom output filename (without extension)")
    overwrite: bool = Field(False, description="Overwrite existing files")
    multi_channel_audio: bool = Field(True, description="Enable multi-channel audio")
    audio_channels: int = Field(2, description="Number of audio channels")
    audio_bit_depth: int = Field(16, description="Audio bit depth (16 or 24)")
    audio_sample_rate: int = Field(48000, description="Audio sample rate")


class RenderJob(BaseModel):
    """Model representing a render job."""
    id: str
    status: str
    progress: float
    output_path: str
    settings: Dict[str, Any]


def register_tools(app):
    """Register render tools with the FastMCP app."""
    
    @app.tool()
    async def render_timeline(
        output_path: str,
        format: RenderFormat = RenderFormat.MP4,
        codec: Optional[RenderCodec] = None,
        resolution: Optional[str] = None,
        frame_rate: Optional[float] = None,
        timeline_name: Optional[str] = None,
        use_timeline_name: bool = True,
        custom_name: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Render the current or specified timeline to a file.
        
        Args:
            output_path: Directory to save the rendered file
            format: Output format (mp4, mov, etc.)
            codec: Codec to use (optional, format-specific)
            resolution: Output resolution as "WxH" (e.g., "1920x1080")
            frame_rate: Output frame rate (optional, uses timeline rate if None)
            timeline_name: Optional name of the timeline to render
            use_timeline_name: Whether to include the timeline name in the output filename
            custom_name: Custom filename (without extension)
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with render job details
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Set the current timeline
                project.SetCurrentTimeline(timeline)
                
                # Configure render settings
                render_settings = {
                    'SelectAllFrames': True,
                    'CustomName': custom_name or (timeline.GetName() if use_timeline_name else "render"),
                    'TargetDir': os.path.dirname(os.path.abspath(output_path)),
                    'ExportVideo': True,
                    'ExportAudio': True,
                    'FormatWidth': 1920,  # Default values, will be updated
                    'FormatHeight': 1080,
                    'FrameRate': frame_rate or float(timeline.GetSetting('timelineFrameRate') or '24.0'),
                    'PixelAspectRatio': 'square',
                    'VideoQuality': 0,  # 0 = Best, 1 = Good, 2 = Max Render Quality
                    'AudioBitDepth': 16,
                    'AudioSampleRate': 48000,
                    'ColorSpaceTag': 'Same as Project',
                    'GammaTag': 'Same as Project',
                    'OverwriteExistingFile': overwrite,
                }
                
                # Set format-specific settings
                if format == RenderFormat.MP4:
                    render_settings['Format'] = 'mp4'
                    render_settings['VideoCodec'] = codec or 'h264'
                    render_settings['AudioCodec'] = 'aac'
                    render_settings['AudioBitRate'] = 192000
                elif format == RenderFormat.MOV:
                    render_settings['Format'] = 'mov'
                    render_settings['VideoCodec'] = codec or 'h264'
                    render_settings['AudioCodec'] = 'aac'
                elif format == RenderFormat.DNXHD:
                    render_settings['Format'] = 'mxf'
                    render_settings['VideoCodec'] = codec or 'dnxhd_220'
                elif format == RenderFormat.PRO_RES:
                    render_settings['Format'] = 'mov'
                    render_settings['VideoCodec'] = codec or 'prores_422_hq'
                elif format in [RenderFormat.DPX, RenderFormat.EXR, RenderFormat.TIFF, RenderFormat.PNG, RenderFormat.JPEG]:
                    render_settings['Format'] = format.lower()
                    render_settings['ExportAudio'] = False
                
                # Set resolution if specified
                if resolution and 'x' in resolution:
                    width, height = map(int, resolution.lower().split('x'))
                    render_settings['FormatWidth'] = width
                    render_settings['FormatHeight'] = height
                
                # Set output path
                if not os.path.isabs(output_path):
                    output_path = os.path.abspath(output_path)
                
                if os.path.isdir(output_path):
                    # If output_path is a directory, create a filename
                    filename = f"{render_settings['CustomName']}.{format}"
                    output_path = os.path.join(output_path, filename)
                
                # Add the render job
                job_id = project.AddRenderJob()
                if job_id == -1:
                    raise ResolveOperationError("Failed to create render job")
                
                # Set render settings
                for key, value in render_settings.items():
                    project.SetCurrentRenderFormatAndCodec(render_settings['Format'], render_settings.get('VideoCodec', ''))
                    project.SetCurrentRenderMode(0)  # 0 = Single Clip, 1 = Individual Clips
                    project.SetRenderSettings(key, value)
                
                # Start rendering
                project.StartRendering(job_id)
                
                # Wait for render to complete
                while project.IsRenderingInProgress():
                    import time
                    time.sleep(1)  # Check every second
                
                # Check if render was successful
                if project.GetRenderJobStatus(job_id)['Status'] == 'Complete':
                    return {
                        "status": "success",
                        "message": "Render completed successfully",
                        "output_path": output_path,
                        "job_id": job_id
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Render failed: {project.GetRenderJobStatus(job_id).get('Status', 'Unknown error')}",
                        "job_id": job_id
                    }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to render timeline: {str(e)}")

    @app.tool()
    async def get_render_presets() -> List[Dict[str, Any]]:
        """
        Get a list of available render presets.
        
        Returns:
            List of render presets with their settings
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                presets = []
                preset_count = project.GetRenderPresetCount()
                
                for i in range(preset_count):
                    preset_name = project.GetRenderPresetName(i)
                    presets.append({
                        "name": preset_name,
                        "index": i
                    })
                
                return {
                    "status": "success",
                    "presets": presets
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to get render presets: {str(e)}")

    @app.tool()
    async def render_with_preset(
        preset_name: str,
        output_path: str,
        timeline_name: Optional[str] = None,
        use_timeline_name: bool = True,
        custom_name: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Render the timeline using a specific preset.
        
        Args:
            preset_name: Name of the render preset to use
            output_path: Directory to save the rendered file
            timeline_name: Optional name of the timeline to render
            use_timeline_name: Whether to include the timeline name in the output filename
            custom_name: Custom filename (without extension)
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with render job details
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                # Get the specified timeline or current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                
                # Set the current timeline
                project.SetCurrentTimeline(timeline)
                
                # Find the preset
                preset_index = -1
                preset_count = project.GetRenderPresetCount()
                for i in range(preset_count):
                    if project.GetRenderPresetName(i) == preset_name:
                        preset_index = i
                        break
                
                if preset_index == -1:
                    raise ResolveOperationError(f"Render preset '{preset_name}' not found")
                
                # Set the render preset
                project.LoadRenderPreset(preset_index)
                
                # Configure output settings
                output_filename = custom_name or (timeline.GetName() if use_timeline_name else "render")
                project.SetCurrentRenderFormatAndCodec(
                    project.GetSetting('format'),
                    project.GetSetting('codec')
                )
                project.SetRenderSettings('TargetDir', os.path.dirname(os.path.abspath(output_path)))
                project.SetRenderSettings('CustomName', output_filename)
                project.SetRenderSettings('OverwriteExistingFile', overwrite)
                
                # Add the render job
                job_id = project.AddRenderJob()
                if job_id == -1:
                    raise ResolveOperationError("Failed to create render job")
                
                # Start rendering
                project.StartRendering(job_id)
                
                # Wait for render to complete
                while project.IsRenderingInProgress():
                    import time
                    time.sleep(1)  # Check every second
                
                # Check if render was successful
                if project.GetRenderJobStatus(job_id)['Status'] == 'Complete':
                    output_file = os.path.join(
                        os.path.dirname(os.path.abspath(output_path)),
                        f"{output_filename}.{project.GetSetting('format')}"
                    )
                    return {
                        "status": "success",
                        "message": "Render completed successfully",
                        "output_path": output_file,
                        "job_id": job_id
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Render failed: {project.GetRenderJobStatus(job_id).get('Status', 'Unknown error')}",
                        "job_id": job_id
                    }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to render with preset: {str(e)}")

    @app.tool()
    async def get_render_job_status(job_id: int) -> Dict[str, Any]:
        """
        Get the status of a render job.
        
        Args:
            job_id: ID of the render job to check
            
        Returns:
            Dictionary with job status and details
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                
                status = project.GetRenderJobStatus(job_id)
                if not status:
                    raise ResolveOperationError(f"No render job found with ID {job_id}")
                
                return {
                    "status": "success",
                    "job_id": job_id,
                    "job_status": status.get('Status', 'Unknown'),
                    "progress": status.get('Completion', 0.0),
                    "output_path": status.get('TargetDir', '')
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to get render job status: {str(e)}")

    return app
