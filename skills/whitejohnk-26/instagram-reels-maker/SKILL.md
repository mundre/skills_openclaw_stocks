---
name: instagram-reels-maker
version: "1.0.0"
displayName: "Instagram Reels Maker — Create and Export Reels Videos"
description: >
  Get 1080p MP4 files from your video clips or images using this instagram-reels-maker tool. It runs AI Reels creation on cloud GPUs, so your machine does zero heavy lifting. Instagram creators and social media marketers can creating short vertical videos formatted for Instagram Reels in roughly 30-60 seconds — supports MP4, MOV, AVI, WebM.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Drop your video clips or images here and tell me what to do with it. Describe your idea if you don't have files yet.

**Try saying:**
- "create a 60-second vertical phone recording into a 1080p MP4"
- "cut to 30 seconds, add trending music and captions, format for Instagram Reels"
- "creating short vertical videos formatted for Instagram Reels for Instagram creators and social media marketers"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Instagram Reels Maker — What You Get

So here's how this works. You give me video clips or images and I AI Reels creation it through NemoVideo's backend. No local software, no plugins, no GPU on your end.

Tested it with a a 60-second vertical phone recording last week. Asked for cut to 30 seconds, add trending music and captions, format for Instagram Reels and had a MP4 back in 30-60 seconds. 1080p quality, decent file size.

vertical 9:16 video works best — no cropping needed for Reels. That's about it.

## Request Routing

Your request is matched to one of several actions depending on what you typed.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## How It Works Internally

Everything happens on cloud infrastructure. Your instagram reels maker job gets queued, rendered on GPU nodes, and the finished file comes back as a download link.

All calls go to `https://mega-api-prod.nemovideo.ai`. The main endpoints:

1. **Session** — `POST /api/tasks/me/with-session/nemo_agent` with `{"task_name":"project","language":"<lang>"}`. Gives you a `session_id`.
2. **Chat (SSE)** — `POST /run_sse` with `session_id` and your message in `new_message.parts[0].text`. Set `Accept: text/event-stream`. Up to 15 min.
3. **Upload** — `POST /api/upload-video/nemo_agent/me/<sid>` — multipart file or JSON with URLs.
4. **Credits** — `GET /api/credits/balance/simple` — returns `available`, `frozen`, `total`.
5. **State** — `GET /api/state/nemo_agent/me/<sid>/latest` — current draft and media info.
6. **Export** — `POST /api/render/proxy/lambda` with render ID and draft JSON. Poll `GET /api/render/proxy/lambda/<id>` every 30s for `completed` status and download URL.

Formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `instagram-reels-maker`
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

## Quick Start Guide

1. Send your video clips or images (drag and drop works)
2. Tell me what you want: "cut to 30 seconds, add trending music and captions, format for Instagram Reels"
3. Wait 30-60 seconds for processing
4. Download your MP4 file

That's it. No account needed for your first 100 credits. Supports MP4, MOV, AVI, WebM.

## Common Workflows

**From scratch**: Describe what you want and the AI generates a draft. You refine from there.

**Polish existing content**: Upload your video clips or images, ask for specific changes — cut to 30 seconds, drop in trending music and captions, format for Instagram Reels, adjust colors, swap music. The backend handles rendering.

**Export ready**: Once you're happy, export at 1080p in MP4. File lands in your downloads.

## FAQ

**What resolution can I get?** Up to 1080p. Input quality matters though — garbage in, garbage out.

**Can I use this on my phone footage?** Yes. Vertical (9:16), horizontal (16:9), square — all work. Just upload and specify what you want.

**Credits?** 100 free to start. Most operations cost 1-5 credits depending on video length.
