---
name: markdown-editor-with
version: "1.0.0"
displayName: "Markdown Editor With — Convert Markdown Into Videos"
description: >
  Turn a 300-word markdown script with headers and bullet points into 1080p structured video slides just by typing what you need. Whether it's turning markdown documents into formatted video presentations or quick social content, drop your text or script and describe the result you want. No timeline dragging, no export settings — 1-2 minutes from upload to download.
metadata: {"openclaw": {"emoji": "📝", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Ready when you are. Drop your text or script here or describe what you want to make.

**Try saying:**
- "convert a 300-word markdown script with headers and bullet points into a 1080p MP4"
- "convert this markdown outline into a narrated explainer video with slides"
- "turning markdown documents into formatted video presentations for developers and technical writers"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Markdown Editor With — Convert Markdown Into Videos

This tool takes your text or script and runs markdown-based video creation through a cloud rendering pipeline. You upload, describe what you want, and download the result.

Say you have a 300-word markdown script with headers and bullet points and want to convert this markdown outline into a narrated explainer video with slides — the backend processes it in about 1-2 minutes and hands you a 1080p MP4.

Tip: use clear heading levels in your markdown to define scene breaks automatically.

## Matching Input to Actions

User prompts referencing markdown editor with, aspect ratio, text overlays, or audio tracks get routed to the corresponding action via keyword and intent classification.

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

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `markdown-editor-with`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

Include `Authorization: Bearer <NEMO_TOKEN>` and all attribution headers on every request — omitting them triggers a 402 on export.

Draft JSON uses short keys: `t` for tracks, `tt` for track type (0=video, 1=audio, 7=text), `sg` for segments, `d` for duration in ms, `m` for metadata.

Example timeline summary:
```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

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

The backend processes faster when you're specific. Instead of "make it look better", try "convert this markdown outline into a narrated explainer video with slides" — concrete instructions get better results.

Max file size is 200MB. Stick to MD, TXT, DOCX, PDF for the smoothest experience.

Export as MP4 for widest compatibility across platforms and players.

## Common Workflows

**Quick edit**: Upload → "convert this markdown outline into a narrated explainer video with slides" → Download MP4. Takes 1-2 minutes for a 30-second clip.

**Batch style**: Upload multiple files in one session. Process them one by one with different instructions. Each gets its own render.

**Iterative**: Start with a rough cut, preview the result, then refine. The session keeps your timeline state so you can keep tweaking.
