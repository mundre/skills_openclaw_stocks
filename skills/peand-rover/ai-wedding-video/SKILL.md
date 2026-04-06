---
name: ai-wedding-video
version: "1.0.0"
displayName: "AI Wedding Video Maker — Create Cinematic Wedding Films and Highlight Reels"
description: >
  Create cinematic wedding films, highlight reels, and save-the-date videos using AI-powered editing. NemoVideo synchronizes multi-camera footage, extracts vow audio, applies slow-motion to key moments, generates same-day social cuts, and produces the 4-minute highlight reel that makes couples cry at minute two — all without the 6-month wait from a traditional videographer.
metadata: {"openclaw": {"emoji": "💍", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Wedding Video Maker — Cinematic Wedding Films and Highlight Reels

A wedding generates 8-14 hours of raw footage containing approximately 45 minutes of emotionally significant content — the vow delivery, the first-look reaction, the parent dances, the toast that made everyone laugh-cry — buried inside hours of guests finding seats, the DJ testing levels, and the reception dance floor after midnight when the lighting is terrible and the footage is just bass-driven blur. The couple wants three things: the 4-minute highlight reel that tells the story of their day set to music, the 20-minute ceremony edit they'll show their future children, and the 60-second Instagram clip they'll repost on every anniversary. NemoVideo delivers all three by processing multi-camera footage simultaneously, identifying emotional peaks through audio analysis (applause, laughter, tears-in-voice), synchronizing face-cam reactions with ceremony audio, and assembling a narrative arc that transforms a chaotic, beautiful, overwhelming day into a story that feels exactly how the couple remembers it — which is to say, more perfect than it actually was, because that's what memory does and that's what great wedding editing replicates.

## Use Cases

1. **Cinematic Highlight Reel (3-5 min)** — The signature wedding video. NemoVideo processes 10+ hours from 3 cameras plus drone: getting-ready moments (bride's first mirror look, groom adjusting tie — 20 sec), first look with reaction close-up in slow motion (15 sec), ceremony — processional wide, vow exchange with full lapel-mic audio, ring exchange, first kiss with confetti exit (60 sec), golden-hour couple portraits with drone pullback (15 sec), reception entrance, first dance with dip in slow-mo, parent dances, toast highlights (15 sec each from best man and maid of honor), cake cutting, sparkler exit tunnel (90 sec total). Music: romantic acoustic building to joyful celebration. Color grade: warm-filmic. Dissolve to names and date on final frame.
2. **Full Ceremony Edit (15-25 min)** — Processional to recessional, multi-camera with officiant lapel-mic audio. NemoVideo syncs 3 angles (wide, aisle, altar close-up), switches by active speaker, enhances vow audio (de-noise, gentle compression), and adds chapter markers: Processional, Readings, Vows, Ring Exchange, Kiss, Recessional.
3. **Same-Day Social Edit (60 sec)** — Posted before the reception ends. NemoVideo produces a fast-turnaround 9:16 vertical cut within 4 hours of footage upload: first look, ceremony kiss, exit, one reception moment — synced to a trending audio track with couple names and date as text overlay. The same-day post generates more videographer referrals than any portfolio page.
4. **Save-the-Date Video (30 sec)** — Pre-wedding content from engagement-session footage. NemoVideo creates: couple footage intercut with elegant text animations (names, date, venue, RSVP URL). Exported 9:16 for Instagram Stories and 16:9 for email invitations.
5. **Parent Thank-You Video (2 min)** — A private post-wedding gift. NemoVideo extracts all moments featuring the specific parent: walking down the aisle, parent-child dance, reception candids, the toast. Assembled with the couple's voiceover message. Delivered as a private link — not for social media.

## How It Works

### Step 1 — Upload All Wedding Footage
Batch-upload from every camera: ceremony, reception, getting-ready, drone, photo-booth, and guest-submitted smartphone clips. NemoVideo accepts mixed formats and auto-synchronizes by audio fingerprint.

### Step 2 — Select Outputs and Music
Choose the deliverables: highlight reel, ceremony edit, social cut, save-the-date. Select or upload a licensed music track. NemoVideo's library includes 500+ wedding tracks by mood: romantic, joyful, cinematic, acoustic, modern.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-wedding-video",
    "prompt": "Create a 4-minute cinematic highlight reel. Couple: Emily and David. Source: 11 hours, 3 cameras (Sony A7IV) + DJI Mini 4 Pro drone. Music: romantic acoustic opening, builds to joyful during reception. Getting ready: Emily seeing herself in dress, David writing vows, 20 sec. First look: David turns, tears, slow-motion embrace, 15 sec. Ceremony: processional wide shot, vows with full audio from lapel mic, ring exchange, first kiss with petal toss, 60 sec. Golden hour: drone pulling away from couple on vineyard hilltop, 15 sec. Reception: grand entrance with crowd cheering, first dance with lift in 0.5x slow-mo, father-daughter dance close-up, best man toast punchline, maid of honor tears, cake smash, sparkler tunnel exit, 90 sec. Closing: couple walking into sunset, dissolve to Emily and David, March 28 2026. Color grade: warm, slightly desaturated, filmic.",
    "duration": "4 min",
    "style": "cinematic-highlight",
    "multi_camera": true,
    "audio_enhancement": true,
    "color_grade": "warm-filmic",
    "slow_motion": true,
    "music": "romantic-acoustic-to-joyful",
    "format": "16:9"
  }'
```

### Step 4 — Review with Couple and Deliver
Share preview link for feedback. Adjust music sync, clip selection, or color grade. Export: 4K for archival USB drive, 1080p for online sharing, 9:16 for Instagram anniversary reposts.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the wedding, footage, key moments, and desired structure |
| `duration` | string | | Target length: "30 sec", "60 sec", "4 min", "20 min" |
| `style` | string | | "cinematic-highlight", "full-ceremony", "same-day-social", "save-the-date", "parent-thankyou" |
| `multi_camera` | boolean | | Sync and switch between multiple camera angles (default: true) |
| `audio_enhancement` | boolean | | De-noise and enhance vow/toast audio (default: true) |
| `color_grade` | string | | "warm-filmic", "bright-airy", "moody-dramatic", "vintage", "natural" |
| `slow_motion` | boolean | | Apply slow-mo to key moments: kiss, dance, exit (default: true) |
| `music` | string | | Track ID from library or "upload" for custom |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "awv-20260328-001",
  "status": "completed",
  "title": "Emily & David — Wedding Highlight Film",
  "duration_seconds": 248,
  "format": "mp4",
  "resolution": "3840x2160",
  "file_size_mb": 418.2,
  "output_files": {
    "4k_archival": "emily-david-highlight-4k.mp4",
    "1080p_sharing": "emily-david-highlight-1080p.mp4",
    "social_reel": "emily-david-60s-9x16.mp4"
  },
  "sections": [
    {"label": "Getting Ready", "start": 0, "end": 20},
    {"label": "First Look", "start": 20, "end": 35},
    {"label": "Ceremony", "start": 35, "end": 95},
    {"label": "Golden Hour + Drone", "start": 95, "end": 110},
    {"label": "Reception Highlights", "start": 110, "end": 235},
    {"label": "Sparkler Exit + Closing", "start": 235, "end": 248}
  ],
  "cameras_synced": 3,
  "slow_motion_moments": 4,
  "audio_enhancements": ["vow_de-noise", "toast_compression", "music_ducking"],
  "color_grade": "warm-filmic (shadows +8 warm, midtones +12 orange, saturation -15%)"
}
```

## Tips

1. **Vow audio is irreplaceable** — The most-rewatched moment in any wedding video. Invest in a lapel mic on the officiant or an audio recorder at the altar. NemoVideo enhances vow audio but cannot recover what was never captured.
2. **First-look reactions require a close-up camera** — The wide shot shows the scene; the close-up captures the tears. Without the close-up, the most emotional moment of the day is a distant figure turning around.
3. **Same-day social cuts drive referrals** — The couple posting a 60-second Reel during the reception generates more videographer inquiries than any website portfolio. Prioritize fast-turnaround delivery.
4. **Warm-filmic is the safest color grade** — Flatters all skin tones, makes outdoor venues glow, and ages well. Trendy heavy-grade looks date the video within 2 years.
5. **Slow motion on 3-5 moments, not everything** — First kiss, dance dip, sparkler exit earn slow-mo. Applied everywhere, it makes the video feel sluggish instead of cinematic.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Full highlight / ceremony edit / archival USB |
| MP4 9:16 | 1080p | Instagram Reels / TikTok / Stories |
| MP4 1:1 | 1080p | Facebook / Twitter wedding announcement |
| GIF | 720p | First-kiss moment / ring-exchange loop |

## Related Skills

- [ai-mental-health-video](/skills/ai-mental-health-video) — Mental health education
- [ai-cooking-video](/skills/ai-cooking-video) — Recipe and food content
- [ai-sports-video](/skills/ai-sports-video) — Sports highlight production
