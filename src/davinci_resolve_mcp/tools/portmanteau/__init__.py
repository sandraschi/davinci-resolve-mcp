"""
DaVinci Resolve MCP Portmanteau Tools.

Consolidated tool interfaces following FastMCP 2.13+ best practices.
Reduces 26 individual tools to 7 portmanteau tools.
"""
from .project import setup_project_portmanteau
from .media import setup_media_portmanteau
from .timeline import setup_timeline_portmanteau
from .color import setup_color_portmanteau
from .render import setup_render_portmanteau
from .audio import setup_audio_portmanteau
from .system import setup_system_portmanteau


def setup_all_portmanteau_tools(app):
    """Register all portmanteau tools with the FastMCP app."""
    setup_project_portmanteau(app)
    setup_media_portmanteau(app)
    setup_timeline_portmanteau(app)
    setup_color_portmanteau(app)
    setup_render_portmanteau(app)
    setup_audio_portmanteau(app)
    setup_system_portmanteau(app)


__all__ = [
    "setup_all_portmanteau_tools",
    "setup_project_portmanteau",
    "setup_media_portmanteau",
    "setup_timeline_portmanteau",
    "setup_color_portmanteau",
    "setup_render_portmanteau",
    "setup_audio_portmanteau",
    "setup_system_portmanteau",
]

