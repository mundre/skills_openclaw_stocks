---
name: image-to-video-maker-ai
version: "1.0.0"
displayName: "Image to Video Maker AI — Convert Images into Videos"
description: >
  Get animated video clips ready to post, without touching a single slider. Upload your still images (JPG, PNG, WEBP, HEIC, up to 200MB), say something like "turn these photos into a 30-second video with transitions and background music", and download 1080p MP4 when it's done. Built for social media creators who move fast and want to create videos from photos without video editing skills.
metadata: {"openclaw": {"emoji": "🖼️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your still images and I'll handle the AI video creation. Or just describe what you're after.

**Try saying:**
- "convert three product photos in JPG format into a 1080p MP4"
- "turn these photos into a 30-second video with transitions and background music"
- "turning product or travel photos into shareable videos for social media creators"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Image to Video Maker AI — Convert Images into Videos

Send me your still images and describe the result you want. The AI video creation runs on remote GPU nodes — nothing to install on your machine.

A quick example: upload three product photos in JPG format, type "turn these photos into a 30-second video with transitions and background music", and you'll get a 1080p MP4 back in roughly 30-60 seconds. All rendering happens server-side.

Worth noting: using 5-10 images gives the AI enough content to build smooth transitions.

## Matching Input to Actions

User prompts referencing image to video maker ai, aspect ratio, text overlays, or audio tracks get routed to the corresponding action via keyword and intent classification.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render Pipeline Details

Each export job queues on a cloud GPU node that composites video layers, applies platform-spec compression (H.264, up to 1080x1920), and returns a download URL within 30-90 seconds. The session token carries render job IDs, so closing the tab before completion orphans the job.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `image-to-video-maker-ai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

Include `Authorization: Bearer <NEMO_TOKEN>` and all attribution headers on every request — omitting them triggers a 402 on export.

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

## Common Workflows

**Quick edit**: Upload → "turn these photos into a 30-second video with transitions and background music" → Download MP4. Takes 30-60 seconds for a 30-second clip.

**Batch style**: Upload multiple files in one session. Process them one by one with different instructions. Each gets its own render.

**Iterative**: Start with a rough cut, preview the result, then refine. The session keeps your timeline state so you can keep tweaking.

## Tips and Tricks

The backend processes faster when you're specific. Instead of "make it look better", try "turn these photos into a 30-second video with transitions and background music" — concrete instructions get better results.

Max file size is 200MB. Stick to JPG, PNG, WEBP, HEIC for the smoothest experience.

Export as MP4 for widest compatibility across social platforms.
