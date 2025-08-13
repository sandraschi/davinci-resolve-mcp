# DaVinci Resolve MCP - Help System Guide

## Overview

The DaVinci Resolve MCP includes a powerful, context-aware help system designed to provide the right level of information based on your experience and needs. This document explains how to use the help system effectively.

## Table of Contents

- [Getting Help](#getting-help)
- [User Levels](#user-levels)
- [Available Help Topics](#available-help-topics)
- [Customizing Help Content](#customizing-help-content)
- [Extending the Help System](#extending-the-help-system)
- [Troubleshooting](#troubleshooting)

## Getting Help

### Basic Usage

```python
from davinci_resolve_mcp import help, get_help, UserLevel

# Get general help
help()

# Get help on a specific topic
help("Project")  # Get help on Project class
help("create_project")  # Get help on creating projects

# Get help at a specific user level
get_help("color_grading", level="beginner")  # Beginner-friendly help
get_help("color_grading", level="advanced")  # Advanced technical details

# Change the default user level
help.set_user_level("intermediate")  # Options: beginner, intermediate, advanced, developer
```

### Command Line Help

You can also access help from the command line:

```bash
# Show general help
davinci-resolve-mcp help

# Get help on a specific topic
davinci-resolve-mcp help Project
davinci-resolve-mcp help create_project

# Set the user level for help
davinci-resolve-mcp help --level=advanced
```

## User Levels

The help system provides different levels of detail based on your expertise:

### Beginner
- Simple, non-technical explanations
- Basic examples
- Focus on common tasks

### Intermediate (Default)
- More detailed explanations
- Practical examples
- Some technical details

### Advanced
- In-depth technical information
- Advanced usage patterns
- Performance considerations

### Developer
- Implementation details
- API references
- Extension points

## Available Help Topics

### Core Concepts
- `Project` - Working with DaVinci Resolve projects
- `MediaPool` - Managing media assets
- `Timeline` - Timeline editing operations
- `ColorGrade` - Color correction and grading
- `AudioMixer` - Audio processing and mixing
- `RenderQueue` - Rendering and export

### Common Tasks
- `create_project` - Creating new projects
- `import_media` - Importing media files
- `create_timeline` - Creating and managing timelines
- `color_grading` - Color correction workflows
- `audio_mixing` - Audio processing workflows
- `render_project` - Rendering projects

### Advanced Topics
- `scripting` - Automation and scripting
- `performance` - Performance optimization
- `troubleshooting` - Common issues and solutions

## Customizing Help Content

### Setting Default User Level

You can set the default user level for all help output:

```python
from davinci_resolve_mcp import help

# Set default user level to advanced
help.set_user_level("advanced")

# Now all help output will be at the advanced level
help("Project")
```

### Adding Custom Help Content

You can extend the help system with your own content:

```python
from davinci_resolve_mcp.tools import HelpTool, UserLevel

# Get the help instance
help = HelpTool()

# Add a new help topic
help.add_topic(
    name="my_custom_tool",
    description="My custom tool for specialized tasks",
    content={
        UserLevel.BEGINNER: "Simple explanation of what this tool does",
        UserLevel.ADVANCED: "Detailed technical documentation"
    },
    examples={
        UserLevel.BEGINNER: ["my_custom_tool --option1 value1"],
        UserLevel.ADVANCED: [
            "my_custom_tool --option1 value1 --option2 value2",
            "my_custom_tool --advanced-option"
        ]
    },
    related=["Project", "Timeline"]
)
```

## Extending the Help System

### Creating Custom Help Handlers

For more advanced use cases, you can create custom help handlers:

```python
from typing import Optional, Dict, Any
from davinci_resolve_mcp.tools import HelpContent, UserLevel

def custom_help_handler(topic: str, level: UserLevel) -> Optional[HelpContent]:
    if topic == "my_custom_topic":
        return HelpContent(
            name="My Custom Topic",
            description="Custom help content for my topic",
            content={
                UserLevel.BEGINNER: "Beginner content",
                UserLevel.ADVANCED: "Advanced content"
            },
            examples={
                UserLevel.BEGINNER: ["Example 1", "Example 2"],
                UserLevel.ADVANCED: ["Advanced Example 1", "Advanced Example 2"]
            },
            related=["Project", "Timeline"]
        )
    return None

# Register the custom handler
help = HelpTool()
help.add_handler(custom_help_handler)
```

## Troubleshooting

### Common Issues

#### Help Topic Not Found
If you get a "Help topic not found" error, try:
1. Checking the spelling of the topic
2. Using a more general term
3. Listing all available topics with `help()`

#### Incorrect User Level
If the help content is too basic or too advanced:
1. Check your current user level with `help.get_user_level()`
2. Change the user level with `help.set_user_level("advanced")`

### Getting Help

For additional assistance, please refer to:
- [Documentation](https://github.com/yourusername/davinci-resolve-mcp)
- [Issue Tracker](https://github.com/yourusername/davinci-resolve-mcp/issues)
- [Community Forum](https://github.com/yourusername/davinci-resolve-mcp/discussions)

## Contributing

We welcome contributions to improve the help system. To contribute:

1. Fork the repository
2. Create a new branch for your changes
3. Add or update help content
4. Submit a pull request

When adding new help content, please ensure it's available at all user levels where appropriate.
