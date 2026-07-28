"""
Unit tests for subtitle operations: add, get, edit, delete, SRT import/export.
"""

import os
import tempfile
from unittest.mock import MagicMock

import pytest

from davinci_resolve_mcp.tools.subtitle_tools import (
    add_subtitle_impl,
    delete_subtitle_impl,
    edit_subtitle_impl,
    export_srt_impl,
    get_subtitles_impl,
    import_srt_impl,
)
from davinci_resolve_mcp.utils.exceptions import ResolveOperationError


class TestSubtitleOperations:
    """Tests for subtitle add/get/edit/delete."""

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
        timeline.GetName.return_value = "Test Timeline"
        timeline.GetTrackCount.return_value = 1
        project.GetCurrentTimeline.return_value = timeline
        project.GetTimelineByName.return_value = timeline
        resolve.GetProjectManager.return_value.GetCurrentProject.return_value = project
        mgr.get_connection.return_value = resolve
        return app

    @pytest.mark.asyncio
    async def test_add_subtitle_success(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        timeline.InsertSubtitle = MagicMock(return_value=MagicMock())
        timeline.InsertSubtitle.return_value.SetClipProperty = MagicMock()
        result = await add_subtitle_impl(
            mock_app, track_index=1, name="Sub1", start_frame=0, end_frame=48, text="Hello"
        )
        assert result["status"] == "success"
        assert result["name"] == "Sub1"
        assert result["text"] == "Hello"

    @pytest.mark.asyncio
    async def test_add_subtitle_no_api(self, mock_app):
        with pytest.raises(ResolveOperationError, match="InsertSubtitle not available"):
            await add_subtitle_impl(mock_app, track_index=1, name="S", start_frame=0, end_frame=10)

    @pytest.mark.asyncio
    async def test_add_subtitle_invalid_track(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        timeline.GetTrackCount.return_value = 0
        with pytest.raises(ResolveOperationError, match="Invalid subtitle track"):
            await add_subtitle_impl(mock_app, track_index=5, name="S", start_frame=0, end_frame=10)

    @pytest.mark.asyncio
    async def test_get_subtitles_empty(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        timeline.GetSubtitleList = MagicMock(return_value=[])
        result = await get_subtitles_impl(mock_app, track_index=1)
        assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_subtitles_no_tracks(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        timeline.GetTrackCount.return_value = 0
        result = await get_subtitles_impl(mock_app, track_index=1)
        assert result["count"] == 0
        assert "No subtitle tracks" in result["message"]

    @pytest.mark.asyncio
    async def test_get_subtitles_with_data(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        mock_item = MagicMock()
        mock_item.GetName.return_value = "Sub1"
        mock_item.GetStartFrame.return_value = 0
        mock_item.GetEndFrame.return_value = 48
        mock_item.GetClipProperty.return_value = "Hello"
        timeline.GetSubtitleList = MagicMock(return_value=[mock_item])
        result = await get_subtitles_impl(mock_app, track_index=1)
        assert result["count"] == 1
        assert result["subtitles"][0]["text"] == "Hello"

    @pytest.mark.asyncio
    async def test_edit_subtitle_success(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        mock_item = MagicMock()
        mock_item.SetClipProperty = MagicMock()
        mock_item.SetName = MagicMock()
        timeline.GetSubtitleList = MagicMock(return_value=[mock_item])
        result = await edit_subtitle_impl(mock_app, track_index=1, subtitle_index=0, text="Updated")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_subtitle_success(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        timeline.DeleteSubtitle = MagicMock()
        result = await delete_subtitle_impl(mock_app, track_index=1, subtitle_index=0)
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_import_srt_file(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        timeline.GetSetting.return_value = "24.0"
        mock_sub = MagicMock()
        mock_sub.SetClipProperty = MagicMock()
        timeline.InsertSubtitle = MagicMock(return_value=mock_sub)

        srt_content = """1
00:00:01,000 --> 00:00:03,000
Hello world

2
00:00:04,000 --> 00:00:06,000
Second line
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False, encoding="utf-8") as f:
            f.write(srt_content)
            srt_path = f.name

        try:
            result = await import_srt_impl(mock_app, srt_path=srt_path, track_index=1)
            assert result["status"] == "success"
            assert result["imported_count"] == 2
        finally:
            os.unlink(srt_path)

    @pytest.mark.asyncio
    async def test_import_srt_file_not_found(self, mock_app):
        with pytest.raises(ResolveOperationError, match="SRT file not found"):
            await import_srt_impl(mock_app, srt_path="nonexistent.srt")

    @pytest.mark.asyncio
    async def test_export_srt(self, mock_app):
        timeline = mock_app.state.connection_manager.get_connection.return_value.GetProjectManager.return_value.GetCurrentProject.return_value.GetCurrentTimeline.return_value
        timeline.GetSetting.return_value = "24.0"
        mock_item = MagicMock()
        mock_item.GetStartFrame.return_value = 0
        mock_item.GetEndFrame.return_value = 48
        mock_item.GetClipProperty.return_value = "Hello"
        timeline.GetSubtitleList = MagicMock(return_value=[mock_item])

        output = tempfile.mkstemp(suffix=".srt")[1]
        try:
            result = await export_srt_impl(mock_app, output_path=output)
            assert result["status"] == "success"
            assert result["exported_count"] == 1
            assert os.path.exists(output)
            with open(output, encoding="utf-8") as f:
                content = f.read()
                assert "Hello" in content
                assert "-->" in content
        finally:
            if os.path.exists(output):
                os.unlink(output)
