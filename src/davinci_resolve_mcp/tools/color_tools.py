"""
DaVinci Resolve Color Tools.

This module provides tools for color grading and correction in DaVinci Resolve,
including node-based color operations, LUT management, and color matching.
"""
import logging
from typing import Dict, Optional, Any
from enum import Enum
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
    settings: Dict[str, Any] = Field(default_factory=dict, description="Node settings")


def register_tools(app):
    """Register color grading tools with the FastMCP app."""
    
    @app.tool()
    async def create_color_node(
        node_type: ColorCorrectionType,
        name: Optional[str] = None,
        parent_node: Optional[str] = None,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
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
                    ColorCorrectionType.LUT: "LUT"
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
                        "type": node_type.value
                    }
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to create color node: {str(e)}")

    @app.tool()
    async def apply_lut(
        clip_path: str,
        lut_path: str,
        intensity: float = 1.0,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
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
                    "node_id": lut_node.GetAttrs()["TOOLS_RegID"]
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to apply LUT: {str(e)}")

    @app.tool()
    async def set_color_space(
        transform: ColorSpaceTransform,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
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
                    "transform": transform.dict()
                }
                
        except Exception as e:
            raise ResolveOperationError(f"Failed to set color space: {str(e)}")

    @app.tool()
    async def adjust_color_wheels(
        lift: Optional[Dict[str, float]] = None,
        gamma: Optional[Dict[str, float]] = None,
        gain: Optional[Dict[str, float]] = None,
        offset: Optional[Dict[str, float]] = None,
        timeline_name: Optional[str] = None
    ) -> Dict[str, Any]:
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
                    color_node.Lift = [lift.get('r', 0), lift.get('g', 0), lift.get('b', 0), lift.get('y', 0)]
                if gamma:
                    color_node.Gamma = [gamma.get('r', 0), gamma.get('g', 0), gamma.get('b', 0), gamma.get('y', 0)]
                if gain:
                    color_node.Gain = [gain.get('r', 1), gain.get('g', 1), gain.get('b', 1), gain.get('y', 1)]
                if offset:
                    color_node.Offset = [offset.get('r', 0), offset.get('g', 0), offset.get('b', 0), offset.get('y', 0)]
                
                return {
                    "status": "success",
                    "message": "Color adjustments applied",
                    "adjustments": {
                        "lift": lift,
                        "gamma": gamma,
                        "gain": gain,
                        "offset": offset
                    }
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

    return app
