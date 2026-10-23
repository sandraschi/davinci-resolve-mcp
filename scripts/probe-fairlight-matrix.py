"""Fairlight API matrix probe — run with Resolve OPEN + project + timeline open.

Usage:
  uv run python scripts/probe-fairlight-matrix.py

Dumps hasattr matrix for every timeline/Fusion call our fairlight_tools depend on,
so Dani (Serato brain) and Sandra see what's Free-real vs invented — no guessing.
Exits 2 when Resolve isn't running (honest, not fake).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "src")

TIMELINE_METHODS = [
    "GetTrackCount",
    "GetTrackName",
    "GetIsTrackMuted",
    "GetIsTrackSolo",
    "GetIsTrackLocked",
    "SetTrackMute",
    "SetTrackSolo",
    "SetTrackVolume",
    "SetTrackPan",
    "GetTrackVolume",
    "GetTrackPan",
    "GetSetting",
    "SetTrackProperty",
    "GetTrackProperty",
    "GetName",
]
FUSION_NODES = ["AudioEQ", "AudioCompressor", "AudioLimiter", "AudioNormalize", "AudioLoudness"]
BUS_KEYS = ["busMainCount", "busSubCount", "busAuxCount"]


def main() -> int:
    from davinci_resolve_mcp.connection.environment import ResolveEnvironment

    env = ResolveEnvironment()
    print(f"resolve_running={env.check_resolve_running()}")
    print(f"install={env.detect_resolve_installation()}")
    if not env.check_resolve_running():
        print("MATRIX: disconnected — start Resolve, open a project + timeline, retry.")
        return 2
    env.setup_environment_variables()
    try:
        import DaVinciResolveScript as dvr  # type: ignore
    except ImportError as e:
        print(f"MATRIX: no scripting module: {e}")
        print("Enable Preferences -> General -> External scripting using: Local")
        return 2
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("MATRIX: scriptapp returned None — scripting bridge off?")
        return 2
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject() if pm else None
    print(f"project={proj.GetName() if proj else None}")
    tl = proj.GetCurrentTimeline() if proj else None
    print(f"timeline={tl.GetName() if tl else None}")
    if not tl:
        print("MATRIX: open a timeline first.")
        return 2
    print(f"audio_tracks={tl.GetTrackCount('audio')}")
    for m in TIMELINE_METHODS:
        print(f"hasattr timeline.{m}={hasattr(tl, m)}")
    try:
        fusion = resolve.Fusion()
        comp = fusion.GetCurrentComp() if fusion else None
    except Exception as e:
        print(f"fusion_error={e}")
        comp = None
    print(f"fusion_comp={bool(comp)}")
    if comp:
        for n in FUSION_NODES:
            try:
                print(f"findtool {n}={bool(comp.FindTool(n))}")
            except Exception as e:
                print(f"findtool {n}=error {e}")
    for k in BUS_KEYS:
        try:
            print(f"getsetting {k}={tl.GetSetting(k)}")
        except Exception as e:
            print(f"getsetting {k}=error {e}")
    print(f"script_api={Path(__file__).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
