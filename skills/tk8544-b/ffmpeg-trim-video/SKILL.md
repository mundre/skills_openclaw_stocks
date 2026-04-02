---
name: ffmpeg-trim-video
version: "1.0.0"
displayName: "FFmpeg Video Trimmer — Precisely Cut and Trim Video Clips with Ease"
description: >
  Turn raw, unedited footage into clean, polished clips by trimming video files with frame-accurate precision. This ffmpeg-trim-video skill lets you cut any video to exact start and end timestamps, remove unwanted sections, and export trimmed clips without re-encoding for blazing-fast results. Built for content creators, developers, and video editors who need reliable, scriptable trimming — no bloated software required.
metadata: {"openclaw": {"emoji": "✂️", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm here to help you trim video files with precision using FFmpeg — whether you need to cut a single clip or batch-process a whole library. Tell me your video's start time, end time, and what you'd like to keep, and let's get trimming!

**Try saying:**
- "Trim my video from 00:01:15 to 00:03:45 and save it as a new MP4 file without re-encoding"
- "Cut out the first 30 seconds and last 10 seconds from this recorded Zoom call"
- "Split a 1-hour webinar into 5-minute segments starting at every 5-minute mark"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Cut the Noise — Keep Only What Matters

Raw video footage is almost never ready to share straight out of the camera. There are awkward pauses at the beginning, dead air at the end, and unwanted sections buried in the middle. The ffmpeg-trim-video skill gives you a fast, reliable way to cut your video files down to exactly what you need — down to the second or even the frame.

Whether you're trimming a long recording to extract a single highlight, chopping up a webinar into digestible segments, or preparing clips for social media, this skill handles the heavy lifting. You specify the start time, end time, and output format — and it delivers a clean, trimmed file ready to use.

Unlike consumer video editors that force you through a GUI workflow, this skill is built for speed and repeatability. It's ideal for anyone who works with video programmatically — developers automating pipelines, creators processing batches of clips, or teams standardizing how footage gets prepared before publishing.

## Routing Your Trim Requests

When you specify a timecode range — like `-ss 00:01:30 -to 00:02:45` or a duration flag — the skill parses your input and routes the trim job to the appropriate processing endpoint based on format, codec, and whether you need keyframe-accurate or frame-precise cutting.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud FFmpeg API Reference

The backend spins up an isolated FFmpeg instance in the cloud, applying your `-ss`, `-t`, `-to`, and `-c copy` or re-encode parameters server-side — no local FFmpeg installation required. Processed clips are returned via a secure download link, with the original stream metadata and container format preserved unless you explicitly request a transcode.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ffmpeg-trim-video`
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

## Common Workflows

One of the most common workflows is lossless trimming — using stream copy to cut a video without re-encoding. This is the fastest approach and preserves the original quality exactly. Just specify your in and out points, and the skill trims the container without touching the codec data.

Another frequent workflow is segment extraction for social media. Users provide a single long video and a list of timestamp pairs, and the skill outputs multiple short clips — each trimmed and ready for upload. This is popular for turning conference talks or interviews into shareable soundbites.

A third workflow involves trimming combined with format conversion — for instance, trimming a section of an MKV file and outputting it as an H.264 MP4 for broader compatibility. This is useful when source footage comes from cameras or screen recorders that produce formats not natively supported by all platforms.

## Use Cases

The ffmpeg-trim-video skill fits naturally into a wide range of real-world workflows. Content creators use it to extract highlight clips from long-form recordings — pulling a 90-second moment from a two-hour livestream without sitting through a full export cycle. Podcast producers with video tracks use it to remove pre-show chatter and post-show wind-down before publishing.

Developers building media pipelines rely on it to programmatically slice uploaded videos into defined segments — for example, trimming user-submitted videos to a platform's maximum allowed length. Marketing teams use it to repurpose long product demos into short, punchy clips sized for LinkedIn, Instagram, or YouTube Shorts.

Educators and course creators trim recorded lectures into topic-specific modules, making content easier to navigate. Essentially, anyone who regularly works with video files and needs to cut them cleanly and consistently will find immediate value here.

## Integration Guide

Integrating ffmpeg-trim-video into your workflow is straightforward. The skill accepts a video file path or URL, a start timestamp, and an end timestamp — all in standard HH:MM:SS or seconds format. You can optionally specify whether to use stream copy mode (no re-encoding, ultra-fast) or a specific codec for the output.

For batch processing, you can chain multiple trim requests in sequence, passing in a list of segments with their respective time ranges. Output files can be named dynamically based on timestamps or custom labels you provide, making it easy to organize trimmed clips automatically.

The skill integrates cleanly into automation platforms, CI/CD pipelines, or custom scripts. If you're processing uploads in a web application, simply pass the file reference and trimming parameters — the skill returns the path or binary of the trimmed output ready for storage or delivery.
