---
name: ffmpeg-converter
version: "1.0.0"
displayName: "FFmpeg Converter — Batch Convert, Compress & Transform Any Media File"
description: >
  Tired of manually wrestling with ffmpeg command-line syntax just to convert a video or compress an audio file? The ffmpeg-converter skill takes the complexity out of media conversion by letting you describe what you want in plain English. Whether you need to transcode MP4 to WebM, extract audio from video, resize resolution, adjust bitrate, or batch convert entire folders, ffmpeg-converter handles it without requiring you to memorize a single flag. Built for video editors, developers, and content creators who move fast.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm your ffmpeg-converter assistant — ready to help you convert, compress, trim, or transform any video or audio file using the full power of ffmpeg. Tell me what you're working with and what you need, and let's get it done.

**Try saying:**
- "Convert all MKV files in this folder to MP4 using H.264 and AAC audio, keeping the original resolution"
- "Extract the audio from this video file and save it as a high-quality MP3 at 320kbps"
- "Compress this 4K video to under 100MB while keeping the best possible visual quality"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/ffmpeg-converter/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Convert Any Media File Without Touching the Terminal

Most people who need to convert video or audio files hit the same wall: ffmpeg is incredibly powerful, but its command-line interface is dense, unforgiving, and full of flags that are easy to get wrong. One typo in a codec name, one missed parameter, and your output file is corrupted, bloated, or simply wrong.

The ffmpeg-converter skill was built specifically to bridge that gap. You describe your conversion goal in natural language — 'convert this MKV to MP4 with H.264 encoding and keep the subtitles' — and the skill generates the precise ffmpeg command to make it happen, then executes it directly. No guessing, no Stack Overflow rabbit holes, no trial and error.

This skill is especially useful for content creators processing large batches of footage, developers automating media pipelines, and anyone who regularly works with mixed format libraries. From simple format swaps to complex multi-stream operations involving video filters, audio normalization, and thumbnail extraction, ffmpeg-converter handles the full range of what ffmpeg is capable of — with you staying in control of the outcome.

## Routing Your Conversion Requests

When you specify a target format, codec, bitrate, resolution, or filter chain, your request is parsed and dispatched directly to the appropriate FFmpeg processing pipeline based on the media type and transformation parameters detected.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing Backend Reference

All transcoding jobs run on a cloud-hosted FFmpeg engine that handles muxing, demuxing, codec negotiation, and filter graph execution server-side — no local FFmpeg installation required. Heavy operations like multi-pass encoding, audio normalization, and frame-rate conversion are fully offloaded, so output is returned as a downloadable link or stream.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ffmpeg-converter`
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

## Performance Notes

FFmpeg conversion speed depends heavily on your hardware and the codec you're targeting. Software encoding with libx264 or libx265 is CPU-intensive — expect longer processing times for large or high-resolution files. If your machine has a compatible GPU, ask ffmpeg-converter to use hardware acceleration (NVIDIA NVENC, AMD AMF, or Apple VideoToolbox) to dramatically reduce encoding time.

For quick format swaps where both the source and target support the same codec, request a 'stream copy' conversion using `-c copy`. This remuxes the file without re-encoding, completing in seconds regardless of file size — ideal for changing container formats like MKV to MP4 when the internal codecs are already compatible.

Keep in mind that two-pass encoding produces better quality-to-size ratios for final output files, while single-pass is faster for drafts or previews. Specify your priority — speed or quality — and ffmpeg-converter will choose the appropriate approach.

## Tips and Tricks

When using ffmpeg-converter, the more specific your request, the better your output. Instead of saying 'convert this video,' try 'convert this video to 1080p MP4 with H.265 encoding and stereo audio at 192kbps.' Codec choices matter enormously for file size and compatibility — H.264 is safest for broad device support, while H.265 (HEVC) cuts file sizes nearly in half at the same quality.

For batch operations, mention the source folder and target format together so the skill can build a loop-based command rather than individual conversions. If you're preparing video for web delivery, ask specifically for 'web-optimized' output — this triggers the `-movflags +faststart` flag that enables progressive loading in browsers.

Need to preserve subtitles, multiple audio tracks, or chapter markers? Just say so explicitly. FFmpeg supports copying these streams without re-encoding, which keeps conversion fast and lossless for those elements.

## Quick Start Guide

Getting started with ffmpeg-converter is straightforward. Begin by telling the skill the file or files you want to work with and your desired output format. A basic starting request looks like: 'Convert video.mov to video.mp4 using H.264.' That's enough to get a working result.

If you have a specific use case — social media export, archival encoding, streaming preparation, or audio extraction — mention that context upfront. The skill will tailor the ffmpeg parameters to match industry-standard settings for that scenario rather than using generic defaults.

For users new to media formats, you can also ask ffmpeg-converter to explain what a generated command does before running it. This is a great way to learn which flags control which behaviors, so you can make informed adjustments on future conversions. The skill supports iterative refinement — if your first output isn't quite right, describe what needs to change and it will update the command accordingly.
