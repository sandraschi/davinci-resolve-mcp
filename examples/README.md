# DaVinci Resolve MCP - Configuration Examples

This directory contains example configurations for common DaVinci Resolve MCP setups.

## Files

### `claude_desktop_config.json`
Basic Claude Desktop configuration for MCP server integration.

**Usage:**
- Copy this file to your Claude Desktop configuration directory
- On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

### `advanced_config.json`
Advanced configuration with explicit paths and environment variables.

**Usage:**
- Use this when you need custom paths or environment settings
- Replace the placeholder paths with your actual installation paths
- Particularly useful for development or custom installations

## Common Configurations

### Cursor IDE Setup
Add to Cursor settings (`mcp` key in settings.json):

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

See `CURSOR_FIX.md` in the project root for full Cursor setup and troubleshooting.

### Development Setup
For developers working on the MCP server:

```json
{
  "mcpServers": {
    "davinci-resolve-dev": {
      "command": "python",
      "args": ["run_mcp.py"],
      "cwd": "/path/to/davinci-resolve-mcp",
      "env": {
        "PYTHONPATH": "/path/to/davinci-resolve-mcp/src",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Production Setup
For production use with DaVinci Resolve:

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "davinci-resolve-mcp",
      "args": ["mcp"],
      "env": {
        "LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

### Custom Resolve Location
If DaVinci Resolve is installed in a non-standard location:

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "davinci-resolve-mcp",
      "args": ["mcp"],
      "env": {
        "RESOLVE_SCRIPT_API_PATH": "C:\\Custom\\DaVinci\\Resolve\\Path\\Support\\Developer\\Scripting"
      }
    }
  }
}
```

## Troubleshooting

### Extension Not Loading
If the MCP server doesn't load:
1. Check that `davinci-resolve-mcp` is in your PATH
2. Verify DaVinci Resolve is installed and running
3. Check the Claude Desktop logs for error messages

### Path Issues
If you encounter path-related errors:
1. Use absolute paths in the configuration
2. Ensure proper escaping of backslashes on Windows
3. Verify the `RESOLVE_SCRIPT_API_PATH` points to the correct location

### Permission Issues
If you get permission errors:
1. Ensure Claude Desktop has access to the DaVinci Resolve installation
2. Check that the Scripting API is enabled in DaVinci Resolve preferences
3. Run Claude Desktop as administrator (Windows) or with appropriate permissions
