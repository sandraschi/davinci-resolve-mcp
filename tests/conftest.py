"""
Pytest configuration and fixtures for DaVinci Resolve MCP tests.
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add source directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / 'test_data'
os.makedirs(TEST_DATA_DIR, exist_ok=True)

# Fixtures
@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to the test data directory."""
    return TEST_DATA_DIR

@pytest.fixture
def mock_resolve():
    """Create a mock DaVinci Resolve instance."""
    mock_resolve = MagicMock()
    
    # Mock project manager
    mock_project_manager = MagicMock()
    mock_project = MagicMock()
    
    # Set up mock project properties
    mock_project.GetName.return_value = "Test Project"
    mock_project.GetSetting.side_effect = lambda x: {
        'timelineFrameRate': '24.0',
        'timelineResolutionWidth': '1920',
        'timelineResolutionHeight': '1080',
        'pixelAspectRatio': '1.0',
        'playbackFrameRate': '24.0',
        'timelineFormat': 'HD 1080p 24'
    }.get(x, '')
    
    mock_project_manager.GetCurrentProject.return_value = mock_project
    mock_project_manager.GetProjectListInCurrentFolder.return_value = ["Project 1", "Test Project", "Project 2"]
    
    mock_resolve.GetProjectManager.return_value = mock_project_manager
    
    # Mock media pool
    mock_media_pool = MagicMock()
    mock_media_pool.GetCurrentFolder.return_value = {"name": "Root"}
    mock_media_pool.GetRootFolder.return_value = {"name": "Root"}
    mock_media_pool.GetSubFolders.return_value = {}
    mock_media_pool.GetClipsInFolder.return_value = {}
    
    mock_project.GetMediaPool.return_value = mock_media_pool
    
    # Mock version info
    mock_resolve.GetVersionString.return_value = "18.5.0"
    mock_resolve.GetApiVersion.return_value = "1.0"
    mock_resolve.IsConsole.return_value = False
    mock_resolve.IsRenderingInProgress.return_value = False
    
    return mock_resolve

@pytest.fixture
def mock_connection_manager(mock_resolve):
    """Create a mock connection manager."""
    with patch('davinci_resolve_mcp.connection.manager.ResolveConnectionManager') as mock_manager:
        mock_instance = mock_manager.return_value
        mock_instance.get_connection.return_value = mock_resolve
        mock_instance.project_manager = mock_resolve.GetProjectManager.return_value
        mock_instance.current_project = mock_resolve.GetProjectManager.return_value.GetCurrentProject.return_value
        yield mock_instance

@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    from davinci_resolve_mcp.config import DaVinciResolveConfig
    
    mock_config = MagicMock(spec=DaVinciResolveConfig)
    mock_config.max_workers = 4
    mock_config.connection.timeout = 30
    mock_config.connection.retry_attempts = 3
    mock_config.connection.retry_delay = 1.0
    
    return mock_config

@pytest.fixture
def app_state(mock_config, mock_connection_manager):
    """Create an app state with mocked dependencies."""
    from types import SimpleNamespace
    
    state = SimpleNamespace()
    state.config = mock_config
    state.connection_manager = mock_connection_manager
    state.connection_pool = MagicMock()
    state.should_exit = False
    
    return state

@pytest.fixture
def test_app():
    """Create a test FastMCP application."""
    from fastmcp import FastMCP

    test_app = FastMCP(
        name="Test DaVinci Resolve MCP",
        instructions="Test application",
        version="0.1.0"
    )

    return test_app

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, tmp_path):
    """Set up test environment."""
    # Set up test directories
    test_data_dir = tmp_path / "test_data"
    test_data_dir.mkdir()
    
    # Mock environment variables
    monkeypatch.setenv("RESOLVE_SCRIPT_API_PATH", str(test_data_dir / "Scripts"))
    monkeypatch.setenv("RESOLVE_SCRIPT_LIB_PATH", str(test_data_dir / "Libraries"))
    
    # Create test files
    (test_data_dir / "test_video.mp4").write_bytes(b"fake video data")
    (test_data_dir / "test_audio.wav").write_bytes(b"fake audio data")
    (test_data_dir / "test_image.jpg").write_bytes(b"fake image data")
    
    return test_data_dir
