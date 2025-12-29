"""
Color grading and correction data models for DaVinci Resolve.

This module contains data models for managing color grading nodes, LUTs, scopes,
and other color-related functionality in DaVinci Resolve.
"""
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pydantic import Field
from .common import ResolveObject, ColorSpace


class ColorNodeType(str, Enum):
    """Types of nodes in the DaVinci Resolve color grading node graph."""
    # Basic node types
    SERIAL = "serial"
    PARALLEL = "parallel"
    LAYER = "layer"
    
    # Color correction nodes
    CORRECTOR = "corrector"
    CORRECTOR_3D = "corrector_3d"
    
    # Adjustment nodes
    BLUR = "blur"
    SHARPEN = "sharpen"
    NOISE_REDUCTION = "noise_reduction"
    
    # Keying nodes
    QUALIFIER = "qualifier"
    WINDOW = "window"
    TRACKER = "tracker"
    
    # Special nodes
    GROUP = "group"
    TIMELINE = "timeline"
    CLIP = "clip"
    
    # Fusion nodes
    FUSION = "fusion"


class ColorNode(ResolveObject):
    """
    Represents a node in the DaVinci Resolve color grading node graph.
    
    Attributes:
        node_id: Unique identifier for the node
        node_type: Type of the node
        name: Display name of the node
        is_active: Whether the node is active
        is_bypassed: Whether the node is bypassed
        is_collapsed: Whether the node is collapsed in the UI
        position: Position in the node graph (x, y)
        size: Size of the node (width, height)
        input_count: Number of input connections
        output_count: Number of output connections
        parent_id: ID of the parent node (for nested nodes)
        children: List of child node IDs
        parameters: Dictionary of node parameters
        metadata: Additional metadata
    """
    node_id: str = Field(..., description="Unique node identifier")
    node_type: ColorNodeType = Field(..., description="Type of node")
    name: str = Field(default="", description="Display name")
    is_active: bool = Field(default=True, description="Active status")
    is_bypassed: bool = Field(default=False, description="Bypass status")
    is_collapsed: bool = Field(default=False, description="Collapsed in UI")
    position: Tuple[float, float] = Field(
        default=(0.0, 0.0),
        description="(x, y) position in node graph"
    )
    size: Tuple[float, float] = Field(
        default=(200.0, 100.0),
        description="(width, height) of the node"
    )
    input_count: int = Field(default=1, ge=0, description="Number of inputs")
    output_count: int = Field(default=1, ge=0, description="Number of outputs")
    parent_id: Optional[str] = Field(default=None, description="Parent node ID")
    children: List[str] = Field(
        default_factory=list,
        description="List of child node IDs"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Node parameters"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    def add_parameter(self, name: str, value: Any, param_type: str = "float") -> None:
        """
        Add a parameter to the node.
        
        Args:
            name: Parameter name
            value: Parameter value
            param_type: Parameter type (float, int, bool, string, color, etc.)
        """
        self.parameters[name] = {
            "value": value,
            "type": param_type,
            "default": value
        }
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """
        Get a parameter value by name.
        
        Args:
            name: Parameter name
            default: Default value if parameter doesn't exist
            
        Returns:
            The parameter value or default if not found
        """
        param = self.parameters.get(name)
        return param["value"] if param and "value" in param else default


class ColorGrade(ResolveObject):
    """
    Represents a complete color grade with multiple nodes.
    
    Attributes:
        name: Name of the grade
        nodes: Dictionary of nodes by ID
        root_node_id: ID of the root node
        selected_node_id: ID of the currently selected node
        version: Version of the grade
        created_at: When the grade was created
        modified_at: When the grade was last modified
        description: Optional description
        tags: List of tags for organization
        thumbnail: Path to thumbnail image
        is_shared: Whether the grade is shared
        is_read_only: Whether the grade is read-only
    """
    name: str = Field(..., description="Name of the grade")
    nodes: Dict[str, ColorNode] = Field(
        default_factory=dict,
        description="Dictionary of nodes by ID"
    )
    root_node_id: Optional[str] = Field(
        default=None,
        description="ID of the root node"
    )
    selected_node_id: Optional[str] = Field(
        default=None,
        description="ID of the selected node"
    )
    version: str = Field(default="1.0", description="Version string")
    created_at: str = Field(..., description="Creation timestamp")
    modified_at: str = Field(..., description="Last modified timestamp")
    description: Optional[str] = Field(
        default=None,
        description="Optional description"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tags"
    )
    thumbnail: Optional[str] = Field(
        default=None,
        description="Path to thumbnail image"
    )
    is_shared: bool = Field(
        default=False,
        description="Shared status"
    )
    is_read_only: bool = Field(
        default=False,
        description="Read-only status"
    )
    
    def add_node(self, node: ColorNode, parent_id: Optional[str] = None) -> str:
        """
        Add a node to the grade.
        
        Args:
            node: The node to add
            parent_id: Optional parent node ID
            
        Returns:
            The ID of the added node
        """
        if node.node_id in self.nodes:
            raise ValueError(f"Node with ID {node.node_id} already exists")
            
        self.nodes[node.node_id] = node
        
        if parent_id:
            if parent_id not in self.nodes:
                raise ValueError(f"Parent node {parent_id} not found")
            self.nodes[parent_id].children.append(node.node_id)
            node.parent_id = parent_id
        elif not self.root_node_id:
            self.root_node_id = node.node_id
            
        return node.node_id
    
    def get_node(self, node_id: str) -> Optional[ColorNode]:
        """
        Get a node by ID.
        
        Args:
            node_id: The node ID
            
        Returns:
            The node, or None if not found
        """
        return self.nodes.get(node_id)
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node and all its children.
        
        Args:
            node_id: The node ID to remove
            
        Returns:
            True if successful, False otherwise
        """
        if node_id not in self.nodes:
            return False
            
        # Remove all children first
        node = self.nodes[node_id]
        for child_id in node.children:
            self.remove_node(child_id)
            
        # Remove from parent's children list
        if node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            if node_id in parent.children:
                parent.children.remove(node_id)
                
        # Remove the node
        del self.nodes[node_id]
        
        # Update root node if needed
        if self.root_node_id == node_id:
            self.root_node_id = next(iter(self.nodes), None)
            
        return True


class LUTInfo(ResolveObject):
    """
    Information about a Look-Up Table (LUT) in DaVinci Resolve.
    
    Attributes:
        name: Name of the LUT
        path: Filesystem path to the LUT file
        format: Format of the LUT (e.g., 'cube', '3dl', 'dat')
        color_space: Color space the LUT is designed for
        input_color_space: Input color space
        output_color_space: Output color space
        is_builtin: Whether this is a built-in LUT
        category: Category for organization
        description: Optional description
        thumbnail: Path to thumbnail image
        is_read_only: Whether the LUT is read-only
    """
    name: str = Field(..., description="Name of the LUT")
    path: str = Field(..., description="Filesystem path")
    format: str = Field(..., description="LUT format (cube, 3dl, dat, etc.)")
    color_space: ColorSpace = Field(
        default=ColorSpace.REC709,
        description="Target color space"
    )
    input_color_space: Optional[ColorSpace] = Field(
        default=None,
        description="Input color space"
    )
    output_color_space: Optional[ColorSpace] = Field(
        default=None,
        description="Output color space"
    )
    is_builtin: bool = Field(
        default=False,
        description="Built-in LUT status"
    )
    category: Optional[str] = Field(
        default=None,
        description="Category for organization"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional description"
    )
    thumbnail: Optional[str] = Field(
        default=None,
        description="Path to thumbnail image"
    )
    is_read_only: bool = Field(
        default=False,
        description="Read-only status"
    )


class ColorWheels(ResolveObject):
    """
    Represents the color wheels in DaVinci Resolve.
    
    Attributes:
        lift: Lift color adjustments (shadows)
        gamma: Gamma color adjustments (midtones)
        gain: Gain color adjustments (highlights)
        offset: Offset color adjustments (overall)
        contrast: Contrast value (-1.0 to 1.0)
        pivot: Pivot point for contrast (0.0 to 1.0)
        saturation: Saturation value (0.0 to 2.0)
        luma_mix: Luma mix value (0.0 to 1.0)
        hue_vs_sat: Hue vs Saturation curve adjustments
        luma_vs_sat: Luma vs Saturation curve adjustments
        hue_vs_hue: Hue vs Hue curve adjustments
        hue_vs_luma: Hue vs Luma curve adjustments
        luma_vs_hue: Luma vs Hue curve adjustments
    """
    lift: Tuple[float, float, float, float] = Field(
        default=(0.0, 0.0, 0.0, 0.0),
        description="Lift (shadows) RGBA values"
    )
    gamma: Tuple[float, float, float, float] = Field(
        default=(0.0, 0.0, 0.0, 0.0),
        description="Gamma (midtones) RGBA values"
    )
    gain: Tuple[float, float, float, float] = Field(
        default=(1.0, 1.0, 1.0, 1.0),
        description="Gain (highlights) RGBA values"
    )
    offset: Tuple[float, float, float, float] = Field(
        default=(0.0, 0.0, 0.0, 0.0),
        description="Offset RGBA values"
    )
    contrast: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Contrast adjustment"
    )
    pivot: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Contrast pivot point"
    )
    saturation: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Saturation adjustment"
    )
    luma_mix: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Luma mix value"
    )
    hue_vs_sat: List[Tuple[float, float]] = Field(
        default_factory=list,
        description="Hue vs Saturation curve points"
    )
    luma_vs_sat: List[Tuple[float, float]] = Field(
        default_factory=list,
        description="Luma vs Saturation curve points"
    )
    hue_vs_hue: List[Tuple[float, float]] = Field(
        default_factory=list,
        description="Hue vs Hue curve points"
    )
    hue_vs_luma: List[Tuple[float, float]] = Field(
        default_factory=list,
        description="Hue vs Luma curve points"
    )
    luma_vs_hue: List[Tuple[float, float]] = Field(
        default_factory=list,
        description="Luma vs Hue curve points"
    )


class ColorSpaceTransform(ResolveObject):
    """
    Represents a color space transformation in DaVinci Resolve.
    
    Attributes:
        input_color_space: Input color space
        output_color_space: Output color space
        input_gamma: Input gamma curve
        output_gamma: Output gamma curve
        tone_mapping: Tone mapping method
        gamut_mapping: Gamut mapping method
        use_white_point_adaption: Whether to use white point adaptation
        white_point: White point coordinates (x, y)
        apply_chromatic_adaption: Whether to apply chromatic adaptation
        chromatic_adaption_method: Chromatic adaptation method
        apply_black_offset: Whether to apply black offset
        black_offset: Black offset value
    """
    input_color_space: ColorSpace = Field(
        default=ColorSpace.REC709,
        description="Input color space"
    )
    output_color_space: ColorSpace = Field(
        default=ColorSpace.REC709,
        description="Output color space"
    )
    input_gamma: str = Field(
        default="2.4",
        description="Input gamma curve"
    )
    output_gamma: str = Field(
        default="2.4",
        description="Output gamma curve"
    )
    tone_mapping: str = Field(
        default="None",
        description="Tone mapping method"
    )
    gamut_mapping: str = Field(
        default="None",
        description="Gamut mapping method"
    )
    use_white_point_adaption: bool = Field(
        default=True,
        description="Use white point adaptation"
    )
    white_point: Tuple[float, float] = Field(
        default=(0.3127, 0.3290),
        description="White point coordinates (x, y)"
    )
    apply_chromatic_adaption: bool = Field(
        default=True,
        description="Apply chromatic adaptation"
    )
    chromatic_adaption_method: str = Field(
        default="Bradford",
        description="Chromatic adaptation method"
    )
    apply_black_offset: bool = Field(
        default=False,
        description="Apply black offset"
    )
    black_offset: float = Field(
        default=0.0,
        description="Black offset value"
    )


class ScopesSettings(ResolveObject):
    """
    Settings for the scopes in DaVinci Resolve.
    
    Attributes:
        waveform_type: Type of waveform display
        waveform_style: Style of waveform display
        vectorscope_style: Style of vectorscope display
        histogram_style: Style of histogram display
        parade_style: Style of parade display
        rgb_overlay: Whether to show RGB overlay
        y_only: Whether to show Y-only
        show_skin_tone_indicator: Whether to show skin tone indicator
        show_clipping: Whether to show clipping indicators
        show_legal_lines: Whether to show legal lines
        show_legal_matte: Whether to show legal matte
        show_cursor_position: Whether to show cursor position
        show_audio_waveform: Whether to show audio waveform
        show_audio_spectrum: Whether to show audio spectrum
        scope_size: Size of the scopes (0.0 to 1.0)
        opacity: Opacity of the scopes (0.0 to 1.0)
        background_brightness: Background brightness (0.0 to 1.0)
    """
    waveform_type: str = Field(
        default="RGB",
        description="Type of waveform display (RGB, YC, Y, YCbCr, YPbPr, YUV, HLS, HSV, HSL, YCgCo, YDzDx, RGB Parade, YCbCr Parade, YPbPr Parade, YUV Parade, HLS Parade, HSV Parade, HSL Parade, YCgCo Parade, YDzDx Parade)"
    )
    waveform_style: str = Field(
        default="Overlay",
        description="Style of waveform display (Overlay, Parade, Stacked)"
    )
    vectorscope_style: str = Field(
        default="Vectorscope",
        description="Style of vectorscope display (Vectorscope, Vectorscope 2x, Vectorscope 5x, Vectorscope 10x, Vectorscope 20x)"
    )
    histogram_style: str = Field(
        default="RGB",
        description="Style of histogram display (RGB, YC, Y, YCbCr, YPbPr, YUV, HLS, HSV, HSL, YCgCo, YDzDx)"
    )
    parade_style: str = Field(
        default="RGB",
        description="Style of parade display (RGB, YC, Y, YCbCr, YPbPr, YUV, HLS, HSV, HSL, YCgCo, YDzDx)"
    )
    rgb_overlay: bool = Field(
        default=False,
        description="Show RGB overlay"
    )
    y_only: bool = Field(
        default=False,
        description="Show Y-only"
    )
    show_skin_tone_indicator: bool = Field(
        default=True,
        description="Show skin tone indicator"
    )
    show_clipping: bool = Field(
        default=True,
        description="Show clipping indicators"
    )
    show_legal_lines: bool = Field(
        default=True,
        description="Show legal lines"
    )
    show_legal_matte: bool = Field(
        default=False,
        description="Show legal matte"
    )
    show_cursor_position: bool = Field(
        default=True,
        description="Show cursor position"
    )
    show_audio_waveform: bool = Field(
        default=False,
        description="Show audio waveform"
    )
    show_audio_spectrum: bool = Field(
        default=False,
        description="Show audio spectrum"
    )
    scope_size: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Size of the scopes"
    )
    opacity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Opacity of the scopes"
    )
    background_brightness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Background brightness"
    )
