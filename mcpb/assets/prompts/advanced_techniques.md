# Advanced Techniques - DaVinci Resolve MCP

## Fusion Compositing

### Node-Based VFX
```
Fusion workflow:
1. Add Fusion comp to timeline
2. Build node tree
3. Add effects (blur, glow, keying)
4. Animate parameters (keyframes)
5. Preview and refine
```

### Common Fusion Operations
```python
# Green screen keying
chroma_key(clip, key_color="green", tolerance=0.1)

# Text animation
add_fusion_text(text="Title", animation="fade_in", duration=2)

# Particle effects
add_particles(type="snow", count=1000, speed=5)
```

## Advanced Color Grading

### Node Structure
```
Serial nodes (in sequence):
Node 1: Balance/correction
Node 2: Primary creative grade
Node 3: Secondary (skin, sky, etc.)
Node 4: Vignette/finishing

Parallel nodes (mixed):
- Separate treatments blended
- Skin tones vs background
```

### Power Windows
```
Shape-based targeting:
- Circle (faces, objects)
- Linear (gradients, sky)
- Curve (custom shapes)
- Tracking (follow subjects)
```

## Speed Effects

### Slow Motion / Time Remap
```python
# Slow motion (50% speed)
change_clip_speed(clip, speed_percent=50, optical_flow=True)

# Speed ramp
add_speed_ramp(clip, start_speed=100, end_speed=25, duration=2)
```

---

**Austrian Innovation**: Technical excellence meets creative vision! 🇦🇹⚡

