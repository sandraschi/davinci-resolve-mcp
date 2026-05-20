"""
Integration tests for the DaVinci Resolve MCP API endpoints.
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from davinci_resolve_mcp.config import DaVinciResolveConfig
from davinci_resolve_mcp.server import AppState, app


class TestResolveAPI:
    """Integration tests for the DaVinci Resolve MCP API."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path, mock_resolve, mock_connection_manager):
        """Set up test environment."""
        # Create a test config
        self.config = DaVinciResolveConfig()

        # Create a test app with our mocks
        self.test_app = app

        # Set up app state with our mocks
        self.test_app.state = AppState(self.config)
        self.test_app.state.connection_manager = mock_connection_manager

        # Create a test client
        self.client = TestClient(self.test_app)

        # Set up test data
        self.test_project_name = "Test Project"
        self.test_media_path = str(tmp_path / "test_video.mp4")

        # Create a test media file
        with open(self.test_media_path, 'wb') as f:
            f.write(b"fake video data")

        # Set up mock Resolve instance
        self.mock_resolve = mock_resolve
        self.mock_project_manager = mock_resolve.GetProjectManager.return_value
        self.mock_project = self.mock_project_manager.GetCurrentProject.return_value
        self.mock_media_pool = self.mock_project.GetMediaPool.return_value

        # Configure mock project
        self.mock_project.GetName.return_value = self.test_project_name
        self.mock_project.GetSetting.side_effect = lambda x: {
            'timelineFrameRate': '24.0',
            'timelineResolutionWidth': '1920',
            'timelineResolutionHeight': '1080',
            'pixelAspectRatio': '1.0',
            'playbackFrameRate': '24.0',
            'timelineFormat': 'HD 1080p 24'
        }.get(x, '')

        # Configure mock media pool
        self.mock_media_pool.GetCurrentFolder.return_value = {"name": "Root"}
        self.mock_media_pool.GetRootFolder.return_value = {"name": "Root"}
        self.mock_media_pool.GetSubFolders.return_value = {}
        self.mock_media_pool.GetClipsInFolder.return_value = {}

    def test_get_resolve_info(self):
        """Test getting Resolve information."""
        # Configure mock
        self.mock_resolve.GetVersionString.return_value = "18.5.0"
        self.mock_resolve.GetApiVersion.return_value = "1.0"
        self.mock_resolve.IsConsole.return_value = False

        # Make the request
        response = self.client.get("/api/v1/resolve/info")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["version"] == "18.5.0"
        assert data["api_version"] == "1.0"
        assert data["is_console"] is False

    def test_list_projects(self):
        """Test listing all projects."""
        # Configure mock
        self.mock_project_manager.GetProjectListInCurrentFolder.return_value = [
            "Project 1",
            self.test_project_name,
            "Project 2"
        ]

        # Make the request
        response = self.client.get("/api/v1/projects")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["current_project"] == self.test_project_name
        assert "Project 1" in data["projects"]
        assert self.test_project_name in data["projects"]
        assert "Project 2" in data["projects"]

    def test_create_project(self):
        """Test creating a new project."""
        # Configure mock
        self.mock_project_manager.CreateProject.return_value = self.mock_project
        self.mock_project.SaveProject.return_value = True

        # Test data
        project_data = {
            "name": "New Project",
            "frame_rate": 30.0,
            "width": 1920,
            "height": 1080
        }

        # Make the request
        response = self.client.post("/api/v1/projects", json=project_data)

        # Verify the response
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["project"]["name"] == project_data["name"]
        assert data["project"]["frame_rate"] == project_data["frame_rate"]
        assert data["project"]["resolution"] == f"{project_data['width']}x{project_data['height']}"

        # Verify the project was created with the correct settings
        self.mock_project_manager.CreateProject.assert_called_once_with(project_data["name"])
        self.mock_project.SetSetting.assert_any_call('timelineFrameRate', str(project_data["frame_rate"]))
        self.mock_project.SetSetting.assert_any_call('timelineResolutionWidth', str(project_data["width"]))
        self.mock_project.SetSetting.assert_any_call('timelineResolutionHeight', str(project_data["height"]))

    def test_get_project_settings(self):
        """Test getting project settings."""
        # Make the request
        response = self.client.get(f"/api/v1/projects/{self.test_project_name}/settings")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["project_name"] == self.test_project_name
        assert "settings" in data
        assert data["settings"]["timelineFrameRate"] == "24.0"
        assert data["settings"]["timelineResolutionWidth"] == "1920"
        assert data["settings"]["timelineResolutionHeight"] == "1080"

    def test_update_project_settings(self):
        """Test updating project settings."""
        # Configure mock
        self.mock_project.SaveProject.return_value = True

        # Test data
        settings_update = {
            "timelineFrameRate": "30.0",
            "timelineResolutionWidth": "1280",
            "timelineResolutionHeight": "720"
        }

        # Make the request
        response = self.client.patch(
            f"/api/v1/projects/{self.test_project_name}/settings",
            json=settings_update
        )

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["project_name"] == self.test_project_name
        assert "updated_settings" in data

        # Verify the settings were updated
        self.mock_project.SetSetting.assert_any_call("timelineFrameRate", "30.0")
        self.mock_project.Setting.assert_any_call("timelineResolutionWidth", "1280")
        self.mock_project.Setting.assert_any_call("timelineResolutionHeight", "720")

    def test_import_media(self):
        """Test importing media files."""
        # Configure mock
        self.mock_media_pool.ImportMedia.return_value = True

        # Create a test file
        test_file_path = self.test_media_path

        # Prepare file upload
        files = [("files", (Path(test_file_path).name, open(test_file_path, "rb")))]

        # Make the request
        response = self.client.post(
            "/api/v1/media/import",
            files=files,
            data={"target_folder": ""}
        )

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["imported_count"] == 1
        assert Path(test_file_path).name in str(data["imported_items"])

    def test_list_media(self):
        """Test listing media in the current folder."""
        # Configure mock
        mock_clip = MagicMock()
        mock_clip.GetName.return_value = "test_clip.mp4"
        mock_clip.GetMediaPath.return_value = "/path/to/test_clip.mp4"
        mock_clip.GetClipProperty.side_effect = lambda x: {
            "Duration": "00:01:30:00",
            "FPS": "24.0",
            "Width": "1920",
            "Height": "1080",
            "Has Video": "1",
            "Has Audio": "1"
        }.get(x, "")

        self.mock_media_pool.GetClipsInFolder.return_value = {1: mock_clip}

        # Make the request
        response = self.client.get("/api/v1/media")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["current_folder"] == "/"
        assert len(data["media_items"]) == 1
        assert data["media_items"][0]["name"] == "test_clip.mp4"
        assert data["media_items"][0]["has_video"] is True

    def test_create_folder(self):
        """Test creating a new folder in the media pool."""
        # Configure mock
        mock_folder = {"name": "New Folder"}
        self.mock_media_pool.AddSubFolder.return_value = mock_folder

        # Test data
        folder_data = {"name": "New Folder"}

        # Make the request
        response = self.client.post("/api/v1/media/folders", json=folder_data)

        # Verify the response
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["folder"]["name"] == "New Folder"
        assert "path" in data["folder"]

        # Verify the folder was created
        self.mock_media_pool.AddSubFolder.assert_called_once()

    def test_get_media_metadata(self):
        """Test getting metadata for a media item."""
        # Configure mock
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
            "Audio Channels": "2",
            "Sample Rate": "48000",
            "Codec": "H.264",
            "File Size": "1024000",
            "Date Created": "2025-01-01 12:00:00",
            "Date Modified": "2025-01-01 12:30:00"
        }.get(x, "")

        self.mock_media_pool.GetClipsInFolder.return_value = {1: mock_clip}

        # Make the request
        response = self.client.get("/api/v1/media/metadata/test_clip.mp4")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "metadata" in data
        assert data["metadata"]["name"] == "test_clip.mp4"
        assert data["metadata"]["type"] == "video"
        assert data["metadata"]["frame_rate"] == "24.0"
        assert data["metadata"]["resolution"] == "1920x1080"
        assert data["metadata"]["has_audio"] is True
        assert data["metadata"]["audio_channels"] == "2"
