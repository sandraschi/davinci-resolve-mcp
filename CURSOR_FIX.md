# DaVinci Resolve MCP - Cursor IDE Startup Fix

## Issue
Server does not start in Cursor IDE when using the MCP configuration.

## Solution

The server has been updated to use structured logging and proper FastMCP 2.14.1 async startup. Use one of these configurations:

### Option 1: Direct Script (Recommended for Cursor)

Add to your Cursor MCP settings (`.cursor/mcp.json` or Cursor settings):

```json
{
  "mcpServers": {
    "davinci-resolve-mcp": {
      "command": "python",
      "args": ["run_mcp.py"],
      "cwd": "${workspaceFolder}/davinci-resolve-mcp",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/davinci-resolve-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Option 2: Module Format (Requires Package Installation)

If the package is installed (`pip install -e .`):

```json
{
  "mcpServers": {
    "davinci-resolve-mcp": {
      "command": "python",
      "args": ["-m", "davinci_resolve_mcp.main", "mcp"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/davinci-resolve-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Changes Made

1. **Structured Logging**: Replaced standard logging with `structlog` (JSON to stderr only)
2. **Lazy Initialization**: Server can start even if DaVinci Resolve is not running
3. **Async Startup**: Uses `run_stdio_async()` for FastMCP 2.14.1 compliance
4. **Error Handling**: Initialization errors are logged but don't prevent server startup

## Testing

Test the server startup:

```powershell
cd D:\Dev\repos\davinci-resolve-mcp
python run_mcp.py
```

The server should start and wait for MCP protocol messages on stdin. Press Ctrl+C to stop.

## Troubleshooting

1. **Import Errors**: Ensure `PYTHONPATH` includes the `src` directory
2. **DaVinci Resolve Not Running**: Server will start but tools will report errors when used
3. **Module Not Found**: Use `run_mcp.py` script instead of module format
4. **Structured Logs**: Check stderr for JSON-formatted log messages

## Notes

- Server uses structured logging (JSON) to stderr only
- MCP protocol uses stdout for communication
- DaVinci Resolve connection is lazy - tools handle connection errors gracefully
- Server lifespan manages startup/shutdown lifecycle
