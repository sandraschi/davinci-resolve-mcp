"""
Tests for the DaVinci Resolve project tools.
"""
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from davinci_resolve_mcp.tools.project_tools import ProjectInfo, ProjectSettings, register_tools


class TestProjectInfo:
    """Tests for the ProjectInfo model."""

    def test_create_project_info(self):
        """Test creating a ProjectInfo instance with valid data."""
        project = ProjectInfo(
            name="Test Project",
            path="/path/to/project.drp",
            frame_rate=24.0,
            resolution="1920x1080",
            is_active=True
        )

        assert project.name == "Test Project"
        assert project.path == "/path/to/project.drp"
        assert project.frame_rate == 24.0
        assert project.resolution == "1920x1080"
        assert project.is_active is True

    def test_project_info_validation(self):
        """Test ProjectInfo field validation."""
        # Name is required
        with pytest.raises(ValidationError):
            ProjectInfo()

        # Name must be a string
        with pytest.raises(ValidationError):
            ProjectInfo(name=123)

        # Frame rate must be a positive number if provided
        with pytest.raises(ValidationError):
            ProjectInfo(name="Test", frame_rate=-1.0)


class TestProjectSettings:
    """Tests for the ProjectSettings model."""

    def test_create_project_settings(self):
        """Test creating a ProjectSettings instance with valid data."""
        settings = ProjectSettings(
            frame_rate=30.0,
            resolution_width=1920,
            resolution_height=1080,
            pixel_aspect_ratio=1.0,
            playback_framerate=30.0,
            timeline_format="HD 1080p 30"
        )

        assert settings.frame_rate == 30.0
        assert settings.resolution_width == 1920
        assert settings.resolution_height == 1080
        assert settings.pixel_aspect_ratio == 1.0
        assert settings.playback_framerate == 30.0
        assert settings.timeline_format == "HD 1080p 30"

    def test_project_settings_validation(self):
        """Test ProjectSettings field validation."""
        # Frame rate must be within valid range
        with pytest.raises(ValidationError):
            ProjectSettings(frame_rate=0)

        # Resolution width must be within valid range
        with pytest.raises(ValidationError):
            ProjectSettings(resolution_width=100)

        # Resolution height must be within valid range
        with pytest.raises(ValidationError):
            ProjectSettings(resolution_height=100)

        # Pixel aspect ratio must be within valid range
        with pytest.raises(ValidationError):
            ProjectSettings(pixel_aspect_ratio=0.1, resolution_width=1920, resolution_height=1080)


class TestProjectTools:
    """Tests for the project tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_resolve, mock_connection_manager):
        """Set up test environment."""
        self.app = FastMCP(
            name="Test App",
            instructions="Test application",
            version="0.1.0"
        )

        # Register tools
        register_tools(self.app)

        # Set up mocks
        self.mock_resolve = mock_resolve
        self.mock_project_manager = mock_resolve.GetProjectManager.return_value
        self.mock_project = self.mock_project_manager.GetCurrentProject.return_value

        # Set up connection manager in module state
        from davinci_resolve_mcp.server import app as server_app
        server_app.state.connection_manager = mock_connection_manager

        # Set up project manager return values
        self.mock_project_manager.GetProjectListInCurrentFolder.return_value = ["Project 1", "Test Project"]
        self.mock_project.GetName.return_value = "Test Project"
        self.mock_project.GetSetting.side_effect = lambda x: {
            'timelineFrameRate': '24.0',
            'timelineResolutionWidth': '1920',
            'timelineResolutionHeight': '1080',
            'pixelAspectRatio': '1.0',
            'playbackFrameRate': '24.0',
            'timelineFormat': 'HD 1080p 24'
        }.get(x, '')

    async def test_create_project_success(self):
        """Test creating a new project successfully."""
        # Mock project creation
        self.mock_project_manager.CreateProject.return_value = self.mock_project
        self.mock_project.SaveProject.return_value = True

        # Get the create_project tool
        create_project = self.app.get_tool("create_project")

        # Call the tool
        result = await create_project("New Project", 30.0, 1920, 1080)

        # Verify the result
        assert result["status"] == "success"
        assert result["project"]["name"] == "New Project"
        assert result["project"]["frame_rate"] == 30.0
        assert result["project"]["resolution"] == "1920x1080"

        # Verify the project was created with the correct settings
        self.mock_project_manager.CreateProject.assert_called_once_with("New Project")
        self.mock_project.SetSetting.assert_any_call('timelineFrameRate', '30.0')
        self.mock_project.SetSetting.assert_any_call('timelineResolutionWidth', '1920')
        self.mock_project.SetSetting.assert_any_call('timelineResolutionHeight', '1080')
        self.mock_project.SaveProject.assert_called_once()

    async def test_create_project_failure(self):
        """Test project creation failure."""
        # Mock project creation failure
        self.mock_project_manager.CreateProject.return_value = None

        # Get the create_project tool
        create_project = self.app.get_tool("create_project")

        # Call the tool and expect an exception
        with pytest.raises(Exception) as exc_info:
            await create_project("New Project")

        assert "Failed to create project" in str(exc_info.value)

    async def test_open_project_success(self):
        """Test opening an existing project successfully."""
        # Mock project loading
        self.mock_project_manager.LoadProject.return_value = self.mock_project

        # Get the open_project tool
        open_project = self.app.get_tool("open_project")

        # Call the tool
        result = await open_project("Test Project")

        # Verify the result
        assert result["status"] == "success"
        assert result["project"]["name"] == "Test Project"
        assert result["project"]["frame_rate"] == 24.0
        assert result["project"]["resolution"] == "1920x1080"

        # Verify the project was loaded
        self.mock_project_manager.LoadProject.assert_called_once_with("Test Project")

    async def test_open_project_not_found(self):
        """Test opening a non-existent project."""
        # Mock project not found
        self.mock_project_manager.LoadProject.return_value = None

        # Get the open_project tool
        open_project = self.app.get_tool("open_project")

        # Call the tool and expect an exception
        with pytest.raises(Exception) as exc_info:
            await open_project("Nonexistent Project")

        assert "not found" in str(exc_info.value).lower()

    async def test_list_projects(self):
        """Test listing all projects."""
        # Set up test data
        self.mock_project_manager.GetProjectListInCurrentFolder.return_value = ["Project 1", "Project 2"]

        # Get the list_projects tool
        list_projects = self.app.get_tool("list_projects")

        # Call the tool
        result = await list_projects()

        # Verify the result
        assert result["status"] == "success"
        assert result["current_project"] == "Test Project"
        assert "Project 1" in result["projects"]
        assert "Project 2" in result["projects"]

    async def test_get_project_settings(self):
        """Test getting project settings."""
        # Get the get_project_settings tool
        get_settings = self.app.get_tool("get_project_settings")

        # Call the tool
        result = await get_settings()

        # Verify the result
        assert result["status"] == "success"
        assert result["project_name"] == "Test Project"
        assert "settings" in result
        assert result["settings"]["timelineFrameRate"] == "24.0"
        assert result["settings"]["timelineResolutionWidth"] == "1920"
        assert result["settings"]["timelineResolutionHeight"] == "1080"

    async def test_update_project_settings(self):
        """Test updating project settings."""
        # Mock project save
        self.mock_project.SaveProject.return_value = True

        # Get the update_project_settings tool
        update_settings = self.app.get_tool("update_project_settings")

        # Call the tool
        result = await update_settings({
            "timelineFrameRate": "30.0",
            "timelineResolutionWidth": "1280",
            "timelineResolutionHeight": "720"
        })

        # Verify the result
        assert result["status"] == "success"
        assert result["project_name"] == "Test Project"
        assert "updated_settings" in result

        # Verify the settings were updated
        self.mock_project.SetSetting.assert_any_call("timelineFrameRate", "30.0")
        self.mock_project.SetSetting.assert_any_call("timelineResolutionWidth", "1280")
        self.mock_project.SetSetting.assert_any_call("timelineResolutionHeight", "720")
        self.mock_project.SaveProject.assert_called_once()
