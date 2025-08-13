"""
Help tool for the DaVinci Resolve MCP package.

This module provides a help system that offers self-documentation with support for
multiple user levels and context-aware help.
"""
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Type, Union, get_type_hints
import inspect
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import TypeVar, Generic

from ..models import (
    ResolveObject, Project, MediaPool, Timeline, RenderQueue,
    ColorGrade, AudioMixer, get_available_models, get_model_dependencies
)

# Type variable for generic help content
T = TypeVar('T')

class UserLevel(Enum):
    """User experience levels for documentation."""
    BEGINNER = "beginner"       # New users, needs basic guidance
    INTERMEDIATE = "intermediate"  # Some experience, needs detailed info
    ADVANCED = "advanced"       # Experienced users, needs technical details
    DEVELOPER = "developer"     # Developers working on the package

@dataclass
class HelpContent(Generic[T]):
    """Container for help content with user-level specific information."""
    name: str
    description: str
    content: Dict[UserLevel, str] = field(default_factory=dict)
    examples: Dict[UserLevel, List[str]] = field(default_factory=dict)
    related: List[str] = field(default_factory=list)
    
    def add_content(self, level: UserLevel, content: str) -> 'HelpContent':
        """Add content for a specific user level."""
        self.content[level] = content
        return self
    
    def add_example(self, level: UserLevel, example: str) -> 'HelpContent':
        """Add an example for a specific user level."""
        if level not in self.examples:
            self.examples[level] = []
        self.examples[level].append(example)
        return self
    
    def add_related(self, related_item: str) -> 'HelpContent':
        """Add a related help topic."""
        if related_item not in self.related:
            self.related.append(related_item)
        return self

class HelpTool:
    """
    Help system for the DaVinci Resolve MCP package.
    
    Provides context-aware help and documentation for different user levels.
    """
    
    def __init__(self, user_level: UserLevel = UserLevel.BEGINNER):
        """
        Initialize the help tool.
        
        Args:
            user_level: The default user level for help content.
        """
        self.user_level = user_level
        self._help_content: Dict[str, HelpContent] = {}
        self._load_builtin_help()
    
    def set_user_level(self, level: Union[UserLevel, str]) -> None:
        """
        Set the user level for help content.
        
        Args:
            level: The user level as a UserLevel enum or string.
        """
        if isinstance(level, str):
            level = UserLevel(level.lower())
        self.user_level = level
    
    def _load_builtin_help(self) -> None:
        """Load built-in help content."""
        # Help for core classes
        self._add_class_help(ResolveObject, "Base class for all Resolve objects.")
        self._add_class_help(Project, "Represents a DaVinci Resolve project.")
        self._add_class_help(MediaPool, "Manages media items and bins in a project.")
        self._add_class_help(Timeline, "Represents a timeline in a project.")
        self._add_class_help(RenderQueue, "Manages render jobs for a project.")
        self._add_class_help(ColorGrade, "Manages color grading for a clip or timeline.")
        self._add_class_help(AudioMixer, "Manages audio tracks and mixing.")
        
        # Add help for common tasks
        self._add_task_help(
            "create_project",
            "Create a new project.",
            {
                UserLevel.BEGINNER: "Create a project with default settings.",
                UserLevel.INTERMEDIATE: "Create a project with custom resolution and frame rate.",
                UserLevel.ADVANCED: "Create a project with advanced settings like color science and working folders.",
                UserLevel.DEVELOPER: "Create a project with full control over all parameters.",
            },
            {
                UserLevel.BEGINNER: [
                    "create_project('My Project')"
                ],
                UserLevel.INTERMEDIATE: [
                    "create_project('My Project', width=1920, height=1080, frame_rate=24.0)"
                ],
                UserLevel.ADVANCED: [
                    "create_project('My Project', width=3840, height=2160, frame_rate=24.0, \
                    color_science='ACEScct', working_folder='/path/to/project')"
                ],
            },
            ["Project", "MediaPool", "Timeline"]
        )
        
        # Add more common tasks...
    
    def _add_class_help(self, cls: Type, description: str) -> None:
        """Add help content for a class."""
        class_name = cls.__name__
        docstring = inspect.getdoc(cls) or ""
        
        # Extract method signatures
        methods = []
        for name, member in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):  # Skip private methods
                sig = inspect.signature(member)
                methods.append(f"{name}{sig}")
        
        # Format the help content
        content = f"{class_name}\n{'=' * len(class_name)}\n\n{description}\n\n"
        
        if docstring:
            content += f"{docstring}\n\n"
        
        if methods:
            content += "Methods:\n"
            for method in sorted(methods):
                content += f"- {method}\n"
        
        # Add to help content
        self._help_content[class_name.lower()] = HelpContent(
            name=class_name,
            description=description,
            content={level: content for level in UserLevel},
            examples={},
            related=[]
        )
    
    def _add_task_help(
        self,
        name: str,
        description: str,
        content: Dict[UserLevel, str],
        examples: Dict[UserLevel, List[str]],
        related: List[str]
    ) -> None:
        """Add help content for a specific task."""
        help_content = HelpContent(
            name=name,
            description=description,
            content=content,
            examples=examples,
            related=related
        )
        self._help_content[name.lower()] = help_content
    
    def get_help(self, topic: Optional[str] = None, level: Optional[UserLevel] = None) -> str:
        """
        Get help for a specific topic or general help if no topic is provided.
        
        Args:
            topic: The topic to get help for. If None, returns general help.
            level: The user level for the help content. Uses the default if not specified.
            
        Returns:
            str: The formatted help text.
        """
        level = level or self.user_level
        
        if topic is None:
            return self._get_general_help(level)
        
        topic_lower = topic.lower()
        
        # Check for exact match
        if topic_lower in self._help_content:
            return self._format_help_content(self._help_content[topic_lower], level)
        
        # Check for partial matches
        matches = [k for k in self._help_content.keys() if topic_lower in k]
        
        if not matches:
            return f"No help found for '{topic}'. Type 'help()' to see available topics."
        
        if len(matches) == 1:
            return self._format_help_content(self._help_content[matches[0]], level)
        
        # Multiple matches found
        result = f"Multiple matches found for '{topic}':\n\n"
        for match in sorted(matches):
            result += f"- {self._help_content[match].name}: {self._help_content[match].description}\n"
        result += "\nType 'help(topic)' where 'topic' is one of the above for more information."
        return result
    
    def _get_general_help(self, level: UserLevel) -> str:
        """Get general help information."""
        help_text = f"""DaVinci Resolve MCP Help
{'=' * 30}

Welcome to the DaVinci Resolve MCP help system. This tool provides documentation
and examples for using the DaVinci Resolve MCP package.

Current user level: {level.value.capitalize()}

Available topics:
"""
        
        # Group topics by category
        categories = {
            "Core Classes": [
                "ResolveObject", "Project", "MediaPool", "Timeline", 
                "RenderQueue", "ColorGrade", "AudioMixer"
            ],
            "Common Tasks": [
                "create_project", "import_media", "create_timeline",
                "add_clip", "apply_lut", "render_project"
            ],
            "Advanced": [
                "color_grading", "audio_mixing", "render_settings"
            ]
        }
        
        for category, topics in categories.items():
            help_text += f"\n{category}:\n"
            for topic in topics:
                if topic.lower() in self._help_content:
                    help_text += f"- {topic}: {self._help_content[topic.lower()].description}\n"
        
        help_text += """

For help on a specific topic, type 'help("topic")' where 'topic' is the name
of the class or task you need help with.

To change the user level, use 'set_user_level("beginner"|"intermediate"|"advanced"|"developer")'.
"""
        return help_text
    
    def _format_help_content(self, content: HelpContent, level: UserLevel) -> str:
        """Format help content for display."""
        # Find the most appropriate content level
        content_level = level
        while content_level not in content.content and content_level != UserLevel.BEGINNER:
            # Move to a lower level if content isn't available at the requested level
            content_level = UserLevel(max(content_level.value - 1, 1))
        
        # Fall back to any available content if needed
        if content_level not in content.content and content.content:
            content_level = next(iter(content.content.keys()))
        
        # Build the help text
        help_text = f"{content.name}\n{'=' * len(content.name)}\n\n"
        
        # Add description
        help_text += f"{content.description}\n\n"
        
        # Add content for the selected level
        if content.content and content_level in content.content:
            help_text += f"{content.content[content_level]}\n"
        
        # Add examples if available
        if content.examples and content_level in content.examples:
            help_text += "\nExamples:\n"
            for i, example in enumerate(content.examples[content_level], 1):
                help_text += f"{i}. {example}\n"
        
        # Add related topics if available
        if content.related:
            help_text += "\nRelated topics:\n"
            for related in content.related:
                if related.lower() in self._help_content:
                    help_text += f"- {related}: {self._help_content[related.lower()].description}\n"
        
        # Add note about user level if content was shown at a different level
        if content_level != level:
            help_text += f"\nNote: Content shown at '{content_level.value}' level as content for '{level.value}' was not available.\n"
        
        return help_text
    
    def __call__(self, topic: Optional[str] = None) -> str:
        """Make the help tool callable as help(topic)."""
        return self.get_help(topic)
    
    def __str__(self) -> str:
        """String representation of the help tool."""
        return self.get_help()

# Create a default instance for easy access
help = HelpTool()

def get_help(topic: Optional[str] = None, level: Optional[Union[UserLevel, str]] = None) -> str:
    """
    Get help for a topic at a specific user level.
    
    This is a convenience function that uses the default help instance.
    
    Args:
        topic: The topic to get help for. If None, returns general help.
        level: The user level for the help content. Uses the default if not specified.
        
    Returns:
        str: The formatted help text.
    """
    if level is not None:
        if isinstance(level, str):
            level = UserLevel(level.lower())
        help.set_user_level(level)
    return help.get_help(topic)
