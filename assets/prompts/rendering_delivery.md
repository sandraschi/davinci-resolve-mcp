# Rendering & Delivery - DaVinci Resolve MCP

## Export Formats and Presets

### Platform-Specific Exports

#### **YouTube**
```python
render_youtube(
    resolution="1080p",  # or 4K
    quality="high",
    audio_codec="AAC",
    audio_bitrate="320kbps"
)

Settings:
- Codec: H.264 or H.265
- Bitrate: 8-12 Mbps (1080p), 35-45 Mbps (4K)
- Frame rate: Match source
- Audio: AAC 320kbps stereo
```

#### **Instagram**
```python
render_instagram(
    format="square",  # 1:1, or "portrait" 9:16, "landscape" 16:9
    duration=60,  # Reels/Posts max
    quality="high"
)

Requirements:
- Max 60 seconds (Reels/Posts)
- Max 15 minutes (IGTV)
- Square 1:1 or vertical 9:16 popular
- H.264, < 100 MB file size
```

#### **Professional Delivery**
```python
# ProRes for mastering
render_prores(
    codec="ProRes 422 HQ",
    resolution="4K",
    colorspace="Rec.2020",
    audio="Uncompressed PCM"
)

# DNxHD for editing
render_dnxhd(
    quality="DNxHD 220x",
    resolution="1080p"
)
```

### Render Queue Management
```python
# Batch render multiple formats
add_to_render_queue([
    {"preset": "YouTube 4K", "name": "Project_YT_4K"},
    {"preset": "Instagram Square", "name": "Project_IG"},
    {"preset": "ProRes Master", "name": "Project_Master"}
])

start_render(notify_on_complete=True)
```

---

## Quality Control

### Pre-Render Checklist
- ✅ Timeline markers removed (or hidden)
- ✅ All clips rendered/optimized
- ✅ Color grade applied to all clips
- ✅ Audio levels proper (-6dB max peaks)
- ✅ Graphics/titles checked
- ✅ Export range correct (entire timeline or in/out)

### Post-Render Verification
- ✅ File size appropriate
- ✅ Duration matches timeline
- ✅ Video plays smoothly (no corruption)
- ✅ Audio in sync
- ✅ Quality acceptable on target platform

---

**Austrian Standards**: Professional delivery, every time! 🇦🇹📦

