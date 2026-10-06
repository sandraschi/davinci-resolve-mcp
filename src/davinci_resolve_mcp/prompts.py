"""
MCP prompts and resources for DaVinci Resolve MCP.

Prompts give clients reusable, skill-grounded starting points. Resources expose
the skill registry and live server status over the MCP transport (the same data
the REST layer serves at /api/v1/skills and /api/v1/status).
"""

from typing import Any

SKILL_CATALOG: list[dict[str, Any]] = [
    {
        "name": "resolve_project",
        "uri": "skill://davinci-resolve/resolve_project",
        "operations": ["create", "open", "list", "get_settings", "update_settings"],
    },
    {
        "name": "resolve_media",
        "uri": "skill://davinci-resolve/resolve_media",
        "operations": ["import", "list", "create_folder", "get_metadata"],
    },
    {
        "name": "resolve_timeline",
        "uri": "skill://davinci-resolve/resolve_timeline",
        "operations": [
            "create",
            "info",
            "add_clip",
            "cut",
            "set_playhead",
            "add_marker",
            "get_markers",
            "delete_marker",
            "add_keyframe",
            "get_keyframes",
            "delete_keyframe",
            "set_clip_property",
        ],
    },
    {
        "name": "resolve_color",
        "uri": "skill://davinci-resolve/resolve_color",
        "operations": [
            "create_node",
            "apply_lut",
            "set_color_space",
            "adjust_wheels",
            "grab_still",
            "get_stills",
            "apply_grade_from_still",
        ],
    },
    {
        "name": "resolve_render",
        "uri": "skill://davinci-resolve/resolve_render",
        "operations": ["timeline", "presets", "with_preset", "job_status"],
    },
    {
        "name": "resolve_audio",
        "uri": "skill://davinci-resolve/resolve_audio",
        "operations": ["get_tracks", "add_effect", "adjust_levels", "normalize"],
    },
    {
        "name": "resolve_fairlight",
        "uri": "skill://davinci-resolve/resolve_fairlight",
        "operations": [
            "open_page",
            "get_tracks",
            "set_mute",
            "set_solo",
            "set_volume",
            "track_eq",
            "track_send",
            "get_buses",
            "track_automation",
        ],
    },
    {
        "name": "resolve_subtitle",
        "uri": "skill://davinci-resolve/resolve_subtitle",
        "operations": ["add", "get", "edit", "delete", "import_srt", "export_srt"],
    },
    {
        "name": "resolve_system",
        "uri": "skill://davinci-resolve/resolve_system",
        "operations": ["info", "status", "health", "help", "host_status", "host_launch"],
    },
]


def setup_prompts(app) -> None:
    """Register MCP prompt templates."""

    @app.prompt()
    def edit_plan(timeline_name: str, goal: str) -> str:
        """
        Build a step-by-step Resolve edit plan for a timeline and goal.

        ## Return Format
        Numbered plan referencing resolve_* tool actions.

        ## Examples
        edit_plan(timeline_name="Main Edit", goal="tighten interview pacing")
        """
        skills = ", ".join(s["name"] for s in SKILL_CATALOG)
        return (
            f"Draft an edit plan for timeline '{timeline_name}' with goal: {goal}.\n"
            f"Available skills: {skills}.\n"
            "Respond with numbered steps, each naming the exact tool action "
            "(e.g. resolve_timeline add_marker, resolve_color apply_lut, "
            "resolve_render with_preset) and its required arguments. "
            "Flag any step that needs a running Resolve session first."
        )

    @app.prompt()
    def color_recipe(look: str, clip: str = "current clip") -> str:
        """
        Build a color-grading recipe (nodes, LUT, wheels) for a described look.

        ## Return Format
        Ordered node/LUT/wheel steps for resolve_color actions.

        ## Examples
        color_recipe(look="warm filmic highlight rolloff")
        """
        return (
            f"Design a color recipe for {clip} with look: {look}.\n"
            "Respond with: 1) node tree (resolve_color create_node order), "
            "2) color space transform settings if needed, "
            "3) lift/gamma/gain starting values, 4) whether a LUT applies "
            "(resolve_color apply_lut with lut_path), 5) a gallery-still "
            "checkpoint (grab_still) before delivery."
        )

    @app.prompt()
    def render_checklist(destination: str, timeline_name: str = "current timeline") -> str:
        """
        Build a delivery checklist (preset, codec, queue, verify) for a destination.

        ## Return Format
        Preset choice + queue steps + verification for resolve_render actions.

        ## Examples
        render_checklist(destination="YouTube 4K")
        """
        return (
            f"Build a delivery checklist for {timeline_name} to {destination}.\n"
            "Respond with: 1) recommended preset (resolve_render presets), "
            "2) render settings to confirm (format, codec, resolution), "
            "3) queue steps (resolve_render with_preset), "
            "4) post-render verification (resolve_render job_status, watch the file)."
        )


def setup_resources(app) -> None:
    """Register MCP resources (skill registry + live status)."""

    @app.resource("skill://davinci-resolve/skills")
    def skills_resource() -> dict[str, Any]:
        """Static skill registry: the 9 resolve_* domains and their operations."""
        return {"skills": SKILL_CATALOG}

    @app.resource("resolve://status")
    def status_resource() -> dict[str, Any]:
        """Live server status snapshot for MCP clients."""
        manager = getattr(getattr(app, "state", None), "connection_manager", None)
        if manager is None:
            return {"status": "uninitialized", "message": "Connection manager not initialized"}
        try:
            get_status = getattr(manager, "get_status", None)
            if callable(get_status):
                result = get_status()
                if isinstance(result, dict):
                    return result
                return {"status": "ok", "detail": str(result)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "ok", "message": "Connection manager present"}
