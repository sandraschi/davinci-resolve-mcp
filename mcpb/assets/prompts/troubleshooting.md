# Troubleshooting - DaVinci Resolve MCP

## Connection Issues

### Problem: Cannot Connect to Resolve

**Solutions:**
1. ✅ Verify DaVinci Resolve is running
2. ✅ Check Scripting API enabled (Preferences → System → General)
3. ✅ Restart Resolve
4. ✅ Check port 9000 available
5. ✅ Run MCP server with admin rights (Windows)

### Problem: Resolve API Not Responding

**Solutions:**
- Close and reopen Resolve
- Check for Resolve updates
- Verify Python version compatibility (3.8+)
- Check console for Python errors
- Try Resolve Studio (Free version has limitations)

## Import/Export Issues

### Problem: Media Won't Import

**Causes:**
- Unsupported codec/format
- File path too long (>260 chars Windows)
- File permissions
- Corrupted media file

**Solutions:**
- Transcode to supported format (MP4 H.264, MOV ProRes)
- Shorten file path
- Check file plays in media player
- Use MediaInfo to check codec

### Problem: Render Fails

**Troubleshooting:**
1. Check disk space (renders are large!)
2. Verify output path writeable
3. Check codec selection valid
4. Disable GPU acceleration (if crashes)
5. Render shorter sections (find problematic clip)
6. Check Resolve console for errors

---

## Performance Issues

### Slow Playback
```
Solutions:
- Generate optimized media (proxy files)
- Lower playback quality (half/quarter res)
- Render in place (pre-render complex sections)
- Close other applications
- Check GPU/CPU usage
```

### Out of Memory
```
Solutions:
- Close unused projects
- Clear cache (Playback → Delete Render Cache)
- Increase allocated RAM (Preferences)
- Render timeline in sections
- Optimize media (proxies, lower res)
```

---

## DaVinci-Specific Issues

### Color Page Issues
```
Nodes not affecting image:
- Check node is enabled (not bypassed)
- Verify clip selected
- Check if grade copied/pasted correctly

Scopes not showing:
- Enable in View menu
- Check video signal present
```

### Fairlight Issues
```
No audio in timeline:
- Verify audio tracks not muted
- Check master bus level
- Verify correct audio mapping
- Check source has audio
```

---

**Austrian Troubleshooting**: Systematic, methodical, solution-focused! 🇦🇹🔧

