"""
Unit tests for timeline markers, keyframes, and extended operations.

These tests validate the new _impl functions added in Phase 2-3.
"""

from unittest.mock import MagicMock

import pytest

from davinci_resolve_mcp.tools.timeline_tools import (
    add_keyframe_impl,
    add_marker_impl,
    delete_keyframe_impl,
    delete_marker_impl,
    get_keyframes_impl,
    get_markers_impl,
)
from davinci_resolve_mcp.utils.exceptions import ResolveOperationError


class TestMarkerOperations:
    """Tests for timeline marker add/get/delete operations."""

    @pytest.fixture
    def mock_app(self):
        app = MagicMock()
        app.state = MagicMock()
        app.state.connection_manager = MagicMock()
        mgr = app.state.connection_manager
        mgr.resolve = MagicMock()
        project = MagicMock()
        timeline = MagicMock()
        timeline.GetName.return_value = "Test Timeline"
        project.GetCurrentTimeline.return_value = timeline
        project.GetTimelineByName.return_value = timeline
        mgr.current_project = project
        return app

    @pytest.mark.asyncio
    async def test_add_marker_success(self, mock_app):
        mock_app.state.connection_manager.current_project.GetCurrentTimeline.return_value.AddMarker = MagicMock()
        result = await add_marker_impl(mock_app, frame=120, color="Red", name="VFX", note="Add explosion", duration=5)
        assert result["status"] == "success"
        assert result["color"] == "Red"
        assert result["frame"] == 120
        assert result["name"] == "VFX"

    @pytest.mark.asyncio
    async def test_add_marker_invalid_color_fallback(self, mock_app):
        mock_app.state.connection_manager.current_project.GetCurrentTimeline.return_value.AddMarker = MagicMock()
        result = await add_marker_impl(mock_app, frame=50, color="Magenta")
        assert result["color"] == "Blue"

    @pytest.mark.asyncio
    async def test_add_marker_no_api_support(self, mock_app):
        timeline = mock_app.state.connection_manager.current_project.GetCurrentTimeline.return_value
        del timeline.AddMarker
        timeline.AddMarker = None
        with pytest.raises(ResolveOperationError, match="does not support AddMarker"):
            await add_marker_impl(mock_app, frame=0)

    @pytest.mark.asyncio
    async def test_get_markers_empty(self, mock_app):
        timeline = mock_app.state.connection_manager.current_project.GetCurrentTimeline.return_value
        timeline.GetMarkers.return_value = {}
        result = await get_markers_impl(mock_app)
        assert result["status"] == "success"
        assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_markers_with_data(self, mock_app):
        timeline = mock_app.state.connection_manager.current_project.GetCurrentTimeline.return_value
        timeline.GetMarkers.return_value = {
            "0": {"color": "Blue", "name": "Start", "note": "", "duration": 1},
            "100": {"color": "Red", "name": "Cut", "note": "Action", "duration": 1},
        }
        result = await get_markers_impl(mock_app)
        assert result["count"] == 2
        assert result["markers"][0]["color"] == "Blue"

    @pytest.mark.asyncio
    async def test_delete_marker_success(self, mock_app):
        timeline = mock_app.state.connection_manager.current_project.GetCurrentTimeline.return_value
        timeline.DeleteMarkerAtFrame = MagicMock()
        result = await delete_marker_impl(mock_app, frame=120)
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_marker_with_named_timeline(self, mock_app):
        timeline = mock_app.state.connection_manager.current_project.GetTimelineByName.return_value
        timeline.AddMarker = MagicMock()
        timeline.GetName.return_value = "Named Timeline"
        result = await add_marker_impl(mock_app, frame=0, timeline_name="Named Timeline")
        assert result["timeline_name"] == "Named Timeline"

    @pytest.mark.asyncio
    async def test_no_connection_raises(self, mock_app):
        mock_app.state.connection_manager.resolve = None
        with pytest.raises(ResolveOperationError, match="Not connected"):
            await add_marker_impl(mock_app, frame=0)


class TestKeyframeOperations:
    """Tests for clip keyframe add/get/delete operations."""

    @pytest.fixture
    def mock_app(self):
        app = MagicMock()
        app.state = MagicMock()
        app.state.connection_manager = MagicMock()
        mgr = app.state.connection_manager
        mgr.resolve = MagicMock()
        resolve = MagicMock()
        project = MagicMock()
        timeline = MagicMock()
        clip = MagicMock()
        clip.GetName.return_value = "Test Clip"
        timeline.GetCurrentVideoItem.return_value = clip
        timeline.GetName.return_value = "Test Timeline"
        project.GetCurrentTimeline.return_value = timeline
        project.GetTimelineByName.return_value = timeline
        resolve.GetProjectManager.return_value.GetCurrentProject.return_value = project
        mgr.get_connection.return_value = resolve
        return app

    @pytest.mark.asyncio
    async def test_add_keyframe_success(self, mock_app):
        clip = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value.GetCurrentVideoItem.return_value
        clip.AddKeyframe = MagicMock()
        result = await add_keyframe_impl(mock_app, clip_path="", property_name="Zoom", frame=0, value=1.0)
        assert result["status"] == "success"
        assert result["value"] == 1.0

    @pytest.mark.asyncio
    async def test_add_keyframe_no_api(self, mock_app):
        with pytest.raises(ResolveOperationError, match="does not support AddKeyframe"):
            await add_keyframe_impl(mock_app, clip_path="", property_name="Zoom", frame=0, value=2.0)

    @pytest.mark.asyncio
    async def test_get_keyframes_with_data(self, mock_app):
        clip = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value.GetCurrentVideoItem.return_value
        clip.GetKeyframeList = MagicMock(return_value={0: 1.0, 24: 1.2, 48: 1.5})
        result = await get_keyframes_impl(mock_app, property_name="Zoom")
        assert result["count"] == 3

    @pytest.mark.asyncio
    async def test_delete_keyframe_success(self, mock_app):
        clip = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value.GetCurrentVideoItem.return_value
        clip.DeleteKeyframe = MagicMock()
        result = await delete_keyframe_impl(mock_app, property_name="Zoom", frame=24)
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_keyframe_no_clip_raises(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        timeline.GetCurrentVideoItem.return_value = None
        with pytest.raises(ResolveOperationError, match="No clip"):
            await add_keyframe_impl(mock_app, clip_path="", property_name="Zoom", frame=0, value=1.0)
