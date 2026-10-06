# davinci-resolve-mcp — Copilot instructions

9 portmanteau tools (`resolve_project/media/timeline/color/render/audio/
fairlight/subtitle/system`) drive a running DaVinci Resolve session.
Backend :10843 serves `/api/v1/*` (ASGI object `server:api_app`).
Check `resolve_system` → `host_status` before mutating; run `just lint`
and `just test` after tool changes; never commit `*.bak*` or `reports/`.
