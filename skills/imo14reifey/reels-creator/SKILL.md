---
name: reels-creator
version: "1.0.0"
displayName: "Reels Creator — Make Instagram Reels, TikTok and YouTube Shorts with AI Editor"
description: >
  Create scroll-stopping Reels, TikTok videos, and YouTube Shorts from raw footage or text prompts using AI. NemoVideo handles vertical formatting, trending audio sync, auto-captions, hook optimization, beat-matched transitions, cover frame selection for grid consistency, and multi-platform batch export — producing native short-form content for every vertical video platform from a single source without reformatting, re-editing, or re-exporting.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Reels Creator — Make Short-Form Vertical Video for Every Platform

Short-form vertical video is the dominant content format across social media — Instagram Reels, TikTok, YouTube Shorts, Facebook Reels, Snapchat Spotlight, and LinkedIn Video all reward vertical, fast-paced, captioned content that hooks in the first second and delivers value before the viewer's thumb reaches the screen to swipe. But each platform has slightly different rules: TikTok favors raw energy and trending audio. Instagram rewards polished aesthetics and grid-consistent cover frames. YouTube Shorts benefits from searchable titles and descriptions. LinkedIn wants professional value in under 60 seconds. Creating native content for each platform individually means editing the same footage 4 different ways — or accepting that 3 of the 4 versions look like lazy reposts (which the algorithms detect and suppress). NemoVideo's Reels creator solves multi-platform short-form by building every video vertical-first with platform-specific optimizations applied at export: TikTok gets bold captions and trending audio. Instagram gets clean typography and a curated cover frame. YouTube gets SEO-optimized titles. LinkedIn gets professional framing. One edit session, four native outputs — each one looks like it was made specifically for that platform because the formatting differences are applied in the final render, not the creative process.

## Use Cases

1. **Talking-Head Hook Reel (30-60 sec)** — A creator films a 3-minute talking-head video. NemoVideo produces: identifies the most engaging 8 words from the transcript, places them as a bold text hook in frame one ("I lost $200K before I learned this"), cuts the original rambling intro, adds a zoom-cut pattern interrupt at second 2, trims to the strongest 45 seconds, applies word-by-word animated captions, syncs background music to speech cadence, and exports: 9:16 with TikTok-bold captions, 9:16 with Instagram-clean captions, and 9:16 with YouTube-optimized title card.
2. **Product Showcase — Before/After (15-30 sec)** — A skincare brand shows product results. NemoVideo creates: split-screen transition (before on left slides to after on right), product name and benefit text animation, close-up slow-motion of texture/application, price and CTA ("Shop link in bio"), and trending audio at -15dB. The 15-second format gets the highest save rate on Instagram because it loops 4-6 times before the viewer realizes.
3. **Travel Montage — Cinematic Vertical (15-45 sec)** — 20 clips from a trip. NemoVideo sequences: wide establishing shot, movement transition (pan/drone), detail close-up, people moment, wide pullback — repeating the visual rhythm for natural pacing. Smooth cross-dissolve transitions (not hard cuts — Instagram aesthetic). Color graded warm with desaturated blues. Location name and date as elegant text overlay. Trending chill audio synced to scene changes.
4. **Tutorial Quick-Tip (30-60 sec)** — A tech creator shares a phone tip. NemoVideo structures: hook question ("Did you know your iPhone can do THIS?", 2 sec), screen recording of the tip with zoom-in on the relevant setting (15 sec), result demonstration (10 sec), "Save this for later" CTA (3 sec). Step-number overlays ("Step 1", "Step 2") for clarity. Exported with captions because screen-recording content is inherently visual-instruction content.
5. **Batch Content Week — 1 Shoot → 5 Reels** — A fitness creator films a 20-minute workout session. NemoVideo segments into 5 standalone Reels: warm-up exercise (30 sec), upper-body move (30 sec), lower-body move (30 sec), core finisher (30 sec), and full-workout summary montage (45 sec). Each Reel: standalone hook, exercise name overlay, rep counter, and independent music track. Scheduled across the week for daily posting without re-filming.

## How It Works

### Step 1 — Upload Source Content
Provide raw footage (any orientation — NemoVideo reframes horizontal to vertical), screen recordings, photos for slideshow, or just a text prompt for AI-generated content.

### Step 2 — Set Platform and Style
Choose target platforms (one or multiple), duration, caption style, music preference, and whether this is a single Reel or a batch series.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "reels-creator",
    "prompt": "Create a 45-second talking-head Reel from 3 minutes of footage. Hook: extract the most engaging sentence from transcript and display as bold text in the first 1.5 seconds. Pattern interrupt at 2.5 sec (zoom cut + pop sound). Trim to strongest 45 seconds. Captions: word-by-word highlight, bold white with yellow active word, black outline. Music: trending lo-fi at -16dB. End: 3-sec CTA Follow for more. Export for all platforms: TikTok (bold captions), Instagram (clean captions + cover frame), YouTube Shorts (title card intro).",
    "duration": "45 sec",
    "style": "talking-head-hook",
    "platforms": ["tiktok", "instagram", "youtube-shorts"],
    "captions": "word-highlight",
    "hook_optimization": true,
    "cover_frame": true,
    "music": "trending-lofi",
    "format": "9:16"
  }'
```

### Step 4 — Review Per-Platform Versions and Publish
Preview each platform version. Select Instagram cover frame for grid consistency. Schedule across platforms or post immediately.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the content, footage, and desired Reel |
| `duration` | string | | "15 sec", "30 sec", "45 sec", "60 sec", "90 sec" |
| `style` | string | | "talking-head-hook", "product-showcase", "travel-montage", "tutorial-tip", "batch-series" |
| `platforms` | array | | ["tiktok", "instagram", "youtube-shorts", "linkedin", "facebook"] |
| `captions` | string | | "word-highlight", "tiktok-bold", "instagram-clean", "minimal", "none" |
| `hook_optimization` | boolean | | Auto-detect and front-load the strongest hook (default: true) |
| `cover_frame` | boolean | | Select optimal cover frame for Instagram grid (default: true) |
| `music` | string | | "trending-lofi", "upbeat-pop", "chill-ambient", "energetic", "none" |
| `format` | string | | "9:16" (default), "1:1" |

## Output Example

```json
{
  "job_id": "rc-20260328-001",
  "status": "completed",
  "duration_seconds": 44,
  "platform_exports": {
    "tiktok": {
      "file": "reel-tiktok-bold.mp4",
      "captions": "tiktok-bold",
      "audio": "trending-lofi",
      "resolution": "1080x1920"
    },
    "instagram": {
      "file": "reel-instagram-clean.mp4",
      "captions": "instagram-clean",
      "cover_frame": {"timestamp": 8.2, "description": "Speaker mid-gesture, strong expression"},
      "resolution": "1080x1920"
    },
    "youtube_shorts": {
      "file": "reel-shorts-titled.mp4",
      "title_card": "How I Lost $200K Before Learning This",
      "resolution": "1080x1920"
    }
  },
  "hook": {
    "text": "I lost $200K before I learned this",
    "placement": "0:00-1.5s bold overlay + audio",
    "original_position": "1:42 in source"
  }
}
```

## Tips

1. **The hook decides everything** — The algorithm measures swipe-away rate in the first 1-2 seconds. If the viewer doesn't have a reason to stay by second 2, they won't. NemoVideo's hook_optimization finds the most compelling moment and front-loads it.
2. **Platform-specific captions matter** — TikTok audiences expect bold Impact-style text. Instagram audiences expect clean sans-serif. Using TikTok's aesthetic on Instagram signals "this is a repost" and the algorithm suppresses reach.
3. **Cover frame selection is an Instagram-only concern** — TikTok doesn't show cover frames in feeds. Instagram shows them permanently on the creator's grid. A bad cover frame makes the entire profile look inconsistent.
4. **30-45 seconds is the cross-platform sweet spot** — Short enough for TikTok's preference for quick content, long enough for Instagram's preference for slightly longer Reels, and within YouTube Shorts' 60-second limit.
5. **Batch series from one shoot maximizes content output** — One 20-minute filming session producing 5 Reels means daily posting for a week. Consistency in posting frequency matters more than any individual video's quality.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 9:16 (TikTok) | 1080x1920 | TikTok with bold captions |
| MP4 9:16 (Instagram) | 1080x1920 | Reels with clean captions + cover |
| MP4 9:16 (Shorts) | 1080x1920 | YouTube Shorts with title card |
| MP4 1:1 | 1080x1080 | Cross-post to LinkedIn / Facebook feed |
| JPG | 1080x1920 | Cover frame export |

## Related Skills

- [instagram-reels-editor](/skills/instagram-reels-editor) — Instagram-specific Reels editing
- [tiktok-video-editor](/skills/tiktok-video-editor) — TikTok-specific editing
- [video-editor-ai](/skills/video-editor-ai) — Full AI video editing
