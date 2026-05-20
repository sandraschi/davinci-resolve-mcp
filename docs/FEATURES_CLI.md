# CLI Commands

Direct terminal access to DaVinci Resolve operations.

## Overview

```
davinci-resolve-mcp [command] [args...]
```

| Command | Description |
|---------|-------------|
| `mcp` (default) | Start MCP server in stdio mode for Claude Desktop / Cursor |
| `start` | Start HTTP MCP server on port 8000 |
| `web` | Start webapp API backend on port 10843 |
| `check` | Verify Resolve installation and connection |
| `run-script` | Execute arbitrary Resolve Python script |
| `render` | Render a timeline to file |
| `import-media` | Import media files into a project |
| `open-project` | Open (or create) a project |

## run-script

Execute any Python script with pre-initialized `resolve`, `project`, `project_manager`, and `fusion` globals.

```
davinci-resolve-mcp run-script my_custom_export.py
davinci-resolve-mcp run-script batch_render.py --project "MyFilm"
davinci-resolve-mcp run-script test.py --dry-run
```

### Script template example:
```python
# my_custom_export.py
for timeline in project.GetTimelineCount():
    timeline_name = project.GetTimelineByIndex(i + 1).GetName()
    print(f"Found timeline: {timeline_name}")

timeline = project.GetCurrentTimeline()
project.SetCurrentRenderFormatAndCodec("mp4", "h264")
job_id = project.AddRenderJob()
project.SetRenderSettings("TargetDir", "C:/output/")
project.SetRenderSettings("CustomName", timeline.GetName())
project.StartRendering(job_id)
```

## render

Render a timeline from the command line.

```
davinci-resolve-mcp render C:/output/
davinci-resolve-mcp render C:/output/ --timeline "Main Edit" --format mov --codec prores_422_hq
davinci-resolve-mcp render C:/output/out.mp4 -r 3840x2160 --fps 24 --overwrite
davinci-resolve-mcp render C:/output/ --dry-run
```

## import-media

Import media files or list media pool contents.

```
davinci-resolve-mcp import-media C:/footage/scene1.mp4 C:/footage/scene2.mp4
davinci-resolve-mcp import-media C:/frames/*.png --sequence
davinci-resolve-mcp import-media --list
davinci-resolve-mcp import-media C:/clips/ --folder "Raw Footage" --project "MyFilm"
```

## open-project

Open an existing project or create a new one.

```
davinci-resolve-mcp open-project "My Edit"
davinci-resolve-mcp open-project "New Project" --create
```

## Requirements

All CLI commands require DaVinci Resolve to be running with the scripting API accessible.
