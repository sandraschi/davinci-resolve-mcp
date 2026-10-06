# Configuration — davinci-resolve-mcp

All knobs, one place. Copy `.env.example` to `.env` for local overrides
(`.env` is gitignored; never commit secrets).

## Environment variables

| Var | Default | Purpose |
|-----|---------|---------|
| `RESOLVE_TOOL_MODE` | `portmanteau` | `portmanteau` (9 `resolve_*` tools) or `individual` (38 tools) |
| `MCP_TRANSPORT` | `stdio` | `stdio` (Claude Desktop/Cursor) or `http` |
| `MCP_HOST` / `MCP_PORT` | `127.0.0.1` / `10843` | HTTP transport bind |
| `HOST` / `PORT` | `127.0.0.1` / `10843` | Web dashboard backend bind |
| `WEB_PORT` | `10843` | Backend port injected by the fleet launcher |
| `VITE_PORT` | `10842` | Frontend dev port |
| `VITE_API_TARGET` | `http://127.0.0.1:10843` | API target for production preview |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Local LLM proxy target |
| `LM_STUDIO_URL` | `http://127.0.0.1:1234` | LM Studio probe target |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | unset | Cloud flags in `/llm/providers` (never key bytes; never in responses) |
| `RESOLVE_SCRIPT_API` | auto-detected | Override Resolve scripting support path |
| `RESOLVE_SCRIPT_LIB` | auto-detected | Override `fusionscript` library path |

## Ports (fleet registry)

Backend **10843**, frontend **10842** — adjacent pair, registered in
`mcp-central-docs/operations/WEBAPP_PORTS.md`. Never use 3000/5000/5173/8000/8080.

## Transports

- `just run` / `just mcp` — stdio for MCP clients.
- `just serve` — `uvicorn davinci_resolve_mcp.server:api_app` on 10843
  (the fleet `UvicornTarget`; `server:app` is the raw FastMCP object, not ASGI).
- `just web` — Typer CLI web entry (same backend).
- `just start` — HTTP MCP server on port 8000 (legacy; prefer `serve`).

## CORS

Explicit origins (`localhost:10842`, `127.0.0.1:10842`, Tauri schemes) plus an
`allow_origin_regex` covering Tailscale/LAN. The frontend calls same-origin
`/api/v1/*` (vite proxy); the absolute backend URL lives behind a Tauri gate
in `web_sota/src/lib/api.ts`.
