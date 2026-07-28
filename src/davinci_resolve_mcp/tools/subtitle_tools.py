"""
DaVinci Resolve Subtitle Tools.

Subtitle track management: create subtitle items, set text, get/delete subtitles.
Uses the Resolve Scripting API timeline clip properties for subtitle manipulation.
"""

import logging
from typing import Any

from ..connection.manager import ResolveConnectionManager
from ..utils.exceptions import ResolveOperationError

logger = logging.getLogger(__name__)


async def add_subtitle_impl(
    app,
    track_index: int,
    name: str,
    start_frame: int,
    end_frame: int,
    text: str = "",
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Add a subtitle item to a subtitle track."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        subtitle_track_count = timeline.GetTrackCount("subtitle")
        if track_index < 1 or track_index > subtitle_track_count + 1:
            raise ResolveOperationError(f"Invalid subtitle track index: {track_index}")

        if hasattr(timeline, "InsertSubtitle"):
            subtitle = timeline.InsertSubtitle(track_index, name, start_frame, end_frame)
            if not subtitle:
                raise ResolveOperationError("Failed to insert subtitle")
            if text and hasattr(subtitle, "SetClipProperty"):
                subtitle.SetClipProperty("Text", text)
            return {
                "status": "success",
                "timeline_name": timeline.GetName(),
                "track_index": track_index,
                "name": name,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "text": text,
                "message": f"Added subtitle '{name}' at frames {start_frame}-{end_frame}",
            }
        else:
            raise ResolveOperationError("InsertSubtitle not available in this API version")

    except Exception as e:
        logger.error(f"Error adding subtitle: {e!s}")
        raise ResolveOperationError(f"Failed to add subtitle: {e!s}") from e


async def get_subtitles_impl(
    app,
    track_index: int = 1,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Get all subtitle items from a subtitle track."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        subtitle_track_count = timeline.GetTrackCount("subtitle")
        if subtitle_track_count == 0:
            return {
                "status": "success",
                "timeline_name": timeline.GetName(),
                "subtitles": [],
                "count": 0,
                "message": "No subtitle tracks found",
            }

        subtitles = []
        if hasattr(timeline, "GetSubtitleList"):
            items = timeline.GetSubtitleList(track_index) or []
            for item in items:
                sub_info = {
                    "name": item.GetName() if hasattr(item, "GetName") else "",
                    "start_frame": item.GetStartFrame() if hasattr(item, "GetStartFrame") else 0,
                    "end_frame": item.GetEndFrame() if hasattr(item, "GetEndFrame") else 0,
                }
                if hasattr(item, "GetClipProperty"):
                    sub_info["text"] = item.GetClipProperty("Text") or ""
                subtitles.append(sub_info)

        return {
            "status": "success",
            "timeline_name": timeline.GetName(),
            "track_index": track_index,
            "subtitles": subtitles,
            "track_count": subtitle_track_count,
            "count": len(subtitles),
        }

    except Exception as e:
        logger.error(f"Error getting subtitles: {e!s}")
        raise ResolveOperationError(f"Failed to get subtitles: {e!s}") from e


async def edit_subtitle_impl(
    app,
    track_index: int,
    subtitle_index: int,
    text: str | None = None,
    start_frame: int | None = None,
    end_frame: int | None = None,
    name: str | None = None,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Edit an existing subtitle item's properties."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        if hasattr(timeline, "GetSubtitleList"):
            items = timeline.GetSubtitleList(track_index) or []
            if subtitle_index < 0 or subtitle_index >= len(items):
                raise ResolveOperationError(f"Invalid subtitle index: {subtitle_index}")
            subtitle = items[subtitle_index]
            changes = {}
            if text is not None and hasattr(subtitle, "SetClipProperty"):
                subtitle.SetClipProperty("Text", text)
                changes["text"] = text
            if name is not None and hasattr(subtitle, "SetName"):
                subtitle.SetName(name)
                changes["name"] = name
            if start_frame is not None and hasattr(subtitle, "SetStartFrame"):
                subtitle.SetStartFrame(start_frame)
                changes["start_frame"] = start_frame
            if end_frame is not None and hasattr(subtitle, "SetEndFrame"):
                subtitle.SetEndFrame(end_frame)
                changes["end_frame"] = end_frame
            return {"status": "success", "changes": changes, "message": "Subtitle updated"}
        else:
            raise ResolveOperationError("GetSubtitleList not available in this API version")

    except Exception as e:
        logger.error(f"Error editing subtitle: {e!s}")
        raise ResolveOperationError(f"Failed to edit subtitle: {e!s}") from e


async def delete_subtitle_impl(
    app,
    track_index: int,
    subtitle_index: int,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Delete a subtitle item from a subtitle track."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        if hasattr(timeline, "DeleteSubtitle"):
            timeline.DeleteSubtitle(track_index, subtitle_index)
            return {
                "status": "success",
                "track_index": track_index,
                "subtitle_index": subtitle_index,
                "message": "Subtitle deleted",
            }
        else:
            raise ResolveOperationError("DeleteSubtitle not available in this API version")

    except Exception as e:
        logger.error(f"Error deleting subtitle: {e!s}")
        raise ResolveOperationError(f"Failed to delete subtitle: {e!s}") from e


async def import_srt_impl(
    app,
    srt_path: str,
    track_index: int = 1,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Import an SRT subtitle file into the timeline as subtitle items."""
    try:
        import os as _os

        if not _os.path.exists(srt_path):
            raise ResolveOperationError(f"SRT file not found: {srt_path}")
        import re

        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        frame_rate = float(timeline.GetSetting("timelineFrameRate") or "24.0")

        def _ts_to_frames(ts_str):
            h, m, s_ms = ts_str.replace(",", ".").split(":")
            s, ms = s_ms.split(".")
            total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
            return int(total_seconds * frame_rate)

        with open(srt_path, encoding="utf-8") as f:
            content = f.read()

        blocks = re.split(r"\n\n+", content.strip())
        imported = 0
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue
            try:
                _ = int(lines[0])
            except ValueError:
                continue
            ts_line = lines[1]
            ts_match = re.match(r"(\S+)\s*-->\s*(\S+)", ts_line)
            if not ts_match:
                continue
            start_frame = _ts_to_frames(ts_match.group(1))
            end_frame = _ts_to_frames(ts_match.group(2))
            text = "\n".join(lines[2:])
            if hasattr(timeline, "InsertSubtitle"):
                subtitle = timeline.InsertSubtitle(track_index, f"Subtitle {imported + 1}", start_frame, end_frame)
                if subtitle and hasattr(subtitle, "SetClipProperty"):
                    subtitle.SetClipProperty("Text", text)
                    imported += 1

        return {
            "status": "success",
            "srt_path": srt_path,
            "imported_count": imported,
            "track_index": track_index,
            "message": f"Imported {imported} subtitles from SRT",
        }

    except Exception as e:
        logger.error(f"Error importing SRT: {e!s}")
        raise ResolveOperationError(f"Failed to import SRT: {e!s}") from e


async def export_srt_impl(
    app,
    output_path: str,
    track_index: int = 1,
    timeline_name: str | None = None,
) -> dict[str, Any]:
    """Export timeline subtitle items to an SRT file."""
    try:
        connection = app.state.connection_manager
        if not connection or not connection.resolve:
            raise ResolveOperationError("Not connected to DaVinci Resolve")

        resolve = connection.get_connection()
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            raise ResolveOperationError("No project is currently open")

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if not timeline:
                raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
        else:
            timeline = project.GetCurrentTimeline()
            if not timeline:
                raise ResolveOperationError("No timeline is currently open")

        frame_rate = float(timeline.GetSetting("timelineFrameRate") or "24.0")

        def _frames_to_ts(frame):
            total_seconds = frame / frame_rate
            h = int(total_seconds // 3600)
            m = int((total_seconds % 3600) // 60)
            s = int(total_seconds % 60)
            ms = int((total_seconds - int(total_seconds)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        srt_lines = []
        index = 1

        if hasattr(timeline, "GetSubtitleList"):
            items = timeline.GetSubtitleList(track_index) or []
            for item in items:
                start = item.GetStartFrame() if hasattr(item, "GetStartFrame") else 0
                end = item.GetEndFrame() if hasattr(item, "GetEndFrame") else 0
                text = ""
                if hasattr(item, "GetClipProperty"):
                    text = item.GetClipProperty("Text") or ""
                srt_lines.append(str(index))
                srt_lines.append(f"{_frames_to_ts(start)} --> {_frames_to_ts(end)}")
                srt_lines.append(text)
                srt_lines.append("")
                index += 1

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))

        return {
            "status": "success",
            "output_path": output_path,
            "exported_count": index - 1,
            "message": f"Exported {index - 1} subtitles to {output_path}",
        }

    except Exception as e:
        logger.error(f"Error exporting SRT: {e!s}")
        raise ResolveOperationError(f"Failed to export SRT: {e!s}") from e


def register_tools(app):
    """Register subtitle tools with the FastMCP app."""

    @app.tool()
    async def add_subtitle(
        track_index: int,
        name: str,
        start_frame: int,
        end_frame: int,
        text: str = "",
        timeline_name: str | None = None,
    ) -> dict[str, Any]:
        """Add a subtitle item to a subtitle track."""
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                if hasattr(timeline, "InsertSubtitle"):
                    subtitle = timeline.InsertSubtitle(track_index, name, start_frame, end_frame)
                    if text and subtitle and hasattr(subtitle, "SetClipProperty"):
                        subtitle.SetClipProperty("Text", text)
                    return {
                        "status": "success",
                        "name": name,
                        "start_frame": start_frame,
                        "end_frame": end_frame,
                        "text": text,
                    }
                raise ResolveOperationError("InsertSubtitle not available")
        except Exception as e:
            raise ResolveOperationError(f"Failed to add subtitle: {e!s}") from e

    @app.tool()
    async def get_subtitles(
        track_index: int = 1,
        timeline_name: str | None = None,
    ) -> dict[str, Any]:
        """Get all subtitle items from a subtitle track."""
        try:
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                sub_count = timeline.GetTrackCount("subtitle")
                if sub_count == 0:
                    return {"status": "success", "subtitles": [], "count": 0}
                subtitles = []
                if hasattr(timeline, "GetSubtitleList"):
                    items = timeline.GetSubtitleList(track_index) or []
                    for item in items:
                        info = {"name": item.GetName() if hasattr(item, "GetName") else ""}
                        if hasattr(item, "GetStartFrame"):
                            info["start_frame"] = item.GetStartFrame()
                        if hasattr(item, "GetEndFrame"):
                            info["end_frame"] = item.GetEndFrame()
                        if hasattr(item, "GetClipProperty"):
                            info["text"] = item.GetClipProperty("Text") or ""
                        subtitles.append(info)
                return {"status": "success", "track_count": sub_count, "subtitles": subtitles, "count": len(subtitles)}
        except Exception as e:
            raise ResolveOperationError(f"Failed to get subtitles: {e!s}") from e

    @app.tool()
    async def import_subtitles_srt(
        srt_path: str,
        track_index: int = 1,
        frame_rate: float = 24.0,
        timeline_name: str | None = None,
    ) -> dict[str, Any]:
        """Import subtitles from an SRT file into the timeline."""
        try:
            import os as _os
            import re

            if not _os.path.exists(srt_path):
                raise ResolveOperationError(f"SRT file not found: {srt_path}")
            with ResolveConnectionManager() as resolve:
                project = resolve.GetProjectManager().GetCurrentProject()
                if not project:
                    raise ResolveOperationError("No project is currently open")
                if timeline_name:
                    timeline = project.GetTimelineByName(timeline_name)
                    if not timeline:
                        raise ResolveOperationError(f"Timeline '{timeline_name}' not found")
                else:
                    timeline = project.GetCurrentTimeline()
                    if not timeline:
                        raise ResolveOperationError("No timeline is currently open")
                if not hasattr(timeline, "InsertSubtitle"):
                    raise ResolveOperationError("InsertSubtitle not available")

                def _ts_to_frames(ts_str):
                    h, m, s_ms = ts_str.replace(",", ".").split(":")
                    s, ms = s_ms.split(".")
                    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
                    return int(total_seconds * frame_rate)

                with open(srt_path, encoding="utf-8") as f:
                    content = f.read()
                blocks = re.split(r"\n\n+", content.strip())
                imported = 0
                for block in blocks:
                    lines = block.strip().split("\n")
                    if len(lines) < 3:
                        continue
                    try:
                        _ = int(lines[0])
                    except ValueError:
                        continue
                    ts_match = re.match(r"(\S+)\s*-->\s*(\S+)", lines[1])
                    if not ts_match:
                        continue
                    start = _ts_to_frames(ts_match.group(1))
                    end = _ts_to_frames(ts_match.group(2))
                    text = "\n".join(lines[2:])
                    subtitle = timeline.InsertSubtitle(track_index, f"Sub {imported + 1}", start, end)
                    if subtitle and hasattr(subtitle, "SetClipProperty"):
                        subtitle.SetClipProperty("Text", text)
                        imported += 1
                return {"status": "success", "imported_count": imported, "message": f"Imported {imported} subtitles"}
        except Exception as e:
            raise ResolveOperationError(f"Failed to import SRT: {e!s}") from e
