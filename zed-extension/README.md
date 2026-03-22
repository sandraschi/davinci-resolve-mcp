# DaVinci Resolve MCP - Zed Extension

DaVinci Resolve MCP packaged as a Zed extension: control Resolve from the editor via MCP.

## Features

- **Natural Language Control**: Control DaVinci Resolve through conversational AI commands
- **FastMCP 3.1+**: MCP tools; sampling where the client supports it (see mcp-central-docs `standards/SOTA_REQUIREMENTS.md`)
- **Portmanteau tools**: Seven consolidated tools grouped by editing area
- **Agentic Workflows**: SEP-1577 sampling for autonomous orchestration of complex editing tasks

## Installation

1. Clone this repository
2. Install the extension in Zed:
   ```
   zed: install extension from /path/to/davinci-resolve-mcp/zed-extension
   ```

## Requirements

- **DaVinci Resolve**: Version 18.0 or later
- **Python**: 3.8 or later
- **Zed**: Build with MCP support enabled

## Usage

Once installed, the extension exposes MCP tools for:

- **Project Management**: Create, open, and manage DaVinci Resolve projects
- **Media Operations**: Import, organize, and search media in the media pool
- **Timeline Editing**: Perform cuts, trims, and timeline operations
- **Color Grading**: Apply LUTs, adjust color wheels, create correction nodes
- **Audio Processing**: Adjust levels, apply effects, sync audio tracks
- **Rendering**: Queue render jobs, monitor progress, export timelines

## Example Commands

- "Create a new 4K project called 'Summer Vacation'"
- "Import all videos from my Desktop folder"
- "Apply the cinematic LUT to all clips"
- "Render the timeline in YouTube format"

## Configuration

The extension tries to detect DaVinci Resolve and wire the server. For extra options, see the main project documentation.

## Troubleshooting

- Ensure DaVinci Resolve is running before using the extension
- Check that Python 3.8+ is available in your PATH
- Verify that the extension is properly installed in Zed

## License

MIT License - see LICENSE file for details
