"""
Integration tests for project-related tool workflows.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastmcp import FastMCP

from davinci_resolve_mcp.tools.media_tools import register_tools as register_media_tools
from davinci_resolve_mcp.tools.project_tools import register_tools
from tests.conftest import call_tool_dict


class TestProjectWorkflow:
    """Integration tests for project-related tool workflows."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_resolve, mock_connection_manager):
        """Set up test environment."""
        # Create a test app
        self.app = FastMCP(name="Test App", instructions="Test application", version="0.1.0")

        # Register tools
        register_tools(self.app)
        register_media_tools(self.app)

        # Set up mocks
        self.mock_resolve = mock_resolve
        self.mock_project_manager = mock_resolve.GetProjectManager.return_value
        self.mock_project = self.mock_project_manager.GetCurrentProject.return_value
        self.mock_media_pool = self.mock_project.GetMediaPool.return_value

        # Set up connection manager (fresh FastMCP has no .state until assigned)
        self.app.state = SimpleNamespace(connection_manager=mock_connection_manager)

        # Configure mock project
        self.test_project_name = "Test Project"
        self.mock_project.GetName.return_value = self.test_project_name
        # Stateful settings store: SetSetting writes, GetSetting reads (like Resolve)
        self._settings_store = {
            "timelineFrameRate": "24.0",
            "timelineResolutionWidth": "1920",
            "timelineResolutionHeight": "1080",
            "pixelAspectRatio": "1.0",
            "playbackFrameRate": "24.0",
            "timelineFormat": "HD 1080p 24",
        }
        self.mock_project.GetSetting.side_effect = lambda x: self._settings_store.get(x, "")
        self.mock_project.SetSetting.side_effect = lambda k, v: self._settings_store.update({k: v})

        # Seed the pool with one clip (import/list/metadata steps read it back)
        _clip_props = {
            "Duration": "00:01:30:00",
            "FPS": "24.0",
            "Width": "1920",
            "Height": "1080",
            "Has Video": "1",
            "Has Audio": "1",
        }
        _mock_clip = MagicMock()
        _mock_clip.GetName.return_value = "test_video.mp4"
        _mock_clip.GetMediaPath.return_value = "/pool/test_video.mp4"
        _mock_clip.GetClipProperty.side_effect = lambda *a: dict(_clip_props) if not a else _clip_props.get(a[0], "")
        _videos_folder = {"name": "Videos"}
        _test_folder = {"name": "Test"}

        def _subfolders(current):
            # Simulate the Videos/Test structure the workflow creates
            if current is _videos_folder:
                return {"Test": _test_folder}
            return {"Videos": _videos_folder}

        self.mock_media_pool.GetSubFolders.side_effect = _subfolders
        self.mock_media_pool.GetClipsInFolder.return_value = {1: _mock_clip}

    async def test_create_project_and_import_media_workflow(self, tmp_path):
        """Test the workflow of creating a project and importing media."""
        # Create a test media file
        test_video = tmp_path / "test_video.mp4"
        test_video.write_bytes(b"fake video data")

        # Step 1: Create a new project
        project_result = await call_tool_dict(
            self.app, "create_project", {"name": "New Project", "frame_rate": 30.0, "width": 1920, "height": 1080}
        )

        # Verify project creation
        assert project_result["status"] == "success"
        assert project_result["project"]["name"] == "New Project"
        assert project_result["project"]["frame_rate"] == 30.0
        assert project_result["project"]["resolution"] == "1920x1080"

        # Step 2: Create a folder in the media pool (registered param is `path`)
        folder_result = await call_tool_dict(self.app, "create_folder", {"path": "Videos/Test"})

        # Verify folder creation
        assert folder_result["status"] == "success"
        assert "Videos/Test" in folder_result["path"]

        # Step 3: Import media into the folder
        import_result = await call_tool_dict(
            self.app, "import_media", {"paths": [str(test_video)], "target_folder": "Videos/Test"}
        )

        # Verify media import
        assert import_result["status"] == "success"
        assert import_result["imported_count"] == 1
        assert str(test_video.name) in str(import_result["imported_items"])

        # Step 4: List media in the folder
        list_result = await call_tool_dict(self.app, "list_media", {"folder_path": "Videos/Test"})

        # Verify media listing
        assert list_result["status"] == "success"
        assert list_result["current_folder"] == "Videos/Test"
        assert len(list_result["media_items"]) > 0

        # Step 5: Get media metadata
        metadata_result = await call_tool_dict(self.app, "get_media_metadata", {"clip_path": str(test_video.name)})

        # Verify metadata retrieval
        assert metadata_result["status"] == "success"
        assert "metadata" in metadata_result
        assert metadata_result["metadata"]["name"] == test_video.name

    async def test_project_settings_workflow(self):
        """Test the workflow of updating and retrieving project settings."""
        # Step 1: Get current project settings
        initial_settings = await call_tool_dict(self.app, "get_project_settings", {})

        # Verify initial settings
        assert initial_settings["status"] == "success"
        assert initial_settings["project_name"] == self.test_project_name
        assert initial_settings["settings"]["timelineFrameRate"] == "24.0"

        # Step 2: Update project settings
        update_result = await call_tool_dict(
            self.app,
            "update_project_settings",
            {
                "settings": {
                    "timelineFrameRate": "30.0",
                    "timelineResolutionWidth": "1280",
                    "timelineResolutionHeight": "720",
                }
            },
        )

        # Verify settings update
        assert update_result["status"] == "success"
        assert "updated_settings" in update_result

        # Step 3: Verify updated settings
        updated_settings = await call_tool_dict(self.app, "get_project_settings", {})
        assert updated_settings["status"] == "success"
        assert updated_settings["settings"]["timelineFrameRate"] == "30.0"
        assert updated_settings["settings"]["timelineResolutionWidth"] == "1280"
        assert updated_settings["settings"]["timelineResolutionHeight"] == "720"

    async def test_project_switching_workflow(self):
        """Test the workflow of switching between projects."""
        # Set up mock for project list
        self.mock_project_manager.GetProjectListInCurrentFolder.return_value = [
            "Project 1",
            "Project 2",
            self.test_project_name,
        ]

        # Step 1: List all projects (impl returns name/is_active dicts)
        projects_result = await call_tool_dict(self.app, "list_projects", {})

        # Verify project listing
        assert projects_result["status"] == "success"
        assert self.test_project_name in [p["name"] for p in projects_result["projects"]]

        # Step 2: Create a mock for the new project
        mock_new_project = MagicMock()
        mock_new_project.GetName.return_value = "Project 2"
        mock_new_project.GetSetting.side_effect = lambda x: {
            "timelineFrameRate": "25.0",
            "timelineResolutionWidth": "1920",
            "timelineResolutionHeight": "1080",
            "pixelAspectRatio": "1.0",
            "playbackFrameRate": "25.0",
            "timelineFormat": "HD 1080p 25",
        }.get(x, "")

        # Configure project loading
        self.mock_project_manager.LoadProject.return_value = mock_new_project

        # Step 3: Open a different project
        open_result = await call_tool_dict(self.app, "open_project", {"name": "Project 2"})

        # Verify project was opened
        assert open_result["status"] == "success"
        assert open_result["project"]["name"] == "Project 2"
        assert open_result["project"]["frame_rate"] == 25.0

        # Verify the project was loaded
        self.mock_project_manager.LoadProject.assert_called_once_with("Project 2")

        # Step 4: Verify current project is updated
        settings_result = await call_tool_dict(self.app, "get_project_settings", {})

        # Verify we're now looking at the new project's settings
        assert settings_result["status"] == "success"
        assert settings_result["project_name"] == "Project 2"
        assert settings_result["settings"]["timelineFrameRate"] == "25.0"
