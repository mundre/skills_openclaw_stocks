---
name: ffmpeg-online
version: "1.0.0"
displayName: "FFmpeg Online — Convert, Edit & Process Video and Audio in Your Browser"
description: >
  Turn raw footage into polished, web-ready media without installing a single program. ffmpeg-online brings the full power of FFmpeg's command-line processing to a simple chat interface — trim clips, convert between formats, extract audio, adjust bitrates, and more. Perfect for developers, content creators, and video editors who need fast, flexible media processing without the local setup headache.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm your ffmpeg-online assistant — ready to help you convert, trim, compress, or transform any video or audio file using FFmpeg's full capabilities. Tell me what you'd like to do with your media file and we'll get started right away!

**Try saying:**
- "Convert my video.mp4 to a WebM file optimized for web playback"
- "Trim the first 30 seconds off my recording.mp4 and export just the remaining footage"
- "Extract the audio from my interview.mp4 and save it as a 128kbps MP3"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/ffmpeg-online/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Process Any Video or Audio File, Instantly

FFmpeg is one of the most powerful media processing tools ever built — but its command-line interface has always been a barrier for people who just want to get things done. ffmpeg-online removes that barrier entirely. Instead of memorizing complex flags and syntax, you simply describe what you want: trim a clip, convert an MP4 to WebM, extract an audio track, or resize a video for social media.

This skill translates your plain-English requests into precise FFmpeg commands, executes them, and delivers results you can actually use. Whether you're a developer preparing assets for a web app, a podcaster extracting clean audio from a recorded video call, or a marketer resizing footage for different platforms, ffmpeg-online handles the heavy lifting.

No local FFmpeg installation required. No digging through documentation. No trial-and-error with cryptic flags. Just describe your goal, and let the skill figure out the right command for the job — then run it.

## Routing FFmpeg Commands to Processing

When you submit a transcode request, remux job, or filter graph operation, the skill parses your intent and dispatches it to the appropriate FFmpeg Online processing endpoint based on codec, container format, and operation type.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Backend API Reference

FFmpeg Online runs a managed cloud backend that executes real FFmpeg builds server-side, supporting a wide range of codecs, muxers, and filter chains without requiring any local installation. Jobs are queued, processed, and the output file is returned via a secure download link tied to your session.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ffmpeg-online`
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

## Quick Start Guide

Getting started with ffmpeg-online is straightforward. Upload or reference the media file you want to work with, then describe your goal in plain language — no FFmpeg syntax knowledge needed.

For example, you might say: 'Compress this video to under 50MB while keeping 1080p resolution' or 'Convert this WAV file to AAC for use in a mobile app.' The skill will interpret your request, generate the appropriate FFmpeg command, and process the file.

If you already know FFmpeg and want to pass a specific command directly, you can do that too — just paste the command and it will be executed as-is. This makes ffmpeg-online equally useful for beginners who want guidance and power users who want a fast execution environment without spinning up a local terminal.

## Tips and Tricks

To get the best results from ffmpeg-online, be specific about your output requirements. Instead of saying 'make the file smaller,' try 'compress this to under 20MB using H.264 at 720p.' The more context you provide, the more precisely the skill can match the right FFmpeg settings to your needs.

If you're unsure what format a platform requires, just mention the platform — for example, 'format this for WhatsApp video status' — and the skill will apply the appropriate codec, resolution, and duration constraints automatically.

For audio work, always mention your target use case (streaming, podcast hosting, mobile playback) since bitrate and codec choices vary significantly. And if a first attempt doesn't produce exactly what you wanted, just reply with a correction — the skill will adjust the command and re-process without you needing to start over.

## Use Cases

ffmpeg-online covers a wide range of real-world media tasks. Content creators use it to reformat videos for YouTube, Instagram Reels, or TikTok — each platform has different resolution, codec, and bitrate requirements that ffmpeg handles effortlessly.

Developers rely on it to generate thumbnails from video frames, convert audio formats for browser compatibility (like MP3 to OGG), or batch-process assets during prototyping without setting up a local processing pipeline.

Podcasters and educators use it to strip audio from screen recordings, normalize volume levels, or merge multiple audio segments into a single clean file. Video editors use it to quickly re-encode footage into a format compatible with their editing software when native imports fail.

Even simple tasks — like rotating a video shot in the wrong orientation or adding a watermark — are handled cleanly through natural conversation with the skill.
