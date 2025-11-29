# Color Grading Guide - DaVinci Resolve MCP

## DaVinci Resolve Color Page (Industry Standard!)

### Color Grading Workflow
```
1. Balance (correct exposure, white balance)
2. Contrast (set blacks/whites, tonal range)
3. Color (creative look, mood)
4. Secondary (targeted adjustments)
5. Finalize (vignettes, film grain, sharpening)
```

### Primary Color Correction
```python
# Color wheels: Lift (shadows), Gamma (midtones), Gain (highlights)
adjust_color_wheels(
    clip=current_clip,
    lift={"red": 0, "green": 0, "blue": 0, "lum": -0.05},
    gamma={"red": 0, "green": 0, "blue": 0, "lum": 0},
    gain={"red": 0, "green": 0.05, "blue": 0, "lum": 0.10}
)

# Curves for precise control
adjust_curves(curve_type="rgb", points=[(0,0), (128, 140), (255,255)])
```

### LUTs (Look-Up Tables)
```
Creative LUTs:
- Cinematic (teal/orange, desaturated, filmic)
- Vintage (faded, retro, film emulation)
- High contrast (modern, punchy)

Technical LUTs:
- Log to Rec.709 (camera log conversion)
- Rec.709 to DCI-P3 (color space conversion)
```

### Scopes for Accurate Grading
```
Waveform: Check luminance (0-100 IRE)
Vectorscope: Check color saturation/hue
Parade: RGB balance (no color casts)
Histogram: Overall tonal distribution

Professional targets:
- Blacks: 0-10 IRE
- Whites: 90-100 IRE
- Skin tones: Vectorscope I-line
```

### Common Looks
```
Cinematic Teal/Orange:
- Shadows: Teal/cyan push
- Highlights: Warm/orange push
- Contrast: Crushed blacks, rolled highlights

Film Emulation:
- Slightly desaturated
- Softer highlights
- Film grain overlay
- Warmer skin tones

Commercial/Clean:
- Saturated colors
- Bright, punchy contrast
- White balance accurate
- Sharp, detailed
```

---

## Austrian Precision: Science of color, art of mood! 🇦🇹🎨

