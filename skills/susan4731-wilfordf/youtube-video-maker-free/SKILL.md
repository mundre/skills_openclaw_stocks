---
name: youtube-video-maker-free
version: "1.0.0"
displayName: "YouTube Video Maker Free — Create & Export 1080p MP4s Online"
description: >
  Get a finished 1080p MP4 ready to upload to YouTube without paying for software. This free YouTube video maker handles the full creation process — script to screen — so marketers, educators, and YouTubers don't need a separate editing suite. Use it as a free online video creator, an AI YouTube video generator, or a no-cost video production tool; the exported file drops straight into YouTube Studio at up to 1920×1080 resolution with no watermark added.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Paste your script or topic and I'll build a YouTube-ready 1080p MP4 from it. No script yet? Describe your video idea in one sentence.

**Try saying:**
- "make a free YouTube video from my blog post text"
- "create a 60-second YouTube intro video free no watermark"
- "generate a YouTube tutorial video free using AI from a script"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn a Script or Idea Into a YouTube-Ready MP4

Paste your script, topic, or bullet points into the chat. The skill builds a structured video — titles, transitions, and timed text — then delivers an MP4 at 1080p.

Example: input a 200-word product walkthrough script, specify a 60-second target length, and receive a rendered file with synchronized captions and a title card. No footage library required.

Adjust pacing, swap background music, or change the aspect ratio to 16:9 before final export. Each render takes under 90 seconds for clips up to 3 minutes.

## Matching Clips To Export Actions

When you drop a clip into the YouTube Video Maker Free timeline, the tool reads the file's resolution and frame rate metadata to route it to either the 1080p upscale queue or the direct 1080p MP4 export pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render Pipeline Details

Exports run on shared cloud GPU nodes that encode your 1080p MP4 using H.264 at a 16 Mbps target bitrate, so a 3-minute video typically finishes rendering in under 90 seconds. The final file lands in your browser's download folder automatically once the render node pushes it through the CDN.

Include `Authorization: Bearer <NEMO_TOKEN>` and all attribution headers on every request — omitting them triggers a 402 on export.

Headers are derived from this file's YAML frontmatter. `X-Skill-Source` is `youtube-video-maker-free`, `X-Skill-Version` comes from the `version` field, and `X-Skill-Platform` is detected from the install path (`~/.clawhub/` = `clawhub`, `~/.cursor/skills/` = `cursor`, otherwise `unknown`).

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

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

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

### Reading the SSE Stream

Text events go straight to the user (after GUI translation). Tool calls stay internal. Heartbeats and empty `data:` lines mean the backend is still working — show "⏳ Still working..." every 2 minutes.

About 30% of edit operations close the stream without any text. When that happens, poll `/api/state` to confirm the timeline changed, then tell the user what was updated.

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

## Troubleshooting: Export Errors and File Issues

If the exported MP4 won't upload to YouTube Studio, check that the file is under 256 GB and encoded in H.264 — YouTube rejects files above that threshold or in unsupported codecs.

A render that stalls past 3 minutes usually means the input script exceeded 1,500 words. Split it into two separate jobs, each targeting a 3-minute clip, and concatenate them after download.

Caption sync problems happen when the script contains timestamps in a non-standard format. Strip out any manual timestamps before pasting; the free YouTube video maker assigns timing automatically based on word count and pacing settings. Re-run the job and sync issues resolve in the new output file.

## Tips and Tricks: Get Better Results From Your Free YouTube Video Maker

Front-load your strongest sentence in the first 5 words of the script. YouTube's algorithm reads retention data from the first 30 seconds, so the opening line directly affects click-through rate.

Set the target duration before generating, not after. Asking for a 90-second free online video creation pass produces tighter cuts than trimming a 3-minute render down to 90 seconds in post.

For faceless YouTube channels, specify a visual style in the prompt — 'dark background, white sans-serif text, minimal motion' — rather than leaving it unspecified. The AI YouTube video generator picks a default style when none is given, and changing it after render costs an extra generation cycle. One style note in the initial prompt saves that step entirely.
