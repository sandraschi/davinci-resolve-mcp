# Fleet Hardware Controller Guide (Sub-$500)

## Design Goal

Every fleet repo with a 3D viewport, DAW, NLE, or robot sim deserves a physical interface. Hands-on control
is faster than mouse/keyboard for continuous parameters (color wheels, camera moves, robot joints, faders).
All controllers listed below are **reprogrammable** — they expose USB HID or MIDI which can be routed to
game engines (Godot), DAWs (Fairlight/JUCE), robot sims (Gazebo/Yahboom), or custom Python bridges.

**Price cap: $500.** Everything here ships for less. Multiple can be combined for a sub-$500 desk setup.

---

## Category 1: Color Grading / Creative Consoles

### BMD DaVinci Resolve Micro Color Panel — **$559** (slightly over cap)

- 3 high-quality trackballs (lift/gamma/gain)
- 12 primary corrector knobs (contrast, pivot, saturation, hue, midtone detail, etc.)
- Dedicated keys for PowerWindows, qualifiers, tracking, still store
- Bluetooth + USB-C, bus-powered (no wall wart)
- USB-HID protocol — only works with Resolve's proprietary panel driver
- **Not programmable for other apps** — Resolve-only

**Verdict**: Best value for a *dedicated* Resolve color panel. Not useful for other repos.

---

### Monogram Creative Console — **$200-500** (modular)

Modular snap-together blocks with CNC aluminum bodies, gold-plated connectors, neodymium magnets.

| Module | Price | What |
|--------|-------|------|
| **Core** (required) | $129 | Powers the chain, 2 mechanical keys, USB-C to PC/Mac |
| **Orbiter** | $109 | Pressure-sensitive disc + infinite encoder ring. 2D/3D express control. Best for color wheels, virtual camera orbit, pan/tilt. |
| **Dial** | $99 | 3 endless encoders with push-buttons. 135 programmable functions. |
| **Slider** | $99 | 3 linear potentiometers (horizontal or vertical). 45 functions. |
| **Essential Keys** | $79 | 3 mechanical switches. 45 functions per module. On-screen labels. |

**Starter kit: Core + Orbiter + Dial = $337.** Add a Slider for $436. Add Keys for $515 (slightly over).

**Why it's ideal for the fleet:**
- **Open API**: Monogram Creator app exposes a **WebSocket server** on `localhost:43042`. Any app can listen for events. Python SDK available. Godot GDScript bridge exists. Unreal Engine Blueprint integration confirmed (CineTracer uses it).
- **Pre-built integrations**: DaVinci Resolve, Premiere Pro, Lightroom, Capture One, Ableton Live, Logic Pro, Final Cut, Unreal Engine, Photoshop. All work out of the box.
- **Virtual production**: Matt Workman (CineTracer) uses Orbiter for virtual camera control in UE4. Magnopus used it on Lion King VR project.
- **Zero config switching**: Press a button, the whole console remaps for a different app. Orbiter becomes a color wheel in Resolve, a camera orbit in Godot, a jog wheel in audio.

**Fleet cross-connect potential**:
```
Orbiter → Resolve (color wheels) or Godot (camera) or Resonite (world navigation)
Dial   → Fairlight (EQ bands) or Gazebo (joint control) or Blender (timeline scrub)
Slider → Fairlight (faders) or Yahboom (servo speed) or DVR (primary bars)
Keys   → Any app (macro triggers, timeline markers, record/stop)
```

---

### Loupedeck CT — **$469** (discontinued sales announced March 2025)

- Touchscreen with 6 physical dials, 8 buttons, jog wheel
- Native Resolve, Lightroom, Premiere, Photoshop, Ableton integrations
- Loupedeck Marketplace with 200+ community plugins
- **March 2025**: Loupedeck announced end of sales. Existing units still work but the ecosystem is sunsetting.
- Not recommended for new purchases. Buy used or switch to Monogram.

---

## Category 2: MIDI Controllers (Universal Reprogrammability)

Every MIDI device sends standard CC (Control Change) messages. Any software that can listen to MIDI
can use them — Python via `python-rtmidi` / `mido`, Godot via `godot-midi`, webapps via WebMIDI API,
DAWs natively. This makes them the **most flexible fleet controllers**.

### Korg nanoKONTROL2 — **$60**

- 8 faders, 8 rotary knobs, 24 buttons (mute/solo/rec for each channel + transport)
- USB bus-powered, tiny (fits next to keyboard)
- Standard MIDI CC — every control sends a unique CC number
- **Perfect for**: Fairlight faders, Godot animation blend trees, Gazebo joint velocity, any parameter strip

### Behringer X-Touch Mini — **$80**

- 8 endless rotary encoders with LED rings (shows current value visually)
- 16 backlit buttons, 1 motorized fader (60mm)
- Two layers (A/B) — double the controls
- Mackie Control protocol support (works with any DAW natively)
- **Perfect for**: Fairlight channel strips, DVR primary bars, virtual camera rigs

### Akai MPK Mini Play MK3 — **$130**

- 25 mini keys (velocity-sensitive), 8 backlit MPC pads, 4 rotary knobs
- Built-in speaker + 128 sounds (works standalone as a synth)
- MIDI over USB + 3.5mm TRS MIDI out
- **Perfect for**: Godot music/rhythm games, Resonite instrument server, Fairlight virtual instruments

### Novation Launchpad Mini MK3 — **$110**

- 64 velocity-sensitive RGB pads (8×8 grid)
- USB bus-powered
- **Perfect for**: Godot grid-based games, clip launching in DAWs, Resonite toggle panels, Gazebo command grids

### Faderfox UC4 — **$250** (German made)

- 8 faders, 8 rotary encoders, 8 buttons, all freely assignable
- No software needed — all configuration done on-device via menus
- MIDI over USB + DIN MIDI. Built like a tank (metal chassis).
- **Perfect for**: The "one controller for everything" option. No PC dependencies.

---

## Category 3: Game Controllers

Standard gamepads are fully supported in Godot, Unity, Unreal, Resonite, and Gazebo via
SDL/evdev/DirectInput/HID. Modern controllers expose axes (analog triggers, joysticks),
buttons, gyroscope, accelerometer, and haptic feedback.

### Xbox Wireless Controller — **$60**

- Best cross-platform support (XInput on Windows, native on Linux via xpad, macOS via driver)
- 2 analog sticks, D-pad, 4 face buttons, 2 shoulder, 2 analog triggers
- Bluetooth + USB-C, works wirelessly
- **NASA uses Xbox controllers for robot arm control** (seriously — they're that reliable)
- **For**: Godot character control, Gazebo teleop, Resonite avatar movement, Yahboom robot driving

### Sony DualSense (PS5) — **$70**

- Haptic feedback (voice coil actuators, not rumble motors — precise vibration)
- Adaptive triggers (can dynamically change resistance via API)
- Touchpad (dual-touch, clickable), 6-axis gyroscope + accelerometer
- Gyro + touchpad make it a **poor man's 6DOF spacemouse**
- Linux kernel driver (`hid-playstation`) since 5.12, Windows via Steam Input
- **For**: Godot physics-based interaction, Resonite gesture control, robot end-effector teleoperation

### 8BitDo Pro 2 — **$50**

- SNES-style with modern features: 2 analog sticks, gyro, 2 back paddles, turbo
- Switch between XInput, DInput, Switch, and macOS modes
- Built-in profile switching (3 profiles on controller, no software needed)
- Hall effect joystick version available (no drift, ever) — **$55**
- **For**: Retro-style Godot games, any project needing a dead-simple, never-break controller

### 8BitDo Ultimate 2C — **$20**

- The cheapest quality controller on the market
- Hall effect sticks + triggers, 2 back paddles, 2.4GHz dongle + USB-C + Bluetooth
- **Buy 4 for $80** — equip a whole testing bench
- **For**: Multiplayer Godot games, classroom/testing setups, "use and abuse" scenarios

---

## Category 4: Macro Pads & Specialized Input

### Elgato Stream Deck MK.2 — **$150** (15 LCD buttons)

- 15 programmable LCD keys that display custom icons
- Can trigger keyboard shortcuts, launch scripts, HTTP requests, MIDI commands
- Open-source alternatives exist: `streamdeck-linux-gui`, `Bitfocus Companion`
- Plugin marketplace with hundreds of integrations (OBS, Twitch, Resolve, Photoshop, etc.)
- WebSocket API for custom integration (`streamdeck-ws` Python library)
- **For**: Any repo that needs a "mission control" panel — trigger renders, switch scenes, start/stop servers

### Elgato Stream Deck Mini — **$60** (6 LCD buttons)

- Same platform, fewer buttons. Good as a secondary panel or starter unit.

### XPPen ACK05 Shortcut Remote — **$40**

- 10 programmable keys + scroll wheel dial, wireless (2.4GHz dongle), tiny
- Sends standard keyboard shortcuts (config via driver)
- **Budget alternative to Stream Deck** for macro/trigger use

---

## Category 5: DIY / SBC-Based Controllers

If your fleet needs a *custom* controller (specific knob layout, embedded display, etc.),
build one with off-the-shelf parts:

### Raspberry Pi Pico + CircuitPython — **$5-15**

- Native USB HID support (appears as keyboard, mouse, gamepad, or MIDI device)
- 26 GPIO pins for buttons, encoders, pots (ADC), I2C displays
- `adafruit_hid` library makes it trivial — 20 lines of Python for a custom HID device
- **$30 total**: Pico ($5) + 4 rotary encoders ($8) + 4 buttons ($4) + OLED ($5) + case ($8)
- **For**: Building a custom resolve panel clone, a robot control pendant, a specialized game controller

### Arduino Micro / Pro Micro — **$10-20**

- Native ATmega32U4 with hardware USB HID
- Extensive MIDI library support (MIDIUSB, Control Surface)
- **Best for**: A dedicated MIDI controller with custom knob/fader layout

---

## Fleet Repo Assignments (Recommended)

| Repo | Controller(s) | Budget | Rationale |
|------|--------------|--------|-----------|
| **davinci-resolve-mcp** | Monogram Core + Orbiter + Dial ($337) | $337 | Color wheels via Orbiter, primary bars via Dial. Or BMD Micro for dedicated Resolve use. |
| **godot-mcp** | Xbox Controller ($60) + 8BitDo Ultimate 2C × 2 ($40) | $100 | Game input testing, character control, multiplayer development |
| **resonite-mcp** | DualSense ($70) + Stream Deck Mini ($60) | $130 | 6DOF gyro for world navigation, Stream Deck for scene switching |
| **gazebo-mcp** | Behringer X-Touch Mini ($80) + Xbox Controller ($60) | $140 | Knobs for joint control, gamepad for teleop |
| **yahboom-mcp** | Xbox Controller ($60) + Korg nanoKONTROL2 ($60) | $120 | Gamepad for driving, faders for servo speed/position |
| **reaper-mcp / audiotool-nexus** | Korg nanoKONTROL2 ($60) + Behringer X-Touch Mini ($80) | $140 | Faders + knobs for mixing, transport control |
| **freecad-mcp** | 3Dconnexion SpaceMouse Compact ($150) or DualSense ($70) | $150 | 6DOF navigation for CAD viewports |
| **blender-mcp** | Monogram Orbiter ($109 + Core $129 = $238) or DIY Pico controller ($30) | $30-238 | Orbiter for camera/scene navigation |
| **multi-backup-mcp** | Stream Deck Mini ($60) | $60 | One-button backup triggers, status display |

---

## Software Bridge Layer (Universal Python MIDI/HID ↔ MCP)

A single Python bridge running alongside the MCP server can translate any MIDI/HID device
into MCP tool calls. Example architecture:

```
MIDI Device → mido / python-rtmidi → Fleet Bridge → MCP tool calls
HID Device  → hidapi / evdev        →              → resolve_color("adjust_wheels", ...)
WebSocket   → Monogram Creator API   →              → resolve_fairlight("set_volume", ...)
```

This is the next logical addition — a `controller_bridge.py` module that listens for
connected devices and routes their inputs to portmanteau tool calls. All 9 repos
above could share the same bridge code.

## Procurement Strategy (Total Fleet Cost)

| Priority | Item | Qty | Unit | Total |
|----------|------|-----|------|-------|
| 1 | Monogram Core + Orbiter + Dial | 1 | $337 | $337 |
| 2 | Xbox Wireless Controller | 3 | $60 | $180 |
| 3 | 8BitDo Ultimate 2C (Hall) | 4 | $20 | $80 |
| 4 | Behringer X-Touch Mini | 1 | $80 | $80 |
| 5 | Korg nanoKONTROL2 | 1 | $60 | $60 |
| 6 | Stream Deck Mini | 1 | $60 | $60 |
| 7 | Elgato Stream Deck MK.2 | 1 | $150 | $150 |
| 8 | Raspberry Pi Pico (DIY kit parts) | 2 | $30 | $60 |
| | **TOTAL** | | | **$1,007** |

That's ~$3/day amortized over a year, covering 9 repos with physical interfaces.
Start with #1 (Monogram) and #2 (Xbox controllers) — those cover 80% of use cases.
