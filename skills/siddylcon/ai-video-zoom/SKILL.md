---
name: ai-video-zoom
version: 1.0.1
displayName: "AI Video Zoom — Add Zoom Effects Pan Shots and Focus Pulls to Any Video"
description: >
  Add zoom effects, pan shots, and focus pulls to any video with AI — create smooth zoom-ins on key moments, zoom-out reveals, Ken Burns motion on photos, tracking zoom that follows subjects, zoom-cut editing for talking heads, and cinematic dolly zoom effects. NemoVideo adds camera movement to static footage: turning a fixed-angle recording into dynamic multi-shot content. Zoom video AI, add zoom to video, zoom effect maker, Ken Burns effect, zoom cut editor, pan and zoom video, dolly zoom effect, dynamic zoom video.
metadata: {"openclaw": {"emoji": "🔍", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Zoom — Add Camera Movement That Was Not There When You Filmed

Camera movement communicates. A zoom-in on a face conveys intimacy and importance. A zoom-out reveals context and scale. A slow pan across a landscape creates contemplation. A tracking zoom that follows a subject creates engagement. A zoom-cut between focal lengths resets attention. Professional videographers plan and execute these movements during filming using dollies, gimbals, sliders, drones, and motorized camera heads — equipment costing $500-50,000. A static tripod shot contains none of this movement. A handheld phone shot contains random movement but not intentional movement. NemoVideo adds intentional camera movement after filming. The AI applies: smooth zoom-ins and zoom-outs at specified moments or subjects, Ken Burns motion (gentle pan and zoom) on still images, zoom-cuts for talking-head content (alternating between focal lengths to create multi-camera illusion), tracking zoom that follows a subject through the frame, pan movements across wide scenes, and the cinematic dolly zoom (background scales while subject stays same size — the Vertigo effect). Every movement is smooth, intentional, and serves the content's visual storytelling.

## Use Cases

1. **Talking-Head Zoom-Cuts — Multi-Camera from One Camera (any length)** — A YouTube video filmed on one static camera needs visual variety to hold attention. NemoVideo applies zoom-cuts: alternating between 100% (full frame) and 112-120% (closer crop) every 6-8 seconds, timed to natural sentence breaks (not mid-word), with instant cuts between zoom levels (simulating a director switching between two cameras). One static recording becomes a dynamic two-camera production. The single highest-impact edit for any talking-head content.

2. **Product Focus — Zoom to Detail (30-120s)** — A product overview video needs to draw attention to specific features: the texture of the material, the button placement, the screen quality, the logo detail. NemoVideo applies smooth 3-second zoom-ins on each feature as it is mentioned in the voiceover, holds the close-up for the feature explanation, then smooth zoom-out to full product view before the next feature. The zoom guides the viewer's eye exactly where the message needs them to look.

3. **Photo Slideshow — Ken Burns Motion (any number of photos)** — A collection of photos needs to become a video. Static photos displayed in sequence feel like a PowerPoint. NemoVideo applies Ken Burns motion: each photo gets a unique slow zoom and pan (zoom in on a face, pan across a landscape, zoom out from a detail to reveal the full scene), creating cinematic motion from static images. The difference between a boring slideshow and a compelling visual story.

4. **Reaction Zoom — Emphasize Key Moments (any length)** — A reaction video, interview, or comedy clip has moments where a facial expression or gesture deserves emphasis. NemoVideo applies quick zoom-in at those moments (0.3-second zoom to 150%, hold for 1-2 seconds, zoom back), optionally with a subtle camera shake for comedic or dramatic effect. The internet's signature "zoom on the reaction" technique that highlights the most entertaining or impactful moments.

5. **Establishing Shot — Zoom-Out Reveal (5-15s)** — A video needs an opening that reveals the setting. Start tight (close-up of a detail — a coffee cup, a keyboard, a flower) and slowly zoom out to reveal the full environment (the café, the office, the garden). NemoVideo: applies smooth 5-10 second zoom-out from 300% to 100%, with optional parallax effect (foreground elements moving faster than background for depth), creating a cinematic opening that establishes context through discovery.

## How It Works

### Step 1 — Upload Video or Photos
Any static footage that needs camera movement added, or photos for Ken Burns treatment.

### Step 2 — Describe Zoom Movements
Specify: where to zoom, how fast, how far, on what subject, and the creative purpose.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-zoom",
    "prompt": "Apply zoom effects to a 10-minute talking-head YouTube video. Zoom-cuts: alternate between 100%% and 115%% every 7 seconds, cut on sentence breaks (not mid-word). At 2:30, apply a smooth 3-second zoom-in on the product being held up (track the product, zoom to 200%%). At 5:15, zoom-in on face for emotional emphasis (smooth 1-second zoom to 140%%, hold 3 seconds, zoom back). Opening: start at 130%% zoomed in on face, smooth 3-second zoom-out to full frame (reveal). Export 16:9 for YouTube + extract zoomed reaction moments as 9:16 clips.",
    "zoom_operations": [
      {"type": "zoom-cuts", "interval": 7, "range": "100-115", "timing": "sentence-breaks"},
      {"type": "smooth-zoom-in", "at": "2:30", "to": "200%%", "duration": 3, "track": "product"},
      {"type": "smooth-zoom-in", "at": "5:15", "to": "140%%", "duration": 1, "hold": 3, "track": "face"},
      {"type": "opening-reveal", "from": "130%%", "to": "100%%", "duration": 3}
    ],
    "formats": ["16:9"],
    "extract_moments": {"format": "9:16", "at": ["2:30", "5:15"]}
  }'
```

### Step 4 — Preview Zoom Movements
Watch each zoom: smooth entry and exit, subject stays centered, no jarring cuts. Adjust timing or zoom levels if needed.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Zoom effect descriptions |
| `zoom_operations` | array | | [{type, at, to, from, duration, track, hold}] |
| `zoom_cuts` | object | | {interval, range, timing} for recurring zoom-cuts |
| `ken_burns` | boolean | | Apply Ken Burns to photos |
| `tracking` | string | | "face", "subject", "product", "center" |
| `reaction_zooms` | array | | [{at, intensity, duration}] quick emphasis zooms |
| `formats` | array | | ["16:9", "9:16", "1:1"] |
| `extract_moments` | object | | {format, at} — extract zoomed clips |

## Output Example

```json
{
  "job_id": "avzoom-20260328-001",
  "status": "completed",
  "source_duration": "10:15",
  "zoom_operations_applied": {
    "zoom_cuts": 88,
    "smooth_zooms": 2,
    "opening_reveal": 1
  },
  "outputs": {
    "main": {"file": "video-zoomed-16x9.mp4", "resolution": "1920x1080"},
    "reaction_clips": [
      {"file": "product-zoom-9x16.mp4", "at": "2:30", "duration": "0:08"},
      {"file": "face-zoom-9x16.mp4", "at": "5:15", "duration": "0:06"}
    ]
  }
}
```

## Tips

1. **Zoom-cuts every 6-8 seconds are the single highest-impact edit for talking-head content** — Proven by every top YouTube creator: the subtle focal length alternation resets viewer attention and creates the illusion of multi-camera production from a single camera.
2. **Zoom-in on what matters, zoom-out for context** — The zoom direction should match the narrative need. Zooming in says "look closely at this." Zooming out says "now see the big picture." Using them backwards confuses the viewer.
3. **Smooth zoom speed should match content energy** — A 3-second slow zoom feels contemplative and dramatic. A 0.5-second snap zoom feels urgent and surprising. Match the zoom speed to the emotional intensity of the content.
4. **Ken Burns transforms photo slideshows from boring to cinematic** — The difference between a static photo on screen for 5 seconds and the same photo with gentle zoom-and-pan motion is enormous. Always apply Ken Burns to any photo used in video.
5. **Reaction zooms should be rare for maximum impact** — A quick zoom on every reaction becomes noise. A single zoom on the ONE reaction that deserves emphasis becomes the video's most memorable moment. Use sparingly.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |

## Related Skills

- [ai-video-speed-changer](/skills/ai-video-speed-changer) — Speed changes
- [ai-video-mirror](/skills/ai-video-mirror) — Mirror effects
- [ai-video-effects](/skills/ai-video-effects) — Video effects
