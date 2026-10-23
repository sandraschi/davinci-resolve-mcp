# Fairlight plan — davinci-resolve-mcp (2026-10-22)

DR Free = free as in beer, Fairlight included. This repo has neglected it: backend 9 ops exist but uneven, webapp `fairlight.tsx` is mute/solo only. Fix in place, don't holdall into democraft-mcp.

## Ground truth (do first, no code)

Resolve Scripting API is the boss, not our wrappers. Against installed Free build, verify each call and write matrix in `docs/DAVINCI_RESOLVE.md`:

- `GetTrackCount(audio)`, `GetTrackName`, `GetIsTrackMuted/Solo/Locked`, `SetTrackMute/Solo/Volume`, `GetTrackVolume/Pan`, `SetTrackPan` — which exist on Free?
- `GetSetting busMainCount/Sub/Aux` — real keys or invented? Current `get_buses` falls back to Master-only, prove why.
- `SetTrackProperty sendXLevelY` — real or invented? Current `track_send` likely wrong.
- Fusion `AudioEQ/AudioCompressor/AudioNormalize/AudioLoudness` nodes — exist on current comp on Free? Current `track_eq`/`add_audio_effect` assume them.
- Automation: read-only today via Fusion comp, 4 params. Is write possible at all?

## Backend honesty (Phase 1)

1. Unify `audio_tools.get_audio_tracks` vs `fairlight_get_timeline_tracks` — one returns volume/pan, other mute/solo/locked. Single impl returns all six + type/channel.
2. `fairlight.tsx` only calls tracks/mute/solo. Expose volume/pan already in impls before adding new ops.
3. `track_send` / `get_buses`: either bind to verified API or return `unsupported_on_free` explicitly, never fake success with invented property names.
4. `track_eq`: keep Fusion path but mark `fusion_fallback`, probe native Fairlight EQ first if API exposes it. Log which path won per call.
5. `normalize_audio`: today just adds a Normalize node per track. Either drive real loudness or rename to `tag_normalize`.
6. Tests: fake Resolve object covering Free vs Studio differences, no live Resolve required for `just ci`.

## Toolset coverage (Phase 2)

Only after Phase 1 matrix is green:
- clip-level: list/move/trim audio clips, fades, split
- loudness: real LUFS read where API allows, else honest `unavailable`
- automation write (volume/pan/mute at minimum, EQ gain if possible)
- bus assign + audio-only render preset (`resolve_render` already has timeline/presets, add fairlight bounce path)
- keep 9 portmanteaus, no new top-level tools — extend ops inside `resolve_fairlight` / `resolve_audio`.

## Webapp beautiful pages (Phase 3)

`fairlight.tsx` 7.4k today: list + mute/solo + open-page. Target mixer, dark slate, amber accent already started:
- faders for volume + pan, polling refresh, per-track meters where API allows (else honest empty state, no fake meters)
- EQ panel (6-band read, edit where backend allows), sends/buses card, automation lane view (read first)
- `data-testid` on every control: `fairlight-volume-*`, `fairlight-pan-*`, `fairlight-eq-*`
- empty/disconnected states already good — keep them, add Free-vs-Studio note (Atmos etc. Studio-only)
- follow WEBAPP_SOTA catch-them-all, no light backgrounds

## Docs (Phase 4)

- `docs/FEATURES_FAIRLIGHT.md` + `docs/TOOLS.md` regenerated from impls, mark Free vs Studio per op
- `docs/ONBOARDING.md`: Free download link, no account, scripting enable steps, AbletonOSC-style pitfall section (what silently does nothing and why)
- `llms-full.txt` regen via `scripts/build-llms-full.ps1`
- `docs/TOMORROW` pointer closed, session-log entry per change

## Out of scope

- democraft-mcp stays ArtCraft-only. No Resolve logic there.
- No `daw-mcp` in this pass. When it comes, it calls this repo's `resolve_fairlight`, not a copy.
- No RIPX integration. Manual sidecar only (see TOMORROW-2026-10-23).

## Tomorrow lazy order

1. matrix (30 min, Resolve open, no code)
2. unify get_tracks (volume/pan/mute/solo/locked in one)
3. wire volume to webapp fader
4. decide send/bus honest unsupported vs real fix
