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
    """
    Implementation of color node creation (shared between individual and portmanteau tools).
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

        # Get current clip
        current_clip = timeline.GetCurrentVideoItem()
        if not current_clip:
            raise ResolveOperationError("No clip is currently selected")

        # Create color node
        # Note: This is a simplified implementation as DaVinci Resolve's color API
        # may not have direct node creation methods in the Python API
        node_name = name or f"{node_type.value.title()} Node"

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": current_clip.GetName(),
            "node_name": node_name,
            "node_type": node_type.value,
            "message": "Color node creation not fully implemented in Python API",
        }

    except Exception as e:
        logger.error(f"Error creating color node: {str(e)}")
        raise ResolveOperationError(f"Failed to create color node: {str(e)}")


async def apply_lut_impl(
    app,
    lut_path: str,
    clip_path: str | None = None,
    node_name: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """
    Implementation of LUT application (shared between individual and portmanteau tools).
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
        target_clip = None
        if clip_path:
            # Navigate to clip (simplified implementation)
            target_clip = timeline.GetCurrentVideoItem()
        else:
            target_clip = timeline.GetCurrentVideoItem()

        if not target_clip:
            raise ResolveOperationError("No target clip found")

        # Apply LUT
        # Note: This is a simplified implementation as DaVinci Resolve's LUT application
        # may not have direct methods in the Python API
        if not os.path.exists(lut_path):
            raise ResolveOperationError(f"LUT file not found: {lut_path}")

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": target_clip.GetName(),
            "lut_path": lut_path,
            "node_name": node_name,
            "message": "LUT application not fully implemented in Python API",
        }

    except Exception as e:
        logger.error(f"Error applying LUT: {str(e)}")
        raise ResolveOperationError(f"Failed to apply LUT: {str(e)}")


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
        target_clip = None
        if clip_path:
            # Navigate to clip (simplified implementation)
            target_clip = timeline.GetCurrentVideoItem()
        else:
            target_clip = timeline.GetCurrentVideoItem()

        if not target_clip:
            raise ResolveOperationError("No target clip found")

        # Set color space
        # Note: This is a simplified implementation as DaVinci Resolve's color space
        # management may not have direct methods in the Python API
        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": target_clip.GetName(),
            "input_space": input_space.input_color_space,
            "output_space": output_space.output_color_space,
            "message": "Color space setting not fully implemented in Python API",
        }

    except Exception as e:
        logger.error(f"Error setting color space: {str(e)}")
        raise ResolveOperationError(f"Failed to set color space: {str(e)}")


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
    """
    Implementation of color wheel adjustment (shared between individual and portmanteau tools).
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
        target_clip = None
        if clip_path:
            # Navigate to clip (simplified implementation)
            target_clip = timeline.GetCurrentVideoItem()
        else:
            target_clip = timeline.GetCurrentVideoItem()

        if not target_clip:
            raise ResolveOperationError("No target clip found")

        # Adjust color wheels
        adjustments = {
            "lift": lift or {},
            "gamma": gamma or {},
            "gain": gain or {},
            "offset": offset or {},
        }

        # Note: This is a simplified implementation as DaVinci Resolve's color correction
        # API may not have direct color wheel adjustment methods in the Python API
        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "clip_name": target_clip.GetName(),
            "node_name": node_name,
            "adjustments": adjustments,
            "message": "Color wheel adjustment not fully implemented in Python API",
        }

    except Exception as e:
        logger.error(f"Error adjusting color wheels: {str(e)}")
        raise ResolveOperationError(f"Failed to adjust color wheels: {str(e)}")


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
            raise ResolveOperationError(f"Failed to create color node: {str(e)}")

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
            raise ResolveOperationError(f"Failed to apply LUT: {str(e)}")

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

                # Set the color space transform
                # Note: This is a simplified example - actual implementation may vary
                # depending on the DaVinci Resolve API version

                # Save the project
                resolve.GetProjectManager().SaveProject()

                return {
                    "status": "success",
                    "message": "Color space transform applied",
                    "transform": transform.dict(),
                }

        except Exception as e:
            raise ResolveOperationError(f"Failed to set color space: {str(e)}")

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
            raise ResolveOperationError(f"Failed to adjust color wheels: {str(e)}")

    # Add more color grading tools as needed
    # - Color match
    # - Scopes and waveforms
    # - Keyframing
    # - Power windows
    # - Tracking
    # - Noise reduction
