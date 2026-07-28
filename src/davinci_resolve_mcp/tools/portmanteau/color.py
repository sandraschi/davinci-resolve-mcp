"""
DaVinci Resolve Color Portmanteau Tool.

Consolidates color grading operations into a single tool.
"""

import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)


_MUTATING = {}


def setup_color_portmanteau(app):
    """Register the color portmanteau tool."""

    @app.tool(annotations=_MUTATING)
    async def resolve_color(
        action: Literal[
            "create_node",
            "apply_lut",
            "set_color_space",
            "adjust_wheels",
            "grab_still",
            "get_stills",
            "apply_grade_from_still",
        ],
        node_type: str = "primary",
        node_name: str | None = None,
        parent_node: str | None = None,
        timeline_name: str | None = None,
        clip_path: str | None = None,
        lut_path: str | None = None,
        intensity: float = 1.0,
        input_color_space: str | None = None,
        output_color_space: str | None = None,
        input_gamma: str | None = None,
        output_gamma: str | None = None,
        lift: dict[str, float] | None = None,
        gamma: dict[str, float] | None = None,
        gain: dict[str, float] | None = None,
        offset: dict[str, float] | None = None,
        still_name: str | None = None,
        still_index: int = 0,
    ) -> dict[str, Any]:
        """
        Comprehensive color grading for DaVinci Resolve.

        PORTMANTEAU PATTERN: Consolidates 4 color tools into 1.

        SUPPORTED ACTIONS:
        - create_node: Create color correction node (requires: node_type)
        - apply_lut: Apply LUT to clip (requires: clip_path, lut_path)
        - set_color_space: Set color space transform
        - adjust_wheels: Adjust color wheels (lift/gamma/gain/offset)
        - grab_still: Grab still from current clip (optional: node_name)
        - get_stills: List gallery stills
        - apply_grade_from_still: Apply grade from still (requires: still_index)

        Args:
            action: Operation to perform (create_node, apply_lut, set_color_space, adjust_wheels)
            node_type: Node type (primary, log, hdr, curves, qualifier, window, lut). Default: primary
            node_name: Name for the node. Optional.
            parent_node: Parent node to connect to. Optional.
            timeline_name: Target timeline. Optional.
            clip_path: Path to clip. Required for: apply_lut
            lut_path: Path to LUT file. Required for: apply_lut
            intensity: LUT intensity (0.0-1.0). Default: 1.0
            input_color_space: Input color space. Used by: set_color_space
            output_color_space: Output color space. Used by: set_color_space
            input_gamma: Input gamma. Used by: set_color_space
            output_gamma: Output gamma. Used by: set_color_space
            lift: Lift adjustments {r, g, b, y}. Used by: adjust_wheels
            gamma: Gamma adjustments {r, g, b, y}. Used by: adjust_wheels
            gain: Gain adjustments {r, g, b, y}. Used by: adjust_wheels
            offset: Offset adjustments {r, g, b, y}. Used by: adjust_wheels

        Returns:
            Dict with operation results

        Examples:
            # Create primary color node
            resolve_color("create_node", node_type="primary", node_name="Base Grade")

            # Apply LUT
            resolve_color("apply_lut", clip_path="C:/clip.mp4", lut_path="C:/LUTs/Film.cube")

            # Adjust color wheels
            resolve_color("adjust_wheels", lift={"r": 0.1, "g": 0.0, "b": -0.1})
        """
        from ..color_tools import (
            ColorCorrectionType,
            ColorSpaceTransform,
        )
        from ..color_tools import (
            adjust_color_wheels_impl as adjust_color_wheels,
        )
        from ..color_tools import (
            apply_grade_from_still_impl as apply_grade_from_still,
        )
        from ..color_tools import (
            apply_lut_impl as apply_lut,
        )
        from ..color_tools import (
            create_color_node_impl as create_color_node,
        )
        from ..color_tools import (
            get_stills_impl as get_stills,
        )
        from ..color_tools import (
            grab_still_impl as grab_still,
        )
        from ..color_tools import (
            set_color_space_impl as set_color_space,
        )

        # Map node_type string to enum
        node_type_map = {
            "primary": ColorCorrectionType.PRIMARY,
            "log": ColorCorrectionType.LOG,
            "hdr": ColorCorrectionType.HDR,
            "curves": ColorCorrectionType.CURVES,
            "qualifier": ColorCorrectionType.QUALIFIER,
            "window": ColorCorrectionType.WINDOW,
            "tracker": ColorCorrectionType.TRACKER,
            "blur": ColorCorrectionType.BLUR,
            "sharpen": ColorCorrectionType.SHARPEN,
            "noise_reduction": ColorCorrectionType.NOISE_REDUCTION,
            "resize": ColorCorrectionType.RESIZE,
            "lut": ColorCorrectionType.LUT,
        }

        if action == "create_node":
            node_type_enum = node_type_map.get(node_type.lower(), ColorCorrectionType.PRIMARY)
            return await create_color_node(app, node_type_enum, node_name, parent_node, timeline_name)

        elif action == "apply_lut":
            if not clip_path or not lut_path:
                return {
                    "status": "error",
                    "message": "clip_path and lut_path required for apply_lut",
                }
            return await apply_lut(app, lut_path, clip_path, None, timeline_name)

        elif action == "set_color_space":
            if not all([input_color_space, output_color_space]):
                return {
                    "status": "error",
                    "message": "input_color_space and output_color_space required",
                }
            input_transform = ColorSpaceTransform(
                input_color_space=input_color_space, output_color_space=input_color_space
            )
            output_transform = ColorSpaceTransform(
                input_color_space=output_color_space, output_color_space=output_color_space
            )
            return await set_color_space(app, input_transform, output_transform, clip_path, timeline_name)

        elif action == "adjust_wheels":
            return await adjust_color_wheels(app, lift, gamma, gain, offset, clip_path, node_name, timeline_name)

        elif action == "grab_still":
            return await grab_still(app, still_name or node_name, timeline_name)

        elif action == "get_stills":
            return await get_stills(app)

        elif action == "apply_grade_from_still":
            return await apply_grade_from_still(app, still_index, timeline_name)

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    logger.info("Registered resolve_color portmanteau tool")
