# DaVinci Resolve MCP - Zed Extension

Professional AI-powered video editing automation for DaVinci Resolve, integrated as a Zed extension.

## Features

- **Natural Language Control**: Control DaVinci Resolve through conversational AI commands
- **FastMCP 2.14.3**: Latest MCP protocol with conversational tools and sampling capabilities
- **Portmanteau Design**: 7 consolidated tools preventing explosion while maintaining full functionality
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
- **Zed**: Latest version with MCP support

## Usage

Once installed, the extension provides AI-powered assistance for:

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

The extension automatically detects DaVinci Resolve installations and configures the connection. For advanced configuration, see the main project documentation.

## Troubleshooting

- Ensure DaVinci Resolve is running before using the extension
- Check that Python 3.8+ is available in your PATH
- Verify that the extension is properly installed in Zed

## License

MIT License - see LICENSE file for details
