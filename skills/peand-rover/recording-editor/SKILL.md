---
name: recording-editor
version: "1.0.0"
displayName: "Recording Editor — Edit and Export Clean Recordings"
description: >
  edit raw recordings into edited recording clips with this recording-editor skill. Works with MP4, MOV, AVI, WebM files up to 500MB. content creators, educators, remote workers use it for trimming and polishing raw recordings for sharing or publishing — processing takes 1-2 minutes on cloud GPUs and you get 1080p MP4 files.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your raw recordings and I'll handle the AI video editing. Or just describe what you're after.

**Try saying:**
- "edit a 3-minute screen or voice recording into a 1080p MP4"
- "cut the silences, add intro music, and export as a clean MP4"
- "trimming and polishing raw recordings for sharing or publishing for content creators, educators, remote workers"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Recording Editor — Edit and Export Clean Recordings

Send me your raw recordings and describe the result you want. The AI video editing runs on remote GPU nodes — nothing to install on your machine.

A quick example: upload a 3-minute screen or voice recording, type "cut the silences, add intro music, and export as a clean MP4", and you'll get a 1080p MP4 back in roughly 1-2 minutes. All rendering happens server-side.

Worth noting: splitting long recordings into segments before uploading speeds up processing.

## Matching Input to Actions

User prompts referencing recording editor, aspect ratio, text overlays, or audio tracks get routed to the corresponding action via keyword and intent classification.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render Pipeline Details

Each export job queues on a cloud GPU node that composites video layers, applies platform-spec compression (H.264, up to 1080x1920), and returns a download URL within 30-90 seconds. The session token carries render job IDs, so closing the tab before completion orphans the job.

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

Three attribution headers are required on every request and must match this file's frontmatter:

| Header | Value |
|--------|-------|
| `X-Skill-Source` | `recording-editor` |
| `X-Skill-Version` | frontmatter `version` |
| `X-Skill-Platform` | auto-detect: `clawhub` / `cursor` / `unknown` from install path |

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

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

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Translating GUI Instructions

The backend responds as if there's a visual interface. Map its instructions to API calls:

- "click" or "点击" → execute the action via the relevant endpoint
- "open" or "打开" → query session state to get the data
- "drag/drop" or "拖拽" → send the edit command through SSE
- "preview in timeline" → show a text summary of current tracks
- "Export" or "导出" → run the export workflow

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

## Tips and Tricks

The backend processes faster when you're specific. Instead of "make it look better", try "cut the silences, add intro music, and export as a clean MP4" — concrete instructions get better results.

Max file size is 500MB. Stick to MP4, MOV, AVI, WebM for the smoothest experience.

Export as MP4 for widest compatibility across platforms and devices.

## Common Workflows

**Quick edit**: Upload → "cut the silences, add intro music, and export as a clean MP4" → Download MP4. Takes 1-2 minutes for a 30-second clip.

**Batch style**: Upload multiple files in one session. Process them one by one with different instructions. Each gets its own render.

**Iterative**: Start with a rough cut, preview the result, then refine. The session keeps your timeline state so you can keep tweaking.
