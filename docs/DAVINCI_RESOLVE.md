# DaVinci Resolve

This MCP server drives **Blackmagic DaVinci Resolve** through the **official scripting API** (Python module `DaVinciResolveScript`, `scriptapp("Resolve")`). It is **not** a generic REST bridge to a random port unless you add one yourself.

## What you need

| Requirement | Notes |
|-------------|--------|
| **Resolve installed** | Studio or free; version **18+** is the usual target |
| **Same machine** | The Python process must load Resolve’s scripting module; typical setup is Resolve + MCP on one workstation |
| **Resolve running** | Start Resolve before operations that need the API |
| **Scripting enabled** | **Preferences → General → External scripting using** → choose **Local** (wording varies slightly by version). Without this, imports or `scriptapp` fail |

## How connection works

1. The server checks the environment and imports `DaVinciResolveScript`.
2. It obtains the Resolve app object via `scriptapp("Resolve")`.
3. Project/media/timeline operations go through that API.

If Resolve is closed, wrong build, or scripting is off, tools return connection errors—see logs and the web dashboard status page.

## Paths and environment

The repo’s `connection/` and `config` code try to locate Resolve install and API paths on Windows/macOS/Linux. If you use a non-default install, set the variables your deployment documents (see `config.py` and [USAGE.md](USAGE.md) for `RESOLVE_*` / `PYTHONPATH` patterns).

## Trademarks

DaVinci Resolve is a trademark of **Blackmagic Design**. This project is **not** affiliated with Blackmagic; see the root [README](../README.md#license).

## Further reading

- Blackmagic scripting documentation shipped with Resolve (Help / developer docs)  
- [ARCHITECTURE.md](ARCHITECTURE.md) — how this repo wraps the API  
- [INSTALL.md](INSTALL.md) — install and web UI ports  
