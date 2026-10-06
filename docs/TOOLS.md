# Tools — davinci-resolve-mcp

Default mode (`RESOLVE_TOOL_MODE=portmanteau`): 9 consolidated tools. Every tool
returns `{success|status, message, ...data}` dialogic dicts. Annotations:
`resolve_system` is READ-ONLY; the other eight are MUTATING.

| Tool | Actions |
|------|---------|
| `resolve_project` | create, open, list, get_settings, update_settings |
| `resolve_media` | import, list, create_folder, get_metadata |
| `resolve_timeline` | create, info, add_clip, cut, set_playhead, add_marker, get_markers, delete_marker, add_keyframe, get_keyframes, delete_keyframe, set_clip_property |
| `resolve_color` | create_node, apply_lut, set_color_space, adjust_wheels, grab_still, get_stills, apply_grade_from_still |
| `resolve_render` | timeline, presets, with_preset, job_status |
| `resolve_audio` | get_tracks, add_effect, adjust_levels, normalize |
| `resolve_fairlight` | open_page, get_tracks, set_mute, set_solo, set_volume, track_eq, track_send, get_buses, track_automation |
| `resolve_subtitle` | add, get, edit, delete, import_srt, export_srt |
| `resolve_system` | info, status, health, help, host_status, host_launch |

Plus: `help` (multi-level docs), `get_status` (connection state), agentic
workflow tools in `agentic.py` (accept `ctx: Context`), and a confirm-gated
`shutdown` tool.

Set `RESOLVE_TOOL_MODE=individual` for 38 single-purpose tools
(`tools/*_tools.py`), each with `_impl()` shared logic.

## REST (prefix `/api/v1`, backend :10843)

`health`, `status`, `diagnostics`, `logs`, `capabilities`, `skills`,
`resolve-info`, `projects`, `timeline`, `fairlight/*`, `host-status`,
`host/launch`, `shutdown` (POST), `llm/models`, `llm/load` (POST),
`llm/generate` (POST), `llm/discover`, `llm/providers`, `llm/onboarding`.

Full parameter reference: `llms-full.txt` + `docs/USAGE.md`.
