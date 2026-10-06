---
name: davinci-resolve
description: Drive a running DaVinci Resolve session (projects, media, timeline, color, render, Fairlight) via 9 resolve_* portmanteau tools
---

# DaVinci Resolve skill

- Tool surface: `resolve_project`, `resolve_media`, `resolve_timeline`,
  `resolve_color`, `resolve_render`, `resolve_audio`, `resolve_fairlight`,
  `resolve_subtitle`, `resolve_system` (READ-ONLY) — see `docs/TOOLS.md`.
- Recall: check `resolve_system` action `host_status` before any mutation;
  without a running Resolve every write fails.
- Save: after tool changes run `just lint` + `just test` and sync `docs/TOOLS.md`.
