# AGENTS.md — DaVinci Resolve MCP

## Project Identity

- **Name**: davinci-resolve-mcp
- **Version**: 0.3.0-beta
- **Purpose**: FastMCP 3.1+ server that exposes a running DaVinci Resolve session to AI agents via the Model Context Protocol
- **Language**: Python 3.12+ (backend), TypeScript/React (webapp)
- **Ports**: 10842 (webapp frontend), 10843 (API backend)
- **License**: MIT

## Architecture

```
src/davinci_resolve_mcp/
├── main.py              # Typer CLI entry (start, mcp, web, check, run-script, render, import-media, open-project)
├── server.py            # FastMCP 3.1+ app, init, tool registration
├── transport.py          # Dual transport (stdio/HTTP/SSE)
├── config.py             # Pydantic settings models
├── agentic.py            # Agentic workflow tools (LLM sampling)
├── connection/
│   ├── manager.py        # ResolveConnectionManager (async retry, health, pool)
│   ├── environment.py    # Cross-platform DVR install detection
│   └── host_app_probe.py # 4-state host lifecycle probe
├── tools/
│   ├── project_tools.py  # Project CRUD
│   ├── media_tools.py    # Media import/pool/folders
│   ├── timeline_tools.py # Timeline + markers + keyframes
│   ├── color_tools.py    # Color grading + gallery stills
│   ├── render_tools.py   # Render queue/presets/jobs
│   ├── audio_tools.py    # Audio tracks/effects/levels
│   ├── fairlight_tools.py # Fairlight page + EQ + sends + buses + automation
│   ├── subtitle_tools.py # Subtitles + SRT import/export
│   ├── help_tool.py      # Multi-level help system
│   └── portmanteau/      # 9 consolidated tools (resolve_*)
├── models/               # Pydantic v2 models
├── api/routes.py         # FastAPI routes for webapp
└── utils/                # Exceptions, error handling, validators
web_sota/src/
├── App.tsx               # React Router v6
├── pages/                # 12 page components
└── components/           # Layout + UI primitives
```

## Portmanteau Tools (default mode)

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

## Key Rules for Agents

### Tool Implementation Pattern
- Each tools file has `_impl()` functions (shared logic) and `register_tools(app)` (FastMCP decorators)
- `_impl` functions use `app.state.connection_manager` for Resolve access
- `register_tools` functions use `with ResolveConnectionManager() as resolve:` context manager
- Portmanteau tools import and delegate to `_impl` functions
- Tool mode controlled by `RESOLVE_TOOL_MODE` env var (default: `portmanteau`)

### Connection Flow
1. `ResolveEnvironment.setup_environment_variables()` sets `RESOLVE_SCRIPT_API`, `RESOLVE_SCRIPT_LIB`, `PYTHONPATH`
2. `ResolveConnectionManager.connect()` imports `DaVinciResolveScript`, calls `scriptapp("Resolve")`
3. All tools require Resolve running with scripting API enabled

### File Patterns
- New tools: create `tools/<name>_tools.py` with `_impl` functions + `register_tools(app)`
- New portmanteau: create `tools/portmanteau/<name>.py` with `setup_<name>_portmanteau(app)`
- Register in `tools/portmanteau/__init__.py` and `server.py:register_tools()`
- New pages: create `web_sota/src/pages/<name>.tsx`, add route in `App.tsx`, add nav in `sidebar.tsx`

### Linting & Quality
- Python: `just lint` (ruff) or `just fix` (ruff + format)
- Webapp: `just lint` runs Biome CI; `just fix` runs Biome check --write
- Run `just test` before committing
- No console.log in webapp (Biome enforces this)
- No f-strings in docstrings
- Use `Annotated[T, Field(description="...")]` for all tool parameters

### CLI Commands
```
just run              # MCP stdio (default)
just mcp              # MCP stdio explicit
just web              # Webapp API on 10843
just start            # HTTP MCP server
just check            # Verify Resolve env
just open <name>      # Open/create project
just render <t> <out> # Render timeline
just run-script <f>   # Execute Resolve Python script
```

### Dependencies
- Python: `uv sync` or `just install`
- Webapp: `npm install` in `web_sota/`
- Dev deps: `uv sync --all-extras` or `just install-dev`

### Testing
- Unit tests: `tests/unit/` — mock-based, no Resolve needed
- Integration tests: `tests/integration/` — need running Resolve
- New tests: `tests/unit/tools/test_timeline_extended.py`, `tests/unit/tools/test_subtitle_tools.py`
