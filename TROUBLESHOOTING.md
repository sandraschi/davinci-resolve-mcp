# Troubleshooting Guide

This guide provides solutions to common issues you might encounter while using the DaVinci Resolve MCP package.

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Installation Problems](#installation-problems)
3. [Project and Media Issues](#project-and-media-issues)
4. [Timeline and Editing Problems](#timeline-and-editing-problems)
5. [Rendering Issues](#rendering-issues)
6. [Performance Problems](#performance-problems)
7. [Common Error Messages](#common-error-messages)
8. [Getting Help](#getting-help)

## Connection Issues

### Cannot Connect to DaVinci Resolve

**Symptoms:**
- Error: "Failed to connect to DaVinci Resolve"
- The script can't find a running instance of DaVinci Resolve

**Solutions:**
1. Ensure DaVinci Resolve is running before executing your script
2. Check that the Resolve API is enabled:
   - Go to DaVinci Resolve > Preferences > System > General
   - Under "External Scripting Using", ensure "Local" is selected
   - Note the port number (default is usually 11046)
3. Verify the host and port in your connection code:
   ```python
   resolve = Resolve(host='localhost', port=11046)
   ```
4. If using a remote connection, ensure the firewall allows the connection

### Connection Drops During Operation

**Symptoms:**
- Script works initially but loses connection to DaVinci Resolve
- Operations fail with connection errors after some time

**Solutions:**
1. Add error handling and reconnection logic:
   ```python
   import time
   from davinci_resolve_mcp import Resolve, ResolveError
   
   def get_resolve_connection():
       max_retries = 3
       for attempt in range(max_retries):
           try:
               return Resolve()
           except ResolveError as e:
               if attempt == max_retries - 1:
                   raise
               print(f"Connection failed, retrying... ({attempt + 1}/{max_retries})")
               time.sleep(2)  # Wait before retrying
   ```
2. Ensure DaVinci Resolve isn't being closed or crashing
3. Check for system sleep/hibernation that might affect the connection

## Installation Problems

### Package Installation Fails

**Symptoms:**
- `pip install` command fails with errors
- Dependencies can't be resolved

**Solutions:**
1. Ensure you have the latest version of pip:
   ```bash
   python -m pip install --upgrade pip
   ```
2. Try installing with the `--user` flag:
   ```bash
   pip install --user davinci-resolve-mcp
   ```
3. If using a virtual environment, ensure it's activated before installing
4. Check that your Python version is 3.8 or higher:
   ```bash
   python --version
   ```

### Import Errors

**Symptoms:**
- `ModuleNotFoundError` when importing the package
- `ImportError` for dependencies

**Solutions:**
1. Verify the package is installed in the correct Python environment
2. Check your PYTHONPATH environment variable
3. If using an IDE, ensure it's using the correct Python interpreter
4. Try reinstalling the package:
   ```bash
   pip uninstall davinci-resolve-mcp
   pip install davinci-resolve-mcp
   ```

### Cursor IDE: Server Does Not Start

**Symptoms:**
- davinci-resolve-mcp does not appear in Cursor MCP tools
- "No module named davinci_resolve_mcp.__main__" in logs

**Solutions:**
1. See [CURSOR_FIX.md](CURSOR_FIX.md) for full setup
2. Use `run_mcp.py` with explicit cwd and PYTHONPATH in Cursor settings
3. Ensure `pip install -e .` if using `python -m davinci_resolve_mcp`
4. Check `%APPDATA%\Cursor\logs\MCP user-davinci-resolve-mcp.log` for errors

## Project and Media Issues

### Project Won't Open

**Symptoms:**
- `open_project()` fails
- Project appears in the list but can't be opened

**Solutions:**
1. Check if the project is already open in another instance of DaVinci Resolve
2. Verify you have the correct project name (case-sensitive)
3. Check if the project database is corrupted (try opening it manually in DaVinci Resolve)
4. Ensure you have the necessary permissions to access the project

### Media Files Not Found

**Symptoms:**
- Media appears offline in the timeline
- `import_media()` fails with file not found errors

**Solutions:**
1. Verify the file paths are correct and accessible
2. Check for network drive mappings if using remote media
3. Ensure the files haven't been moved or deleted
4. Try using absolute paths instead of relative paths

## Timeline and Editing Problems

### Clips Not Appearing in Timeline

**Symptoms:**
- `append_clip()` or `insert_clip()` doesn't add the clip
- No error is raised, but the timeline remains unchanged

**Solutions:**
1. Check that the clip was successfully imported into the media pool
2. Verify the track number is valid (1-based index)
3. Ensure the track is not locked or disabled
4. Try getting the timeline again after adding the clip:
   ```python
   timeline = project.get_current_timeline()  # Refresh the timeline reference
   ```

### Incorrect Clip Duration

**Symptoms:**
- Clips have unexpected durations
- Media handles are not as expected

**Solutions:**
1. Check the source media properties:
   ```python
   media_item = media_pool.import_media("path/to/clip.mp4")
   print(f"Duration: {media_item.duration} frames")
   print(f"Frame rate: {media_item.frame_rate}")
   ```
2. Verify the timeline frame rate matches your source media
3. Check for any in/out points set on the media item

## Rendering Issues

### Render Job Fails

**Symptoms:**
- `start_rendering()` returns False
- Render queue shows an error

**Solutions:**
1. Check the render settings for invalid values
2. Verify the output directory exists and is writable
3. Look for error messages in the DaVinci Resolve UI
4. Try a simpler render preset to isolate the issue

### No Progress During Rendering

**Symptoms:**
- The render starts but doesn't progress
- Progress percentage stays at 0%

**Solutions:**
1. Check if DaVinci Resolve's UI is showing render progress
2. Ensure the render queue isn't paused
3. Look for system resource issues (CPU, disk I/O)
4. Try a different output format or codec

## Performance Problems

### Script Runs Slowly

**Symptoms:**
- Operations take longer than expected
- High CPU or memory usage

**Solutions:**
1. Optimize your script to minimize API calls
2. Batch operations when possible:
   ```python
   # Instead of this:
   for clip in clips:
       timeline.append_clip(clip)
   
   # Do this:
   media_pool.import_media(clips)  # Import all at once
   timeline.append_clips(clips)    # Add all clips in one operation
   ```
3. Close unused projects and timelines
4. Increase DaVinci Resolve's memory allocation in Preferences > Memory and GPU

### DaVinci Resolve Becomes Unresponsive

**Symptoms:**
- UI freezes during script execution
- Script times out waiting for responses

**Solutions:**
1. Add timeouts to long-running operations
2. Break large operations into smaller chunks
3. Ensure you're not making too many rapid API calls
4. Close unnecessary applications to free up system resources

## Common Error Messages

### "Project not found"

**Cause:** The specified project doesn't exist or can't be accessed.

**Solution:**
```python
# List all available projects first
projects = resolve.get_project_list()
print("Available projects:", projects)

# Then use the exact name from the list
if "My Project" in projects:
    project = resolve.open_project("My Project")
```

### "Media not found"

**Cause:** The specified media file doesn't exist at the given path.

**Solution:**
```python
import os

media_path = "path/to/media.mp4"
if os.path.exists(media_path):
    media_item = media_pool.import_media(media_path)
else:
    print(f"File not found: {media_path}")
```

### "Timeline not found"

**Cause:** The specified timeline doesn't exist in the current project.

**Solution:**
```python
# List all timelines in the project
timelines = project.get_timeline_list()
print("Available timelines:", [t.name for t in timelines])

# Get timeline by index (1-based)
timeline = project.get_timeline_by_index(1)
```

## Getting Help

If you've tried the solutions above and are still experiencing issues:

1. **Check the Documentation**
   - [API Reference](API_REFERENCE.md)
   - [Usage Examples](USAGE_EXAMPLES.md)

2. **Search for Similar Issues**
   - Check the [GitHub Issues](https://github.com/yourusername/davinci-resolve-mcp/issues) for similar problems

3. **Create a New Issue**
   When creating a new issue, please include:
   - DaVinci Resolve version
   - Python version
   - Operating system
   - Steps to reproduce the issue
   - Relevant error messages or logs
   - Any code that triggers the issue

4. **Community Support**
   - Join our community forum (link in README)
   - Ask questions on Stack Overflow with the `davinci-resolve` and `python` tags

## Debugging Tips

1. **Enable Debug Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check DaVinci Resolve Logs**
   - On Windows: `%APPDATA%\Blackmagic Design\DaVinci Resolve\logs`
   - On macOS: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/logs`
   - On Linux: `~/.local/share/DaVinciResolve/logs`

3. **Test with a Simple Script**
   ```python
   from davinci_resolve_mcp import Resolve
   
   try:
       resolve = Resolve()
       print(f"Connected to DaVinci Resolve {resolve.get_version()}")
       print("Projects:", resolve.get_project_list())
   except Exception as e:
       print(f"Error: {e}")
   ```

Remember to check for updates to the DaVinci Resolve MCP package, as issues may be fixed in newer versions.
