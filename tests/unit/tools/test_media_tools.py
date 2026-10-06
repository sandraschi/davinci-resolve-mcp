"""
Tests for the DaVinci Resolve media tools.
"""

from unittest.mock import MagicMock

import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from davinci_resolve_mcp.tools.media_tools import FolderInfo, MediaItem, register_tools
from tests.conftest import call_tool_dict


class TestMediaItem:
    """Tests for the MediaItem model."""

    def test_create_media_item(self):
        """Test creating a MediaItem instance with valid data."""
        media = MediaItem(
            name="test_video.mp4",
            file_path="/path/to/test_video.mp4",
            media_type="video",
            duration=60.5,
            frame_rate=29.97,
            resolution="1920x1080",
            channels=2,
            sample_rate=48000.0,
        )

        assert media.name == "test_video.mp4"
        assert media.file_path == "/path/to/test_video.mp4"
        assert media.media_type == "video"
        assert media.duration == 60.5
        assert media.frame_rate == 29.97
        assert media.resolution == "1920x1080"
        assert media.channels == 2
        assert media.sample_rate == 48000.0

    def test_media_item_validation(self):
        """Test MediaItem field validation."""
        # Name and file_path are required
        with pytest.raises(ValidationError):
            MediaItem(media_type="video")

        # media_type must be a string
        with pytest.raises(ValidationError):
            MediaItem(name="test", file_path="/test.mp4", media_type=123)

        # duration must be positive if provided
        with pytest.raises(ValidationError):
            MediaItem(name="test", file_path="/test.mp4", media_type="video", duration=-1.0)


class TestFolderInfo:
    """Tests for the FolderInfo model."""

    def test_create_folder_info(self):
        """Test creating a FolderInfo instance with valid data."""
        folder = FolderInfo(name="Videos", path="/Videos", item_count=5, subfolder_count=2)

        assert folder.name == "Videos"
        assert folder.path == "/Videos"
        assert folder.item_count == 5
        assert folder.subfolder_count == 2

    def test_folder_info_defaults(self):
        """Test FolderInfo default values."""
        folder = FolderInfo(name="Videos", path="/Videos")

        assert folder.item_count == 0
        assert folder.subfolder_count == 0


class TestMediaTools:
    """Tests for the media tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_resolve, mock_connection_manager):
        """Set up test environment."""
        self.app = FastMCP(name="Test App", instructions="Test application", version="0.1.0")

        # Register tools
        register_tools(self.app)

        # Set up connection manager in module state
        from davinci_resolve_mcp.server import app as server_app

        server_app.state.connection_manager = mock_connection_manager

        # Set up mocks
        self.mock_resolve = mock_resolve
        self.mock_project_manager = mock_resolve.GetProjectManager.return_value
        self.mock_project = self.mock_project_manager.GetCurrentProject.return_value
        self.mock_media_pool = self.mock_project.GetMediaPool.return_value

        # Set up connection manager (fresh FastMCP has no .state until assigned)
        from types import SimpleNamespace

        self.app.state = SimpleNamespace(connection_manager=mock_connection_manager)

        # Set up media pool mocks
        self.mock_media_pool.GetCurrentFolder.return_value = {"name": "Root"}
        self.mock_media_pool.GetRootFolder.return_value = {"name": "Root"}
        self.mock_media_pool.GetSubFolders.return_value = {}
        self.mock_media_pool.GetClipsInFolder.return_value = {}

    async def test_import_media_success(self, tmp_path):
        """Test importing media files successfully."""
        # Create test files
        video_file = tmp_path / "test_video.mp4"
        video_file.write_bytes(b"fake video data")

        # Mock media pool operations
        self.mock_media_pool.ImportMedia.return_value = True

        # Call the tool (FastMCP 3.x: async call_tool + structured dict)
        result = await call_tool_dict(self.app, "import_media", {"paths": [str(video_file)]})

        # Verify the result
        assert result["status"] == "success"
        assert result["imported_count"] == 1
        assert str(video_file) in result["imported_items"]

        # Verify the media was imported
        self.mock_media_pool.ImportMedia.assert_called_once()
        call_args = self.mock_media_pool.ImportMedia.call_args[0][0]
        assert str(video_file) in call_args

    async def test_import_media_to_folder(self, tmp_path):
        """Test importing media to a specific folder."""
        # Create test file
        video_file = tmp_path / "test_video.mp4"
        video_file.write_bytes(b"fake video data")

        # Mock folder operations
        mock_folder = MagicMock()
        self.mock_media_pool.AddSubFolder.return_value = mock_folder
        self.mock_media_pool.ImportMedia.return_value = True

        # Call the tool with a target folder
        result = await call_tool_dict(
            self.app, "import_media", {"paths": [str(video_file)], "target_folder": "Videos/Test"}
        )

        # Verify the result
        assert result["status"] == "success"

        # Verify the folder was created
        self.mock_media_pool.AddSubFolder.assert_called()
        self.mock_media_pool.SetCurrentFolder.assert_called_with(mock_folder)

    async def test_import_media_nonexistent_file(self):
        """Test importing a non-existent file."""
        # Call the tool with a non-existent file
        result = await call_tool_dict(self.app, "import_media", {"paths": ["/nonexistent/file.mp4"]})

        # Verify the result
        assert result["status"] == "failed"
        assert result["imported_count"] == 0
        assert result["failed_count"] == 1

    async def test_list_media_root(self):
        """Test listing media in the root folder."""
        # Mock media pool contents
        mock_clip = MagicMock()
        mock_clip.GetName.return_value = "test_clip.mp4"
        mock_clip.GetMediaPath.return_value = "/path/to/test_clip.mp4"
        mock_clip.GetClipProperty.side_effect = lambda x: {
            "Duration": "00:01:30:00",
            "FPS": "24.0",
            "Width": "1920",
            "Height": "1080",
            "Has Video": "1",
            "Has Audio": "1",
        }.get(x, "")

        self.mock_media_pool.GetClipsInFolder.return_value = {1: mock_clip}

        # Call the tool
        result = await call_tool_dict(self.app, "list_media", {})

        # Verify the result
        assert result["status"] == "success"
        assert result["current_folder"] == "/"
        assert len(result["media_items"]) == 1
        assert result["media_items"][0]["name"] == "test_clip.mp4"
        assert result["media_items"][0]["has_video"] is True

    async def test_list_media_subfolder(self):
        """Test listing media in a subfolder."""
        # Mock folder structure
        mock_subfolder = {"name": "Videos"}
        self.mock_media_pool.GetSubFolders.return_value = {"Videos": mock_subfolder}

        # Call the tool with a subfolder path
        result = await call_tool_dict(self.app, "list_media", {"folder_path": "Videos"})

        # Verify the result
        assert result["status"] == "success"
        assert result["current_folder"] == "Videos"

    async def test_create_folder_success(self):
        """Test creating a new folder."""
        # Mock folder creation
        mock_folder = {"name": "New Folder"}
        self.mock_media_pool.AddSubFolder.return_value = mock_folder

        # Call the tool (registered param is `path`)
        result = await call_tool_dict(self.app, "create_folder", {"path": "New Folder"})

        # Verify the result
        assert result["status"] == "success"
        assert "New Folder" in result["path"]
        self.mock_media_pool.AddSubFolder.assert_called_once()

    async def test_create_nested_folder_success(self):
        """Test creating a nested folder structure."""
        # Mock folder structure
        mock_parent = {"name": "Parent"}
        mock_child = {"name": "Child"}

        # First call: create parent, second call: create child
        self.mock_media_pool.AddSubFolder.side_effect = [mock_parent, mock_child]

        # Call the tool with a nested path (registered param is `path`)
        result = await call_tool_dict(self.app, "create_folder", {"path": "Parent/Child"})

        # Verify the result
        assert result["status"] == "success"
        assert "Parent/Child" in result["path"]
        assert self.mock_media_pool.AddSubFolder.call_count == 2

    async def test_get_media_metadata_success(self):
        """Test getting metadata for a media item."""
        # Mock clip (impl calls GetClipProperty() with no args for the full
        # dict, then per-key; the mock serves both)
        mock_clip = MagicMock()
        mock_clip.GetName.return_value = "test_clip.mp4"
        mock_clip.GetMediaPath.return_value = "/path/to/test_clip.mp4"
        all_props = {
            "Duration": "00:01:30:00",
            "FPS": "24.0",
            "Width": "1920",
            "Height": "1080",
            "Has Video": "1",
            "Has Audio": "1",
            "Audio Channels": "2",
            "Sample Rate": "48000",
            "Codec": "H.264",
            "File Size": "1024000",
            "Date Created": "2025-01-01 12:00:00",
            "Date Modified": "2025-01-01 12:30:00",
        }

        def _clip_props(*args):
            if not args:
                return dict(all_props)
            return all_props.get(args[0], "")

        mock_clip.GetClipProperty.side_effect = _clip_props

        # Mock media pool to return our clip
        self.mock_media_pool.GetClipsInFolder.return_value = {1: mock_clip}

        # Call the tool
        result = await call_tool_dict(self.app, "get_media_metadata", {"clip_path": "/path/to/test_clip.mp4"})

        # Verify the result
        assert result["status"] == "success"
        assert "metadata" in result
        metadata = result["metadata"]
        assert metadata["name"] == "test_clip.mp4"
        assert metadata["path"] == "/path/to/test_clip.mp4"
        assert metadata["type"] == "video"
        assert metadata["frame_rate"] == "24.0"
        assert metadata["resolution"] == "1920x1080"
        assert metadata["has_audio"] is True
        assert metadata["audio_channels"] == "2"

    async def test_get_media_metadata_not_found(self):
        """Test getting metadata for a non-existent media item."""
        # Mock empty media pool
        self.mock_media_pool.GetClipsInFolder.return_value = {}

        # Call the tool with a non-existent path and expect an exception
        # (individual tools raise; call .fn directly to bypass FastMCP error wrapping)
        get_metadata = (await self.app.get_tool("get_media_metadata")).fn
        with pytest.raises(Exception) as exc_info:
            await get_metadata(clip_path="/nonexistent/file.mp4")

        assert "not found" in str(exc_info.value).lower()
