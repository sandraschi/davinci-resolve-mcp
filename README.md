# DaVinci Resolve MCP

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/sandraschi/davinci-resolve-mcp)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.14.3-green.svg)](https://github.com/jlowin/fastmcp)
[![DaVinci Resolve](https://img.shields.io/badge/DaVinci%20Resolve-18+-red.svg)](https://www.blackmagicdesign.com/products/davinciresolve)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/sandraschi/davinci-resolve-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/davinci-resolve-mcp/actions)
[![Code Coverage](https://codecov.io/gh/sandraschi/davinci-resolve-mcp/branch/master/graph/badge.svg)](https://codecov.io/gh/sandraschi/davinci-resolve-mcp)

**Professional AI-powered video editing automation for DaVinci Resolve through natural language commands and advanced MCP protocols.**

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

DaVinci Resolve MCP is the first comprehensive Model Context Protocol (MCP) server for Blackmagic Design's DaVinci Resolve, enabling AI agents to control professional video editing workflows through natural language commands. Built with FastMCP 2.14.3, it provides conversational tool returns, sampling capabilities, and agentic workflow orchestration.

### What Makes This Revolutionary

- **Natural Language Control**: Transform complex video editing operations into simple conversations
- **FastMCP 2.14.3 Compliance**: Latest MCP protocol with conversational tools and SEP-1577 sampling
- **Portmanteau Design**: 7 consolidated tools preventing interface explosion while maintaining full functionality
- **Agentic Orchestration**: LLM-driven autonomous workflow execution
- **Professional Grade**: Supports 4K, 8K, HDR workflows with frame-accurate editing

### Supported Workflows

- **Project Management**: Create, open, manage projects with professional settings
- **Media Operations**: Import, organize, search media pool with advanced metadata
- **Timeline Editing**: Perform cuts, trims, transitions with precision
- **Color Grading**: Apply LUTs, primary/secondary corrections, nodes
- **Audio Processing**: Adjust levels, apply effects, synchronize tracks
- **Rendering**: Queue jobs, batch processing, monitor progress
- **System Integration**: Health checks, status monitoring, help systems

---

## Key Features

### 🤖 AI-Powered Automation
- **Conversational Interface**: Natural language control of complex editing operations
- **Intelligent Workflows**: AI-driven orchestration of multi-step processes
- **Context Awareness**: Understands project state and suggests optimal actions

### ⚡ High Performance
- **FastMCP 2.14.3**: Latest protocol with sampling and conversational capabilities
- **Efficient Architecture**: Portmanteau design reduces API complexity by 73%
- **Optimized Operations**: Batch processing and parallel execution support

### 🎯 Professional Features
- **4K/8K/HDR Support**: Full resolution workflows with professional color spaces
- **Frame Accuracy**: Precise timeline operations with sub-frame precision
- **Multi-Format**: Support for all major video codecs and containers
- **Color Science**: Rec.709, Rec.2020, P3, and custom color spaces

### 🔧 Developer Experience
- **Comprehensive Testing**: 95%+ code coverage with integration tests
- **Type Safety**: Full mypy compliance with strict type checking
- **Documentation**: Complete API reference and usage examples
- **CI/CD**: Automated testing, building, and deployment

### 📦 Distribution Options
- **MCPB Packages**: Optimized binary packages for MCP registries
- **Zed Extension**: Native integration with Zed editor
- **PyPI Package**: Standard Python package distribution
- **Docker Support**: Containerized deployment options

---

## Architecture

### FastMCP 2.14.3 Integration

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Claude/Groq   │───▶│  FastMCP 2.14.3  │───▶│ DaVinci Resolve │
│   AI Agent      │    │  Server           │    │   API           │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Portmanteau      │
                       │ Tools (7 total)  │
                       └──────────────────┘
```

### Tool Architecture

The server implements a portmanteau design consolidating 26 individual tools into 7 logical groups:

1. **resolve_project**: Project lifecycle management
2. **resolve_media**: Media pool operations and organization
3. **resolve_timeline**: Timeline editing and composition
4. **resolve_color**: Professional color grading
5. **resolve_audio**: Audio processing and mixing
6. **resolve_render**: Rendering and export operations
7. **resolve_system**: System utilities and information

### Conversational Returns

All tools return structured responses with conversational elements:

```python
{
    "success": True,
    "operation": "system_info",
    "message": "DaVinci Resolve 18.5.0 connected with project 'Summer Edit' open",
    "version": "18.5.0",
    "api_version": "1.0",
    "is_rendering": false,
    "project_name": "Summer Edit"
}
```

### Sampling Capabilities (SEP-1577)

Agentic workflows use FastMCP sampling to autonomously orchestrate complex operations:

```python
# Example: Intelligent project setup workflow
result = await agentic_resolve_workflow(
    workflow_prompt="Create a new 4K project and import media from Desktop",
    available_tools=["resolve_project", "resolve_media"],
    max_iterations=5
)
```

---

## Installation

### System Requirements

- **DaVinci Resolve**: Version 18.0 or later
- **Python**: 3.8 or later
- **Operating System**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB for installation, additional space for media

### Option 1: MCPB Package (Recommended)

```bash
# Download from releases or registry
mcp install davinci-resolve-mcp-0.2.0.mcpb

# Or build from source
git clone https://github.com/sandraschi/davinci-resolve-mcp
cd davinci-resolve-mcp
python build_mcpb.py
```

### Option 2: PyPI Package

```bash
pip install davinci-resolve-mcp

# For development
pip install davinci-resolve-mcp[dev]
```

### Option 3: Zed Extension

```bash
# Install extension
zed: install extension from https://github.com/sandraschi/davinci-resolve-mcp/zed-extension

# Or manual installation
git clone https://github.com/sandraschi/davinci-resolve-mcp
cd davinci-resolve-mcp
python -m scripts.build_zed
# Copy dist/davinci-resolve-mcp-zed-extension.zip to Zed extensions directory
```

### Post-Installation Setup

1. **Verify DaVinci Resolve**: Ensure DaVinci Resolve is installed and can be launched
2. **Environment Variables**: Configure connection settings if needed
3. **Test Connection**: Run `davinci-resolve-mcp check` to verify setup

---

## Configuration

### Environment Variables

```bash
# Connection settings
RESOLVE_HOST=localhost          # DaVinci Resolve API host
RESOLVE_PORT=8080              # DaVinci Resolve API port
RESOLVE_TIMEOUT=30             # Connection timeout in seconds

# Server settings
HOST=127.0.0.1                 # MCP server host
PORT=8000                      # MCP server port
DEBUG=false                    # Enable debug logging

# Tool configuration
RESOLVE_TOOL_MODE=portmanteau   # portmanteau or individual
PYTHONPATH=/path/to/src         # Python path for imports
```

### Configuration File

Create `config.yaml` or `config.json`:

```yaml
# config.yaml
davinci_resolve:
  host: localhost
  port: 8080
  timeout: 30
  auto_start: false

server:
  host: 127.0.0.1
  port: 8000
  debug: false
  log_level: INFO

tools:
  mode: portmanteau
  max_concurrent: 4
  request_timeout: 120

logging:
  level: INFO
  format: json
  file: logs/davinci_resolve_mcp.log
```

---

## Usage

### Basic Usage

```python
from davinci_resolve_mcp import DaVinciResolveMCP

# Initialize server
server = DaVinciResolveMCP()
server.start()

# Or use CLI
davinci-resolve-mcp start --host 127.0.0.1 --port 8000
```

### MCP Integration

Configure your MCP client (Claude Desktop, Zed, etc.):

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "python",
      "args": ["-m", "davinci_resolve_mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/davinci-resolve-mcp/src"
      }
    }
  }
}
```

### Example Conversations

**Project Setup:**
```
User: "Create a new 4K project for my vacation videos"
AI: Records request, creates project with optimal 4K settings
Response: "Created 'Vacation 4K' project with UHD timeline"
```

**Media Import:**
```
User: "Import all MP4 files from my Desktop"
AI: Scans Desktop, imports compatible files, organizes by date
Response: "Imported 12 MP4 files, organized in media pool"
```

**Color Grading:**
```
User: "Apply cinematic LUT to all clips"
AI: Applies professional LUT, adjusts for consistency
Response: "Applied Cinematic LUT with automatic color balancing"
```

### Advanced Workflows

**Batch Rendering:**
```python
# Intelligent batch processing
result = await intelligent_video_processing(
    projects=[project_data],
    processing_goal="Render all timelines in H.264 and H.265",
    available_operations=["resolve_render", "resolve_timeline"],
    quality_priority="balanced"
)
```

**Agentic Editing:**
```python
# Autonomous workflow execution
result = await agentic_resolve_workflow(
    workflow_prompt="Edit wedding video: cut ceremony, add music, color grade",
    available_tools=["resolve_timeline", "resolve_audio", "resolve_color"],
    max_iterations=10
)
```

---

## API Reference

### Core Tools

#### resolve_project
Project management operations.

```python
# Create new project
await resolve_project("create", name="My Project", format="UHD")

# Open existing project
await resolve_project("open", name="Existing Project")

# Get project info
await resolve_project("info", project_id="123")
```

#### resolve_media
Media pool operations.

```python
# Import media
await resolve_media("import", paths=["/path/to/video.mp4"], folder="Footage")

# Search media
await resolve_media("search", query="interview", media_type="video")

# Organize media
await resolve_media("create_folder", name="Interviews", parent="Root")
```

#### resolve_timeline
Timeline editing operations.

```python
# Create timeline
await resolve_timeline("create", name="Main Edit", format="UHD_2398")

# Add clips
await resolve_timeline("add_clip", media_id="123", position="00:00:10:00")

# Edit operations
await resolve_timeline("cut", clip_id="456", position="00:01:30:15")
```

#### resolve_color
Color grading operations.

```python
# Apply LUT
await resolve_color("apply_lut", clip_id="123", lut_path="/path/to/lut.cube")

# Adjust primaries
await resolve_color("adjust_primary", node_id="789", lift=[0.1, 0.0, -0.1])

# Create node
await resolve_color("create_node", clip_id="123", node_type="corrector")
```

#### resolve_audio
Audio processing operations.

```python
# Adjust levels
await resolve_audio("adjust_levels", clip_id="123", gain=3.0)

# Apply effect
await resolve_audio("add_effect", track_id="456", effect="compressor")

# Sync audio
await resolve_audio("sync", video_clip_id="123", audio_clip_id="456")
```

#### resolve_render
Rendering and export operations.

```python
# Add render job
await resolve_render("add_job", timeline_id="123", format="H264", preset="YouTube")

# Monitor progress
await resolve_render("job_status", job_id="789")

# Batch render
await resolve_render("batch", job_ids=["123", "456", "789"])
```

#### resolve_system
System utilities and information.

```python
# Get system info
await resolve_system("info")

# Health check
await resolve_system("health")

# Get help
await resolve_system("help", topic="color_grading", level="advanced")
```

### Agentic Tools

#### agentic_resolve_workflow
Autonomous workflow execution using sampling.

```python
result = await agentic_resolve_workflow(
    workflow_prompt="Create project, import media, basic edit",
    available_tools=["resolve_project", "resolve_media", "resolve_timeline"],
    max_iterations=5
)
```

#### intelligent_video_processing
Smart batch processing with optimization.

```python
result = await intelligent_video_processing(
    projects=[project_data],
    processing_goal="Optimize and render all projects",
    available_operations=["resolve_render", "resolve_color"],
    processing_strategy="adaptive"
)
```

#### conversational_resolve_assistant
Natural language assistance with context.

```python
result = await conversational_resolve_assistant(
    user_query="How do I color grade a sunset scene?",
    context_level="detailed",
    expertise_level="intermediate"
)
```

---

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/sandraschi/davinci-resolve-mcp
cd davinci-resolve-mcp

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Unix

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
pytest tests/ -v

# Run linting
ruff check src/ tests/
ruff format src/ tests/
```

### Project Structure

```
davinci-resolve-mcp/
├── src/davinci_resolve_mcp/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # FastMCP server implementation
│   ├── agentic.py           # Sampling and agentic workflows
│   ├── config.py            # Configuration management
│   ├── types.py             # Type definitions
│   ├── connection/          # DaVinci Resolve API connection
│   ├── tools/               # Tool implementations
│   │   ├── portmanteau/     # Consolidated tools
│   │   └── individual/      # Legacy individual tools
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── docs/                    # Documentation
├── mcpb/                    # MCPB package configuration
├── zed-extension/           # Zed editor integration
├── scripts/                 # Development scripts
├── pyproject.toml           # Project configuration
├── build_mcpb.py           # MCPB packaging script
└── README.md               # This file
```

### Testing

```bash
# Run all tests
pytest tests/ -v --cov=src/davinci_resolve_mcp

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests

# Run with coverage
pytest --cov=src/davinci_resolve_mcp --cov-report=html

# Run linting
ruff check src/ tests/
ruff format src/ tests/
```

### Building

```bash
# Build Python package
python -m build

# Build MCPB package
python build_mcpb.py

# Build Zed extension
python -m scripts.build_zed
```

---

## Contributing

We welcome contributions from the community. Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -e .[dev]`)
4. Install pre-commit hooks (`pre-commit install`)
5. Make your changes
6. Run tests (`pytest tests/ -v`)
7. Run linting (`ruff check src/ tests/ && ruff format src/ tests/`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

### Code Standards

- **Python**: 3.8+ compatibility
- **Type Hints**: Full mypy compliance
- **Formatting**: Ruff formatting
- **Linting**: Ruff linting with strict rules
- **Testing**: 95%+ code coverage required
- **Documentation**: Complete docstrings for public APIs

### Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag
4. GitHub Actions handles the rest:
   - Run tests and quality checks
   - Build packages (PyPI, MCPB, Zed)
   - Create GitHub release
   - Deploy documentation

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- FastMCP: MIT License
- DaVinci Resolve API: Blackmagic Design EULA
- Python dependencies: Various permissive licenses

---

## Support

- **Documentation**: [https://sandraschi.github.io/davinci-resolve-mcp](https://sandraschi.github.io/davinci-resolve-mcp)
- **Issues**: [https://github.com/sandraschi/davinci-resolve-mcp/issues](https://github.com/sandraschi/davinci-resolve-mcp/issues)
- **Discussions**: [https://github.com/sandraschi/davinci-resolve-mcp/discussions](https://github.com/sandraschi/davinci-resolve-mcp/discussions)
- **Email**: sandra@sandraschi.dev

### Community

- **Discord**: [DaVinci Resolve MCP Community](https://discord.gg/davinci-resolve-mcp)
- **Reddit**: r/davinciresolve
- **Forum**: Blackmagic Design Forums

---

## Acknowledgments

- **Blackmagic Design** for DaVinci Resolve and their API
- **FastMCP Community** for the excellent MCP framework
- **Open Source Community** for the tools and libraries that make this possible

---

*DaVinci Resolve MCP is not affiliated with Blackmagic Design. DaVinci Resolve is a trademark of Blackmagic Design.*
