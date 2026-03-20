# DaVinci Resolve MCP - Cursor IDE Startup Fix

## Issue
Server does not start in Cursor IDE when using the MCP configuration.

## Solution

The server has been updated with fixes for Cursor stdio compatibility. Use one of these configurations:

### Option 1: Direct Script (Recommended)

**`run_mcp.py` exists in the repo root.** Use either:

- **Project-level:** Copy `.cursor/mcp.json.example` to `.cursor/mcp.json` and set `cwd` to your repo path, or add the block below to your project's `.cursor/mcp.json`.
- **Global:** Add to `%APPDATA%\Cursor\mcp.json` (Windows) or `~/.cursor/mcp.json` (macOS/Linux). Use the `mcpServers` key.

Add to Cursor MCP config (`.cursor/mcp.json` or global mcp.json):

```json
{
  "mcp": {
    "davinci-resolve-mcp": {
      "command": "python",
      "args": ["run_mcp.py"],
      "cwd": "D:/Dev/repos/davinci-resolve-mcp",
      "env": {
        "PYTHONPATH": "D:/Dev/repos/davinci-resolve-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

Replace `D:/Dev/repos/davinci-resolve-mcp` with your actual path.

### Option 2: Module Format (Requires Package Installation)

If the package is installed (`pip install -e .`):

```json
{
  "mcp": {
    "davinci-resolve-mcp": {
      "command": "python",
      "args": ["-m", "davinci_resolve_mcp"],
      "cwd": "D:/Dev/repos/davinci-resolve-mcp",
      "env": {
        "PYTHONPATH": "D:/Dev/repos/davinci-resolve-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Option 3: CLI Command (Package Installed)

```json
{
  "mcp": {
    "davinci-resolve-mcp": {
      "command": "davinci-resolve-mcp",
      "args": ["mcp"]
    }
  }
}
```

## Fixes Applied (2025-02-03)

1. **`__main__.py`**: Added so `python -m davinci_resolve_mcp` works (Cursor may use this format)
2. **RichHandler removal**: RichHandler conflicts with MCP stdio (stdout reserved for JSON-RPC). Replaced with plain StreamHandler(stderr) in MCP mode
3. **Lazy initialization**: Server starts even if DaVinci Resolve is not running
4. **Async startup**: Uses `run_stdio_async()` for FastMCP 2.14.1+ compliance

## Testing

```powershell
cd D:\Dev\repos\davinci-resolve-mcp
python run_mcp.py
```

Or with module format:

```powershell
$env:PYTHONPATH = "D:\Dev\repos\davinci-resolve-mcp\src"
python -m davinci_resolve_mcp
```

The server should start and wait for MCP protocol messages on stdin. Press Ctrl+C to stop.

## Troubleshooting

1. **Import Errors**: Ensure `PYTHONPATH` includes the `src` directory
2. **DaVinci Resolve Not Running**: Server starts but tools report errors when used
3. **Module Not Found**: Use `run_mcp.py` (Option 1) or `pip install -e .`
4. **Cursor uses wrong command**: Cursor may run `python -m davinci_resolve_mcp`; `__main__.py` makes this work
5. **Logs**: Check `%APPDATA%\Cursor\logs\` and `MCP user-davinci-resolve-mcp.log` for errors

## Notes

- Server uses structured logging (JSON) to stderr only
- MCP protocol uses stdout for communication
- DaVinci Resolve connection is lazy - tools handle connection errors gracefully
