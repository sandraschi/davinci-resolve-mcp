# DaVinci Resolve MCP

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/sandraschi/davinci-resolve-mcp)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1+-green.svg)](https://github.com/jlowin/fastmcp)
[![DaVinci Resolve](https://img.shields.io/badge/DaVinci%20Resolve-18+-red.svg)](https://www.blackmagicdesign.com/products/davinciresolve)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/sandraschi/davinci-resolve-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/davinci-resolve-mcp/actions)

> **[DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve)** is Blackmagic Design’s post-production suite: editing, Fusion VFX, color grading, Fairlight audio, and delivery in one timeline.  
> It’s used for everything from YouTube cuts to theatrical finish—**this repo** automates a running session through Resolve’s **Python scripting API**, not a separate cloud service.

---

<p align="center">
  <strong>Drive DaVinci Resolve from your AI assistant</strong><br/>
  <sub>Model Context Protocol (MCP) · FastMCP 3.1+ · Blackmagic scripting API</sub>
</p>

---

**Talk to Resolve in natural language**—projects, media, timelines, color, Fairlight, render—without leaving Claude, Cursor, or another MCP client. Tools are grouped into a small **portmanteau** surface so the model stays focused; **sampling** and agentic helpers run when your host supports them.

|  |  |
|:--|:--|
| **For editors** | Fewer round-trips between the NLE and a separate chat; one server, many operations. |
| **For automators** | Same patterns as other MCP servers in the fleet: stdio, optional HTTP, optional `web_sota` dashboard (**10842** / **10843**). |
| **For operators** | Uses Resolve’s official **Python scripting** module on the same machine—no mystery bridge. |

<p align="center">
  <a href="#quick-start"><strong>Quick start</strong></a>
  &nbsp;·&nbsp;
  <a href="docs/INSTALL.md"><strong>Install</strong></a>
  &nbsp;·&nbsp;
  <a href="docs/USAGE.md"><strong>Usage</strong></a>
  &nbsp;·&nbsp;
  <a href="docs/DAVINCI_RESOLVE.md"><strong>Resolve setup</strong></a>
</p>

---

## Quick start

1. Install **DaVinci Resolve** and enable **external scripting** (local).  
2. Clone the repo and install with **uv** (see [docs/INSTALL.md](docs/INSTALL.md)).  
3. Run the MCP server (stdio for IDEs):

   ```text
   uv run davinci-resolve-mcp mcp
   ```

4. Point your MCP client at that command (examples in [docs/USAGE.md](docs/USAGE.md)).

Resolve must be running for most operations. Same-machine scripting is the normal setup—see [docs/DAVINCI_RESOLVE.md](docs/DAVINCI_RESOLVE.md).

---

## Documentation

| | |
|--|--|
| **[docs/INSTALL.md](docs/INSTALL.md)** | Install paths, web UI (**10842** / **10843**), Zed, MCPB |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Diagram, tools, fleet standards links, repo layout |
| **[docs/DAVINCI_RESOLVE.md](docs/DAVINCI_RESOLVE.md)** | Scripting API, preferences, trademarks |
| **[docs/USAGE.md](docs/USAGE.md)** | Clients, env, config, examples, tool overview |
| **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** | Tests, Ruff, builds, contributing |
| **[docs/README.md](docs/README.md)** | Index of all of the above |

Fleet **2026** conventions (ports, FastMCP 3.1, packaging) are defined in **[mcp-central-docs](https://github.com/sandraschi/mcp-central-docs)**—start at [`standards/AGENT_PROTOCOLS.md`](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/AGENT_PROTOCOLS.md). A compact mapping table lives in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#fleet-standards-2026).

---

## License

MIT—see [LICENSE](LICENSE).

DaVinci Resolve is a trademark of Blackmagic Design. This project is not affiliated with Blackmagic.

---

## Support

- **Issues:** [github.com/sandraschi/davinci-resolve-mcp/issues](https://github.com/sandraschi/davinci-resolve-mcp/issues)  
- **Docs site (if published):** [sandraschi.github.io/davinci-resolve-mcp](https://sandraschi.github.io/davinci-resolve-mcp)  
