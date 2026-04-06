---
name: ai-video-stabilizer
version: 1.0.1
displayName: "AI Video Stabilizer — Stabilize Shaky Video and Smooth Camera Motion with AI"
description: >
  Stabilize shaky video and smooth camera motion with AI — fix handheld shake, walking bounce, vehicle vibration, wind wobble, and accidental camera movement. NemoVideo analyzes frame-by-frame motion and applies intelligent stabilization: removing unwanted shake while preserving intentional camera movement like pans, tilts, and zooms. Produce smooth professional-looking footage from any handheld recording. Stabilize video AI, fix shaky video, video stabilization tool, smooth shaky footage, anti shake video, camera stabilization, steady video maker, remove camera shake.
metadata: {"openclaw": {"emoji": "📹", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Stabilizer — Smooth Footage from Any Camera, Any Situation

Shaky footage is the most common quality problem in video. Gimbal stabilizers cost $100-500 and add weight, setup time, and another device to charge. Tripods eliminate shake but eliminate mobility. Most real-world recording happens handheld: phone in hand while walking, camera at a concert, action cam on a bike, drone in wind, car dashcam on rough roads. All of these produce shake that makes footage look amateur and can cause viewer discomfort. The human eye has built-in stabilization — the vestibulo-ocular reflex keeps our visual field steady even when our head moves. When we watch shaky footage, our brain tries to stabilize it and fails, creating a disconnect that registers as low quality (and for some viewers, actual motion sickness). Professional stabilization in post-production traditionally requires: importing into editing software, applying warp stabilizer or similar tool, waiting for frame-by-frame analysis (minutes to hours depending on length), adjusting settings to balance smoothness vs. crop, re-rendering, and reviewing. For long footage, the process can take hours. NemoVideo stabilizes through AI analysis that distinguishes intentional movement (pans, tilts, tracking shots) from unintentional shake (hand tremor, footstep bounce, vehicle vibration). The AI removes the shake while preserving the creative movement — producing footage that looks like it was shot on a gimbal.

## Use Cases

1. **Walking Footage — Eliminate Footstep Bounce (any length)** — A vlogger records while walking through a city. Every step creates a vertical bounce that makes the footage feel like a shaky-cam horror movie. NemoVideo: analyzes the repetitive vertical oscillation pattern (footstep frequency), removes the bounce while preserving the forward walking motion, maintains horizontal panning (the vlogger looking at different things), and produces footage that feels like a smooth dolly shot. Walking footage that looks like a steadicam.

2. **Concert/Event — Handheld in a Crowd (any length)** — Phone footage from a concert: the shooter is being jostled by the crowd, holding their phone above their head, zoomed in on the stage. Triple shake: crowd pushing, arm fatigue, and digital zoom amplifying every movement. NemoVideo: applies aggressive stabilization appropriate for the extreme shake level, crops slightly to allow stabilization headroom (the AI determines the minimum crop needed), preserves the audio perfectly (stabilization is video-only), and produces watchable footage from nearly unwatchable source material.

3. **Car/Vehicle — Dashcam Vibration (any length)** — Dashboard camera footage from a road with potholes and rough pavement. High-frequency vibration makes every frame slightly blurry and the video uncomfortable to watch. NemoVideo: identifies the high-frequency vibration pattern (different from hand shake — faster, more regular), removes the vibration while keeping the vehicle's actual turning and direction changes, and produces smooth driving footage. Dashcam footage that actually documents the drive clearly.

4. **Drone — Wind Wobble Correction (any length)** — Drone footage in moderate wind. The drone's gimbal handles most stabilization but wind gusts create periodic wobbles — slight tilts and position shifts that the gimbal cannot fully compensate. NemoVideo: detects the irregular wobble pattern (wind gusts are aperiodic, unlike footstep bounce), smooths the wobbles while preserving intentional flight path and camera movements, and produces footage that looks like calm-weather flight. Drone footage usable regardless of wind conditions.

5. **Action Cam — Extreme Motion Stabilization (any length)** — GoPro mounted on a mountain bike, ski helmet, or surfboard. Extreme vibration and rotation that built-in stabilization cannot fully handle. NemoVideo: applies maximum stabilization with AI-powered motion prediction (predicting where the frame should be based on surrounding frames), accepts higher crop ratio for extreme cases (the crop needed for extreme stabilization is compensated by the action cam's wide-angle lens), and produces smooth action footage suitable for highlight reels and social sharing.

## How It Works

### Step 1 — Upload Shaky Video
Any footage with unwanted camera shake. NemoVideo auto-detects the type and severity of shake.

### Step 2 — Set Stabilization Level
Auto (AI decides), gentle (minimal correction, minimal crop), standard (balanced), aggressive (maximum smoothness, more crop), or custom (specify smoothing strength and crop tolerance).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-stabilizer",
    "prompt": "Stabilize a 5-minute handheld walking vlog. Remove footstep bounce and hand shake but preserve intentional panning when I look at things. Standard stabilization — balance between smoothness and crop. Maintain original resolution after crop (scale up slightly). Also generate a 9:16 vertical version with face tracking for TikTok clips.",
    "stabilization": "standard",
    "preserve_motion": ["pan", "tilt", "zoom"],
    "remove_motion": ["shake", "bounce", "vibration"],
    "crop_handling": "scale-to-fill",
    "outputs": [
      {"format": "16:9", "resolution": "1080p"},
      {"format": "9:16", "tracking": "face", "platform": "tiktok"}
    ]
  }'
```

### Step 4 — Compare Before/After
Preview stabilized vs. original side-by-side. Verify: shake is removed, intentional movement is preserved, no warping artifacts. Download.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Stabilization requirements |
| `stabilization` | string | | "auto", "gentle", "standard", "aggressive", "custom" |
| `smoothing` | float | | 0.0-1.0 custom smoothing strength |
| `preserve_motion` | array | | ["pan", "tilt", "zoom", "tracking"] — intentional motions to keep |
| `remove_motion` | array | | ["shake", "bounce", "vibration", "roll"] |
| `crop_handling` | string | | "scale-to-fill", "black-bars", "ai-extend" |
| `max_crop` | float | | Maximum crop percentage (default: 15%%) |
| `outputs` | array | | [{format, resolution, tracking}] |
| `batch` | array | | Multiple videos |

## Output Example

```json
{
  "job_id": "avstab-20260328-001",
  "status": "completed",
  "source_duration": "5:12",
  "shake_analysis": {
    "type": "walking-bounce + hand-shake",
    "severity": "moderate",
    "frequency": "2.1 Hz (footstep) + random (hand)"
  },
  "stabilization_applied": "standard",
  "crop_used": "8.2%%",
  "intentional_motion_preserved": ["horizontal pan", "vertical tilt"],
  "outputs": {
    "main": {"file": "vlog-stabilized-16x9.mp4", "resolution": "1920x1080"},
    "tiktok": {"file": "vlog-stabilized-9x16.mp4", "resolution": "1080x1920", "tracking": "face"}
  }
}
```

## Tips

1. **Standard stabilization is right for 90% of footage** — Gentle leaves visible shake. Aggressive crops too much. Standard balances smoothness and frame preservation for most handheld recordings.
2. **Preserving intentional motion is what separates good stabilization from bad** — A stabilizer that removes everything (pans included) produces eerie, floating footage. NemoVideo's AI distinguishes shake (high-frequency, random) from pans (smooth, directional) and removes only the shake.
3. **Wider lens = easier stabilization** — Wide-angle footage (phone, GoPro, drone) has more frame to work with for cropping. Zoomed-in telephoto footage amplifies shake and leaves less crop margin. When possible, shoot wide and crop in post.
4. **Scale-to-fill after crop maintains resolution** — Stabilization requires slight cropping. Scaling the stabilized result back to full resolution prevents visible borders while maintaining apparent resolution. The slight softening from upscaling is invisible at normal viewing distances.
5. **Audio is never affected by stabilization** — Video stabilization only modifies the visual frames. Audio remains perfectly synced and unaltered. No need to worry about audio drift or quality changes.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |

## Related Skills

- [ai-video-resize](/skills/ai-video-resize) — Video resizing
- [ai-video-rotate](/skills/ai-video-rotate) — Video rotation
- [ai-video-effects](/skills/ai-video-effects) — Video effects
