# Usage Examples

This document provides practical examples of how to use the DaVinci Resolve MCP package to automate various tasks in DaVinci Resolve.

## Table of Contents

1. [Basic Setup](#basic-setup)
2. [Project Management](#project-management)
3. [Media Import and Organization](#media-import-and-organization)
4. [Timeline Operations](#timeline-operations)
5. [Color Grading](#color-grading)
6. [Audio Processing](#audio-processing)
7. [Rendering](#rendering)
8. [Advanced Workflows](#advanced-workflows)

## Basic Setup

### Importing the Package

```python
from davinci_resolve_mcp import (
    Resolve, 
    Project, 
    MediaPool, 
    Timeline,
    RenderQueue,
    ResolveError
)

# Initialize the Resolve object
try:
    resolve = Resolve()
    print(f"Connected to DaVinci Resolve {resolve.get_version()}")
except ResolveError as e:
    print(f"Failed to connect to DaVinci Resolve: {e}")
    exit(1)
```

### Getting Project and Media Pool

```python
# Get the current project
project = resolve.get_current_project()
print(f"Current project: {project.get_name()}")

# Get the media pool
media_pool = project.get_media_pool()
print(f"Media pool root folder: {media_pool.get_root_folder().get_name()}")
```

## Project Management

### Creating a New Project

```python
# Create a new project with custom settings
new_project = resolve.create_project(
    name="My New Project",
    width=3840,
    height=2160,
    frame_rate=24.0,
    pixel_aspect_ratio=1.0,
    is_hdr=False
)
print(f"Created new project: {new_project.get_name()}")
```

### Opening an Existing Project

```python
# Open a project by name
project_names = resolve.get_project_list()
print("Available projects:", project_names)

if "My Project" in project_names:
    project = resolve.open_project("My Project")
    print(f"Opened project: {project.get_name()}")
else:
    print("Project not found")
```

## Media Import and Organization

### Importing Media

```python
# Import a single media file
media_item = media_pool.import_media("C:/Videos/MyClip.mp4")
print(f"Imported: {media_item.get_name()}")

# Import multiple files
media_items = media_pool.import_media([
    "C:/Videos/Clip1.mp4",
    "C:/Videos/Clip2.mp4",
    "C:/Videos/Clip3.mp4"
])
print(f"Imported {len(media_items)} media items")

# Import all files from a folder
folder_items = media_pool.import_media_folder("C:/Videos/Footage")
print(f"Imported {len(folder_items)} items from folder")
```

### Organizing Media in Bins

```python
# Create a new bin
new_bin = media_pool.add_folder("My Clips")
print(f"Created bin: {new_bin.get_name()}")

# Move media items to the new bin
for item in media_items:
    new_bin.move_media(item)
    
print(f"Moved {len(media_items)} items to {new_bin.get_name()}")
```

## Timeline Operations

### Creating a New Timeline

```python
# Create a new timeline with default settings
timeline = project.create_timeline("My Timeline")
print(f"Created timeline: {timeline.get_name()}")

# Create a timeline with custom settings
timeline = project.create_timeline(
    name="4K 24fps Timeline",
    width=3840,
    height=2160,
    frame_rate=24.0,
    sample_rate=48000,
    channel_layout="stereo"
)
```

### Adding Clips to Timeline

```python
# Add a clip to the timeline at the end
last_frame = timeline.get_end_frame()
timeline.append_clip(media_items[0])
print(f"Appended clip to timeline. New end frame: {timeline.get_end_frame()}")

# Insert a clip at a specific position
insert_position = 100  # Frame number
timeline.insert_clip(media_items[1], insert_position)
print(f"Inserted clip at frame {insert_position}")
```

### Basic Editing

```python
# Split a clip at the playhead position
playhead_position = 120  # Frame number
clip = timeline.get_clip_at_position(playhead_position)
if clip:
    timeline.split_clip(clip, playhead_position)
    print(f"Split clip at frame {playhead_position}")

# Delete a clip
clip_to_delete = timeline.get_clip_at_position(150)
if clip_to_delete:
    timeline.delete_clip(clip_to_delete)
    print("Deleted clip")
```

## Color Grading

### Applying LUTs

```python
# Get the current timeline
current_timeline = project.get_current_timeline()

# Apply a LUT to all clips
for clip in current_timeline.get_clips():
    clip.color.apply_lut("C:/LUTs/Rec709_to_LogC.cube")
    print(f"Applied LUT to {clip.get_name()}")
```

### Adjusting Color Wheels

```python
# Adjust color wheels for a specific clip
clip = timeline.get_clip_at_position(100)
if clip:
    color = clip.color
    
    # Adjust lift, gamma, gain
    color.lift = (0.0, -0.1, 0.0, 0.0)  # (R, G, B, Y)
    color.gamma = (0.0, 0.0, 0.1, 0.0)
    color.gain = (1.1, 1.1, 1.0, 1.0)
    
    # Adjust saturation
    color.saturation = 1.2
    
    print(f"Adjusted color for {clip.get_name()}")
```

## Audio Processing

### Adjusting Audio Levels

```python
# Get all audio tracks
audio_tracks = timeline.get_audio_tracks()

# Adjust volume for each track
for i, track in enumerate(audio_tracks):
    # Lower volume by 3dB
    track.set_volume(-3.0)
    print(f"Adjusted volume for track {i+1} to {track.get_volume()}dB")
```

### Applying Audio Effects

```python
# Apply a compressor to the first audio track
if audio_tracks:
    track = audio_tracks[0]
    effect = track.add_effect("Compressor")
    effect.set_parameter("Threshold", -20.0)  # dB
    effect.set_parameter("Ratio", 4.0)
    effect.set_parameter("Attack", 10.0)  # ms
    effect.set_parameter("Release", 100.0)  # ms
    print(f"Added compressor to {track.get_name()}")
```

## Rendering

### Setting Up a Render Job

```python
# Get the render queue
render_queue = project.get_render_queue()

# Add the current timeline to the render queue
job = render_queue.add_job(timeline)

# Configure render settings
job.set_setting("Format", "mp4")
job.set_setting("Codec", "H.264")
job.set_setting("Resolution", "3840x2160")
job.set_setting("FrameRate", 24.0)
job.set_setting("Quality", "Best")
job.set_setting("FileName", "C:/Renders/my_render.mp4")

print(f"Created render job for {timeline.get_name()}")
```

### Starting the Render

```python
# Start rendering
if render_queue.start_rendering():
    print("Rendering started")
    
    # Monitor progress
    while render_queue.is_rendering():
        progress = render_queue.get_progress()
        print(f"Rendering: {progress:.1f}%")
        import time
        time.sleep(5)  # Check every 5 seconds
        
    print("Rendering completed")
else:
    print("Failed to start rendering")
```

## Advanced Workflows

### Batch Processing Multiple Projects

```python
# List all projects
project_names = resolve.get_project_list()

# Process each project
for project_name in project_names:
    try:
        # Open the project
        project = resolve.open_project(project_name)
        print(f"\nProcessing project: {project_name}")
        
        # Get the first timeline
        timeline = project.get_timeline_by_index(1)
        if not timeline:
            print("  No timeline found, skipping...")
            continue
            
        # Apply some processing
        for clip in timeline.get_clips():
            # Example: Apply a LUT to all clips
            clip.color.apply_lut("C:/LUTs/Rec709_to_LogC.cube")
            
        # Set up render
        render_queue = project.get_render_queue()
        job = render_queue.add_job(timeline)
        job.set_setting("Format", "mp4")
        job.set_setting("FileName", f"C:/Renders/{project_name}.mp4")
        
        # Start rendering
        print(f"  Started rendering {project_name}...")
        if render_queue.start_rendering():
            while render_queue.is_rendering():
                time.sleep(5)  # Check every 5 seconds
            print(f"  Completed rendering {project_name}")
        else:
            print(f"  Failed to start rendering {project_name}")
            
    except Exception as e:
        print(f"  Error processing {project_name}: {e}")
    finally:
        # Close the project
        if 'project' in locals():
            resolve.close_project(project)
            
print("\nBatch processing complete")
```

### Creating a Multi-Camera Edit

```python
# Get all clips from a bin
bin_clips = media_pool.get_clips()

# Create a new timeline for multi-cam
timeline = project.create_timeline("Multi-Cam Edit")

# Add clips to separate video tracks
for i, clip in enumerate(bin_clips[:4]):  # Use up to 4 clips
    timeline.append_clip(clip, video_track=i+1)

# Enable multi-cam mode
timeline.enable_multi_cam()
print("Created multi-camera timeline")

# Example of switching camera angles
# This would typically be done interactively, but here's how you could script it:
# timeline.set_multi_cam_angle(1, 0, 10)  # Switch to camera 1 at time 0 for 10 seconds
# timeline.set_multi_cam_angle(2, 10, 20)  # Switch to camera 2 at time 10 for 10 seconds
```

This document provides a starting point for using the DaVinci Resolve MCP package. For more detailed information, refer to the [API Reference](API_REFERENCE.md).
