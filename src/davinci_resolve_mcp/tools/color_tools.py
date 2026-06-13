"""
DaVinci Resolve Color Tools.

This module provides tools for color grading and correction in DaVinci Resolve,
including node-based color operations, LUT management, and color matching.
"""

import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from ..connection.manager import ResolveConnectionManager
from ..utils.exceptions import ResolveOperationError

logger = logging.getLogger(__name__)


class ColorCorrectionType(str, Enum):
    """Types of color correction operations."""

    PRIMARY = "primary"
    LOG = "log"
    HDR = "hdr"
    CURVES = "curves"
    QUALIFIER = "qualifier"
    WINDOW = "window"
    TRACKER = "tracker"
    BLUR = "blur"
    SHARPEN = "sharpen"
    NOISE_REDUCTION = "noise_reduction"
    RESIZE = "resize"
    LUT = "lut"


class ColorSpaceTransform(BaseModel):
    """Model representing a color space transform."""

    input_color_space: str = Field(..., description="Input color space")
    output_color_space: str = Field(..., description="Output color space")
    input_gamma: str = Field(..., description="Input gamma")
    output_gamma: str = Field(..., description="Output gamma")
    tone_mapping: str = Field("Hue Mapping", description="Tone mapping method")


class ColorNode(BaseModel):
    """Model representing a node in the color grading node graph."""

    node_type: str = Field(..., description="Type of node")
    name: str = Field(..., description="Name of the node")
    enabled: bool = Field(True, description="Whether the node is enabled")
    settings: dict[str, Any] = Field(default_factory=dict, description="Node settings")


async def create_color_node(
    app,
    node_type: ColorCorrectionType,
    name: str | None = None,
    parent_node: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a new color correction node in the current clip.

    Args:
        app: FastMCP app instance
        node_type: Type of node to create
        name: Optional name for the node
        parent_node: Optional name of the parent node to connect to
        timeline_name: Optional name of the timeline

    Returns:
        Dict containing node creation result
    """
    return await create_color_node_impl(app, node_type, name, parent_node, timeline_name)


async def apply_lut(
    app,
    lut_path: str,
    clip_path: str | None = None,
    node_name: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Apply a LUT to a clip or color node.

    Args:
        app: FastMCP app instance
        lut_path: Path to the LUT file
        clip_path: Optional path to specific clip
        node_name: Optional name of color node
        timeline_name: Optional name of the timeline

    Returns:
        Dict containing LUT application result
    """
    return await apply_lut_impl(app, lut_path, clip_path, node_name, timeline_name)


async def set_color_space(
    app,
    input_space: ColorSpaceTransform,
    output_space: ColorSpaceTransform,
    clip_path: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Set color space transformation for a clip.

    Args:
        app: FastMCP app instance
        input_space: Input color space
        output_space: Output color space
        clip_path: Optional path to specific clip
        timeline_name: Optional name of the timeline

    Returns:
        Dict containing color space setting result
    """
    return await set_color_space_impl(app, input_space, output_space, clip_path, timeline_name)


async def adjust_color_wheels(
    app,
    lift: dict[str, float] | None = None,
    gamma: dict[str, float] | None = None,
    gain: dict[str, float] | None = None,
    offset: dict[str, float] | None = None,
    clip_path: str | None = None,
    node_name: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Adjust primary color correction wheels.

    Args:
        app: FastMCP app instance
        lift: Lift/shadow adjustments (r, g, b values)
        gamma: Gamma/midtone adjustments (r, g, b values)
        gain: Gain/highlight adjustments (r, g, b values)
        offset: Offset adjustments (r, g, b values)
        clip_path: Optional path to specific clip
        node_name: Optional name of color node
        timeline_name: Optional name of the timeline

    Returns:
        Dict containing color wheel adjustment result
    """
    return await adjust_color_wheels_impl(
        app, lift, gamma, gain, offset, clip_path, node_name, timeline_name
    )


async def create_color_node_impl(
    app,
    node_type: ColorCorrectionType,
    name: str | None = None,
    parent_node: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Implementation of color node creation (shared between individual and portmanteau tools)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        current_clip = timeline.GetCurrentVideoItem()
        if not current_clip:
            raise ResolveOperationError("No clip is currently selected")

        fusion = resolve.Fusion()
        if not fusion:
            raise ResolveOperationError("Could not access Fusion (color grading) interface")

        comp = fusion.GetCurrentComp()
        if not comp:
            raise ResolveOperationError("Could not access current composition")

        node_type_map = {
            ColorCorrectionType.PRIMARY: "Color",
            ColorCorrectionType.LOG: "ColorCurves",
            ColorCorrectionType.HDR: "HDRTool",
            ColorCorrectionType.CURVES: "HueVsCurves",
            ColorCorrectionType.QUALIFIER: "Qualifier",
            ColorCorrectionType.WINDOW: "Window",
            ColorCorrectionType.TRACKER: "Tracker",
            ColorCorrectionType.BLUR: "Blur",
            ColorCorrectionType.SHARPEN: "Sharpen",
            ColorCorrectionType.NOISE_REDUCTION: "NoiseReduction",
            ColorCorrectionType.RESIZE: "Resize",
            ColorCorrectionType.LUT: "LUT",
        }

        node_type_str = node_type_map.get(node_type, "Color")
        new_node = comp.AddTool(node_type_str, -1, -1)
        if not new_node:
            raise ResolveOperationError(f"Failed to create {node_type.value} node")

        node_name = name or f"{node_type.value.title()} Node"
        new_node.SetAttrs({"TOOLS_Name": node_name})

        if parent_node:
            parent = comp.FindTool(parent_node)
            if parent:
                new_node.Input.ConnectTo(parent.Output)

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": current_clip.GetName(),
            "node_name": node_name,
            "node_type": node_type.value,
            "node_id": new_node.GetAttrs()["TOOLS_RegID"],
            "message": f"Created {node_type.value} color node: {node_name}",
        }

    except Exception as e:
        logger.error(f"Error creating color node: {e!s}")
        raise ResolveOperationError(f"Failed to create color node: {e!s}")


async def apply_lut_impl(
    app,
    lut_path: str,
    clip_path: str | None = None,
    node_name: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Implementation of LUT application (shared between individual and portmanteau tools)."""
    try:
        import os as _os

        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if not _os.path.exists(lut_path):
            raise ResolveOperationError(f"LUT file not found: {lut_path}")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        fusion = resolve.Fusion()
        if not fusion:
            raise ResolveOperationError("Could not access Fusion (color grading) interface")

        comp = fusion.GetCurrentComp()
        if not comp:
            raise ResolveOperationError("Could not access current composition")

        lut_node = comp.AddTool("LUT", -1, -1)
        if not lut_node:
            raise ResolveOperationError("Failed to create LUT node")

        lut_node.LUTFile = lut_path
        lut_node.Mix = 1.0

        target_clip = timeline.GetCurrentVideoItem()
        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": target_clip.GetName() if target_clip else "current",
            "lut_path": lut_path,
            "node_name": node_name,
            "node_id": lut_node.GetAttrs()["TOOLS_RegID"],
            "message": f"Applied LUT '{lut_path}'",
        }

    except Exception as e:
        logger.error(f"Error applying LUT: {e!s}")
        raise ResolveOperationError(f"Failed to apply LUT: {e!s}")


async def set_color_space_impl(
    app,
    input_space: ColorSpaceTransform,
    output_space: ColorSpaceTransform,
    clip_path: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Implementation of color space setting (shared between individual and portmanteau tools).
    """
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        project = connection.current_project
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

        # Find the target clip
        target_clip = timeline.GetCurrentVideoItem()

        if not target_clip:
            raise ResolveOperationError("No target clip found")

        # Set color space via Fusion ColorSpaceTransform tool
        resolve = connection.get_connection()
        fusion = resolve.Fusion() if hasattr(resolve, "Fusion") else None
        if not fusion:
            raise ResolveOperationError("Could not access Fusion interface for CST")

        comp = fusion.GetCurrentComp()
        if not comp:
            raise ResolveOperationError("Could not access current composition")

        cst = comp.AddTool("ColorSpaceTransform", -1, -1)
        if not cst:
            raise ResolveOperationError("Failed to create ColorSpaceTransform node")

        cst.SourceSpace = input_space.input_color_space
        cst.SourceGamma = input_space.input_gamma or "Same as Project"
        cst.TargetSpace = output_space.output_color_space
        cst.TargetGamma = output_space.output_gamma or "Same as Project"

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": target_clip.GetName(),
            "input_space": input_space.input_color_space,
            "output_space": output_space.output_color_space,
            "cst_node_id": cst.GetAttrs().get("TOOLS_RegID", ""),
            "message": f"Color space transform: {input_space.input_color_space} → {output_space.output_color_space}",
        }

    except Exception as e:
        logger.error(f"Error setting color space: {e!s}")
        raise ResolveOperationError(f"Failed to set color space: {e!s}")


async def adjust_color_wheels_impl(
    app,
    lift: dict[str, float] | None = None,
    gamma: dict[str, float] | None = None,
    gain: dict[str, float] | None = None,
    offset: dict[str, float] | None = None,
    clip_path: str | None = None,
    node_name: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Implementation of color wheel adjustment (shared between individual and portmanteau tools)."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        current_clip = timeline.GetCurrentVideoItem()
        if not current_clip:
            raise ResolveOperationError("No clip is currently selected")

        fusion = resolve.Fusion()
        if not fusion:
            raise ResolveOperationError("Could not access Fusion (color grading) interface")

        comp = fusion.GetCurrentComp()
        if not comp:
            raise ResolveOperationError("Could not access current composition")

        color_node = comp.FindTool("ColorCorrector")
        if not color_node:
            color_node = comp.AddTool("ColorCorrector", -1, -1)
            if not color_node:
                raise ResolveOperationError("Failed to create color correction node")

        if lift:
            color_node.Lift = [
                lift.get("r", 0),
                lift.get("g", 0),
                lift.get("b", 0),
                lift.get("y", 0),
            ]
        if gamma:
            color_node.Gamma = [
                gamma.get("r", 0),
                gamma.get("g", 0),
                gamma.get("b", 0),
                gamma.get("y", 0),
            ]
        if gain:
            color_node.Gain = [
                gain.get("r", 1),
                gain.get("g", 1),
                gain.get("b", 1),
                gain.get("y", 1),
            ]
        if offset:
            color_node.Offset = [
                offset.get("r", 0),
                offset.get("g", 0),
                offset.get("b", 0),
                offset.get("y", 0),
            ]

        adjustments = {
            "lift": lift or {},
            "gamma": gamma or {},
            "gain": gain or {},
            "offset": offset or {},
        }

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": current_clip.GetName(),
            "node_name": node_name or "ColorCorrector",
            "adjustments": adjustments,
            "message": "Color wheel adjustments applied",
        }

    except Exception as e:
        logger.error(f"Error adjusting color wheels: {e!s}")
        raise ResolveOperationError(f"Failed to adjust color wheels: {e!s}")


# ── Gallery / Stills Operations ─────────────────────────────────────


async def grab_still_impl(
    app,
    still_name: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Grab a still from the current clip in the Color page."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        current_clip = timeline.GetCurrentVideoItem()
        if not current_clip:
            raise ResolveOperationError("No clip is currently selected")

        if hasattr(project, "GetGallery"):
            gallery = project.GetGallery()
            if gallery and hasattr(gallery, "GetCurrentStillAlbum"):
                album = gallery.GetCurrentStillAlbum()
                if album and hasattr(album, "GrabStill"):
                    still = album.GrabStill(still_name or "")
                    if still:
                        return {
                            "status": "success",
                            "still_name": still_name or "Untitled",
                            "clip_name": current_clip.GetName(),
                            "message": f"Grabbed still from '{current_clip.GetName()}'",
                        }
        raise ResolveOperationError("GrabStill not available in this API version")

    except Exception as e:
        logger.error(f"Error grabbing still: {e!s}")
        raise ResolveOperationError(f"Failed to grab still: {e!s}")


async def get_stills_impl(app) -> dict[str, Any]:
    """Get all stills in the current gallery album."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if hasattr(project, "GetGallery"):
            gallery = project.GetGallery()
            if gallery and hasattr(gallery, "GetCurrentStillAlbum"):
                album = gallery.GetCurrentStillAlbum()
                if album and hasattr(album, "GetStills"):
                    stills = album.GetStills() or []
                    still_list = []
                    for i, still in enumerate(stills):
                        still_info = {"index": i}
                        if hasattr(still, "GetLabel"):
                            still_info["label"] = still.GetLabel()
                        if hasattr(still, "GetClipProperty"):
                            still_info["source"] = still.GetClipProperty("Source Clip") or ""
                        still_list.append(still_info)
                    return {"status": "success", "stills": still_list, "count": len(still_list)}

        return {"status": "success", "stills": [], "count": 0, "message": "Gallery stills not available in this API version"}

    except Exception as e:
        logger.error(f"Error getting stills: {e!s}")
        raise ResolveOperationError(f"Failed to get stills: {e!s}")


async def apply_grade_from_still_impl(
    app,
    still_index: int,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Apply a grade from a gallery still to the current clip."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        current_clip = timeline.GetCurrentVideoItem()
        if not current_clip:
            raise ResolveOperationError("No clip is currently selected")

        gallery = project.GetGallery()
        if gallery and hasattr(gallery, "GetCurrentStillAlbum"):
            album = gallery.GetCurrentStillAlbum()
            if album and hasattr(album, "GetStills"):
                stills = album.GetStills() or []
                if still_index < 0 or still_index >= len(stills):
                    raise ResolveOperationError(f"Invalid still index: {still_index}")
                still = stills[still_index]
                if hasattr(current_clip, "ApplyGradeFromStill"):
                    current_clip.ApplyGradeFromStill(still)
                    return {
                        "status": "success",
                        "still_index": still_index,
                        "clip_name": current_clip.GetName(),
                        "message": f"Applied grade from still {still_index} to '{current_clip.GetName()}'",
                    }

        raise ResolveOperationError("ApplyGradeFromStill not available in this API version")

    except Exception as e:
        logger.error(f"Error applying grade from still: {e!s}")
        raise ResolveOperationError(f"Failed to apply grade from still: {e!s}")


def register_tools(app):
    """Register color grading tools with the FastMCP app."""

    @app.tool()
    async def create_color_node(
        node_type: ColorCorrectionType,
        name: str | None = None,
        parent_node: str | None = None,
        timeline_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new color correction node in the current clip.

        Args:
            node_type: Type of node to create
            name: Optional name for the node
            parent_node: Optional name of the parent node to connect to
            timeline_name: Optional name of the timeline

        Returns:
            Dictionary with node creation status and details
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")

                # Get the current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")

                # Get the current clip (if any)
                current_clip = timeline.GetCurrentVideoItem()
                if not current_clip:
                    raise ResolveOperationError("No clip is currently selected")

                # Get the color grading interface
                fusion = resolve.Fusion()
                if not fusion:
                    raise ResolveOperationError("Could not access Fusion (color grading) interface")

                # Get the current composition
                comp = fusion.GetCurrentComp()
                if not comp:
                    raise ResolveOperationError("Could not access current composition")

                # Create a new node of the specified type
                node_type_map = {
                    ColorCorrectionType.PRIMARY: "Color",
                    ColorCorrectionType.LOG: "ColorCurves",
                    ColorCorrectionType.HDR: "HDRTool",
                    ColorCorrectionType.CURVES: "HueVsCurves",
                    ColorCorrectionType.QUALIFIER: "Qualifier",
                    ColorCorrectionType.WINDOW: "Window",
                    ColorCorrectionType.TRACKER: "Tracker",
                    ColorCorrectionType.BLUR: "Blur",
                    ColorCorrectionType.SHARPEN: "Sharpen",
                    ColorCorrectionType.NOISE_REDUCTION: "NoiseReduction",
                    ColorCorrectionType.RESIZE: "Resize",
                    ColorCorrectionType.LUT: "LUT",
                }

                node_type_str = node_type_map.get(node_type, "Color")
                new_node = comp.AddTool(node_type_str, -1, -1)

                if not new_node:
                    raise ResolveOperationError(f"Failed to create {node_type.value} node")

                # Set the node name if provided
                if name:
                    new_node.SetAttrs({"TOOLS_Name": name})

                # Connect to parent node if specified
                if parent_node:
                    parent = comp.FindTool(parent_node)
                    if parent:
                        # Simple connection - actual connection logic depends on node types
                        new_node.Input.ConnectTo(parent.Output)

                return {
                    "status": "success",
                    "message": f"Created {node_type.value} node: {name or 'Unnamed'}",
                    "node": {
                        "id": new_node.GetAttrs()["TOOLS_RegID"],
                        "name": name or f"{node_type.value}_node",
                        "type": node_type.value,
                    },
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to create color node: {e!s}")

    @app.tool()
    async def apply_lut(
        clip_path: str, lut_path: str, intensity: float = 1.0, timeline_name: str | None = None
    ) -> dict[str, Any]:
        """
        Apply a LUT (Look-Up Table) to a clip.

        Args:
            clip_path: Path to the clip to apply the LUT to
            lut_path: Path to the LUT file (.cube, .3dl, etc.)
            intensity: Strength of the LUT effect (0.0 to 1.0)
            timeline_name: Optional name of the timeline

        Returns:
            Dictionary with operation status
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")

                # Get the timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")

                # Get the color grading interface
                fusion = resolve.Fusion()
                if not fusion:
                    raise ResolveOperationError("Could not access Fusion (color grading) interface")

                # Get the current composition
                comp = fusion.GetCurrentComp()
                if not comp:
                    raise ResolveOperationError("Could not access current composition")

                # Create a LUT node
                lut_node = comp.AddTool("LUT", -1, -1)
                if not lut_node:
                    raise ResolveOperationError("Failed to create LUT node")

                # Configure the LUT node
                lut_node.LUTFile = lut_path
                lut_node.Mix = intensity

                # Connect the LUT node to the current clip
                # Note: This is a simplified example - actual connection logic may vary
                # depending on your node graph structure

                return {
                    "status": "success",
                    "message": f"Applied LUT '{lut_path}' with intensity {intensity}",
                    "node_id": lut_node.GetAttrs()["TOOLS_RegID"],
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to apply LUT: {e!s}")

    @app.tool()
    async def set_color_space(
        transform: ColorSpaceTransform, timeline_name: str | None = None
    ) -> dict[str, Any]:
        """
        Set the color space transform for the current clip.

        Args:
            transform: Color space transform settings
            timeline_name: Optional name of the timeline

        Returns:
            Dictionary with operation status
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")

                # Get the current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")

                # Get the current clip (if any)
                current_clip = timeline.GetCurrentVideoItem()
                if not current_clip:
                    raise ResolveOperationError("No clip is currently selected")

                fusion = resolve.Fusion()
                if not fusion:
                    raise ResolveOperationError("Could not access Fusion interface")

                comp = fusion.GetCurrentComp()
                if not comp:
                    raise ResolveOperationError("Could not access current composition")

                cst = comp.AddTool("ColorSpaceTransform", -1, -1)
                if not cst:
                    raise ResolveOperationError("Failed to create ColorSpaceTransform node")

                cst.SourceSpace = transform.input_color_space
                cst.SourceGamma = transform.input_gamma or "Same as Project"
                cst.TargetSpace = transform.output_color_space
                cst.TargetGamma = transform.output_gamma or "Same as Project"

                resolve.GetProjectManager().SaveProject()

                return {
                    "status": "success",
                    "message": f"Color space transform applied: {transform.input_color_space} → {transform.output_color_space}",
                    "transform": {
                        "input_color_space": transform.input_color_space,
                        "input_gamma": transform.input_gamma,
                        "output_color_space": transform.output_color_space,
                        "output_gamma": transform.output_gamma,
                    },
                    "node_id": cst.GetAttrs()["TOOLS_RegID"],
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to set color space: {e!s}")

    @app.tool()
    async def adjust_color_wheels(
        lift: dict[str, float] | None = None,
        gamma: dict[str, float] | None = None,
        gain: dict[str, float] | None = None,
        offset: dict[str, float] | None = None,
        timeline_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Adjust the color wheels for the current clip.

        Args:
            lift: Lift adjustments (R, G, B, luma)
            gamma: Gamma adjustments (R, G, B, luma)
            gain: Gain adjustments (R, G, B, luma)
            offset: Offset adjustments (R, G, B, luma)
            timeline_name: Optional name of the timeline

        Returns:
            Dictionary with operation status
        """
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")

                # Get the current timeline
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")

                # Get the current clip (if any)
                current_clip = timeline.GetCurrentVideoItem()
                if not current_clip:
                    raise ResolveOperationError("No clip is currently selected")

                # Get the color grading interface
                fusion = resolve.Fusion()
                if not fusion:
                    raise ResolveOperationError("Could not access Fusion (color grading) interface")

                # Get the current composition
                comp = fusion.GetCurrentComp()
                if not comp:
                    raise ResolveOperationError("Could not access current composition")

                # Create or get a color correction node
                color_node = comp.FindTool("ColorCorrector")
                if not color_node:
                    color_node = comp.AddTool("ColorCorrector", -1, -1)
                    if not color_node:
                        raise ResolveOperationError("Failed to create color correction node")

                # Apply color adjustments
                if lift:
                    color_node.Lift = [
                        lift.get("r", 0),
                        lift.get("g", 0),
                        lift.get("b", 0),
                        lift.get("y", 0),
                    ]
                if gamma:
                    color_node.Gamma = [
                        gamma.get("r", 0),
                        gamma.get("g", 0),
                        gamma.get("b", 0),
                        gamma.get("y", 0),
                    ]
                if gain:
                    color_node.Gain = [
                        gain.get("r", 1),
                        gain.get("g", 1),
                        gain.get("b", 1),
                        gain.get("y", 1),
                    ]
                if offset:
                    color_node.Offset = [
                        offset.get("r", 0),
                        offset.get("g", 0),
                        offset.get("b", 0),
                        offset.get("y", 0),
                    ]

                return {
                    "status": "success",
                    "message": "Color adjustments applied",
                    "adjustments": {"lift": lift, "gamma": gamma, "gain": gain, "offset": offset},
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to adjust color wheels: {e!s}")

    @app.tool()
    async def grab_still(still_name: str | None = None, timeline_name: str | None = None) -> dict[str, Any]:
        """Grab a still from the current clip to the gallery."""
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                else:
                    timeline = project.GetCurrentTimeline()
                if not timeline:
                    raise ResolveOperationError("No timeline is currently open")
                current_clip = timeline.GetCurrentVideoItem()
                if not current_clip:
                    raise ResolveOperationError("No clip is currently selected")
                gallery = project.GetGallery()
                if gallery and hasattr(gallery, "GetCurrentStillAlbum"):
                    album = gallery.GetCurrentStillAlbum()
                    if album and hasattr(album, "GrabStill"):
                        album.GrabStill(still_name or "")
                        return {"status": "success", "still_name": still_name or "Untitled", "clip_name": current_clip.GetName()}
                raise ResolveOperationError("GrabStill not available")
        except Exception as e:
            raise ResolveOperationError(f"Failed to grab still: {e!s}")

    @app.tool()
    async def get_stills() -> dict[str, Any]:
        """Get all stills in the current gallery album."""
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                if hasattr(project, "GetGallery"):
                    gallery = project.GetGallery()
                    if gallery and hasattr(gallery, "GetCurrentStillAlbum"):
                        album = gallery.GetCurrentStillAlbum()
                        if album and hasattr(album, "GetStills"):
                            stills = album.GetStills() or []
                            still_list = []
                            for i, still in enumerate(stills):
                                info = {"index": i}
                                if hasattr(still, "GetLabel"):
                                    info["label"] = still.GetLabel()
                                still_list.append(info)
                            return {"status": "success", "stills": still_list, "count": len(still_list)}
                return {"status": "success", "stills": [], "count": 0}
        except Exception as e:
            raise ResolveOperationError(f"Failed to get stills: {e!s}")

    @app.tool()
    async def apply_grade_from_still(still_index: int, timeline_name: str | None = None) -> dict[str, Any]:
        """Apply a grade from a gallery still to the current clip."""
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                else:
                    timeline = project.GetCurrentTimeline()
                if not timeline:
                    raise ResolveOperationError("No timeline is currently open")
                current_clip = timeline.GetCurrentVideoItem()
                if not current_clip:
                    raise ResolveOperationError("No clip is currently selected")
                gallery = project.GetGallery()
                if gallery and hasattr(gallery, "GetCurrentStillAlbum"):
                    album = gallery.GetCurrentStillAlbum()
                    if album and hasattr(album, "GetStills"):
                        stills = album.GetStills() or []
                        if still_index < 0 or still_index >= len(stills):
                            raise ResolveOperationError(f"Invalid still index: {still_index}")
                        still = stills[still_index]
                        if hasattr(current_clip, "ApplyGradeFromStill"):
                            current_clip.ApplyGradeFromStill(still)
                            return {"status": "success", "still_index": still_index, "clip_name": current_clip.GetName()}
                raise ResolveOperationError("ApplyGradeFromStill not available")
        except Exception as e:
            raise ResolveOperationError(f"Failed to apply grade from still: {e!s}")

    # Add more color grading tools as needed
    # - Color match
    # - Scopes and waveforms
    # - Keyframing
    # - Power windows
    # - Tracking
    # - Noise reduction
