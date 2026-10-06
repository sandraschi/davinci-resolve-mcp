# Troubleshooting — davinci-resolve-mcp

## "Connection manager not initialized" / status error

Resolve is not running or scripting is disabled.

1. Start DaVinci Resolve and open a project.
2. Preferences → System → General → "External scripting using" → Local.
3. `just check` — must report the scripting paths found.
4. `GET /api/v1/host-status` shows the 4-state probe
   (missing → uninstalled → installed-stopped → running).

## Dashboard shows disconnected

1. Backend up? `GET /api/v1/health` on :10843 must return `{"status":"ok"}`.
2. Port zombie? `Get-NetTCPConnection -LocalPort 10843`; kill the owner,
   or restart via `start.ps1` (it clears the port first).
3. Wrong ASGI target? Serve `davinci_resolve_mcp.server:api_app`, never
   `server:app` (raw FastMCP object — uvicorn cannot serve it).

## Chat: "No local LLM detected"

Install Ollama and pull a model (`ollama pull llama3.1:8b`). The Chat page
proxies through the backend (`/llm/generate`); keys never leave the server.

## Biome `ci` fails with schema mismatch

Pin and schema must agree: `@biomejs/biome` devDep `^2.5.0` with
`$schema .../schemas/2.5.0/schema.json`. After editing TS, run
`npx @biomejs/biome check --write src` (writes CRLF per config).

## Tests red / hanging

- `tests/unit/` (except `connection/`) run without Resolve.
- `tests/unit/connection/` needs Resolve running; without it the suite hangs
  to `--timeout`. Start Resolve first, or ignore that directory.
- `tests/integration/` always needs a running Resolve with scripting enabled.

## Render jobs stuck

Check `resolve_render` action `job_status`, then the Render Queue page.
Resolve must be in the Deliver page codec state the preset expects.
