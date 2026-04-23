---
name: video-editing-ai-open-source
version: "1.0.0"
displayName: "Video Editing AI Open Source — Edit and Export AI Videos"
description: >
  Get edited MP4 clips ready to post, without touching a single slider. Upload your raw video footage (MP4, MOV, AVI, WebM, up to 500MB), say something like "cut silences, add transitions, and export a clean final cut", and download 1080p MP4 when it's done. Built for indie creators and developers who move fast and want free AI editing tools without proprietary software lock-in.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Share your raw video footage and I'll get started on AI-powered video editing. Or just tell me what you're thinking.

**Try saying:**
- "edit my raw video footage"
- "export 1080p MP4"
- "cut silences, add transitions, and export"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Video Editing AI Open Source — Edit and Export AI Videos

Send me your raw video footage and describe the result you want. The AI-powered video editing runs on remote GPU nodes — nothing to install on your machine.

A quick example: upload a 3-minute unedited screen recording, type "cut silences, add transitions, and export a clean final cut", and you'll get a 1080p MP4 back in roughly 1-2 minutes. All rendering happens server-side.

Worth noting: shorter clips under 2 minutes process significantly faster and yield cleaner AI edits.

## Matching Input to Actions

User prompts referencing video editing ai open source, aspect ratio, text overlays, or audio tracks get routed to the corresponding action via keyword and intent classification.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render Pipeline Details

Each export job queues on a cloud GPU node that composites video layers, applies platform-spec compression (H.264, up to 1080x1920), and returns a download URL within 30-90 seconds. The session token carries render job IDs, so closing the tab before completion orphans the job.

All calls go to `https://mega-api-prod.nemovideo.ai`. The main endpoints:

1. **Session** — `POST /api/tasks/me/with-session/nemo_agent` with `{"task_name":"project","language":"<lang>"}`. Gives you a `session_id`.
2. **Chat (SSE)** — `POST /run_sse` with `session_id` and your message in `new_message.parts[0].text`. Set `Accept: text/event-stream`. Up to 15 min.
3. **Upload** — `POST /api/upload-video/nemo_agent/me/<sid>` — multipart file or JSON with URLs.
4. **Credits** — `GET /api/credits/balance/simple` — returns `available`, `frozen`, `total`.
5. **State** — `GET /api/state/nemo_agent/me/<sid>/latest` — current draft and media info.
6. **Export** — `POST /api/render/proxy/lambda` with render ID and draft JSON. Poll `GET /api/render/proxy/lambda/<id>` every 30s for `completed` status and download URL.

Formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

Headers are derived from this file's YAML frontmatter. `X-Skill-Source` is `video-editing-ai-open-source`, `X-Skill-Version` comes from the `version` field, and `X-Skill-Platform` is detected from the install path (`~/.clawhub/` = `clawhub`, `~/.cursor/skills/` = `cursor`, otherwise `unknown`).

Include `Authorization: Bearer <NEMO_TOKEN>` and all attribution headers on every request — omitting them triggers a 402 on export.

Draft JSON uses short keys: `t` for tracks, `tt` for track type (0=video, 1=audio, 7=text), `sg` for segments, `d` for duration in ms, `m` for metadata.

Example timeline summary:
```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Translating GUI Instructions

The backend responds as if there's a visual interface. Map its instructions to API calls:

- "click" or "点击" → execute the action via the relevant endpoint
- "open" or "打开" → query session state to get the data
- "drag/drop" or "拖拽" → send the edit command through SSE
- "preview in timeline" → show a text summary of current tracks
- "Export" or "导出" → run the export workflow

### Reading the SSE Stream

Text events go straight to the user (after GUI translation). Tool calls stay internal. Heartbeats and empty `data:` lines mean the backend is still working — show "⏳ Still working..." every 2 minutes.

About 30% of edit operations close the stream without any text. When that happens, poll `/api/state` to confirm the timeline changed, then tell the user what was updated.

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

## Tips and Tricks

The backend processes faster when you're specific. Instead of "make it look better", try "cut silences, add transitions, and export a clean final cut" — concrete instructions get better results.

Max file size is 500MB. Stick to MP4, MOV, AVI, WebM for the smoothest experience.

Export as MP4 with H.264 codec for the widest compatibility across platforms.

## Common Workflows

**Quick edit**: Upload → "cut silences, add transitions, and export a clean final cut" → Download MP4. Takes 1-2 minutes for a 30-second clip.

**Batch style**: Upload multiple files in one session. Process them one by one with different instructions. Each gets its own render.

**Iterative**: Start with a rough cut, preview the result, then refine. The session keeps your timeline state so you can keep tweaking.
