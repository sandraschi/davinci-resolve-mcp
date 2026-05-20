# DaVinci Resolve MCP

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

[![CI/CD](https://github.com/sandraschi/davinci-resolve-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/davinci-resolve-mcp/actions)
[![Coverage](https://img.shields.io/badge/API_Coverage-~65%25-10B981?style=flat-square)](https://github.com/sandraschi/davinci-resolve-mcp)

> **[DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve)** is Blackmagic Designs post-production suite: editing, Fusion VFX, color grading, Fairlight audio, and delivery in one timeline.  
> Its used for everything from YouTube cuts to theatrical finish**this repo** automates a running session through Resolves **Python scripting API**, not a separate cloud service.

---

<p align="center">
  <strong>Drive DaVinci Resolve from your AI assistant</strong><br/>
  <sub>Model Context Protocol (MCP)  FastMCP 3.1.0+  Blackmagic scripting API</sub>
</p>

---

**Talk to Resolve in natural language**projects, media, timelines, color, Fairlight, renderwithout leaving Claude, Cursor, or another MCP client. Tools are grouped into a small **portmanteau** surface so the model stays focused; **sampling** and agentic helpers run when your host supports them.

|  |  |
|:--|:--|
| **For editors** | Fewer round-trips between the NLE and a separate chat; one server, many operations. |
| **For automators** | Same patterns as other MCP servers in the fleet: stdio, optional HTTP, optional `web_sota` dashboard (**10842** / **10843**). |
| **For operators** | Uses Resolves official **Python scripting** module on the same machineno mystery bridge. |

<p align="center">
  <a href="#quick-start"><strong>Quick start</strong></a>
  &nbsp;&nbsp;
  <a href="docs/INSTALL.md"><strong>Install</strong></a>
  &nbsp;&nbsp;
  <a href="docs/USAGE.md"><strong>Usage</strong></a>
  &nbsp;&nbsp;
  <a href="docs/DAVINCI_RESOLVE.md"><strong>Resolve setup</strong></a>
</p>

---

## Quick Start

```powershell
git clone https://github.com/sandraschi/davinci-resolve-mcp
cd davinci-resolve-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:

## Documentation

| | |
|--|--|
| **[docs/INSTALL.md](docs/INSTALL.md)** | Install paths, web UI (**10842** / **10843**), Zed, MCPB |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Diagram, tools, fleet standards links, repo layout |
| **[docs/DAVINCI_RESOLVE.md](docs/DAVINCI_RESOLVE.md)** | Scripting API, preferences, trademarks |
| **[docs/USAGE.md](docs/USAGE.md)** | Clients, env, config, examples, tool overview |
| **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** | Tests, Ruff, builds, contributing |
| **[docs/README.md](docs/README.md)** | Index of all of the above |

Fleet **2026** conventions (ports, FastMCP 3.1.0, packaging) are defined in **[mcp-central-docs](https://github.com/sandraschi/mcp-central-docs)**start at [`standards/AGENT_PROTOCOLS.md`](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/AGENT_PROTOCOLS.md). A compact mapping table lives in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#fleet-standards-2026).

---


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## License

MITsee [LICENSE](LICENSE).

DaVinci Resolve is a trademark of Blackmagic Design. This project is not affiliated with Blackmagic.

---

## Support

- **Issues:** [github.com/sandraschi/davinci-resolve-mcp/issues](https://github.com/sandraschi/davinci-resolve-mcp/issues)  
- **Docs site (if published):** [sandraschi.github.io/davinci-resolve-mcp](https://sandraschi.github.io/davinci-resolve-mcp)

## GitHub Topics

`da-vinci-resolve` `mcp-server` `fastmcp` `video-editing` `color-grading` `fairlight` `model-context-protocol` `python` `automation` `video-production` `post-production` `nle` `fusion-vfx` `blackmagic-design` `ai-automation` `mcp` `agentic-workflow` `resolve-api` `cli-tool` `beta`
