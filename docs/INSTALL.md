# Installation

Python **3.12+** is required (`pyproject.toml`). The package depends on **FastMCP 3.1+** and talks to Resolve on the **same machine** via the scripting API (see [DAVINCI_RESOLVE.md](DAVINCI_RESOLVE.md)).

## Prerequisites

- **[uv](https://docs.astral.sh/uv/)** (recommended) or another PEP 517 installer
- **DaVinci Resolve** 18+ with scripting enabled ([DAVINCI_RESOLVE.md](DAVINCI_RESOLVE.md))

## From the repo (development)

```text
git clone https://github.com/sandraschi/davinci-resolve-mcp
cd davinci-resolve-mcp
uv sync
uv run davinci-resolve-mcp mcp
```

Stdio MCP (Cursor, Claude Desktop, etc.) uses the `mcp` subcommand (see [USAGE.md](USAGE.md)).

## Run without cloning (`uvx`)

```text
uvx davinci-resolve-mcp mcp
```

(Package must be published to the index `uvx` uses.)

## PyPI

```text
pip install davinci-resolve-mcp
davinci-resolve-mcp mcp
```

Development extras:

```text
pip install "davinci-resolve-mcp[dev]"
```

## MCPB bundle

If you use `.mcpb` with Claude Desktop or another registry:

```text
mcp install davinci-resolve-mcp-0.2.0.mcpb
```

Or build from source: `python build_mcpb.py` (see repo root).

## Zed extension

```text
zed: install extension from https://github.com/sandraschi/davinci-resolve-mcp/zed-extension
```

Or build: `python -m scripts.build_zed` and install the zip from `dist/`.

## Web dashboard (`web_sota/`)

API **10843**, Vite **10842** (fleet range 10700–10800; see [WEBAPP_PORTS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/operations/WEBAPP_PORTS.md)).

1. Start Resolve with scripting enabled.
2. From repo root, start the Python API (example):

   ```text
   uv run davinci-resolve-mcp web --host 127.0.0.1 --port 10843
   ```

3. In `web_sota/`, run `start.ps1` or `start.bat` so the Vite dev server proxies `/api` to **10843**.
4. Open `http://127.0.0.1:10842` (or the host shown in the terminal).

## System requirements (typical)

| Resource | Notes |
|----------|--------|
| OS | Windows 10+, macOS 10.15+, recent Linux |
| RAM | 8 GB minimum; 16 GB+ comfortable with Resolve |
| Disk | A few GB for the app; media is separate |

Resolve itself sets the real bar for GPU and storage.
