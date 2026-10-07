# DaVinci Resolve MCP — User Guide

Talk to DaVinci Resolve in plain language. This guide explains what the
assistant can do, how to ask for it, and what to do when something does not
work. No scripting knowledge required.

## What this is

DaVinci Resolve MCP connects an AI assistant (Claude, Cursor, and other MCP
clients) to a running copy of DaVinci Resolve on your machine. You describe
the edit, grade, mix, caption, or delivery job in words; the assistant drives
Resolve's own scripting API to do it. Everything happens in your real
projects — nothing is simulated, and every action reports back what it did.

It also ships a local web dashboard (project status, timelines, Fairlight
tracks, render queue, logs, chat) on your machine. Nothing leaves your
computer except when you explicitly use a cloud LLM; the default chat path
uses a local model (Ollama or LM Studio).

## Requirements

- DaVinci Resolve 18 or newer, Free or Studio, installed on the same machine.
- External scripting enabled: Resolve Preferences, System, General, "External
  scripting using", set to Local. Open a project — the bridge only answers
  while a project is loaded.
- Python 3.12+ with `uv` for the backend; Node 20+ for the dashboard.
- Optional: Ollama (`ollama pull llama3.1:8b`) for the Chat page.

## First run (five minutes)

1. Install dependencies: `just bootstrap`.
2. Check the environment: `just check` (verifies the Resolve install and the
   scripting paths).
3. Start everything: `start.ps1` (backend on port 10843, dashboard on 10842).
4. Open Resolve, open any project.
5. Ask your assistant: "List my Resolve projects." It should answer with your
   real project names. If it says Resolve is unreachable, see Troubleshooting.

## Connecting an AI client

Claude Desktop: add an `mcpServers` entry pointing at this repo (command is
the full `uv.exe` path, args `run davinci-resolve-mcp mcp`, working directory
the repo root). See README for the exact JSON. Cursor and other MCP clients
use the same shape over stdio. For HTTP transport, set `MCP_TRANSPORT=http`
and point the client at the backend port.

## How to ask (general rules)

- Name things exactly: project names, timeline names, clip paths, track
  numbers. The assistant matches names literally.
- One job per message works best; the assistant confirms each step.
- State frames as integers and always mention the frame rate when converting
  from time ("at frame 120 on a 24 fps timeline").
- Destructive requests (delete, overwrite, update settings) trigger a
  confirmation question first — answer it explicitly.
- If the assistant asks for a missing detail (a path, a name, a preset),
  answer just that; the rest of your request is remembered.

## Cookbook: projects

- "List my projects." / "Which project is open?"
- "Create a project called Summer Ad, 4K, 24 fps, then open it."
- "Open the Client Video project."
- "Show me the current project settings."
- "Set the timeline frame rate to 30."
- "What version of Resolve am I running?"

## Cookbook: media

- "Import C:/Footage/a001.mp4 and C:/Footage/a002.mp4."
- "Import everything in C:/Footage/raw into a folder called Raw."
- "What is in the Raw Footage folder?"
- "Make a folder called Assets/Music."
- "Show metadata for C:/Footage/a001.mp4."
- "What clips are loaded right now?"

## Cookbook: timelines and editing

- "Create a timeline called Main Edit, 3840 by 2160."
- "What is the current timeline? How many video and audio tracks?"
- "Add C:/Footage/a001.mp4 to video track 1."
- "Cut video track 1 at frame 240."
- "Move the playhead to frame 120."
- "Add a red marker at frame 120 called VFX cue."
- "List all markers." / "Delete the marker at frame 120."
- "Add a Zoom keyframe at frame 0 with value 1.0, then list keyframes."
- "Set the Speed of the current clip to 2.0."
- "Delete the Zoom keyframe at frame 24."

## Cookbook: color

- "Create a primary node called Base Grade."
- "Apply C:/LUTs/Film.cube to C:/Footage/a001.mp4 at 80 percent."
- "Set the color space from Rec.709 to DaVinci Wide Gamut."
- "Lift the shadows: red plus 0.1, blue minus 0.1."
- "Grab a still from the current clip."
- "List my gallery stills."
- "Apply the grade from still 0."
- "Give me a warm filmic look for this interview." (uses the color_recipe
  prompt, then executes the steps with your approval)

## Cookbook: audio and Fairlight

- "List the audio tracks on the current timeline."
- "Mute track 2." / "Solo track 1." / "Set track 1 volume to 0.8."
- "Open the Fairlight page."
- "Show me the EQ on track 1."
- "Cut 3.5 dB at band 1, 200 hertz, on track 1."
- "Send track 1 to bus 1 at 0.75, pre-fader."
- "Show the bus configuration."
- "Read the volume automation on track 1."
- "Add an EQ effect to track 1."
- "Normalize all tracks to minus 23 LUFS." / "Normalize tracks 1 to 3."

## Cookbook: subtitles

- "Add a subtitle called Intro from frame 0 to 48 with text Hello."
- "Show subtitles on track 1."
- "Change subtitle 0 text to Welcome back."
- "Delete subtitle 2."
- "Import captions from C:/captions.srt."
- "Export track 1 subtitles to C:/delivery/captions.srt."
- "What frame rate is the timeline? I need my SRT to line up."
  (The assistant converts using the timeline rate and states it.)

## Cookbook: rendering and delivery

- "What render presets do I have?"
- "Render the current timeline to C:/Output as MP4."
- "Render to C:/Output as ProRes 422 HQ, 3840x2160."
- "Render with the YouTube 4K preset to C:/Output."
- "What is the status of render job 1?"
- "Give me a delivery checklist for YouTube 4K." (uses the render_checklist
  prompt: preset, settings, queue, verification)
- "Is anything rendering right now?"

## Cookbook: planning and advice

- "Plan my edit: tighten a 20-minute interview to 8 minutes on Main Edit."
  (uses the edit_plan prompt, then works through it step by step)
- "Why does my export look washed out?" (color space / data levels walkthrough)
- "My dialogue is muddy. What should I do?" (EQ and mix guidance)
- "Suggest three places to cut in this timeline."
- "What should I check before delivering to a broadcaster?"

## Using the Chat page

The Chat page (AI Video Editor) talks to your local LLM through the backend —
no API keys, nothing uploaded. Pick a personality (Editor, Colorist,
Fairlight Engineer, Render Wrangler, Custom) to steer the tone; the assistant
composes the skill list into every answer automatically. Try the example
prompt chips to start. Conversations persist locally (last 100 messages);
export to .txt or clear any time. If no model appears in the dropdown, start
Ollama and pull a model first. Answers stream token by token; if the stream
stalls, the error banner says why (usually: Ollama not running).

## Using the dashboard

- Overview: connection state, active project, version, render state, current
  timeline, and a red onboarding banner whenever something needs attention.
- Projects: library with the active project highlighted; retry on errors.
- Timeline: current timeline metadata, tracks, empty states when none is open.
- Fairlight: track list with working mute/solo buttons, refresh, open-page.
- Render Queue: live job status (never demo numbers).
- Video Tools / Production Actions: shortcut cards into real workflows.
- Inbox: warnings and errors from the server log, auto-refreshed.
- Skills: the 9 capability domains with their operations — the same registry
  the chat uses.
- System Logs: the live ring buffer with level/kind/search filters.
- Settings: bridge host/port, local LLM provider + model (persisted), defaults.
- Help: the full in-app manual.

## Troubleshooting

**"Connection manager not initialized" / disconnected.** Start Resolve, open a
project, enable external scripting, then restart the backend (`start.ps1`).
Check `/api/v1/host-status` for the 4-state probe: it tells you whether
Resolve is missing, stopped, running-unreachable, or ready.

**Dashboard shows Offline.** The backend may not be running: open
`http://127.0.0.1:10843/api/v1/health` — it must return `{"status":"ok"}`.
If the port is stuck, `start.ps1` clears zombies first.

**"No project is currently open."** Open (or create then open) a project with
`resolve_project open` before timeline/media/color work.

**"Folder X not found" / "Clip X not found".** List the parent folder first;
names must match exactly, including case. Ask the assistant to list and pick.

**Import reports per-file errors.** The successes still imported; only the
listed files failed (usually a wrong path). Fix the paths and re-run.

**Render job failed.** Read the job status output; check the Deliver page
codec state in Resolve; do not change settings and re-render blindly — ask
what the error means first.

**Chat: "No local LLM detected."** Install Ollama, run `ollama pull
llama3.1:8b`, reload the page. The model dropdown fills automatically.

**Chat streams nothing / errors.** The backend proxies to Ollama at
`OLLAMA_URL` (default localhost:11434). If Ollama moved, set the variable and
restart the backend.

**Subtitle timing drift.** Confirm the timeline frame rate matches your SRT
assumptions; the bridge converts with the timeline rate and states it.

**Slow responses.** Local models on CPU are slow; smaller models answer
faster. Tool calls themselves are fast — model inference dominates.

## FAQ

**Does it modify my projects without asking?** Reads never need confirmation.
Writes that destroy or overwrite (deletes, overwrites, settings updates,
project creation) ask first. You can always say no.

**Free or Studio?** Both work. Some Fairlight/gallery APIs differ by edition
and version; the assistant relays API-version limits instead of guessing.

**Windows, Mac, Linux?** All three. Paths in examples use Windows style;
use your platform's paths.

**Stdio or HTTP?** Stdio for Claude Desktop/Cursor; HTTP for the dashboard
and API clients. Tool behavior is identical.

**Where is my data?** Projects stay in Resolve. Chat history and settings
live in your browser's local storage. Server logs live in memory only.

**Can it do Fusion/VFX?** No — Fusion has no tool coverage. The assistant
says so instead of faking it.

**Can it watch folders or run on a schedule?** No — it acts when you ask.

## Safety notes

Back up important projects before big automated edits (the assistant reminds
you). Review AI-proposed deletes and overwrites. Verify every delivery export
by watching the file — a queued render is not a finished render until
`job_status` says so and the file plays. Keep Resolve updated; scripting
behavior varies across point releases.

## More things to try: projects and media

- "Create a project from the Wedding template at 25 fps."
- "Duplicate my current setup for a second episode." (create + open + describe)
- "Rename my workflow: open the project I worked on yesterday."
  (list, then open by exact name)
- "Is my project saved?" (status check; save happens on render/project ops)
- "Import this folder but treat the PNGs as an image sequence."
- "Import with forced 23.976 fps because Resolve misdetects it."
- "Force 3840x2160 on import; the files report wrong resolution."
- "Where did I import yesterday's footage?" (list folders, then list)
- "Describe every clip in the Raw folder." (list + per-clip metadata)
- "Which clips have audio? Which are video-only?"
- "Find the 4K clips." (list, filter by resolution in the answer)

## More things to try: editing

- "Create a 1080p timeline called selects at 25 fps starting at frame 100."
- "Add these three clips to track 1 in order." (paths, one call each)
- "Put the b-roll on video track 2 above the interview."
- "Cut out frames 240 to 480 on track 1." (cut at both ends; say so)
- "Jump to the third marker." (get_markers, then set_playhead)
- "Mark every scene change." (watch, then add_marker per cut)
- "Rename marker at frame 120 to VFX cue." (delete + add)
- "Animate a slow zoom from frame 0 to 96." (keyframes with values)
- "Copy the grade-feel: list keyframes on Zoom first." (inspect, then act)
- "Slow this clip to half speed." (set_clip_property Speed 0.5)
- "What is under the playhead right now?" (info + markers)

## More things to try: color, audio, captions, delivery

- "Build a node tree: primary, then a windowed skin-tone node, then grain."
- "Convert this timeline from Rec.709 to DaVinci Wide Gamut."
- "Match this clip to the still I just grabbed."
- "Show me my stills; apply still 2 to the current clip."
- "Unmute everything, then solo the music track."
- "Duck the music under dialogue." (automation-guided manual steps)
- "What buses exist? Route dialogue to the main bus."
- "Read the EQ on track 3 before I touch anything."
- "Shift all subtitles 12 frames later." (get, edit each with new frames)
- "Split this SRT import across two tracks." (import, get, describe moves)
- "Render proxies for the whole timeline." (preset + queue + verify)
- "Render three versions: YouTube 4K, Instagram square preset, ProRes master."
- "Check the queue every minute until everything is done."
- "What failed in last night's render batch?"

## End-to-end scenarios

**Wedding highlight (4 hours of footage to 3 minutes).** Open or create the
project. List media and skim metadata for durations. Build a selects timeline
and add the strongest moments. Cut ruthlessly: the assistant proposes cuts,
you confirm. Add markers for music beats. Color: one primary node plus a
soft LUT at reduced intensity, stills checkpoint before delivery. Audio:
normalize dialogue, gentle music bed under. Subtitles only if the couple
asked. Render a review MP4 first, watch it, then render the master.

**Talking-head course (10 lessons).** One project per lesson or one project
with ten timelines — decide up front, because switching is cheap but
reorganizing is not. Template the timeline (intro card, lesson body, outro)
and duplicate per lesson. Normalize every lesson to the same LUFS. Burned-in
subtitles via SRT import per lesson, exported alongside clean masters.
Render presets per platform (course host + YouTube). Verify each file plays
before uploading; keep the render queue receipts (job statuses) until upload
confirms.

**Short film festival delivery.** Confirm specs first: festivals publish
exact codec/container/loudness rules — read them aloud to the assistant.
Master in ProRes or DNxHD at the timeline rate, never resampled. Captions as
sidecar SRT (separate export, named per spec). Keep a textless master plus a
titled version (two timelines, same grade via still-applied grade). Render,
verify duration against the submission form, and keep checksums if required.

**Podcast video version.** Import the multitrack audio and camera angles.
Sync by waveform (manual step in Resolve — the assistant cannot listen).
Cut cameras on questions. Loudness-normalize the mix bus. Export audio-first
(WAV master) then the video MP4. Captions: auto-transcribe elsewhere, import
the SRT here, verify timing against the timeline rate.

**Archival digitization batch.** Import tapes as image sequences where
applicable (as_sequence). One timeline per tape, markers at content
boundaries. No grade beyond a neutral conversion LUT. ProRes masters plus
H.264 proxies in one queue. Name everything with the archive's catalog
scheme from the start — renaming later breaks the SRT and still references.

## Error message catalog (what each one means)

- "Connection manager not initialized": backend and Resolve are not linked.
  Restart the backend after opening Resolve.
- "Not connected to DaVinci Resolve": Resolve is closed or scripting is off.
- "scriptapp returned None": Resolve runs but the bridge is silent. Open a
  project; set external scripting to Always; retry.
- "No project is currently open": open or create-then-open a project first.
- "Project 'X' not found": name mismatch — list projects and copy the exact name.
- "Folder 'X' not found": list the parent; folders are case-sensitive.
- "Clip 'X' not found": list the folder; try the bare clip name.
- "Timeline ... not found": the timeline name differs — ask for timeline info.
- "Invalid subtitle track index": tracks are 1-based; get the track list first.
- "Failed to create folder": the parent path does not exist — create parents first.
- "Import failed" (per file): the file path is wrong or the format is
  unsupported; the other files still imported.
- "Render failed": read the job status; check Deliver-page codec state.
- "No local LLM available" (chat only): start Ollama and pull a model.
- "Backend starting... (1/3)": the backend is still booting; wait and retry.

## Timecode cheat sheet

- HH:MM:SS:FF — hours, minutes, seconds, frames. Frames run 0 to rate-1.
- 24 fps: 48 frames = 2.0 s. 25 fps: 50 frames = 2.0 s. 30 fps: 48 frames = 1.6 s.
- "At 00:01:30" is ambiguous (timecode vs seconds) — the assistant asks.
- Subtitle math follows the timeline rate, stated every time.
- Markers and keyframes take integer frames; fractions are rejected — round
  explicitly and say the rounded value.

## Prompting tips (get better answers)

- Give the goal first, then constraints ("tighten this interview, keep every
  answer under 20 seconds").
- Paste exact names rather than describing ("the clip" fails; "a001_c03.mp4" works).
- Ask for a plan before a long job ("plan first, then execute step by step").
- Ask for verification ("list the markers after adding them").
- Correct the assistant with the right value ("frame 144, not 120") — it
  adjusts without restarting.
- For looks, reference films or moods plus a constraint ("warm like a western,
  but keep skin tones natural").
- For mixes, state the delivery target ("YouTube stereo, minus 14 LUFS" —
  the assistant maps LUFS targets to normalize calls).

## Action reference (what each request needs)

Project: create needs a name; open needs the exact name; list needs nothing;
settings reads need nothing; updates need a settings dict with Resolve's
exact key names (timelineFrameRate, timelineResolutionWidth,
timelineResolutionHeight, pixelAspectRatio, playbackFrameRate,
timelineFormat). Media: import needs existing file paths; list optionally
takes a folder; folders need a path like Parent/Child; metadata needs a clip
path or bare name. Timeline: create needs a name; clips need a file path;
cuts/playhead/markers/keyframes need integer frames; markers accept 19 named
colors; keyframes need a property name plus frame plus value. Color: nodes
need a type; LUTs need clip plus LUT paths; color space needs both spaces;
wheels need r/g/b/y dicts; stills need an index to apply. Audio: effects need
a track plus a type; levels need a track plus at least one of volume, pan,
mute, solo; normalize optionally takes tracks and a LUFS target. Fairlight:
mute/solo/volume need a track; EQ reads by default and writes when band
fields are given; sends need a bus index and level. Subtitles: adding needs
name plus start plus end frames; edits and deletes need the subtitle index;
SRT import/export need file paths. Render: renders need an output directory;
presets just list; preset renders need preset plus output; job status needs
the job id from the queue call.

## Resolve habits that make automation smooth

- Name timelines, tracks, markers, and bins deliberately; automation keys off names.
- Keep one timeline per deliverable; versions are cheap, untangling is not.
- Put review notes as markers with colors (red = fix, green = approved).
- Grab gallery stills at every approved grade stage; they are your undo history.
- Normalize loudness once at the end, not per clip during the edit.
- Render a small review file before the full master; watch it fully.
- Keep source media paths stable; moved files break pool references and every
  path you previously gave the assistant.
- Back up the project database regularly (Project Manager, backup); automation
  cannot recover a corrupted database.
- Use power bins for shared assets across timelines; keep timeline-local media
  in timeline bins.
- Freeze (lock) finished tracks before batch operations so cuts land where
  you expect.

## Twenty more answers

**Can I undo?** Resolve has undo for manual edits. For assistant actions,
prefer non-destructive steps (new nodes, new timelines, checkpoints via
stills); deletes and overwrites always confirm first.

**Will it overwrite my files?** Renders never overwrite unless you pass
overwrite explicitly (and confirm). Project creation picks new names.

**Can it work while I edit?** Avoid it — you and the assistant share one
Resolve session. Let batch jobs finish before touching the timeline.

**Does it see my screen?** No. It reads API state (names, frames, settings),
not pixels. Describe what you see when it matters ("the third clip from
the left").

**Can it hear audio?** No. It reads meters, track state, and settings — not
sound. Loudness numbers come from the normalize tools, not listening.

**Why did it ask three questions?** Because the request was missing three
facts (usually: which project, which timeline, which file). Answer all three
at once to move faster.

**Can it transcode everything overnight?** Yes: queue per timeline with a
preset, verify job statuses in the morning, spot-check files.

**Can it conform an EDL?** Timeline assembly from clip paths is supported;
EDL parsing itself is a manual step — paste the clip list instead.

**Can it upload to YouTube/Vimeo?** No. It renders the file; you upload.

**Can it generate voiceover or music?** No. It edits, mixes, and places audio
you provide.

**Can it translate subtitles?** It moves and formats subtitle text you
provide; translation quality is yours to verify.

**Can it fix out-of-sync audio?** It can slip clips by frames you specify and
read timing state, but sync judgment (watching lip movement) is yours.

**What frame rate should I use?** Match delivery: 24 for cinema, 25 for
European broadcast, 30 for US web, 60+ for smooth motion. Changing mid-project
breaks caption math — decide once.

**What resolution?** Edit at delivery resolution or higher; proxies keep heavy
timelines smooth. State the delivery size before rendering.

**Which codec?** H.264 for web compatibility, H.265 for efficiency, ProRes or
DNx for masters and handoffs, platform presets when offered.

**How loud?** Streaming targets around minus 14 LUFS integrated; broadcast
often minus 23 or minus 24 with true-peak limits. State the target; the
assistant normalizes to it.

**My export stutters.** Check: timeline rate vs export rate match, proxies
vs originals, effects load, disk speed. Render a short section to isolate.

**Colors shift between Resolve and the web.** Usually data-levels or color
space tag mismatches between the viewer, the export, and the player. Export
a test chart, compare in two players, then lock the transform.

**Can multiple people use it?** One session per machine. Collaboration
projects (Blackmagic Cloud) work, but coordinate who drives automation.

**Is my footage uploaded anywhere?** No. Tools run locally against your
Resolve. Only the Chat page contacts a model — local Ollama by default.

## Choosing a local model

Bigger models follow multi-step instructions better but answer slower on CPU;
smaller models are fast but may skip steps. A practical ladder: start with an
8-billion-parameter class model for everyday edits. If plans get sloppy
(missed steps, invented tool names), move up a size class rather than
repeating yourself louder. Keep one model selected per task type: a fast one
for chatty questions, a stronger one for render-planning sessions. Quantized
variants trade a little accuracy for a lot of speed and fit smaller GPUs.
Whatever you pick, the skill list is composed into every answer, so even
small models stay grounded in real tool names. If answers mention tools that
do not exist, say so — that feedback, plus the Skills page registry, keeps
expectations aligned. Reload the model list after pulling a new model; the
dropdown fills automatically on refresh.

## Privacy and data, precisely

Tool execution is fully local: your projects, media, timelines, and grades
never leave the machine. The dashboard backend serves only localhost and LAN
origins you configure. Chat history persists in your browser profile, not on
any server. Server logs live in process memory and vanish on restart. If you
configure a cloud LLM provider, prompts you send go to that provider under
their terms — the bridge never adds telemetry, and keys are only ever read
from your environment, never written anywhere. Screen content, audio content,
and file bytes are never transmitted by any default flow; the bridge exchanges
names, numbers, settings, and short text.

## Glossary (short)

Project, media pool, bin, timeline, track, playhead, marker, keyframe, node,
LUT, gallery/still, qualifier, power window, scopes, Fairlight bus/send,
automation, EDL, timecode, frame rate, resolution, codec, container, LUFS,
render preset/queue/job, subtitle track, SRT, proxy/optimized media.
