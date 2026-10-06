"""
FastMCP API routes for DaVinci Resolve MCP.
"""

import json
import os
import time

import httpx
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

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
            return {
                "models": [m.get("name") for m in data.get("models", [])],
                "ollama_url": OLLAMA_URL,
            }
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
    """Generate completion from local LLM. Body: { model, prompt, stream?, system? }."""
    model = body.get("model") or ""
    prompt = body.get("prompt") or ""
    stream = body.get("stream", False)
    system = body.get("system")
    if not model or not prompt:
        raise HTTPException(status_code=400, detail="model and prompt required")
    payload: dict = {"model": model, "prompt": prompt, "stream": stream}
    if system:
        payload["system"] = system
    if stream:
        # NDJSON passthrough for token streaming (client reads via getReader)
        from fastapi.responses import StreamingResponse

        async def _stream():
            try:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    async with client.stream("POST", f"{OLLAMA_URL}/api/generate", json=payload) as r:
                        r.raise_for_status()
                        async for line in r.aiter_lines():
                            if line:
                                yield line + "\n"
            except Exception as e:
                yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(_stream(), media_type="application/x-ndjson")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            r.raise_for_status()
            data = _read_ollama_body(r)
            return {"response": data.get("response", ""), "done": data.get("done", True)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------
# Chat (OpenAI-style proxy + skill-aware route)
# ---------------------------------------------------------------------------


@router.post("/llm/chat")
async def llm_chat(body: dict):
    """OpenAI-style chat proxy. Body: { model, messages: [{role, content}], stream? }.

    The ONLY path the Chat page should use for multi-turn conversation.
    Keys never leave the server.
    """
    model = body.get("model") or ""
    messages = body.get("messages") or []
    stream = body.get("stream", False)
    if not model or not messages:
        raise HTTPException(status_code=400, detail="model and messages required")
    payload: dict = {"model": model, "messages": messages, "stream": stream}
    if stream:
        from fastapi.responses import StreamingResponse

        async def _stream():
            try:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as r:
                        r.raise_for_status()
                        async for line in r.aiter_lines():
                            if line:
                                yield line + "\n"
            except Exception as e:
                yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(_stream(), media_type="application/x-ndjson")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            r.raise_for_status()
            data = _read_ollama_body(r)
            message = data.get("message", {}) or {}
            if not isinstance(message, dict):
                message = {}
            text = message.get("content", "") or data.get("response", "")
            return {"response": text, "done": data.get("done", True)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.post("/chat")
async def api_chat(body: dict):
    """Skill-aware chat route. Body: { message, personality?, model? }.

    Composes the skill registry + personality into the system prompt
    server-side, then answers via the local LLM (non-streaming).
    """
    from ..prompts import SKILL_CATALOG

    message = (body.get("message") or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message required")
    personality = body.get("personality") or "You are a senior video editor."
    model = body.get("model") or ""
    if not model:
        discovered = await _probe_json(f"{OLLAMA_URL}/api/tags")
        models = [m.get("name") for m in (discovered or {}).get("models", [])]
        if not models:
            raise HTTPException(status_code=503, detail="No local LLM available")
        model = models[0]
    skill_block = "\n".join(f"- {s['name']}: {', '.join(s['operations'])}" for s in SKILL_CATALOG)
    system = f"{personality}\nAvailable Resolve skills (ground every answer in these):\n{skill_block}"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/generate", json={"model": model, "prompt": message, "system": system}
            )
            r.raise_for_status()
            data = _read_ollama_body(r)
            return {
                "response": data.get("response", ""),
                "model": model,
                "skills": [s["name"] for s in SKILL_CATALOG],
            }
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

        mgr = mcp_app.state.connection_manager
        try:
            if not await mgr.ensure_connection():
                host = mgr.environment.check_resolve_running()
                return {
                    "status": "disconnected",
                    "message": "Could not connect to DaVinci Resolve. Open a project and ensure external scripting is enabled in Resolve Preferences.",
                    "manager_status": {"status": "error", "resolve_running": host, "api_available": False},
                }

            resolve = mgr.get_connection()
            project_manager = resolve.GetProjectManager()
            current_project = project_manager.GetCurrentProject()
            return {
                "status": "connected",
                "version": resolve.GetVersionString(),
                "project_name": current_project.GetName() if current_project else None,
                "is_rendering": resolve.IsRenderingInProgress() if hasattr(resolve, "IsRenderingInProgress") else False,
            }
        except Exception as e:
            host = mgr.environment.check_resolve_running()
            err = str(e)
            if "scriptapp returned None" in err:
                hint = "Resolve is running but the scripting bridge isn't responding. Open a project and check Preferences > System > General > External Scripting."
            elif "not running" in err.lower():
                hint = "DaVinci Resolve is not running. Launch it from the top bar."
            else:
                hint = err
            return {
                "status": "disconnected",
                "message": hint,
                "manager_status": {"status": "error", "resolve_running": host, "api_available": False},
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/projects")
async def get_projects():
    """Get list of DaVinci Resolve projects (name/is_active dicts)."""
    try:
        from ..server import app as mcp_app
        from ..tools.project_tools import list_projects_impl

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            return {"status": "success", "current_project": None, "projects": []}

        result = await list_projects_impl(mcp_app)
        result.setdefault("status", "success")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/projects", status_code=201)
async def create_project(body: dict):
    """Create a new Resolve project. Body: { name, frame_rate?, width?, height?, template? }."""
    try:
        from ..server import app as mcp_app
        from ..tools.project_tools import create_project_impl

        result = await create_project_impl(
            mcp_app,
            body.get("name") or "",
            body.get("frame_rate", 24.0),
            body.get("width", 1920),
            body.get("height", 1080),
            body.get("template"),
        )
        return JSONResponse(status_code=201, content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/projects/{project_name}/settings")
async def get_project_settings(project_name: str):
    """Get settings for a project (current project settings + name echo)."""
    try:
        from ..server import app as mcp_app
        from ..tools.project_tools import get_project_settings_impl

        result = await get_project_settings_impl(mcp_app)
        result["project_name"] = project_name
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch("/projects/{project_name}/settings")
async def update_project_settings(project_name: str, body: dict):
    """Update project settings. Body: { setting: value, ... }."""
    try:
        from ..server import app as mcp_app
        from ..tools.project_tools import update_project_settings_impl

        result = await update_project_settings_impl(mcp_app, body)
        result["project_name"] = project_name
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/media/import")
async def import_media_upload(files: list[UploadFile] = File(...), target_folder: str = Form("")):
    """Upload media files and import them into the Resolve media pool."""
    import tempfile

    try:
        from ..server import app as mcp_app
        from ..tools.media_tools import import_media_impl

        staged: list[str] = []
        tmpdir = tempfile.mkdtemp(prefix="resolve_import_")
        try:
            for upload in files:
                dest = f"{tmpdir}/{upload.filename}"
                with open(dest, "wb") as f:
                    f.write(await upload.read())
                staged.append(dest)
            result = await import_media_impl(mcp_app, staged, target_folder or None)
            return result
        finally:
            import shutil

            shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/media")
async def list_media(folder_path: str = ""):
    """List media in the current (or given) media pool folder."""
    try:
        from ..server import app as mcp_app
        from ..tools.media_tools import list_media_impl

        return await list_media_impl(mcp_app, folder_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/media/folders", status_code=201)
async def create_media_folder(body: dict):
    """Create a folder in the media pool. Body: { name }."""
    try:
        from ..server import app as mcp_app
        from ..tools.media_tools import create_folder_impl

        result = await create_folder_impl(mcp_app, body.get("name") or "")
        return JSONResponse(
            status_code=201,
            content={"status": "success", "folder": {"name": body.get("name"), "path": result.get("path", "")}},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/media/metadata/{clip_name}")
async def get_media_metadata(clip_name: str):
    """Get metadata for a media item by clip name."""
    try:
        from ..server import app as mcp_app
        from ..tools.media_tools import get_media_metadata_impl

        return await get_media_metadata_impl(mcp_app, clip_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/timeline")
async def get_timeline_info():
    """Get basic info about the current timeline."""
    try:
        from ..server import app as mcp_app

        if not hasattr(mcp_app, "state") or not mcp_app.state.connection_manager:
            return {"timeline": None}

        mgr = mcp_app.state.connection_manager
        if not await mgr.ensure_connection():
            return {"timeline": None, "error": "not_connected"}

        resolve = mgr.get_connection()
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


# ── Host App Status & Launch ──────────────────────────────────────────


@router.get("/host-status")
async def get_host_status():
    """Probe if DaVinci Resolve is installed, running, and reachable (4-state lifecycle)."""
    try:
        from ..connection.host_app_probe import probe_host_app
        from ..connection.resolve_probe_config import RESOLVE_PROBE_CONFIG

        status = probe_host_app(**RESOLVE_PROBE_CONFIG)
        return {
            "success": True,
            **status.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/status")
async def api_status():
    """Server status with uptime, tool count, and version info."""
    return {
        "status": "ok",
        "server": "DaVinci Resolve MCP",
        "version": "0.1.0",
        "uptime_seconds": int(time.time() - _start_time) if "_start_time" in dir() else 0,
        "tool_count": 9,
    }


_start_time: float = 0.0


@router.on_event("startup")
async def _record_startup():
    global _start_time
    import time

    _start_time = time.time()


@router.get("/diagnostics")
async def api_diagnostics():
    """Full diagnostics for CUA-NSIS smoke testing."""
    import platform

    import psutil

    return {
        "status": "ok",
        "server": "DaVinci Resolve MCP",
        "version": "0.1.0",
        "uptime_seconds": int(time.time() - _start_time) if _start_time else 0,
        "tool_count": 9,
        "tools": [
            {"name": "resolve_project"},
            {"name": "resolve_media"},
            {"name": "resolve_timeline"},
            {"name": "resolve_color"},
            {"name": "resolve_render"},
            {"name": "resolve_audio"},
            {"name": "resolve_fairlight"},
            {"name": "resolve_subtitle"},
            {"name": "resolve_system"},
        ],
        "system": {
            "platform": platform.platform(),
            "cpu_percent": psutil.cpu_percent(interval=0),
            "memory_percent": psutil.virtual_memory().percent,
            "python_version": platform.python_version(),
        },
        "errors": [],
    }


@router.post("/shutdown")
async def api_shutdown():
    """Gracefully shut down the server (respond 200, then exit after flush)."""
    import threading

    threading.Timer(0.5, lambda: os._exit(0)).start()
    return {"success": True, "message": "Shutting down"}


@router.post("/host/launch")
async def launch_host():
    """Launch DaVinci Resolve if installed but not running."""
    try:
        from ..connection.host_app_probe import launch_app, probe_host_app
        from ..connection.resolve_probe_config import RESOLVE_PROBE_CONFIG

        status = probe_host_app(**RESOLVE_PROBE_CONFIG)
        ok, msg = launch_app(status)
        return {
            "success": ok,
            "message": msg,
            "previous_state": status.state.value,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Fleet standard surface ────────────────────────────────────────────


_TOOL_REGISTRY = [
    {"name": "resolve_project", "actions": ["create", "open", "list", "get_settings", "update_settings"]},
    {"name": "resolve_media", "actions": ["import", "list", "create_folder", "get_metadata"]},
    {
        "name": "resolve_timeline",
        "actions": [
            "create",
            "info",
            "add_clip",
            "cut",
            "set_playhead",
            "add_marker",
            "get_markers",
            "delete_marker",
            "add_keyframe",
            "get_keyframes",
            "delete_keyframe",
            "set_clip_property",
        ],
    },
    {
        "name": "resolve_color",
        "actions": [
            "create_node",
            "apply_lut",
            "set_color_space",
            "adjust_wheels",
            "grab_still",
            "get_stills",
            "apply_grade_from_still",
        ],
    },
    {"name": "resolve_render", "actions": ["timeline", "presets", "with_preset", "job_status"]},
    {"name": "resolve_audio", "actions": ["get_tracks", "add_effect", "adjust_levels", "normalize"]},
    {
        "name": "resolve_fairlight",
        "actions": [
            "open_page",
            "get_tracks",
            "set_mute",
            "set_solo",
            "set_volume",
            "track_eq",
            "track_send",
            "get_buses",
            "track_automation",
        ],
    },
    {"name": "resolve_subtitle", "actions": ["add", "get", "edit", "delete", "import_srt", "export_srt"]},
    {"name": "resolve_system", "actions": ["info", "status", "health", "help", "host_status", "host_launch"]},
]


@router.get("/capabilities")
async def api_capabilities():
    """Standard fleet capability shape for the webapp and IDE clients."""
    return {
        "status": "ok",
        "server": "DaVinci Resolve MCP",
        "version": "0.1.0",
        "transport": ["stdio", "http"],
        "ports": {"frontend": 10842, "backend": 10843},
        "tool_count": len(_TOOL_REGISTRY),
        "tools": _TOOL_REGISTRY,
        "features": {
            "portmanteau_tools": True,
            "agentic_workflows": True,
            "local_llm_proxy": True,
            "tauri_native": True,
        },
    }


@router.get("/skills")
async def api_skills():
    """Declared skill registry (static inventory of the 9 Resolve domains).

    Consumed by the Chat page on mount for skill-first prompt construction.
    """
    return {
        "skills": [
            {
                "name": name,
                "uri": f"skill://davinci-resolve/{name}",
                "description": f"DaVinci Resolve {name.removeprefix('resolve_')} operations "
                f"({', '.join(t['actions'][:4])}, ...)",
                "operations": t["actions"],
            }
            for name, t in ((t["name"], t) for t in _TOOL_REGISTRY)
        ]
    }


_LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234")


async def _probe_json(url: str, timeout: float = 3.0):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
    except Exception:
        return None


def _read_ollama_body(resp: httpx.Response) -> dict:
    """Parse an Ollama response body.

    Thinking models may return NDJSON chunks (one JSON object per line, with
    `thinking`/`response` fragments) even for non-streaming requests, which
    breaks a single ``resp.json()`` call ("Extra data"). Merge fragments.
    """
    try:
        data = resp.json()
    except Exception:
        data = None
    if isinstance(data, dict):
        return data
    merged: dict = {"response": "", "thinking": "", "done": True}
    for line in resp.text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            chunk = json.loads(line)
        except Exception:
            continue
        if isinstance(chunk, dict):
            merged["response"] += str(chunk.get("response", ""))
            merged["thinking"] += str(chunk.get("thinking", ""))
            merged.update({k: v for k, v in chunk.items() if k not in ("response", "thinking")})
    return merged


@router.get("/llm/discover")
async def llm_discover():
    """Auto-detect local LLM providers (Ollama :11434, LM Studio :1234)."""
    ollama = await _probe_json(f"{OLLAMA_URL}/api/tags")
    lmstudio = await _probe_json(f"{_LM_STUDIO_URL}/v1/models")
    return {
        "providers": [
            {"id": "ollama", "label": "Ollama", "detected": ollama is not None, "url": OLLAMA_URL},
            {"id": "lmstudio", "label": "LM Studio", "detected": lmstudio is not None, "url": _LM_STUDIO_URL},
        ]
    }


@router.get("/llm/providers")
async def llm_providers():
    """Provider registry: local detected flags + cloud configured flags (never key bytes).

    Also carries `ollama` / `lm_studio` model arrays in the shape the Settings
    page consumes: [{name}].
    """
    ollama = await _probe_json(f"{OLLAMA_URL}/api/tags")
    lmstudio = await _probe_json(f"{_LM_STUDIO_URL}/v1/models")
    ollama_models = [{"name": m.get("name")} for m in (ollama or {}).get("models", [])]
    lmstudio_models = [{"name": m.get("id")} for m in (lmstudio or {}).get("data", [])]
    return {
        "local": [
            {"id": "ollama", "detected": ollama is not None, "free": True},
            {"id": "lmstudio", "detected": lmstudio is not None, "free": True},
        ],
        "cloud": [
            {"id": "openai", "configured": bool(os.getenv("OPENAI_API_KEY"))},
            {"id": "anthropic", "configured": bool(os.getenv("ANTHROPIC_API_KEY"))},
        ],
        "ollama": ollama_models,
        "lm_studio": lmstudio_models,
    }


@router.get("/llm/onboarding")
async def llm_onboarding():
    """Fresh-install starter facts + recommended path for the under-hero cue."""
    ollama = await _probe_json(f"{OLLAMA_URL}/api/tags")
    models = [m.get("name") for m in (ollama or {}).get("models", [])] if ollama else []
    if models:
        return {
            "ready": True,
            "recommended": {"provider": "ollama", "model": models[0]},
            "facts": [f"Ollama detected with {len(models)} model(s). Chat is ready."],
        }
    return {
        "ready": False,
        "recommended": {"provider": "ollama", "model": None},
        "facts": [
            "No local LLM detected.",
            "Install Ollama (https://ollama.com) and pull a model, e.g. `ollama pull llama3.1:8b`.",
            "Resolve scripting works without an LLM; chat needs one.",
        ],
    }
