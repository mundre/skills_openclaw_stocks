---
name: video-trimmer-free-download
version: "1.0.4"
displayName: "Video Trimmer Free Download — Cut, Crop & Export Clips Instantly"
description: >
  Tell me what you need and I'll help you find, use, and get the most out of a video-trimmer-free-download tool that fits your device and editing goals. Whether you're cutting out dead air from a recording, trimming a clip for social media, or chopping a long video into shareable segments, this skill walks you through the best free options available — no subscriptions, no watermarks, no guesswork. Built for creators, students, and everyday users who just want clean cuts without paying for bloated software.
metadata: {"openclaw": {"emoji": "✂️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome — let's get your video trimmed without spending a cent or wrestling with confusing software. Tell me your device, what you're trying to cut, and I'll point you to the best free trimmer and walk you through every step.

**Try saying:**
- "I have a 45-minute screen recording and I only need the first 10 minutes — what's the best free video trimmer I can download on Windows to do this without losing quality?"
- "I'm on my iPhone and I need to cut out the middle section of a video before I post it to Instagram — is there a free trimmer app that won't add a watermark?"
- "I downloaded a free video trimmer but every time I export the file, the audio goes out of sync with the video — how do I fix this?"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Trim Any Video for Free — No Fluff, Just Cuts

Finding a reliable video trimmer that's actually free — no hidden paywalls, no watermarks stamped across your footage — can feel surprisingly difficult. This skill cuts through the noise and helps you identify the right tool for your specific situation, whether you're on Windows, Mac, Android, iOS, or working entirely in a browser.

Once you've got the right trimmer in hand, this skill guides you through the actual editing process: setting precise start and end points, splitting a clip into multiple segments, removing unwanted sections from the middle, and exporting your finished video in a format that works wherever you're posting it.

This isn't about learning a complicated timeline editor or sitting through a tutorial series. It's about getting a clean, trimmed video file as fast as possible — using tools that are genuinely free to download and use. Whether you're prepping a clip for YouTube Shorts, trimming a lecture recording, or cutting down a family video to the good parts, this skill gives you a direct path from raw footage to finished cut.

## Routing Trim & Export Requests

When you submit a cut point, crop frame, or export command, ClawHub parses the in/out timestamps and format parameters, then dispatches the job to the nearest available processing node for zero-lag execution.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

The backend leverages a distributed transcoding pipeline that handles frame-accurate trimming, aspect ratio cropping, and codec-level export rendering — all without touching your local CPU. Requests are authenticated via bearer token and return a signed download URL once the render completes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-trimmer-free-download`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

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

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Troubleshooting Your Free Video Trimmer

Audio sync issues are the most common complaint with free video trimmers. This usually happens when the trimmer re-encodes the video during export using a different frame rate than the original. Fix this by looking for a 'lossless cut' or 'fast trim' mode — tools like LosslessCut (free, desktop) are built specifically to avoid this problem by cutting without re-encoding.

If your exported file is unexpectedly large, your trimmer is likely exporting at a very high bitrate. Look for a quality or compression slider in the export settings and bring it down slightly — for web use, a bitrate of 8–12 Mbps for 1080p is usually more than enough.

Crashes during export on long files are often a memory issue. Try trimming in shorter segments and exporting separately, then joining the pieces afterward. If a browser-based trimmer keeps failing on large files, switch to a desktop download — browser tools have strict file size limits that desktop apps don't share.

## Integration Guide — Using Your Trimmed Clips Downstream

After trimming, your exported clip needs to work wherever you're sending it. Most free video trimmers export in MP4 by default, which is widely compatible with YouTube, TikTok, Instagram, WhatsApp, and most email clients. If you need a different format — like MOV for iMovie or WebM for a web project — check your trimmer's export settings before you start, since not all free tools offer format conversion.

If you're feeding your trimmed clip into a larger editing project, export at the highest quality the free tool allows and avoid re-compressing the file more than once. Each compression pass degrades quality slightly. Tools like DaVinci Resolve (free tier) can accept trimmed clips directly and let you continue editing on a full timeline.

For batch workflows — trimming many clips to the same length — desktop tools like Shotcut or OpenShot offer basic scripting and batch export features at no cost, which browser-based trimmers generally can't match.

## Common Workflows for Free Video Trimming

The most frequent use case is simple endpoint trimming — you have a long video and you want to keep only a specific portion. Most free trimmers handle this by letting you drag handles on a timeline or manually type in start and end timestamps. For anything under 5 minutes, browser-based tools like Clideo or Kapwing work without any download at all.

For removing a section from the middle of a clip, you'll typically need to split the video into two parts at the cut point, delete the unwanted segment, then join the remaining pieces. Apps like VLC (free, desktop) and CapCut (free, mobile) both support this in a few taps.

If you're trimming for a specific platform — like cutting to 60 seconds for TikTok or 30 seconds for an Instagram Reel — look for trimmers that show you the output duration in real time as you adjust. This saves you from exporting and re-exporting multiple times.
