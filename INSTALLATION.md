# Installation Guide for DaVinci Resolve MCP

This guide provides detailed instructions for installing and setting up the DaVinci Resolve MCP package.

## Prerequisites

Before you begin, ensure you have the following installed:

- **DaVinci Resolve 18+** (Free or Studio version)
- **Python 3.8 or later**
- **pip** (Python package manager)
- **Git** (for development installations)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

1. Open a terminal or command prompt.

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package using pip:
   ```bash
   pip install davinci-resolve-mcp
   ```

### Method 2: Install from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/davinci-resolve-mcp.git
   cd davinci-resolve-mcp
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Configuration

### DaVinci Resolve Setup

1. Launch DaVinci Resolve.
2. Go to `DaVinci Resolve` > `Preferences` > `System` > `General`.
3. Under "External Scripting Using", select "Local" and "Network" options.
4. Note the port number (default is usually 11046).

### Environment Variables

Set the following environment variables as needed:

```bash
# DaVinci Resolve connection settings
export RESOLVE_HOST=localhost
export RESOLVE_PORT=11046

# Optional: Enable debug logging
export DAVINCI_RESOLVE_MCP_DEBUG=1

# Optional: Set log file location
export DAVINCI_RESOLVE_MCP_LOG_FILE=resolve_mcp.log
```

## Verifying the Installation

To verify that the installation was successful, run:

```bash
davinci-resolve-mcp --version
```

You should see the installed version number displayed.

## Integration with MCP Clients

### Claude Desktop

1. Open Claude Desktop.
2. Go to Settings > MCP Configuration.
3. Add: `"davinci-resolve": { "command": "davinci-resolve-mcp", "args": ["mcp"] }`
4. Restart Claude Desktop.

### Cursor IDE

Add to Cursor settings (`mcp` key):

```json
{
  "mcp": {
    "davinci-resolve-mcp": {
      "command": "python",
      "args": ["run_mcp.py"],
      "cwd": "D:/path/to/davinci-resolve-mcp",
      "env": {
        "PYTHONPATH": "D:/path/to/davinci-resolve-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

See [CURSOR_FIX.md](CURSOR_FIX.md) for full setup and troubleshooting.

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure DaVinci Resolve is running.
   - Verify the port number in DaVinci Resolve preferences matches your configuration.
   - Check your firewall settings to ensure it's not blocking the connection.

2. **Module Not Found**
   - Ensure you've activated the virtual environment where you installed the package.
   - Try reinstalling the package with `pip install --force-reinstall davinci-resolve-mcp`.

3. **Permission Denied**
   - On Linux/macOS, you may need to run with `sudo` or adjust file permissions.
   - Ensure your user has the necessary permissions to access DaVinci Resolve's scripting interface.

### Getting Help

If you encounter any issues, please:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md) for known issues and solutions.
2. Search the [GitHub Issues](https://github.com/yourusername/davinci-resolve-mcp/issues) for similar problems.
3. If your issue isn't resolved, open a new issue with detailed information about your setup and the problem you're experiencing.

## Uninstallation

To uninstall the package:

```bash
pip uninstall davinci-resolve-mcp
```

If you installed from source, you can also remove the cloned repository directory.

## Next Steps

- Check out the [Usage Examples](USAGE_EXAMPLES.md) to see what you can do with DaVinci Resolve MCP.
- Explore the [API Reference](API_REFERENCE.md) for detailed documentation on all available functions and classes.
- Join our community forum to connect with other users and share your projects.
