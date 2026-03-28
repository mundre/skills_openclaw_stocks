---
name: slow-motion-video
version: "1.0.0"
displayName: "Slow Motion Video — Create Stunning Slow-Mo Videos with AI Speed Control"
description: >
  Create slow motion videos using AI — apply cinematic slow-mo effects to any footage with intelligent speed control that preserves smooth playback. NemoVideo lets you slow down key moments in your video by describing what to emphasize: product reveals, athletic movements, cooking sizzles, dance moves, nature details, and emotional reactions. Control speed per segment, add dramatic music scoring that matches the slow-mo pacing, and export buttery-smooth results for YouTube, TikTok, Reels, and Shorts.
metadata: {"openclaw": {"emoji": "🐌", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Slow Motion Video — Cinematic Slow-Mo with AI Speed Control

Slow motion is the most cinematic effect available to any creator — and the most misused. When applied to the right moment (a basketball swish through the net, a chef's knife cutting through a tomato, a dancer mid-spin, a champagne cork popping, a dog catching a frisbee), slow-mo transforms a split-second into a breathtaking sequence that viewers replay and share. When applied to the wrong moment (someone walking, a static conversation, a slide transition), it makes the video feel sluggish and amateurish. The difference is intentionality: slow motion should emphasize a specific moment, not slow down the entire video. Traditional slow-mo requires either a high-frame-rate camera (120fps+, which most phones now support but most creators forget to enable) or frame interpolation in post-production (which produces artifacts on complex motion). NemoVideo makes slow motion conversational: describe which moments to slow down ("slow-mo on the product reveal," "0.25x speed when the ball hits the net," "slow the cooking sizzle to half speed"), and the AI applies speed changes with smooth transitions between normal and slow-mo segments, preserving audio pitch and adding optional dramatic music scoring that matches the pacing shift.

## Use Cases

1. **Product Reveal — Hero Moment (any length)** — A product video needs the unboxing moment to land with impact. NemoVideo: plays the video at normal speed through the lead-up, transitions to 0.25x slow-mo as the product emerges from packaging, holds the slow-mo for 3 seconds of product beauty, then ramps back to normal speed for the feature walkthrough. Music drops to a bass hit during the slow-mo and builds back during the return to normal speed. The product reveal becomes a cinematic event.
2. **Sports Highlights — Action Analysis (any length)** — A basketball game has 5 highlight moments (dunks, three-pointers, blocks). NemoVideo: identifies each highlight by timestamp, applies 0.3x slow-mo to each action moment (the dunk, the release, the block), keeps transitions and replays at normal speed, adds dramatic score drops during each slow-mo, and exports a 2-minute highlight reel where the best moments are savored and the connective tissue moves fast.
3. **Cooking — Satisfying Food Shots (30-60s)** — A recipe video needs sensory slow-mo: oil hitting the pan (sizzle at 0.5x), knife through vegetables (0.3x with enhanced cutting sound), sauce drizzle on the finished plate (0.25x), and steam rising from the plated dish (0.4x). NemoVideo applies different speeds to each food moment while keeping instruction segments at normal speed, creating the satisfying ASMR-adjacent food content that performs on TikTok and Reels.
4. **Dance/Movement — Choreography Showcase (15-60s)** — A dancer's routine has 3 key moves that happen too fast to appreciate at normal speed. NemoVideo: plays the routine at normal speed with music, hits 0.3x slow-mo on each showcase move (the flip, the freeze, the floor spin), syncs the speed ramp to the music's beat drops, and returns to normal speed seamlessly. The choreography is experienced at two speeds — performance energy and artistic appreciation.
5. **Nature/Wildlife — Detail Revelation (any length)** — A hummingbird visiting a flower, a wave crashing on rocks, a raindrop hitting a puddle. NemoVideo applies 0.15x extreme slow-mo to nature moments that happen too fast for the human eye, adds ambient sound design (enhanced wing flutter, wave rumble, raindrop impact), and creates meditative nature content from ordinary footage.

## How It Works

### Step 1 — Upload Video
Provide the video. Any format, any frame rate. NemoVideo analyzes the footage to identify motion characteristics and optimal slow-mo points.

### Step 2 — Define Slow-Mo Segments
Describe which moments to slow down — by timestamp, by description ("the product reveal"), or let NemoVideo auto-detect the highest-energy moments for slow-mo emphasis.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "slow-motion-video",
    "prompt": "Apply slow motion to a 90-second product video. Normal speed throughout except: slow-mo 0.25x at 0:22-0:26 (product unboxing reveal), slow-mo 0.5x at 0:45-0:48 (water splash test), slow-mo 0.3x at 1:15-1:18 (drop test impact). Smooth speed ramps into and out of each slow-mo section (0.5 sec ramp). Add dramatic bass hit at each slow-mo entry. Music: cinematic at -16dB, drops to minimal during slow-mo sections. Export 16:9 1080p.",
    "speed_segments": [
      {"start": "0:22", "end": "0:26", "speed": 0.25, "ramp": 0.5},
      {"start": "0:45", "end": "0:48", "speed": 0.5, "ramp": 0.5},
      {"start": "1:15", "end": "1:18", "speed": 0.3, "ramp": 0.5}
    ],
    "music": "cinematic",
    "music_volume": "-16dB",
    "sound_effects": ["bass-hit-on-slowmo-entry"],
    "format": "16:9"
  }'
```

### Step 4 — Preview and Export
Preview each slow-mo transition. Adjust speed, ramp duration, or music. Export.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe slow-mo moments and style |
| `speed_segments` | array | | [{start, end, speed, ramp}] — explicit slow-mo sections |
| `auto_detect` | boolean | | AI finds best moments for slow-mo (default: false) |
| `default_speed` | float | | Speed for non-slow-mo sections (default: 1.0) |
| `ramp_duration` | float | | Speed transition duration in seconds (default: 0.3) |
| `music` | string | | "cinematic", "dramatic", "ambient", "none" |
| `music_volume` | string | | "-12dB" to "-20dB" |
| `sound_effects` | array | | Effects on slow-mo entry: "bass-hit", "whoosh", "silence" |
| `pitch_preserve` | boolean | | Keep original audio pitch during slow-mo (default: true) |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "smv-20260328-001",
  "status": "completed",
  "source_duration": "1:32",
  "output_duration": "1:56",
  "format": "mp4",
  "resolution": "1920x1080",
  "file_size_mb": 48.6,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/smv-20260328-001.mp4",
  "slow_mo_segments": [
    {"original": "0:22-0:26 (4s)", "output": "0:22-0:38 (16s at 0.25x)", "ramp": "0.5s in/out"},
    {"original": "0:45-0:48 (3s)", "output": "0:57-1:03 (6s at 0.5x)", "ramp": "0.5s in/out"},
    {"original": "1:15-1:18 (3s)", "output": "1:33-1:43 (10s at 0.3x)", "ramp": "0.5s in/out"}
  ],
  "added_duration": "24 sec (from slow-mo expansion)"
}
```

## Tips

1. **Slow-mo is for moments, not entire videos** — A 60-second video at 0.5x is just a 120-second slow video. Reserve slow-mo for 2-5 second moments that deserve emphasis. The contrast between normal speed and slow-mo is what creates the cinematic impact.
2. **Speed ramps are more important than the slow-mo itself** — An abrupt cut to slow motion feels jarring. A smooth 0.3-0.5 second ramp from 1.0x to 0.25x creates the satisfying "time is slowing down" sensation that viewers love.
3. **Music should match the speed change** — When video goes slow-mo, music should either drop to a bass hit (dramatic) or fade to ambient (ethereal). Constant uptempo music over slow footage creates a disconnect.
4. **Product reveals are the highest-ROI slow-mo application** — The moment a product is revealed, unboxed, or demonstrated in action is worth slowing down in every product video. It gives the viewer time to appreciate what they're seeing.
5. **0.25x is the sweet spot for most slow-mo** — Slower than 0.15x looks stuttery unless the source is 120fps+. Faster than 0.5x barely registers as slow motion. 0.25x (quarter speed) is dramatic enough to notice and smooth enough to look good.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website / presentation |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram feed |
| GIF | 720p | Slow-mo loop preview |

## Related Skills

- [talking-head-video](/skills/talking-head-video) — Talking head production
- [explainer-video-maker](/skills/explainer-video-maker) — Explainer videos
- [youtube-shorts-maker](/skills/youtube-shorts-maker) — YouTube Shorts
