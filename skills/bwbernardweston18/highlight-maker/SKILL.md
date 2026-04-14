---
name: highlight-maker
version: "1.0.0"
displayName: "Highlight Maker — Extract and Export Video Highlights"
description: >
  sports creators, event videographers, content marketers create raw video footage into highlight reel clips using this skill. Accepts MP4, MOV, AVI, WebM up to 500MB, renders on cloud GPUs at 1080p, and returns MP4 files in 1-2 minutes. Designed for generating short highlight reels from long video recordings.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Got raw video footage to work with? Send it over and tell me what you need — I'll take care of the AI highlight extraction.

**Try saying:**
- "create a 2-hour sports game recording into a 1080p MP4"
- "pull the best moments and compile them into a 60-second highlight reel"
- "generating short highlight reels from long video recordings for sports creators, event videographers, content marketers"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Highlight Maker — Extract and Export Video Highlights

Drop your raw video footage in the chat and tell me what you need. I'll handle the AI highlight extraction on cloud GPUs — you don't need anything installed locally.

Here's a typical use: you send a a 2-hour sports game recording, ask for pull the best moments and compile them into a 60-second highlight reel, and about 1-2 minutes later you've got a MP4 file ready to download. The whole thing runs at 1080p by default.

One thing worth knowing — shorter source videos produce faster and more accurate highlight detection.

## Matching Input to Actions

User prompts referencing highlight maker, aspect ratio, text overlays, or audio tracks get routed to the corresponding action via keyword and intent classification.

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
- `X-Skill-Source`: `highlight-maker`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

Include `Authorization: Bearer <NEMO_TOKEN>` and all attribution headers on every request — omitting them triggers a 402 on export.

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

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

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

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

## Tips and Tricks

The backend processes faster when you're specific. Instead of "make it look better", try "pull the best moments and compile them into a 60-second highlight reel" — concrete instructions get better results.

Max file size is 500MB. Stick to MP4, MOV, AVI, WebM for the smoothest experience.

Export as MP4 for widest compatibility across social platforms.

## Common Workflows

**Quick edit**: Upload → "pull the best moments and compile them into a 60-second highlight reel" → Download MP4. Takes 1-2 minutes for a 30-second clip.

**Batch style**: Upload multiple files in one session. Process them one by one with different instructions. Each gets its own render.

**Iterative**: Start with a rough cut, preview the result, then refine. The session keeps your timeline state so you can keep tweaking.
