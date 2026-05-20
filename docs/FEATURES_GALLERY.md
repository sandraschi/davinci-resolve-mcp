# Gallery Stills & Grade Versioning

Grab stills, list gallery, and apply grades between clips.

## Portmanteau (default)
```
resolve_color("grab_still", still_name="Reference Grade")
resolve_color("adjust_wheels", lift={"r": 0.1, "b": -0.05})
resolve_color("grab_still", still_name="Warm Version")
resolve_color("get_stills")
resolve_color("apply_grade_from_still", still_index=1)
```

## Individual Tools
- `grab_still(still_name, timeline_name)` — Grab still from current clip
- `get_stills()` — List all stills in current gallery album
- `apply_grade_from_still(still_index, timeline_name)` — Apply grade from a still

## Resolve API
Uses `project.GetGallery()`, `gallery.GetCurrentStillAlbum()`, `album.GrabStill()`, `album.GetStills()`, `clip.ApplyGradeFromStill()`.
