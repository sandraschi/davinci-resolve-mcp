# API Reference

This document provides a comprehensive reference for all classes, methods, and properties available in the DaVinci Resolve MCP package.

## Table of Contents

1. [Core Classes](#core-classes)
   - [Resolve](#resolve)
   - [Project](#project)
   - [MediaPool](#mediapool)
   - [Timeline](#timeline)
   - [RenderQueue](#renderqueue)
   - [Color](#color)
   - [Audio](#audio)

2. [Data Models](#data-models)
   - [Common Models](#common-models)
   - [Project Models](#project-models)
   - [Media Models](#media-models)
   - [Timeline Models](#timeline-models)
   - [Render Models](#render-models)
   - [Color Models](#color-models)
   - [Audio Models](#audio-models)

## Core Classes

### Resolve

The main entry point for interacting with DaVinci Resolve.

#### Properties
- `version` (str): The version of DaVinci Resolve.
- `is_connected` (bool): Whether the connection to DaVinci Resolve is active.

#### Methods

##### `get_version()`
Returns the version of DaVinci Resolve.

**Returns:**
- `str`: The version string.

##### `get_project_list()`
Gets a list of all available projects.

**Returns:**
- `List[str]`: List of project names.

##### `open_project(name: str) -> Project`
Opens a project by name.

**Parameters:**
- `name` (str): The name of the project to open.

**Returns:**
- `Project`: The opened project.

**Raises:**
- `ResolveError`: If the project cannot be opened.

##### `create_project(name: str, **settings) -> Project`
Creates a new project.

**Parameters:**
- `name` (str): The name of the new project.
- `**settings`: Additional project settings (width, height, frame_rate, etc.).

**Returns:**
- `Project`: The created project.

### Project

Represents a DaVinci Resolve project.

#### Properties
- `name` (str): The name of the project.
- `path` (str): The file system path to the project.
- `is_active` (bool): Whether this is the currently active project.

#### Methods

##### `get_media_pool() -> MediaPool`
Gets the media pool for this project.

**Returns:**
- `MediaPool`: The media pool object.

##### `get_timeline_by_index(index: int) -> Timeline`
Gets a timeline by its index.

**Parameters:**
- `index` (int): The 1-based index of the timeline.

**Returns:**
- `Timeline`: The timeline object.

##### `get_current_timeline() -> Timeline`
Gets the currently active timeline.

**Returns:**
- `Timeline`: The current timeline.

##### `create_timeline(name: str, **settings) -> Timeline`
Creates a new timeline.

**Parameters:**
- `name` (str): The name of the new timeline.
- `**settings`: Timeline settings (width, height, frame_rate, etc.).

**Returns:**
- `Timeline`: The created timeline.

### MediaPool

Manages media items and bins in a project.

#### Methods

##### `get_root_folder() -> Folder`
Gets the root folder of the media pool.

**Returns:**
- `Folder`: The root folder object.

##### `import_media(path: Union[str, List[str]]) -> List[MediaItem]`
Imports media files into the media pool.

**Parameters:**
- `path` (Union[str, List[str]]): Path(s) to the media file(s).

**Returns:**
- `List[MediaItem]`: List of imported media items.

##### `create_folder(name: str, parent: Optional[Folder] = None) -> Folder`
Creates a new folder in the media pool.

**Parameters:**
- `name` (str): The name of the new folder.
- `parent` (Optional[Folder]): The parent folder (defaults to root).

**Returns:**
- `Folder`: The created folder.

### Timeline

Represents a timeline in a project.

#### Properties
- `name` (str): The name of the timeline.
- `duration` (int): The duration in frames.
- `frame_rate` (float): The frame rate of the timeline.
- `width` (int): The width in pixels.
- `height` (int): The height in pixels.

#### Methods

##### `get_clips() -> List[Clip]`
Gets all clips in the timeline.

**Returns:**
- `List[Clip]`: List of clip objects.

##### `get_clip_at_position(position: int) -> Optional[Clip]`
Gets the clip at the specified position.

**Parameters:**
- `position` (int): The frame position.

**Returns:**
- `Optional[Clip]`: The clip at the position, or None.

##### `append_clip(clip: Union[MediaItem, str], track: int = 1) -> bool`
Appends a clip to the timeline.

**Parameters:**
- `clip` (Union[MediaItem, str]): The clip to append.
- `track` (int): The track number (1-based).

**Returns:**
- `bool`: True if successful.

### RenderQueue

Manages render jobs for a project.

#### Methods

##### `add_job(timeline: Timeline, preset: str = "") -> Job`
Adds a render job for the specified timeline.

**Parameters:**
- `timeline` (Timeline): The timeline to render.
- `preset` (str): Optional render preset name.

**Returns:**
- `Job`: The created render job.

##### `start_rendering() -> bool`
Starts rendering all jobs in the queue.

**Returns:**
- `bool`: True if rendering started successfully.

##### `get_progress() -> float`
Gets the current render progress.

**Returns:**
- `float`: Progress percentage (0-100).

## Data Models

### Common Models

#### `ResolveObject`
Base class for all resolve objects.

#### `TimeCode`
Represents a timecode value.

**Properties:**
- `hours` (int): Hours component.
- `minutes` (int): Minutes component.
- `seconds` (int): Seconds component.
- `frames` (int): Frames component.
- `frame_rate` (float): Frame rate.

#### `Resolution`
Represents a resolution (width × height).

**Properties:**
- `width` (int): Width in pixels.
- `height` (int): Height in pixels.

### Project Models

#### `ProjectSettings`
Contains project settings.

**Properties:**
- `name` (str): Project name.
- `width` (int): Frame width.
- `height` (int): Frame height.
- `frame_rate` (float): Frame rate.
- `pixel_aspect_ratio` (float): Pixel aspect ratio.

### Media Models

#### `MediaItem`
Represents a media item in the media pool.

**Properties:**
- `name` (str): Media item name.
- `path` (str): File system path.
- `duration` (int): Duration in frames.
- `frame_rate` (float): Frame rate.

#### `Folder`
Represents a folder in the media pool.

**Properties:**
- `name` (str): Folder name.

### Timeline Models

#### `Clip`
Represents a clip in a timeline.

**Properties:**
- `name` (str): Clip name.
- `start` (int): Start frame.
- `end` (int): End frame.
- `duration` (int): Duration in frames.
- `media` (MediaItem): The source media item.

### Render Models

#### `Job`
Represents a render job.

**Properties:**
- `name` (str): Job name.
- `status` (str): Current status.
- `progress` (float): Render progress (0-100).

### Color Models

#### `ColorGrade`
Manages color grading for a clip or timeline.

**Methods:**
- `apply_lut(path: str) -> bool`: Applies a LUT.
- `reset_grade() -> None`: Resets all color adjustments.

### Audio Models

#### `AudioTrack`
Represents an audio track in a timeline.

**Properties:**
- `name` (str): Track name.
- `is_muted` (bool): Whether the track is muted.
- `volume` (float): Volume in dB.

## Error Handling

### `ResolveError`
Base exception for all DaVinci Resolve MCP errors.

### `ConnectionError`
Raised when there's an issue connecting to DaVinci Resolve.

### `ProjectError`
Raised for project-related errors.

## Constants

### `ColorSpace`
Enum of supported color spaces:
- `REC709`: Standard Rec.709
- `REC2020`: Rec.2020
- `P3_DCI`: DCI-P3
- `P3_D65`: P3-D65
- `ACES`: ACES
- `ACEScc`: ACEScc
- `ACEScct`: ACEScct
- `ACESproxy`: ACESproxy
- `ARRI_LOGC3`: ARRI LogC3
- `SONY_SLOG3`: Sony S-Log3
- `V_GAMUT`: Panasonic V-Gamut
- `CINEON`: Cineon
- `RED_LOG_FILM`: RED Log Film
- `RED_LOG3G10`: RED Log3G10

### `FileFormat`
Enum of supported file formats:
- `MP4`: MP4 container
- `MOV`: QuickTime Movie
- `MXF`: Material eXchange Format
- `DPX`: Digital Picture Exchange
- `EXR`: OpenEXR
- `TIFF`: Tagged Image File Format
- `PNG`: Portable Network Graphics
- `JPEG`: JPEG image
- `WAV`: Waveform Audio File Format
- `AIFF`: Audio Interchange File Format
- `MP3`: MP3 audio
- `AAC`: Advanced Audio Coding
- `AC3`: Dolby Digital
- `EAC3`: Dolby Digital Plus
- `DTS`: Digital Theater Systems
- `OP1A`: MXF OP-1A
- `AS11`: AS-11
- `DNXHD`: Avid DNxHD
- `DNXHR`: Avid DNxHR
- `PRO_RES`: Apple ProRes
- `HAP`: VFX HAP codec
- `H264`: H.264/AVC
- `H265`: H.265/HEVC
- `AV1`: AOMedia Video 1
- `THEORA`: Theora
- `VP8`: VP8
- `VP9`: VP9
- `WEBM`: WebM
- `MKV`: Matroska
- `AVI`: Audio Video Interleave
- `FLV`: Flash Video
- `F4V`: Flash Video
- `SWF`: Small Web Format
- `M2TS`: MPEG-2 Transport Stream
- `MTS`: AVCHD
- `M2T`: MPEG-2 Transport Stream
- `TS`: MPEG-2 Transport Stream
- `M4V`: MPEG-4 Video
- `3GP`: 3GPP
- `3G2`: 3GPP2
- `ASF`: Advanced Systems Format
- `WMV`: Windows Media Video
- `DIVX`: DivX
- `XVID`: Xvid
- `HEIF`: High Efficiency Image Format
- `HEIC`: High Efficiency Image Container
- `GIF`: Graphics Interchange Format
- `BMP`: Bitmap Image File
- `TGA`: Truevision TGA
- `J2K`: JPEG 2000
- `JP2`: JPEG 2000
- `J2C`: JPEG 2000 Code Stream
- `PPM`: Portable Pixmap Format
- `PGM`: Portable Graymap Format
- `PBM`: Portable Bitmap Format
- `PAM`: Portable Arbitrary Map
- `WEBP`: WebP
- `DNG`: Digital Negative
- `CR2`: Canon Raw 2
- `NEF`: Nikon Electronic Format
- `ARW`: Sony Alpha Raw
- `SR2`: Sony Raw 2
- `SRF`: Sony Raw Format
- `PEF`: Pentax Electronic Format
- `RW2`: Panasonic Raw 2
- `RAF`: Fujifilm Raw
- `ORF`: Olympus Raw Format
- `ERF`: Epson Raw Format
- `MEF`: Mamiya Raw Format
- `MOS`: Leaf Raw Format
- `SRW`: Samsung Raw Format
- `X3F`: Sigma Raw Format
- `RAW`: Raw Image Format
- `BAY`: Casio Raw Format
- `CRW`: Canon Raw
- `CAP`: Phase One Raw Format
- `IIQ`: Phase One Raw Format
- `EIP`: Enhanced Image Package
- `DCR`: Kodak Digital Camera Raw
- `K25`: Kodak K25
- `KDC`: Kodak Digital Camera
- `DNG`: Digital Negative
- `PEF`: Pentax Electronic Format
- `PTX`: Pentax Raw Format
- `PXN`: Logitech Raw Format
- `RWL`: Leica Raw Format
- `SR2`: Sony Raw 2
- `SRF`: Sony Raw Format
- `X3F`: Sigma Raw Format
- `ARW`: Sony Alpha Raw
- `CR2`: Canon Raw 2
- `CR3`: Canon Raw 3
- `CRW`: Canon Raw
- `DNG`: Digital Negative
- `ERF`: Epson Raw Format
- `IIQ`: Phase One Raw Format
- `NEF`: Nikon Electronic Format
- `NRW`: Nikon Raw
- `ORF`: Olympus Raw Format
- `PEF`: Pentax Electronic Format
- `RAF`: Fujifilm Raw
- `RAW`: Raw Image Format
- `RW2`: Panasonic Raw 2
- `RWL`: Leica Raw Format
- `SRW`: Samsung Raw Format
- `SR2`: Sony Raw 2
- `SRF`: Sony Raw Format
- `X3F`: Sigma Raw Format

This reference covers the core functionality of the DaVinci Resolve MCP package. For more detailed usage examples, see the [Usage Examples](USAGE_EXAMPLES.md) document.
