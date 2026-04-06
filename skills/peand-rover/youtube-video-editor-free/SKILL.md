---
name: youtube-video-editor-free
version: "1.0.0"
displayName: "YouTube Video Editor Free — Cut, Trim & Polish Videos Without Paying a Dime"
description: >
  Tired of hitting paywalls every time you try to edit your YouTube videos? The youtube-video-editor-free skill helps creators trim clips, add captions, adjust pacing, and structure content for YouTube — all without a subscription. Whether you're a first-time vlogger or a seasoned channel owner cutting costs, this skill guides you through free editing workflows, tool recommendations, and step-by-step techniques to produce publish-ready YouTube content fast.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! 🎬 Ready to edit your YouTube videos without spending a cent? Tell me about your footage or project, and I'll walk you through a free editing workflow from raw clip to upload-ready video — let's get your content live!

**Try saying:**
- "I have a 20-minute raw recording of a tutorial. How do I trim it down to under 10 minutes using a free editor?"
- "What's the best free YouTube video editor for adding subtitles and captions to my videos?"
- "How do I remove background noise and add intro music to my YouTube video for free?"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/youtube-video-editor-free/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Edit YouTube Videos Without Spending a Single Dollar

Most video editing tools promise simplicity but deliver a paywall. This skill was built specifically for creators who want to produce great YouTube content using free tools — no trials, no watermarks, no surprise charges.

Whether you're working with raw footage from your phone, a screen recording, or a DSLR camera, this skill helps you plan your edits, structure your video for maximum viewer retention, and export a final cut that meets YouTube's technical requirements. You'll get guidance on trimming dead air, adding b-roll transitions, syncing audio, and writing on-screen text — all using tools that cost nothing.

This isn't a generic video editing tutorial. Every recommendation and workflow here is tailored to the YouTube format — from ideal video lengths by niche to thumbnail-ready end screens. If you're ready to stop letting budget be the reason your channel doesn't grow, this skill gives you the practical roadmap to start editing like a pro for free.

## Routing Your Edit Requests

When you submit a cut, trim, or polish request, ClawHub parses your intent and routes it to the appropriate free YouTube video editing endpoint based on the operation type — whether that's a timeline trim, a clip splice, or an export render.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing Backend Reference

All non-destructive edits run through a cloud-based transcoding pipeline that processes your raw footage in temporary buffers, so your original file stays untouched until you confirm the final export. Frame-accurate trimming and cut operations are handled server-side, meaning you don't need a powerful local machine to get clean results.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `youtube-video-editor-free`
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

This skill supports a wide range of YouTube creators who need to edit without a budget. Gaming channels can use it to cut highlight reels from long session recordings, removing slow moments and keeping only the best plays. Tutorial and how-to creators can structure step-by-step walkthroughs with on-screen annotations and chapter markers — all achievable in free tools.

Vloggers benefit from learning how to color-grade footage shot in mixed lighting conditions using free LUTs and correction tools inside DaVinci Resolve. Educators creating lecture-style content can learn to add slides, zoom into key areas, and sync audio from an external mic — all without paying for Adobe Premiere.

Even brands and small businesses producing YouTube content on a shoestring budget can use this skill to create polished product demos, testimonial compilations, or event recaps that look professional without the production cost.

## Quick Start Guide

Getting started with free YouTube video editing is easier than most creators expect. First, choose a free editor that matches your operating system — DaVinci Resolve and CapCut Desktop are strong picks for most users, while iMovie works great if you're on Mac.

Import your raw footage and begin with a rough cut: remove any dead air, false starts, and off-topic tangents. Aim to keep your YouTube video tight — most audiences drop off after the first 30 seconds if the pacing drags. Once your rough cut is done, layer in any b-roll, add captions using the editor's built-in text tools, and adjust your audio levels so voice sits around -12dB.

Export your final video in 1080p MP4 format using H.264 encoding — this is the YouTube-recommended setting and keeps file sizes manageable. Upload directly and use YouTube Studio to add end screens, chapters, and tags.

## Common Workflows

One of the most common workflows for YouTube creators is the 'talk-to-camera' cleanup: you record yourself speaking, then use a free editor to cut every pause longer than one second, add a lower-third name title, and drop in background music at low volume. This alone makes a raw talking-head video feel broadcast-quality.

Another popular workflow is screen recording editing — common for software tutorials. Capture your screen, then trim out navigation fumbles, speed up slow sections using the editor's rate-stretch tool, and add callout boxes to highlight where viewers should click.

For creators repurposing long-form content, a clip extraction workflow works well: take a 30-minute video, identify the three strongest moments, cut them into 60-second shorts, add captions, and export vertically for YouTube Shorts — all using free tools like CapCut or Kdenlive. This workflow alone can double your content output without doubling your filming time.
