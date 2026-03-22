# Usage

## MCP client (stdio)

Default CLI entry (no args) runs MCP stdio—see `main.py`.

Explicit:

```text
davinci-resolve-mcp mcp
```

### Claude Desktop

Add to `claude_desktop_config.json` (adjust paths):

```json
"mcpServers": {
  "davinci-resolve-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/davinci-resolve-mcp", "run", "davinci-resolve-mcp", "mcp"]
  }
}
```

### Generic MCP JSON

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "davinci-resolve-mcp",
      "args": ["mcp"]
    }
  }
}
```

If something in your IDE fails to parse argv, see `CURSOR_FIX.md` in the repo root (if present).

## Environment variables

| Variable | Purpose |
|----------|---------|
| `RESOLVE_HOST` / `RESOLVE_PORT` / `RESOLVE_TIMEOUT` | Connection hints (see `config`) |
| `HOST` / `PORT` | HTTP API / some transports |
| `RESOLVE_TOOL_MODE` | `portmanteau` (default) or `individual` |
| `CONFIG_PATH` | Optional YAML/JSON config file |
| `PYTHONPATH` | If you run from source without install |

Example:

```bash
RESOLVE_TOOL_MODE=portmanteau
```

(use your shell’s syntax; on Windows PowerShell use `$env:RESOLVE_TOOL_MODE = "portmanteau"`)

## Config file

Optional `config.yaml` / `config.json` (path via `CONFIG_PATH`):

```yaml
davinci_resolve:
  host: localhost
  port: 8080
  timeout: 30
  auto_start: false

server:
  host: 127.0.0.1
  port: 8000
  debug: false
  log_level: INFO

tools:
  mode: portmanteau
  max_concurrent: 4
  request_timeout: 120

logging:
  level: INFO
  format: json
  file: logs/davinci_resolve_mcp.log
```

## Python API (advanced)

```python
from davinci_resolve_mcp import DaVinciResolveMCP

server = DaVinciResolveMCP()
server.start()
```

CLI alternative:

```text
davinci-resolve-mcp start --host 127.0.0.1 --port 8000
```

Prefer `mcp` or `web` subcommands for normal MCP / dashboard flows.

## Example prompts (agent)

**Project**

```text
Create a new 4K project for vacation footage.
```

**Media**

```text
Import MP4s from my Desktop into the media pool.
```

**Grade**

```text
Apply a cinematic LUT to the selected clips.
```

## Agentic tools (sampling)

When the host supports sampling, tools such as `agentic_resolve_workflow` can plan steps. Example:

```python
result = await agentic_resolve_workflow(
    workflow_prompt="Create a new 4K project and import media from Desktop",
    available_tools=["resolve_project", "resolve_media"],
    max_iterations=5,
)
```

See `agentic.py` for `intelligent_video_processing` and `conversational_resolve_assistant`.

## Tool reference (sketch)

Portmanteau tools take an `operation` (and action-specific args). Illustrative patterns:

**resolve_project** — `create`, `open`, `info`, …  
**resolve_media** — `import`, `search`, folders, …  
**resolve_timeline** — `create`, `add_clip`, edits, …  
**resolve_color** — LUTs, nodes, primaries, …  
**resolve_audio** — levels, effects, sync, …  
**resolve_render** — jobs, queue, export, …  
**resolve_system** — `info`, `health`, `help`, …  
**resolve_fairlight** — Fairlight page, track mute/solo/volume, …  

Exact operations match the implementation under `tools/portmanteau/`. Use **`resolve_system`** with `help` or the built-in help tool for topic lists.

## Web app

See [INSTALL.md](INSTALL.md#web-dashboard-web_sota).
