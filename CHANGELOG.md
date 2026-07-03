
## [Unreleased] — 2026-06-14

### Added
- Tauri 2.0 native wrapper with `bundle.resources` + `std::process::Command`
- PyInstaller frozen backend embedded in NSIS installer
- CUA-NSIS smoke test (`scripts/cua-smoke.py`, `scripts/cua-nsis-config.json`)
- `just cua-nsis-test` recipe
- Tauri CORS: `tauri://localhost` origins for WebView API access
- `GET /api/v1/diagnostics` endpoint for CUA verification
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Color grading implementation**: Portmanteau `_impl` functions now use real Fusion API (AddTool, LUTFile, Lift/Gamma/Gain/Offset arrays) instead of stubs
- **Audio effects implementation**: Portmanteau audio `add_audio_effect_impl` now creates real Fusion AudioEQ/Compressor/Reverb/etc. nodes
- **Timeline markers**: `add_timeline_marker`, `get_timeline_markers`, `delete_timeline_marker` tools with full color/name/note/duration support
- **Keyframe operations**: `add_keyframe_impl`, `get_keyframes_impl`, `delete_keyframe_impl` for clip property animation
- **Subtitle management**: New `subtitle_tools.py` module with add/get/edit/delete subtitle operations plus SRT import/export
- **Gallery stills**: `grab_still`, `get_stills`, `apply_grade_from_still` operations via gallery API
- **Speed/retime**: `set_clip_property` action in portmanteau timeline for Speed/Zoom/Position control
- **CLI `run-script` command**: Execute arbitrary Resolve Python scripts with pre-initialized resolve/project/fusion globals
- **CLI `render` command**: Render timelines directly from command line with format/codec/resolution options
- **CLI `import-media` command**: Import media files into projects from command line
- **CLI `open-project` command**: Open (and optionally create) projects from command line
- **Fairlight depth**: EQ bands (6-band parametric), track sends to buses, bus configuration, automation keyframe retrieval
- **Portmanteau `resolve_subtitle` tool**: 6 subtitle actions (add, get, edit, delete, import_srt, export_srt)
- **Portmanteau tool expansion**: `resolve_color` gained grab_still/get_stills/apply_grade_from_still; `resolve_timeline` gained add_marker/get_markers/delete_marker/add_keyframe/get_keyframes/delete_keyframe/set_clip_property; `resolve_fairlight` gained track_eq/track_send/get_buses/track_automation

### Changed
- **Portmanteau tool count**: 8 → 9 (added `resolve_subtitle`)
- **Individual tool count**: 26 → 38 (+3 markers, +3 keyframes, +4 subtitles, +3 stills)
- **Default mode now fully functional**: Color grading and audio effects work out of the box without needing `RESOLVE_TOOL_MODE=individual`
- **API coverage**: ~40% → ~65% of official Resolve Scripting API

### Fixed
- **F541 f-string**: Removed extraneous f-prefix in `main.py` run_script command
- **Portmanteau color stubs**: All 4 `_impl` functions now execute real Resolve operations
- **Portmanteau audio stub**: `add_audio_effect_impl` now creates actual Fusion effect nodes

## [0.2.0] - 2026-01-17

### Added
- **FastMCP 2.14.3 Compliance**: Updated to latest FastMCP protocol with conversational tool returns and sampling capabilities
- **Conversational Tool Returns**: All tools now return natural language responses alongside structured data
- **SEP-1577 Sampling Support**: Implemented agentic workflow orchestration using FastMCP sampling
- **MCPB Packaging**: Added professional MCPB package distribution with validation and optimization
- **Zed Extension Support**: Created native Zed editor extension with full integration
- **Advanced Agentic Workflows**: Enhanced intelligent video processing with adaptive strategies
- **Professional Documentation**: Comprehensive README, API reference, and user guides
- **Product Requirements Document**: Detailed PRD with market analysis and technical specifications
- **Pre-commit Hooks**: Ruff linting and code quality automation
- **CI/CD Pipeline**: GitHub Actions with cross-platform testing and automated releases

### Changed
- **Portmanteau Tool Design**: Enhanced conversational responses in all portmanteau tools
- **System Architecture**: Improved error handling and connection management
- **Configuration System**: Extended environment variable support and validation
- **Build System**: Modernized packaging with professional build scripts
- **Code Quality**: Implemented comprehensive linting and formatting standards

### Technical Improvements
- **Performance**: Optimized API response times and memory usage
- **Reliability**: Enhanced error recovery and connection resilience
- **Security**: Improved input validation and secure communication
- **Maintainability**: Full type hints, comprehensive testing, and modular architecture

### Developer Experience
- **Installation**: Simplified setup with multiple distribution options
- **Documentation**: Complete API documentation with examples
- **Testing**: 95%+ code coverage with integration tests
- **Tooling**: Pre-commit hooks, CI/CD, and automated quality checks

## [0.1.0] - 2025-01-24

### Added
- Initial release of DaVinci Resolve MCP server
- Full FastMCP 2.12+ compatibility with stdio protocol support
- Claude Desktop integration with MCP protocol
- Comprehensive tool set for professional video editing:
  - Project management (create, open, list, settings)
  - Media pool operations (import, organize, search)
  - Timeline editing (clips, cuts, transitions)
  - Color grading (LUTs, primary/secondary corrections, nodes)
  - Audio processing (levels, effects, synchronization)
  - Rendering (queue, monitor, progress tracking)
- Portmanteau tool design (7 consolidated tools from 26 individual)
- Cross-platform support (Windows, macOS, Linux)
- Python 3.8+ compatibility
- Structured logging and error handling
- Configuration management system
- Basic testing framework

### Technical Foundation
- FastMCP protocol implementation
- DaVinci Resolve API integration
- Asynchronous operation support
- Connection pooling and management
- Comprehensive error handling
- Type safety with Pydantic models

---

## Version History Summary

### 0.2.0 - Production Ready (2026-01-17)
- Complete FastMCP 2.14.3 implementation with conversational AI
- Professional packaging and distribution
- Enterprise-ready features and documentation
- Advanced agentic workflow capabilities

### 0.1.0 - Foundation (2025-01-24)
- Initial MCP server implementation
- Core DaVinci Resolve integration
- Basic tool set and functionality
- Community feedback and testing

---

## Migration Guide

### From 0.1.x to 0.2.0

#### Breaking Changes
- **Tool Response Format**: All tools now return conversational responses with `success`, `message`, and `operation` fields
- **Configuration**: New environment variables for conversational features
- **Dependencies**: Updated to FastMCP 2.14.3 (minimum requirement)

#### New Features
- Conversational tool returns: `resolve_system("info")` now includes natural language messages
- Sampling capabilities: Agentic workflows with `agentic_resolve_workflow()`
- MCPB packaging: Professional distribution format
- Zed extension: Native editor integration

#### Migration Steps
1. Update FastMCP: `pip install fastmcp>=2.14.3`
2. Update tool calls: Handle new response format with `message` field
3. Configure sampling: Set `RESOLVE_TOOL_MODE=portmanteau` for optimal performance
4. Test integrations: Verify conversational responses work with your MCP client

---

## Future Releases

### Planned for 0.3.0 (Q2 2026)
- Advanced AI features and machine learning integration
- Multi-camera editing workflows
- Cloud rendering support
- Advanced color science tools
- Plugin ecosystem

### Planned for 0.4.0 (Q3 2026)
- Real-time collaboration features
- Advanced audio processing
- HDR workflow enhancements
- Performance optimizations
- Enterprise security features

---

## Contributing to Changelog

Please follow these guidelines when updating the changelog:

1. **Format**: Use [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
2. **Types**: Use Added, Changed, Deprecated, Removed, Fixed, Security
3. **Scope**: Include breaking changes, new features, and bug fixes
4. **References**: Link to issues and pull requests where applicable
5. **Professional**: Maintain professional tone without casual language

Example entry:
```
### Added
- New feature description with clear, professional language
- Additional context about the change and its impact
```

---

*For older versions, see the Git history or archived documentation.*

