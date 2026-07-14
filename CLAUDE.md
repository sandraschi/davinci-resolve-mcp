# CLAUDE.md — DaVinci Resolve MCP

## Quick Start
```powershell
just run              # MCP stdio (Claude Desktop)
just web              # Webapp API on 10843
just lint             # Ruff + Biome
just test             # Unit tests
```

## Ports
- Frontend: 10842 (Vite dev)
- Backend: 10843 (FastAPI)

## Architecture
```
CLI (main.py) → Server (server.py) → Tools (_tools.py) → Connection (manager.py) → DaVinciResolveScript
```
9 portmanteau tools (default) or 38 individual tools. Connection via Resolve Scripting API (COM interop).

## Portmanteau Tools

| Tool | Key Actions | Annotation |
|------|-------------|------------|
| `resolve_project` | create, open, list, get_settings, update_settings | MUTATING |
| `resolve_media` | import, list, create_folder, get_metadata | MUTATING |
| `resolve_timeline` | create, info, add_clip, cut, playhead, markers, keyframes | MUTATING |
| `resolve_color` | create_node, apply_lut, cst, wheels, stills | MUTATING |
| `resolve_render` | timeline, presets, with_preset, job_status | MUTATING |
| `resolve_audio` | get_tracks, add_effect, adjust_levels, normalize | MUTATING |
| `resolve_fairlight` | open_page, get_tracks, mute/solo/volume, eq, sends, buses, automation | MUTATING |
| `resolve_subtitle` | add, get, edit, delete, import_srt, export_srt | MUTATING |
| `resolve_system` | info, status, health, help, host_status, host_launch | READ_ONLY |

## Linting
- Python: `ruff` (E/F/W/I/B/S/UP/RUF, line length 120)
- Webapp: `biome` (CI mode, no console.log)
- No bare `except: pass` — log exceptions
- No `print()` in prod Python — use `logger`
