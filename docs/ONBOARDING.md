# Onboarding — davinci-resolve-mcp

First-timer path from zero to a working Resolve automation session.

## 1. What you need

- **DaVinci Resolve 18+** (Free or Studio) installed on this machine.
  Resolve is the wrappee: every tool drives a *running* Resolve session through
  Blackmagic's official Python scripting API. No Resolve, no joy.
- **External scripting enabled** in Resolve: Preferences → System → General →
  check "External scripting using" → Local (or Network).
- **Python 3.12+** with `uv`, **Node 20+** for the dashboard.
- Optional: **Ollama** for the Chat page (`ollama pull llama3.1:8b`).

## 2. Sanity check (5 minutes)

```powershell
just bootstrap        # deps + pre-commit hooks + web frontend
just check            # verifies Resolve install + scripting env
just serve            # backend on http://127.0.0.1:10843
# in another shell:
Invoke-WebRequest http://127.0.0.1:10843/api/v1/health -UseBasicParsing
```

Open Resolve, open any project, then in Claude Desktop / Cursor ask:
"List my Resolve projects" (tool: `resolve_project`, action `list`).

## 3. Common pitfalls

- **"Connection manager not initialized"** — Resolve is not running, or external
  scripting is off. See `docs/TROUBLESHOOTING.md`.
- **Dashboard shows disconnected** — backend serves 10843, frontend dev-serves
  10842 via `start.ps1`. Check `GET /api/v1/host-status` for the 4-state probe.
- **Chat says no LLM** — install Ollama; the Chat page only proxies to local models.

## 4. Money / accounts

None. Resolve Free works for most tools; Studio unlocks some effects.
No cloud account is required for any default flow.

## 5. Webapp note

The dashboard shows live backend state only. Until onboarding succeeds (Resolve
reachable + optional Ollama), Chat/Render actions return explicit errors —
there are no demo KPIs pretending otherwise.
