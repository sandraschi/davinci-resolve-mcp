#!/usr/bin/env python3
"""
DaVinci Resolve MCP - CLI Entry Point

This module provides the command-line interface for the DaVinci Resolve MCP server.

Logging rules:
- mcp() command: structlog → stderr only. No console.print, no print(). stdout is
  reserved for JSON-RPC. Logging output appears in the Claude Desktop MCP server log.
- start/check/web commands: interactive CLI, console.print() is fine.
- Module level: NO logging.basicConfig here — each command configures its own handlers.
"""

import logging
import sys
from contextlib import contextmanager
from pathlib import Path

import typer
from rich.console import Console

from .connection.environment import ResolveEnvironment
from .server import app as mcp_app
from .server import initialize_server, start_server
from .transport import run_server

# Logger for this module — no handlers configured here; each command sets them up.
logger = logging.getLogger("davinci_resolve_mcp")

# Typer app
app = typer.Typer(
    name="davinci-resolve-mcp",
    help="DaVinci Resolve MCP Server - Control DaVinci Resolve through AI agents",
    add_completion=False,
)

# Console for interactive CLI commands only (start / check / web).
# NEVER use this in mcp() — stdout is the JSON-RPC channel.
console = Console()


def _configure_cli_logging(debug: bool = False) -> None:
    """Set up Rich logging to stderr for interactive CLI commands."""
    from rich.logging import RichHandler

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=Console(stderr=True))],
        force=True,
    )
    logger.setLevel(level)


def _configure_mcp_logging() -> None:
    """Route all logging to stderr for stdio MCP mode (JSON-RPC owns stdout)."""
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    root.addHandler(handler)
    root.setLevel(logging.INFO)


@contextmanager
def _stdio_single_instance_lock():
    """Guard stdio mode with a process lock on Windows (opt-out via env)."""
    import os

    if os.getenv("DAVINCI_MCP_STDIN_SINGLE_INSTANCE", "1") != "1":
        yield
        return

    lock_path = Path.home() / ".davinci-resolve-mcp" / "mcp-stdio.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    if os.name == "nt":
        import msvcrt

        lock_file = open(lock_path, "a+b")
        try:
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            lock_file.close()
            logger.error(
                "davinci-resolve-mcp stdio already running (lock: %s). "
                "Close other MCP clients or set DAVINCI_MCP_STDIN_SINGLE_INSTANCE=0.",
                lock_path,
            )
            raise typer.Exit(1)
        try:
            yield
        finally:
            try:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            finally:
                lock_file.close()
    else:
        yield


def version_callback(value: bool):
    """Display version and exit."""
    if value:
        from importlib.metadata import version

        v = version("davinci-resolve-mcp")
        console.print(f"DaVinci Resolve MCP v{v}")
        raise typer.Exit()


@app.command()
def start(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the server on"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Start the DaVinci Resolve MCP server."""
    _configure_cli_logging(debug)

    try:
        console.print("🔍 Verifying DaVinci Resolve environment...")
        env = ResolveEnvironment()
        install_path = env.detect_resolve_installation()
        if install_path:
            console.print(f"✅ Found DaVinci Resolve at {install_path}")
        else:
            console.print("⚠️  DaVinci Resolve not detected - some features may not work")
    except Exception as e:
        console.print(f"❌ Error: {e!s}", style="red")
        if debug:
            logger.exception("Detailed error:")
        raise typer.Exit(1)

    console.print(f"🚀 Starting DaVinci Resolve MCP server on {host}:{port}")
    try:
        run_server(mcp_app, server_name="davinci-resolve-mcp")
    except KeyboardInterrupt:
        console.print("\n👋 Shutting down server...")
    except Exception as e:
        console.print(f"❌ Server error: {e!s}", style="red")
        if debug:
            logger.exception("Detailed error:")
        raise typer.Exit(1)


@app.command()
def mcp():
    """Run the MCP server in stdio mode for Claude Desktop.

    stdout is reserved for JSON-RPC. All logging goes to stderr and appears
    in the Claude Desktop MCP server log file.
    """
    # Must be first — before any other code that might log or print.
    _configure_mcp_logging()

    # Initialize the server (lazy — don't fail if DaVinci Resolve not running).
    try:
        initialize_server()
        logger.info("Server initialized successfully")
    except Exception as e:
        logger.warning(
            "Server initialization warning: %s — server will start but some tools "
            "may not work until DaVinci Resolve is available.",
            e,
        )

    # Pass pre-built args to bypass argparse re-parsing sys.argv (which still contains
    # the 'mcp' subcommand as an unrecognized positional arg, causing parse failure).
    import argparse as _argparse

    _stdio_args = _argparse.Namespace(
        stdio=True, http=False, sse=False, host=None, port=None, path=None, debug=False
    )
    try:
        with _stdio_single_instance_lock():
            run_server(mcp_app, args=_stdio_args, server_name="davinci-resolve-mcp")
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error("MCP server error: %s", e)
        sys.exit(1)


@app.command()
def web(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the API server to"),
    port: int = typer.Option(10843, "--port", "-p", help="Port for the webapp API (default 10843)"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
):
    """Start the HTTP API server for the SOTA webapp (Vite proxy targets this port)."""
    import os

    _configure_cli_logging(debug)
    os.environ["HOST"] = host
    os.environ["PORT"] = str(port)
    if debug:
        os.environ["DEBUG"] = "true"
    console.print(f"Starting web API on http://{host}:{port} (for webapp proxy)")
    try:
        initialize_server()
    except Exception as e:
        console.print(f"Warning: init had issues: {e}", style="yellow")
    try:
        start_server(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        console.print("\nShutting down...")
    except Exception as e:
        console.print(f"Server error: {e!s}", style="red")
        raise typer.Exit(1)


@app.command()
def check():
    """Check the DaVinci Resolve environment and connection."""
    _configure_cli_logging()
    console.print("🔍 Checking DaVinci Resolve environment...")
    try:
        env = ResolveEnvironment()
        install_path = env.detect_resolve_installation()
        is_running = env.check_resolve_running()

        console.print("✅ [green]DaVinci Resolve Environment:[/green]")
        console.print(f"   • Install Path: {install_path or 'Not Found'}")
        console.print(f"   • Running: {'✅ Yes' if is_running else '❌ No'}")

        if not install_path:
            console.print(
                "\n❌ [yellow]Warning:[/yellow] DaVinci Resolve installation not detected."
            )
            console.print("   Make sure DaVinci Resolve is installed.")
            raise typer.Exit(1)

        if not is_running:
            console.print("\n⚠️  [yellow]Warning:[/yellow] DaVinci Resolve is not running.")
            console.print("   Start DaVinci Resolve before using the MCP server.")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"❌ [red]Error:[/red] {e!s}")
        raise typer.Exit(1)


@app.command()
def run_script(
    script_path: str = typer.Argument(..., help="Path to Python script to execute"),
    project_name: str = typer.Option(None, "--project", "-p", help="Project to open before running script"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be executed without running"),
):
    """Execute an arbitrary DaVinci Resolve Python script.

    The script receives pre-initialized 'resolve' and 'project' globals.
    Use this to run custom Resolve automation scripts through the MCP bridge.

    Examples:
        davinci-resolve-mcp run-script my_export.py
        davinci-resolve-mcp run-script batch_render.py --project "MyProject"
    """
    _configure_cli_logging()

    script_path = Path(script_path).resolve()
    if not script_path.exists():
        console.print(f"❌ [red]Script not found:[/red] {script_path}")
        raise typer.Exit(1)

    if dry_run:
        console.print(f"Would execute: {script_path}")
        console.print(f"Project: {project_name or 'current'}")
        return

    console.print("⚙️  Setting up Resolve scripting environment...")
    env = ResolveEnvironment()
    env.setup_environment_variables()

    if not env.check_resolve_running():
        console.print("❌ [red]DaVinci Resolve is not running. Start it first.[/red]")
        raise typer.Exit(1)

    try:
        import DaVinciResolveScript as dvr_script
    except ImportError as e:
        console.print(f"❌ [red]Cannot import DaVinciResolveScript: {e}[/red]")
        raise typer.Exit(1)

    resolve = dvr_script.scriptapp("Resolve")
    if not resolve:
        console.print("❌ [red]Failed to connect to DaVinci Resolve[/red]")
        raise typer.Exit(1)

    project_manager = resolve.GetProjectManager()
    project = None

    if project_name:
        project = project_manager.LoadProject(project_name)
        if not project:
            console.print(f"⚠️  Project '{project_name}' not found, creating it...")
            project = project_manager.CreateProject(project_name)
        if project:
            console.print(f"✅ Opened project: {project.GetName()}")
    else:
        project = project_manager.GetCurrentProject()

    if project:
        console.print(f"📂 Current project: {project.GetName()}")
    else:
        console.print("⚠️  No project open (some scripts may fail)")

    console.print(f"🚀 Executing: {script_path.name}")
    console.print("─" * 60)

    script_globals = {
        "resolve": resolve,
        "project": project,
        "project_manager": project_manager,
        "fusion": resolve.Fusion() if resolve else None,
        "__name__": "__main__",
    }

    try:
        script_code = script_path.read_text(encoding="utf-8")
        exec(compile(script_code, str(script_path), "exec"), script_globals)
        console.print("─" * 60)
        console.print("✅ [green]Script completed successfully[/green]")
    except Exception as e:
        console.print("─" * 60)
        console.print(f"❌ [red]Script error:[/red] {e}")
        logger.exception("Script execution failed")
        raise typer.Exit(1)


@app.command()
def render(
    output_path: str = typer.Argument(..., help="Output file or directory path"),
    timeline_name: str = typer.Option(None, "--timeline", "-t", help="Timeline to render (uses current if omitted)"),
    project_name: str = typer.Option(None, "--project", "-p", help="Project to open first"),
    format: str = typer.Option("mp4", "--format", "-f", help="Output format (mp4, mov, mxf, png, exr)"),
    codec: str = typer.Option("h264", "--codec", "-c", help="Video codec (h264, h265, prores_422_hq, dnxhd_220)"),
    resolution: str = typer.Option(None, "--resolution", "-r", help="Output resolution WxH (e.g. 1920x1080)"),
    frame_rate: float = typer.Option(None, "--fps", help="Output frame rate"),
    custom_name: str = typer.Option(None, "--name", "-n", help="Custom output filename (without extension)"),
    overwrite: bool = typer.Option(False, "--overwrite", "-y", help="Overwrite existing output file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show render settings without starting"),
):
    """Render a timeline directly from the command line.

    Examples:
        davinci-resolve-mcp render C:/output/
        davinci-resolve-mcp render C:/output/ --timeline "My Edit" --format mov --codec prores_422_hq
        davinci-resolve-mcp render C:/output/out.mp4 -t "Timeline 1" -r 3840x2160
    """
    import os as _os
    import time as _time

    _configure_cli_logging()
    env = ResolveEnvironment()
    env.setup_environment_variables()

    output_path = _os.path.abspath(output_path)
    output_dir = output_path if _os.path.isdir(output_path) else _os.path.dirname(output_path)

    if not env.check_resolve_running():
        console.print("❌ [red]DaVinci Resolve is not running. Start it first.[/red]")
        raise typer.Exit(1)

    try:
        import DaVinciResolveScript as dvr_script
    except ImportError as e:
        console.print(f"❌ [red]Cannot import DaVinciResolveScript: {e}[/red]")
        raise typer.Exit(1)

    resolve = dvr_script.scriptapp("Resolve")
    if not resolve:
        console.print("❌ [red]Failed to connect to DaVinci Resolve[/red]")
        raise typer.Exit(1)

    project_manager = resolve.GetProjectManager()
    if project_name:
        project = project_manager.LoadProject(project_name)
        if not project:
            console.print(f"❌ [red]Project '{project_name}' not found[/red]")
            raise typer.Exit(1)
    else:
        project = project_manager.GetCurrentProject()
        if not project:
            console.print("❌ [red]No project is open[/red]")
            raise typer.Exit(1)

    console.print(f"📂 Project: {project.GetName()}")

    if timeline_name:
        timeline = project.GetTimelineByName(timeline_name)
        if not timeline:
            console.print(f"❌ [red]Timeline '{timeline_name}' not found[/red]")
            raise typer.Exit(1)
    else:
        timeline = project.GetCurrentTimeline()
        if not timeline:
            console.print("❌ [red]No timeline is open[/red]")
            raise typer.Exit(1)

    console.print(f"🎬 Timeline: {timeline.GetName()}")

    filename = custom_name or timeline.GetName()
    if not _os.path.isdir(output_path):
        filename = _os.path.splitext(_os.path.basename(output_path))[0]

    render_settings = {
        "TargetDir": output_dir,
        "CustomName": filename,
        "FormatWidth": 1920,
        "FormatHeight": 1080,
        "FrameRate": frame_rate or float(timeline.GetSetting("timelineFrameRate") or "24.0"),
        "SelectAllFrames": True,
        "ExportVideo": True,
        "ExportAudio": True,
        "VideoQuality": 0,
        "AudioBitDepth": 16,
        "AudioSampleRate": 48000,
        "ColorSpaceTag": "Same as Project",
        "GammaTag": "Same as Project",
        "OverwriteExistingFile": overwrite,
    }

    if resolution and "x" in resolution:
        w, h = map(int, resolution.lower().split("x"))
        render_settings["FormatWidth"] = w
        render_settings["FormatHeight"] = h
    else:
        render_settings["FormatWidth"] = int(timeline.GetSetting("timelineResolutionWidth") or 1920)
        render_settings["FormatHeight"] = int(timeline.GetSetting("timelineResolutionHeight") or 1080)

    fmt = format.lower()
    if fmt == "mp4":
        render_settings["Format"] = "mp4"
        render_settings["VideoCodec"] = codec or "h264"
        render_settings["AudioCodec"] = "aac"
    elif fmt == "mov":
        render_settings["Format"] = "mov"
        render_settings["VideoCodec"] = codec or "h264"
        render_settings["AudioCodec"] = "aac"
    elif fmt in ("png", "exr", "tiff", "jpeg", "dpx"):
        render_settings["Format"] = fmt
        render_settings["ExportAudio"] = False
    else:
        render_settings["Format"] = fmt
        render_settings["VideoCodec"] = codec or "h264"

    if dry_run:
        console.print("⚙️  [yellow]Dry run — render settings:[/yellow]")
        for k, v in render_settings.items():
            console.print(f"   {k}: {v}")
        console.print(f"   Output: {output_dir}/{filename}.{fmt}")
        return

    console.print(f"🎯 Output: {output_dir}/{filename}.{fmt}")
    console.print("🚀 Starting render...")

    job_id = project.AddRenderJob()
    if job_id == -1:
        console.print("❌ [red]Failed to create render job[/red]")
        raise typer.Exit(1)

    for key, value in render_settings.items():
        try:
            project.SetRenderSettings(key, value)
        except Exception:
            pass

    project.SetCurrentRenderFormatAndCodec(render_settings.get("Format", "mp4"), render_settings.get("VideoCodec", "h264"))

    if not project.StartRendering(job_id):
        console.print("❌ [red]Failed to start rendering[/red]")
        raise typer.Exit(1)

    console.print("⏳ Rendering...")
    while project.IsRenderingInProgress():
        status = project.GetRenderJobStatus(job_id)
        if status:
            pct = status.get("Completion", 0.0)
            console.print(f"   Progress: {pct:.0f}%", end="\r")
        _time.sleep(1)

    console.print("")
    status = project.GetRenderJobStatus(job_id)
    if status and status.get("Status") == "Complete":
        console.print(f"✅ [green]Render complete: {output_dir}/{filename}.{fmt}[/green]")
    else:
        err = (status or {}).get("Status", "Unknown error")
        console.print(f"❌ [red]Render failed: {err}[/red]")
        raise typer.Exit(1)


@app.command()
def import_media(
    paths: list[str] = typer.Argument(..., help="File paths to import"),
    project_name: str = typer.Option(None, "--project", "-p", help="Project to import into"),
    folder: str = typer.Option(None, "--folder", "-f", help="Target folder in media pool"),
    as_sequence: bool = typer.Option(False, "--sequence", "-s", help="Import as image sequence"),
    list_only: bool = typer.Option(False, "--list", "-l", help="List media in pool instead of importing"),
):
    """Import media files into a DaVinci Resolve project or list media pool contents.

    Examples:
        davinci-resolve-mcp import-media C:/clips/scene1.mp4 C:/clips/scene2.mp4
        davinci-resolve-mcp import-media C:/frames/*.png --sequence
        davinci-resolve-mcp import-media --list
    """
    _configure_cli_logging()
    env = ResolveEnvironment()
    env.setup_environment_variables()

    if not env.check_resolve_running():
        console.print("❌ [red]DaVinci Resolve is not running. Start it first.[/red]")
        raise typer.Exit(1)

    try:
        import DaVinciResolveScript as dvr_script
    except ImportError as e:
        console.print(f"❌ [red]Cannot import DaVinciResolveScript: {e}[/red]")
        raise typer.Exit(1)

    resolve = dvr_script.scriptapp("Resolve")
    if not resolve:
        console.print("❌ [red]Failed to connect to DaVinci Resolve[/red]")
        raise typer.Exit(1)

    project_manager = resolve.GetProjectManager()
    if project_name:
        project = project_manager.LoadProject(project_name)
        if not project:
            console.print(f"❌ [red]Project '{project_name}' not found[/red]")
            raise typer.Exit(1)
    else:
        project = project_manager.GetCurrentProject()
        if not project:
            console.print("❌ [red]No project is open[/red]")
            raise typer.Exit(1)

    console.print(f"📂 Project: {project.GetName()}")
    media_pool = project.GetMediaPool()
    if not media_pool:
        console.print("❌ [red]Could not access media pool[/red]")
        raise typer.Exit(1)

    if list_only:
        root = media_pool.GetRootFolder()
        clips = media_pool.GetClipList(root) or []
        if not clips:
            console.print("📭 Media pool is empty")
            return
        console.print(f"📋 Media pool contents ({len(clips)} items):")
        for clip in clips:
            name = clip.GetName() if hasattr(clip, "GetName") else "?"
            console.print(f"   • {name}")
        return

    if folder:
        # Navigate to or create target folder
        root = media_pool.GetRootFolder()
        subfolders = media_pool.GetSubFolders(root) or {}
        if folder in subfolders:
            media_pool.SetCurrentFolder(subfolders[folder])
        else:
            media_pool.AddSubFolder(root, folder)
            subfolders = media_pool.GetSubFolders(root) or {}
            if folder in subfolders:
                media_pool.SetCurrentFolder(subfolders[folder])

    valid_paths = [p for p in paths if _os.path.exists(p)]
    if not valid_paths:
        console.print("❌ [red]No valid files found[/red]")
        raise typer.Exit(1)

    console.print(f"📥 Importing {len(valid_paths)} file(s)...")
    clips = media_pool.ImportMedia(valid_paths)
    if clips:
        console.print(f"✅ [green]Imported {len(clips)} clip(s)[/green]")
        for clip in clips:
            name = clip.GetName() if hasattr(clip, "GetName") else "?"
            console.print(f"   • {name}")
    else:
        console.print("⚠️  Import returned no clips (may have failed)")


@app.command()
def open_project(
    name: str = typer.Argument(..., help="Project name to open"),
    create: bool = typer.Option(False, "--create", "-c", help="Create project if it doesn't exist"),
):
    """Open (and optionally create) a DaVinci Resolve project directly from CLI.

    Examples:
        davinci-resolve-mcp open-project "My Edit"
        davinci-resolve-mcp open-project "New Project" --create
    """
    _configure_cli_logging()
    env = ResolveEnvironment()
    env.setup_environment_variables()

    if not env.check_resolve_running():
        console.print("❌ [red]DaVinci Resolve is not running. Start it first.[/red]")
        raise typer.Exit(1)

    try:
        import DaVinciResolveScript as dvr_script
    except ImportError as e:
        console.print(f"❌ [red]Cannot import DaVinciResolveScript: {e}[/red]")
        raise typer.Exit(1)

    resolve = dvr_script.scriptapp("Resolve")
    if not resolve:
        console.print("❌ [red]Failed to connect to DaVinci Resolve[/red]")
        raise typer.Exit(1)

    project_manager = resolve.GetProjectManager()
    project = project_manager.LoadProject(name)
    if not project:
        if create:
            console.print(f"📁 Creating project: {name}")
            project = project_manager.CreateProject(name)
            if project:
                console.print(f"✅ [green]Created and opened: {project.GetName()}[/green]")
                return
        console.print(f"❌ [red]Project '{name}' not found. Use --create to create it.[/red]")
        raise typer.Exit(1)

    console.print(f"✅ [green]Opened project: {project.GetName()}[/green]")


def main():
    """Entry point for the davinci-resolve-mcp console script."""
    # No args → stdio MCP (Cursor/IDE). Else use subcommand from argv.
    if len(sys.argv) == 1:
        sys.argv.append("mcp")
    app()


if __name__ == "__main__":
    main()
