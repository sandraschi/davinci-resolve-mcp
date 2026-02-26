"""
FastMCP API routes for DaVinci Resolve MCP.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["v1"])


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


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
