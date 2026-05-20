"""
Integration tests for project-related tool workflows.
"""
from unittest.mock import MagicMock

import pytest
from fastmcp import FastMCP

from davinci_resolve_mcp.tools.media_tools import register_tools as register_media_tools
from davinci_resolve_mcp.tools.project_tools import register_tools


class TestProjectWorkflow:
    """Integration tests for project-related tool workflows."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_resolve, mock_connection_manager):
        """Set up test environment."""
        # Create a test app
        self.app = FastMCP(
            name="Test App",
            instructions="Test application",
            version="0.1.0"
        )

        # Register tools
        register_tools(self.app)
        register_media_tools(self.app)

        # Set up mocks
        self.mock_resolve = mock_resolve
        self.mock_project_manager = mock_resolve.GetProjectManager.return_value
        self.mock_project = self.mock_project_manager.GetCurrentProject.return_value
        self.mock_media_pool = self.mock_project.GetMediaPool.return_value

        # Set up connection manager
        self.app.state.connection_manager = mock_connection_manager

        # Configure mock project
        self.test_project_name = "Test Project"
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

    async def test_create_project_and_import_media_workflow(self, tmp_path):
        """Test the workflow of creating a project and importing media."""
        # Create a test media file
        test_video = tmp_path / "test_video.mp4"
        test_video.write_bytes(b"fake video data")

        # Step 1: Create a new project
        create_project = self.app.get_tool("create_project")
        project_result = await create_project(
            "New Project",
            frame_rate=30.0,
            width=1920,
            height=1080
        )

        # Verify project creation
        assert project_result["status"] == "success"
        assert project_result["project"]["name"] == "New Project"
        assert project_result["project"]["frame_rate"] == 30.0
        assert project_result["project"]["resolution"] == "1920x1080"

        # Step 2: Create a folder in the media pool
        create_folder = self.app.get_tool("create_folder")
        folder_result = await create_folder("Videos/Test")

        # Verify folder creation
        assert folder_result["status"] == "success"
        assert "Videos/Test" in folder_result["path"]

        # Step 3: Import media into the folder
        import_media = self.app.get_tool("import_media")
        import_result = await import_media(
            paths=[str(test_video)],
            target_folder="Videos/Test"
        )

        # Verify media import
        assert import_result["status"] == "success"
        assert import_result["imported_count"] == 1
        assert str(test_video.name) in str(import_result["imported_items"])

        # Step 4: List media in the folder
        list_media = self.app.get_tool("list_media")
        list_result = await list_media("Videos/Test")

        # Verify media listing
        assert list_result["status"] == "success"
        assert list_result["current_folder"] == "Videos/Test"
        assert len(list_result["media_items"]) > 0

        # Step 5: Get media metadata
        get_metadata = self.app.get_tool("get_media_metadata")
        metadata_result = await get_metadata(str(test_video.name))

        # Verify metadata retrieval
        assert metadata_result["status"] == "success"
        assert "metadata" in metadata_result
        assert metadata_result["metadata"]["name"] == test_video.name

    async def test_project_settings_workflow(self):
        """Test the workflow of updating and retrieving project settings."""
        # Step 1: Get current project settings
        get_settings = self.app.get_tool("get_project_settings")
        initial_settings = await get_settings()

        # Verify initial settings
        assert initial_settings["status"] == "success"
        assert initial_settings["project_name"] == self.test_project_name
        assert initial_settings["settings"]["timelineFrameRate"] == "24.0"

        # Step 2: Update project settings
        update_settings = self.app.get_tool("update_project_settings")
        update_result = await update_settings({
            "timelineFrameRate": "30.0",
            "timelineResolutionWidth": "1280",
            "timelineResolutionHeight": "720"
        })

        # Verify settings update
        assert update_result["status"] == "success"
        assert "updated_settings" in update_result

        # Step 3: Verify updated settings
        updated_settings = await get_settings()
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
            self.test_project_name
        ]

        # Step 1: List all projects
        list_projects = self.app.get_tool("list_projects")
        projects_result = await list_projects()

        # Verify project listing
        assert projects_result["status"] == "success"
        assert self.test_project_name in projects_result["projects"]

        # Step 2: Create a mock for the new project
        mock_new_project = MagicMock()
        mock_new_project.GetName.return_value = "Project 2"
        mock_new_project.GetSetting.side_effect = lambda x: {
            'timelineFrameRate': '25.0',
            'timelineResolutionWidth': '1920',
            'timelineResolutionHeight': '1080',
            'pixelAspectRatio': '1.0',
            'playbackFrameRate': '25.0',
            'timelineFormat': 'HD 1080p 25'
        }.get(x, '')

        # Configure project loading
        self.mock_project_manager.LoadProject.return_value = mock_new_project

        # Step 3: Open a different project
        open_project = self.app.get_tool("open_project")
        open_result = await open_project("Project 2")

        # Verify project was opened
        assert open_result["status"] == "success"
        assert open_result["project"]["name"] == "Project 2"
        assert open_result["project"]["frame_rate"] == 25.0

        # Verify the project was loaded
        self.mock_project_manager.LoadProject.assert_called_once_with("Project 2")

        # Step 4: Verify current project is updated
        get_settings = self.app.get_tool("get_project_settings")
        settings_result = await get_settings()

        # Verify we're now looking at the new project's settings
        assert settings_result["status"] == "success"
        assert settings_result["project_name"] == "Project 2"
        assert settings_result["settings"]["timelineFrameRate"] == "25.0"
