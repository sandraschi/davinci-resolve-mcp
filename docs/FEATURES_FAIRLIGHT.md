# Fairlight Audio Depth

Advanced Fairlight DAW operations: EQ, sends, buses, and automation.

## Portmanteau (default)
```
resolve_fairlight("open_page")
resolve_fairlight("get_tracks")
resolve_fairlight("set_mute", track_index=1, mute=True)
resolve_fairlight("set_solo", track_index=2, solo=True)
resolve_fairlight("set_volume", track_index=1, volume=0.85)
resolve_fairlight("track_eq", track_index=1)  # Read EQ
resolve_fairlight("track_eq", track_index=1, eq_band=1, eq_gain_db=-3.5, eq_frequency=200)
resolve_fairlight("track_send", track_index=1, bus_index=1, send_level=0.75)
resolve_fairlight("get_buses")
resolve_fairlight("track_automation", track_index=1, automation_param="volume")
```

## EQ Operations
Read or set 6-band parametric EQ on a track via Fusion AudioEQ node.
- `eq_band`: 1-6
- `eq_frequency`: Center frequency in Hz
- `eq_gain_db`: Gain in dB
- `eq_q_factor`: Q (bandwidth)
- `eq_band_type`: Filter type (LowPass, HighPass, BandPass, Notch, LowShelf, HighShelf)
- `eq_enabled`: Enable/disable band

## Track Sends
Route audio from a track to a bus:
- `send_level`: 0.0 to 1.0
- `send_pre_fader`: True for pre-fader send
- `send_enabled`: Enable/disable send

## Bus Configuration
Get Main, Sub, Aux, and Master bus layout.

## Automation
Retrieve keyframe automation data for track parameters (volume, pan, mute, EQ band gain).
