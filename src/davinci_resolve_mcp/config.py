"""
Configuration management for DaVinci Resolve MCP Server.

This module handles configuration loading, validation, and management
for the DaVinci Resolve MCP server.
"""

from __future__ import annotations

import logging
import os
import platform
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Configure logger
logger = logging.getLogger(__name__)

# Type variable for generic model type
ModelT = TypeVar("ModelT", bound=BaseModel)


class LogLevel(str, Enum):
    """Standard log levels for consistent configuration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ColorSpace(str, Enum):
    """Supported color spaces."""

    REC709 = "Rec.709"
    REC2020 = "Rec.2020"
    P3_D65 = "DCI-P3 D65"
    ACES = "ACEScct"
    SRGB = "sRGB"
    CUSTOM = "Custom"


class FrameRate(float, Enum):
    """Common frame rates for video projects."""

    FILM_24 = 24.0
    NTSC_DF = 29.97
    NTSC_NDF = 30.0
    PAL = 25.0
    HD_50 = 50.0
    HD_60 = 60.0


class ResolveEnvironmentConfig(BaseModel):
    """
    Environment configuration for DaVinci Resolve API access.

    This configuration handles paths and environment variables needed to access
    the DaVinci Resolve Python API.
    """

    script_api_path: Path | None = Field(
        default=None, description="Path to DaVinci Resolve's Python modules"
    )
    script_lib_path: Path | None = Field(
        default=None, description="Path to additional script libraries"
    )
    python_path_additions: list[Path] = Field(
        default_factory=list, description="Additional paths to add to PYTHONPATH"
    )

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @field_validator("script_api_path", "script_lib_path", mode="before")
    @classmethod
    def validate_paths(cls, v: Any) -> Path | None:
        """Convert string paths to Path objects."""
        if v is None or isinstance(v, Path):
            return v
        return Path(str(v))


class ConnectionConfig(BaseModel):
    """
    Connection configuration for Resolve API.

    This configuration controls how the application connects to and communicates
    with the DaVinci Resolve application.
    """

    timeout: float = Field(
        default=30.0, ge=5.0, le=300.0, description="Timeout in seconds for API operations"
    )
    retry_attempts: int = Field(
        default=3, ge=1, le=10, description="Number of retry attempts for failed operations"
    )
    retry_delay: float = Field(
        default=2.0, ge=0.5, le=30.0, description="Delay in seconds between retry attempts"
    )
    connection_check_interval: float = Field(
        default=5.0, ge=1.0, le=60.0, description="Interval in seconds to check connection health"
    )
    headless_mode: bool = Field(
        default=False, description="Run Resolve in headless mode (if supported)"
    )
    auto_reconnect: bool = Field(
        default=True, description="Automatically attempt to reconnect if connection is lost"
    )

    model_config = ConfigDict(extra="ignore")


class RenderConfig(BaseModel):
    """Default rendering configuration."""

    default_format: str = Field(default="QuickTime")
    default_codec: str = Field(default="Apple ProRes 422")
    default_quality: str = Field(default="High")
    default_resolution: str = Field(default="1920x1080")
    default_frame_rate: float = Field(default=24.0)
    max_concurrent_renders: int = Field(default=2, ge=1, le=8)

    model_config = ConfigDict(extra="allow")


class ProjectConfig(BaseModel):
    """Default project configuration."""

    default_frame_rate: float = Field(default=24.0, ge=23.976, le=120.0)
    default_resolution_width: int = Field(default=1920, ge=640, le=7680)
    default_resolution_height: int = Field(default=1080, ge=360, le=4320)
    default_color_space: str = Field(default="Rec.709")
    auto_save_enabled: bool = Field(default=True)
    auto_save_interval: int = Field(default=5, ge=1, le=60)  # minutes

    model_config = ConfigDict(extra="allow")


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: str | None = None
    max_file_size_mb: int = Field(default=10, ge=1, le=100)
    backup_count: int = Field(default=5, ge=1, le=20)

    model_config = ConfigDict(extra="allow")


class DaVinciResolveConfig(BaseModel):
    """
    Main configuration class for DaVinci Resolve MCP Server.

    This class manages all configuration aspects including Resolve environment
    setup, connection parameters, and operational settings.
    """

    # Environment setup
    environment: ResolveEnvironmentConfig = Field(default_factory=ResolveEnvironmentConfig)

    # Connection settings
    connection: ConnectionConfig = Field(default_factory=ConnectionConfig)

    # Rendering defaults
    rendering: RenderConfig = Field(default_factory=RenderConfig)

    # Project defaults
    project: ProjectConfig = Field(default_factory=ProjectConfig)

    # Logging configuration
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Server settings
    temp_directory: Path = Field(default_factory=lambda: Path.cwd() / "temp")
    max_workers: int = Field(default=4, ge=1, le=16)
    request_timeout: float = Field(default=120.0, ge=30.0, le=600.0)

    # Resolve installation paths (will be auto-detected)
    resolve_executable: str | None = None
    resolve_installation_path: str | None = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @field_validator("temp_directory", mode="before")
    @classmethod
    def validate_temp_directory(cls, v):
        """Ensure temp directory exists."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v

    def setup_environment(self) -> bool:
        """
        Set up environment variables for DaVinci Resolve API access.

        Returns:
            bool: True if environment setup successful
        """
        try:
            system = platform.system().lower()

            # Get platform-specific paths
            api_path, lib_path = self._get_default_paths(system)

            # Use configured paths or defaults
            script_api = self.environment.script_api_path or api_path
            script_lib = self.environment.script_lib_path or lib_path

            if script_api:
                os.environ["RESOLVE_SCRIPT_API"] = script_api
                modules_path = os.path.join(script_api, "Modules")
                if os.path.exists(modules_path):
                    current_path = os.environ.get("PYTHONPATH", "")
                    if modules_path not in current_path:
                        os.environ["PYTHONPATH"] = (
                            f"{current_path};{modules_path}" if current_path else modules_path
                        )

            if script_lib:
                os.environ["RESOLVE_SCRIPT_LIB"] = script_lib

            # Add any additional Python path entries
            if self.environment.python_path_additions:
                current_path = os.environ.get("PYTHONPATH", "")
                additional = ";".join(self.environment.python_path_additions)
                os.environ["PYTHONPATH"] = (
                    f"{current_path};{additional}" if current_path else additional
                )

            return True

        except Exception:
            return False

    def _get_default_paths(self, system: str) -> tuple[str | None, str | None]:
        """Get default installation paths for different operating systems."""

        if system == "windows":
            api_path = r"%PROGRAMDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\"
            lib_path = r"C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\fusionscript.dll"

        elif system == "darwin":  # macOS
            api_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/"
            lib_path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"

        elif system == "linux":
            api_path = "/opt/resolve/Developer/Scripting/"
            lib_path = "/opt/resolve/libs/Fusion/fusionscript.so"

        else:
            return None, None

        return api_path, lib_path

    @classmethod
    def load_from_file(cls, config_path: str | Path) -> DaVinciResolveConfig:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            DaVinciResolveConfig: Loaded configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    @classmethod
    def load_default(cls, config_name: str = "config.yaml") -> DaVinciResolveConfig:
        """
        Load configuration from default locations.

        Searches for configuration in:
        1. Current working directory
        2. User home directory/.davinci-resolve-mcp/
        3. System config directory

        Args:
            config_name: Name of configuration file

        Returns:
            DaVinciResolveConfig: Loaded configuration or default
        """
        search_paths = [
            Path.cwd() / config_name,
            Path.home() / ".davinci-resolve-mcp" / config_name,
            Path("/etc/davinci-resolve-mcp") / config_name,  # Linux/macOS
        ]

        for config_path in search_paths:
            if config_path.exists():
                try:
                    return cls.load_from_file(config_path)
                except Exception:
                    continue

        # Return default configuration if no file found
        return cls()

    def save_to_file(self, config_path: str | Path) -> None:
        """
        Save configuration to YAML file.

        Args:
            config_path: Path to save configuration file
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for YAML serialization
        config_dict = self.model_dump()

        # Convert Path objects to strings
        def convert_paths(obj):
            if isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(item) for item in obj]
            elif isinstance(obj, Path):
                return str(obj)
            return obj

        config_dict = convert_paths(config_dict)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)

    def validate_configuration(self) -> dict[str, bool]:
        """
        Validate configuration settings.

        Returns:
            Dict[str, bool]: Validation results for different components
        """
        results = {}

        # Check temp directory
        results["temp_directory"] = self.temp_directory.exists() and self.temp_directory.is_dir()

        # Check environment paths
        results["environment_setup"] = self.setup_environment()

        # Check if Resolve installation exists
        if self.resolve_executable:
            results["resolve_executable"] = Path(self.resolve_executable).exists()
        else:
            results["resolve_executable"] = False

        return results


def load_default() -> DaVinciResolveConfig:
    """
    Load the default configuration.

    This is a convenience function that creates a new instance of DaVinciResolveConfig
    with default values.

    Returns:
        DaVinciResolveConfig: A new configuration instance with default values
    """
    return DaVinciResolveConfig()
