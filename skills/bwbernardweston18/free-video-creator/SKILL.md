---
name: free-video-creator
version: "1.0.1"
displayName: "Free Video Creator — Generate MP4 Videos Without Paid Tools"
description: >
  Get a polished MP4 video from text prompts, images, or raw footage using the free-video-creator skill — no subscription required. It handles scene assembly, timing, and basic transitions, then outputs a ready-to-share file. Built for content creators, educators, and small teams who don't want to route every project through expensive software. Exports at up to 1080p resolution.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> This is the free-video-creator skill — it turns your text, images, or clips into a finished MP4. Tell me what you're building and let's get started.

**Try saying:**
- "Create a 30-second product demo video from these 8 product screenshots with a voiceover script I'll paste in"
- "Turn my 500-word blog post into a 90-second explainer video with text overlays and a plain background"
- "Combine these 5 short clips into one video with a title card at the start and my logo at the end"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Raw Inputs Into Watchable Videos Fast

The free-video-creator skill takes what you give it — a script, a folder of images, a rough outline — and assembles it into a structured video file. Each scene gets a defined duration, and the output defaults to 1080p MP4 at 30fps unless you specify otherwise. That's the format most platforms accept without re-encoding.

Here's a concrete example: feed it 12 product images, a 200-word script, and a background music file under 10MB, and it returns a 60-second video with synchronized captions and cuts timed to sentence breaks. No manual keyframing. No timeline scrubbing.

This skill doesn't replace a full non-linear editor. It's designed for structured, repeatable video creation where you know the content and want a usable file in under 3 minutes. Teams producing weekly update videos or tutorial clips at consistent formats get the most out of it.

## Matching Input To Video Actions

When you describe what you want — a slideshow, text animation, or clip merge — Free Video Creator parses your intent and routes it to the matching generation action automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering Pipeline Details

Free Video Creator sends your job to a shared cloud GPU queue where FFmpeg-based processing handles frame composition, encoding, and MP4 packaging — you don't need a local GPU. Render times vary based on queue load, but most jobs under 60 seconds of output finish within 2-4 minutes.

Base URL: `https://mega-api-prod.nemovideo.ai`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tasks/me/with-session/nemo_agent` | POST | Start a new editing session. Body: `{"task_name":"project","language":"<lang>"}`. Returns `session_id`. |
| `/run_sse` | POST | Send a user message. Body includes `app_name`, `session_id`, `new_message`. Stream response with `Accept: text/event-stream`. Timeout: 15 min. |
| `/api/upload-video/nemo_agent/me/<sid>` | POST | Upload a file (multipart) or URL. |
| `/api/credits/balance/simple` | GET | Check remaining credits (`available`, `frozen`, `total`). |
| `/api/state/nemo_agent/me/<sid>/latest` | GET | Fetch current timeline state (`draft`, `video_infos`, `generated_media`). |
| `/api/render/proxy/lambda` | POST | Start export. Body: `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll status every 30s. |

Accepted file types: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-video-creator`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

Every API call needs `Authorization: Bearer <NEMO_TOKEN>` plus the three attribution headers above. If any header is missing, exports return 402.

### Error Codes

- `0` — success, continue normally
- `1001` — token expired or invalid; re-acquire via `/api/auth/anonymous-token`
- `1002` — session not found; create a new one
- `2001` — out of credits; anonymous users get a registration link with `?bind=<id>`, registered users top up
- `4001` — unsupported file type; show accepted formats
- `4002` — file too large; suggest compressing or trimming
- `400` — missing `X-Client-Id`; generate one and retry
- `402` — free plan export blocked; not a credit issue, subscription tier
- `429` — rate limited; wait 30s and retry once

### Reading the SSE Stream

Text events go straight to the user (after GUI translation). Tool calls stay internal. Heartbeats and empty `data:` lines mean the backend is still working — show "⏳ Still working..." every 2 minutes.

About 30% of edit operations close the stream without any text. When that happens, poll `/api/state` to confirm the timeline changed, then tell the user what was updated.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

## Troubleshooting

If the output video has misaligned audio, check that your script word count matches the intended duration. At a natural speaking pace, 150 words runs about 60 seconds. Submitting a 400-word script for a 30-second video forces compression that breaks sync.

Blank or black frames usually mean one of your source images wasn't readable — HEIC and TIFF formats aren't supported. Convert to JPG or PNG before submitting.

Scene order coming out wrong? Number your image filenames or explicitly list the sequence in your prompt. The skill reads filenames alphanumerically by default, so IMG_10 sorts before IMG_2 without zero-padding.

## Performance Notes

Export time scales with input complexity. A 60-second video built from 10 static images typically processes in under 90 seconds. Projects with 4K source files or more than 20 scene cuts take longer — plan for 3–5 minutes in those cases.

Output file size depends on scene count and motion. A standard 1-minute MP4 at 1080p runs between 40MB and 120MB. If you need a smaller file for email or web embedding, request H.264 compression at a lower bitrate explicitly.

The free-video-creator skill doesn't buffer or cache your inputs between sessions. Re-submit the full asset list if you're picking up a project after closing the window.

## Quick Start Guide

Start with the simplest input: a numbered list of scenes, one sentence each describing what appears on screen. That's enough for the free-video-creator skill to produce a draft structure you can then refine.

Once the draft looks right, attach your actual assets — images, a voiceover file, or a background track under 5MB. Specify the total target duration in seconds, not minutes, to avoid rounding ambiguity.

Request a preview thumbnail alongside the export. It's a single 1920×1080 JPEG pulled from the first scene and useful for upload previews on YouTube or LinkedIn without extra work on your end.
