# Subtitle Management

Full subtitle track operations with SRT import/export.

## Portmanteau (default)
```
resolve_subtitle("add", name="Sub1", start_frame=0, end_frame=48, text="Hello")
resolve_subtitle("get", track_index=1)
resolve_subtitle("edit", subtitle_index=0, text="Updated text")
resolve_subtitle("delete", subtitle_index=0)
resolve_subtitle("import_srt", srt_path="C:/captions.srt")
resolve_subtitle("export_srt", output_path="C:/out.srt")
```

## Individual Tools
- `add_subtitle(track_index, name, start_frame, end_frame, text, timeline_name)`
- `get_subtitles(track_index, timeline_name)`
- `import_subtitles_srt(srt_path, track_index, frame_rate, timeline_name)`

## SRT Import/Export
The SRT importer parses standard SRT format with timestamp-to-frame conversion.
The SRT exporter converts subtitle items back to SRT format.

```
resolve_subtitle("import_srt", srt_path="captions.srt", track_index=1)
resolve_subtitle("export_srt", output_path="output.srt", track_index=1)
```

## Resolve API
Uses `timeline.InsertSubtitle()`, `timeline.GetSubtitleList()`, `timeline.DeleteSubtitle()`, `subtitle.SetClipProperty("Text", ...)`.
