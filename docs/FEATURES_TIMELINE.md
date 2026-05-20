# Timeline Features: Markers & Keyframes

## Markers

Timeline markers enable labeling frames with colors, names, notes, and duration.

### Portmanteau (default)
```
resolve_timeline("add_marker", frame=120, color="Red", name="VFX cue", note="Add explosion", duration=5)
resolve_timeline("get_markers")
resolve_timeline("delete_marker", frame=120)
```

### Individual Tools
- `add_timeline_marker(frame, color, name, note, duration, timeline_name)`
- `get_timeline_markers(timeline_name)`
- `delete_timeline_marker(frame, timeline_name)`

### Supported Colors
Blue, Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia, Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream

### Resolve API
Uses `timeline.AddMarker()`, `timeline.GetMarkers()`, `timeline.DeleteMarkerAtFrame()`.

---

## Keyframes

Animate clip properties (Zoom, Position, Speed, etc.) across frames.

### Portmanteau (default)
```
resolve_timeline("add_keyframe", property_name="Zoom", frame=0, value=1.0)
resolve_timeline("add_keyframe", property_name="Zoom", frame=48, value=1.5)
resolve_timeline("get_keyframes", property_name="Zoom")
resolve_timeline("delete_keyframe", property_name="Zoom", frame=24)
```

### Clip Property Animation
```
resolve_timeline("set_clip_property", property_name="Speed", value=2.0)
resolve_timeline("set_clip_property", property_name="Position X", value=960)
```

### Resolve API
Uses `timelineItem.AddKeyframe()`, `timelineItem.GetKeyframeList()`, `timelineItem.DeleteKeyframe()`, `clip.SetClipProperty()`.
