---
name: ffmpeg-add-subtitle
version: "1.0.0"
displayName: "FFmpeg Subtitle Embedder — Burn-In or Attach Subtitles to Any Video File"
description: >
  Tell me what you need and I'll help you add subtitles to your videos using FFmpeg — whether you're burning text directly into frames or attaching a soft subtitle track. This ffmpeg-add-subtitle skill handles SRT, ASS, VTT, and more, giving you precise control over font, timing, position, and encoding. Perfect for content creators, educators, translators, and video editors who need reliable subtitle integration without wrestling with command-line syntax.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm here to help you add subtitles to your videos using FFmpeg — whether you want them burned in permanently or attached as a toggleable track. Tell me about your video file and subtitle source, and let's get started!

**Try saying:**
- "Burn in subtitles from an SRT file onto my MP4 video and keep the original audio quality"
- "Attach a soft VTT subtitle track to an MKV file without re-encoding the video stream"
- "Add styled ASS subtitles to a video with a custom font and position them at the top of the frame"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/ffmpeg-add-subtitle/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Embed Subtitles Into Any Video With Precision

Adding subtitles to a video sounds simple — until you're staring at FFmpeg documentation trying to figure out why your SRT file isn't rendering, or why the font looks wrong, or why soft subs aren't showing up in your media player. That's exactly what this skill is built to solve.

With the FFmpeg Add Subtitle skill, you can embed subtitles in two distinct ways: as a hard-coded burn-in (permanently baked into the video frames) or as a soft subtitle stream (a separate track viewers can toggle on or off). Both approaches have real-world use cases, and this skill helps you choose the right one and execute it correctly.

Whether you're localizing a course video, captioning a short film, adding translated subs to a documentary, or preparing accessible content for social media, this skill generates the exact FFmpeg commands you need — with the right filters, codec flags, and file path handling — so you get clean results the first time.

## Routing Subtitle Burn-In Requests

When you submit a subtitle embedding job, the skill parses your input to determine whether you're hardcoding subtitles directly into the video stream via libass filter or attaching a soft subtitle track as a separate mux stream, then routes accordingly.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## FFmpeg Cloud API Reference

The backend spins up an isolated FFmpeg processing node that handles subtitle codec mapping, filter graph construction, and container muxing — supporting SRT, ASS, VTT, and PGS formats across MP4, MKV, and MOV containers. Transcoding jobs run server-side so your local machine never touches the bitstream.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ffmpeg-add-subtitle`
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

## Use Cases

Content creators publishing multilingual videos often use ffmpeg-add-subtitle to batch-process translated SRT files onto the same base video, producing multiple language versions efficiently without re-editing the source.

E-learning developers rely on subtitle embedding to meet accessibility requirements, ensuring that course videos include accurate captions for learners with hearing impairments or those watching in sound-sensitive environments.

Film and video editors working on indie productions use the ASS/SSA format support to embed richly styled subtitles — with custom fonts, colors, and animations — directly into screener copies or festival submissions.

Social media managers frequently need to burn subtitles into square or vertical crops of longer videos, where the subtitle position and size need to be adjusted to avoid overlapping with on-screen graphics. This skill helps dial in those positioning parameters precisely using FFmpeg's filter options.

## Common Workflows

The most frequent workflow is burning an SRT file directly into a video using FFmpeg's `subtitles` filter. This permanently renders the text onto each frame, making it ideal for platforms like Instagram or YouTube Shorts where external subtitle tracks aren't supported. You specify the subtitle file path, optionally define a font name and size, and FFmpeg handles the rest during re-encoding.

For more flexible distribution — such as MKV files intended for media center playback — soft subtitle embedding is the better choice. Here, FFmpeg muxes the subtitle stream alongside the video and audio without touching the actual picture quality. Viewers can enable or disable subtitles in their player.

Another common need is converting subtitle formats before embedding. If you have a WebVTT file but need SRT compatibility, or an ASS file with complex styling you want to simplify, this skill can walk you through the conversion step before the final embed — keeping your workflow clean and your output predictable.
