# Audio Mixing Guide - DaVinci Resolve MCP

## Fairlight Audio Post-Production

### Audio Track Organization
```
Standard track layout:
Track 1-2: Dialogue (stereo)
Track 3-4: Sound effects
Track 5-6: Music
Track 7-8: Ambience
Track 9+: Additional as needed
```

### Dialogue Mixing
```python
# Target levels (professional broadcast)
dialogue_levels = {
    "peak": -6 dB,
    "average": -12 to -18 dB,
    "target_lufs": -16 LUFS (streaming), -24 LUFS (broadcast)
}

# EQ for clarity
eq_dialogue(
    highpass=80,  # Remove rumble
    presence_boost=3000,  # Speech clarity
    sibilance_reduce=8000  # Reduce harsh "s" sounds
)

# Compression
compress_dialogue(
    ratio=3:1,
    threshold=-18,
    attack=5ms,
    release=50ms
)
```

### Music and SFX
```
Music mixing:
- Duck under dialogue (sidechaining)
- EQ to avoid masking dialogue (cut 2-4kHz)
- Volume automation (builds, quieter during dialogue)

Sound effects:
- Foley (footsteps, cloth, props)
- Hard effects (doors, impacts)
- Ambience (room tone, atmosphere)
- Appropriate levels (support, not dominate)
```

### Final Mix
```
Mastering process:
1. Balance all elements
2. Check for clipping
3. Limiter on master (-1dB ceiling)
4. Loudness metering (LUFS target)
5. Listen on multiple systems (headphones, speakers, phone)
6. Export audio mix/stems
```

---

**Austrian Sound**: Clear, balanced, professional! 🇦🇹🔊

