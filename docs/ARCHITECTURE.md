# Architecture

## Fleet standards (2026)

This repo follows **[MCP Central Docs](https://github.com/sandraschi/mcp-central-docs)**. Local clone: `D:\Dev\repos\mcp-central-docs\`.

| Topic | Document |
|-------|----------|
| Hub | [AGENT_PROTOCOLS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/AGENT_PROTOCOLS.md) |
| FastMCP 3.1+ (sampling, prompts, skills) | [SOTA_REQUIREMENTS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/SOTA_REQUIREMENTS.md) |
| Portmanteau tools & docstrings | [TOOL_DESIGN_STANDARDS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/TOOL_DESIGN_STANDARDS.md) |
| Webapp | [WEBAPP_STANDARDS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/WEBAPP_STANDARDS.md) |
| Ports (**10842** / **10843** here) | [WEBAPP_PORTS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/operations/WEBAPP_PORTS.md) |
| Packaging (uv, `llms.txt`, Glama, MCPB) | [PACKAGING_STANDARDS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/PACKAGING_STANDARDS.md) |
| Ruff, pre-commit | [CODE_QUALITY_STANDARDS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/CODE_QUALITY_STANDARDS.md) |

## High-level diagram

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP client    │───▶│  FastMCP 3.1+    │───▶│ DaVinci Resolve │
│   (LLM host)    │    │  Server          │    │  scripting API  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Portmanteau      │
                       │ tools (+ agentic)│
                       └──────────────────┘
```

- **STDIO / HTTP**: MCP transport is configured via CLI and env (see `transport.py`, [USAGE.md](USAGE.md)).
- **HTTP API**: `FastAPI` app (`api_app`) powers the optional web UI; not a substitute for the MCP stream in the IDE.

## Tools (portmanteau mode, default)

Roughly **eight** consolidated tools (plus help / agentic registrations depending on mode):

| Tool | Role |
|------|------|
| `resolve_project` | Projects |
| `resolve_media` | Media pool |
| `resolve_timeline` | Timeline edits |
| `resolve_color` | Grading |
| `resolve_audio` | Audio |
| `resolve_render` | Deliverables |
| `resolve_system` | Status, health, help |
| `resolve_fairlight` | Fairlight page / timeline audio |

Set `RESOLVE_TOOL_MODE=individual` for the legacy surface (many small tools).

## Responses

Tools return **dicts** with fields like `success`, `message`, and operation-specific data. Errors should include enough context to retry or fix (connection, Resolve state, bad args).

## Sampling and agentic helpers

Agent-style tools use **MCP sampling** (`Context.sample` and related APIs) when the host supports it. Details: [SOTA_REQUIREMENTS §2](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/SOTA_REQUIREMENTS.md). Fallback behavior applies when sampling is unavailable.

## Repository layout (abbreviated)

```text
src/davinci_resolve_mcp/
  server.py          # FastMCP app, lifespan, core tools
  agentic.py         # Sampling-oriented workflows
  api/               # FastAPI routes for the web UI
  connection/        # Resolve environment & connection manager
  tools/             # Portmanteau + legacy individual tools
web_sota/            # Vite dashboard
```

## Related

- [DAVINCI_RESOLVE.md](DAVINCI_RESOLVE.md) — Resolve scripting and machine layout  
- [USAGE.md](USAGE.md) — Clients, env, examples  
