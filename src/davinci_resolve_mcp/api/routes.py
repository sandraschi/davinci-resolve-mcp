"""
FastMCP API routes for DaVinci Resolve MCP.
"""

import os

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(tags=["v1"])

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Local LLM (Ollama proxy)
# ---------------------------------------------------------------------------

@router.get("/llm/models")
async def llm_models():
    """List available models from Ollama."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
            data = r.json()
            return {"models": [m.get("name") for m in data.get("models", [])], "ollama_url": OLLAMA_URL}
    except Exception as e:
        return {"models": [], "ollama_url": OLLAMA_URL, "error": str(e)}


@router.post("/llm/load")
async def llm_load(name: str = Query(..., description="Model name to load into memory")):
    """Warm-load a model into Ollama memory (POST /api/generate with minimal prompt)."""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": name, "prompt": "", "stream": False, "keep_alive": 300},
            )
            r.raise_for_status()
            return {"success": True, "model": name}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.post("/llm/generate")
async def llm_generate(body: dict):
    """Generate completion from local LLM. Body: { model, prompt, stream? }."""
    model = body.get("model") or ""
    prompt = body.get("prompt") or ""
    stream = body.get("stream", False)
    if not model or not prompt:
        raise HTTPException(status_code=400, detail="model and prompt required")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": stream},
            )
            r.raise_for_status()
            data = r.json()
            return {"response": data.get("response", ""), "done": data.get("done", True)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------

@router.get("/logs")
async def get_logs():
    """Return in-memory log buffer (real server logs, not mock)."""
    try:
        from ..server import get_log_buffer

        entries = get_log_buffer()
        return {"entries": entries, "count": len(entries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/resolve-info")
async def get_resolve_info():
    """Get connected DaVinci Resolve version and status."""
    try:
        from ..server import app as mcp_app

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            return {"status": "disconnected", "message": "Connection manager not initialized"}

        status = mcp_app.state.connection_manager.get_status()

        # Also try to get the detailed info tool if possible
        info_tool = mcp_app.get_tool("get_resolve_info")
        if info_tool and hasattr(info_tool, "fn"):
            # We would normally call info_tool.fn() but it requires context.
            pass

        # Manually fetch since we have connection manager
        try:
            resolve = mcp_app.state.connection_manager.get_connection()
            project_manager = resolve.GetProjectManager()
            current_project = project_manager.GetCurrentProject()
            return {
                "status": "connected",
                "version": resolve.GetVersionString(),
                "project_name": current_project.GetName() if current_project else None,
                "is_rendering": resolve.IsRenderingInProgress()
                if hasattr(resolve, "IsRenderingInProgress")
                else False,
            }
        except Exception as e:
            return {"status": "error", "message": str(e), "manager_status": status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/projects")
async def get_projects():
    """Get list of DaVinci Resolve projects."""
    try:
        from ..server import app as mcp_app

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            return {"current_project": None, "projects": []}

        resolve = mcp_app.state.connection_manager.get_connection()
        project_manager = resolve.GetProjectManager()

        current_project = project_manager.GetCurrentProject()
        current_project_name = current_project.GetName() if current_project else None

        projects = project_manager.GetProjectListInCurrentFolder() or []

        return {"current_project": current_project_name, "projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/timeline")
async def get_timeline_info():
    """Get basic info about the current timeline."""
    try:
        from ..server import app as mcp_app

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            return {"timeline": None}

        resolve = mcp_app.state.connection_manager.get_connection()
        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject()

        if not project:
            return {"timeline": None}

        timeline = project.GetCurrentTimeline()

        if not timeline:
            return {"timeline": None}

        return {
            "timeline": {
                "name": timeline.GetName(),
                "start_code": timeline.GetStartTimecode(),
                "track_count_video": timeline.GetTrackCount("video"),
                "track_count_audio": timeline.GetTrackCount("audio"),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Fairlight (DAW) endpoints
@router.get("/fairlight/tracks")
async def fairlight_get_tracks(timeline_name: str | None = None):
    """Get audio tracks for current or specified timeline (Fairlight context)."""
    try:
        from ..server import app as mcp_app
        from ..tools.fairlight_tools import fairlight_get_timeline_tracks_impl

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            return {"status": "disconnected", "tracks": [], "track_count": 0}

        result = await fairlight_get_timeline_tracks_impl(mcp_app, timeline_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/fairlight/open-page")
async def fairlight_open_page():
    """Switch DaVinci Resolve UI to the Fairlight page."""
    try:
        from ..server import app as mcp_app
        from ..tools.fairlight_tools import fairlight_open_page_impl

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            raise HTTPException(status_code=503, detail="Connection manager not initialized")

        result = await fairlight_open_page_impl(mcp_app)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/fairlight/track/mute")
async def fairlight_set_mute(track_index: int, mute: bool, timeline_name: str | None = None):
    """Set mute state for an audio track."""
    try:
        from ..server import app as mcp_app
        from ..tools.fairlight_tools import fairlight_set_track_mute_impl

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            raise HTTPException(status_code=503, detail="Connection manager not initialized")

        result = await fairlight_set_track_mute_impl(mcp_app, track_index, mute, timeline_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/fairlight/track/solo")
async def fairlight_set_solo(
    track_index: int = Query(..., ge=1),
    solo: bool = Query(...),
    timeline_name: str | None = Query(None),
):
    """Set solo state for an audio track."""
    try:
        from ..server import app as mcp_app
        from ..tools.fairlight_tools import fairlight_set_track_solo_impl

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            raise HTTPException(status_code=503, detail="Connection manager not initialized")

        result = await fairlight_set_track_solo_impl(mcp_app, track_index, solo, timeline_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/fairlight/track/volume")
async def fairlight_set_volume(
    track_index: int = Query(..., ge=1),
    volume: float = Query(..., ge=0.0, le=2.0),
    timeline_name: str | None = Query(None),
):
    """Set volume for an audio track (0.0 to 2.0)."""
    try:
        from ..server import app as mcp_app
        from ..tools.fairlight_tools import fairlight_set_track_volume_impl

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            raise HTTPException(status_code=503, detail="Connection manager not initialized")

        result = await fairlight_set_track_volume_impl(mcp_app, track_index, volume, timeline_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
