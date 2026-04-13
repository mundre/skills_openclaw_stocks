---
name: magic-light-ai
version: "1.0.1"
displayName: "Magic Light AI — Add Lighting Effects to Your Videos"
description: >
  Got footage that looks flat or poorly lit? magic-light-ai fixes lighting in your videos using cloud-based AI processing. Upload an MP4 or MOV, tell it what you want (warmer tones, golden hour look, neon glow), and get back a 1080p result in under two minutes. No plugins or software needed.
metadata: {"openclaw": {"emoji": "💡", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Ready for magic light ai. Drop your video or tell me what lighting you want.

**Try saying:**
- "warm up the lighting in my clip"
- "add a golden hour glow effect"
- "fix the dark areas in this footage"

### First-Time Connection

On first use, the skill sets up a connection to the cloud backend. You'll see a brief "Setting up..." message.

**Authentication**: If `NEMO_TOKEN` is already in your environment, skip ahead to creating a session.

1. **Get a free token**: Make a UUID for client identification. Send a POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` as the UUID. Grab `data.token` from the response — that's 100 free credits for 7 days.
2. **Open a session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer token auth and body `{"task_name":"project","language":"<detected>"}`. Hang on to the `session_id`.

No raw tokens or JSON get shown to the user.

# Fix Lighting and Add Glow Effects to Footage

Upload your video and describe the lighting change you want. Everything runs on cloud GPUs — nothing to install on your machine.

Real example: I had a dim interview clip shot in a basement. Typed "brighten the subject and add soft warm fill light" and 90 seconds later the MP4 looked like it was filmed in a proper studio. Default output is 1080p.

Worth noting — the AI handles color grading alongside lighting, so asking for "warm sunset tones" gives you both the light direction and the color shift.

## How Requests Get Routed

Depending on what you type, your message goes to different handlers.

| What you say | Where it goes | Skips SSE? |
|---|---|---|
| "export" / "download" / "send video" / "导出" | Export handler | Yes |
| "credits" / "balance" / "积分" / "余额" | Credit check | Yes |
| "status" / "show tracks" / "状态" | State query | Yes |
| "upload" / user attaches file / "上传" | Upload handler | Yes |
| Anything else (lighting, effects, color...) | Main SSE pipeline | No |

## Cloud Rendering Details

Your video gets uploaded to a GPU cluster for processing. The rendering queue re-encodes at 8Mbps for 1080p. Lighting adjustments are frame-accurate — no bleed between edited and unedited segments.

Every API call needs these headers: `Authorization: Bearer <NEMO_TOKEN>` plus attribution headers `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Without them, export returns a 402 error.

Attribution values come from this file's YAML block: `X-Skill-Source` = `magic-light-ai`, `X-Skill-Version` from the `version` field, `X-Skill-Platform` from install path (`~/.clawhub/` = `clawhub`, `~/.cursor/skills/` = `cursor`, else `unknown`).

**Base URL**: `https://mega-api-prod.nemovideo.ai`

**Start session**: POST `/api/tasks/me/with-session/nemo_agent` with `{"task_name":"project","language":"<lang>"}`. Returns `task_id` and `session_id`.

**Send message (SSE)**: POST `/run_sse` with body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` and header `Accept: text/event-stream`. Timeout cap is 15 minutes.

**Upload file**: POST `/api/upload-video/nemo_agent/me/<sid>` — either multipart with `-F "files=@/path"` or JSON `{"urls":["<url>"],"source_type":"url"}`.

**Check credits**: GET `/api/credits/balance/simple` — fields: `available`, `frozen`, `total`.

**Get session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — look at `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`.

**Export video** (no credit cost): POST `/api/render/proxy/lambda` with `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Then poll GET `/api/render/proxy/lambda/<id>` every 30 seconds until `status` is `completed`. Download from `output.url`.

Accepted file types: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### What Errors Mean

| Code | Problem | What to do |
|---|---|---|
| 0 | All good | Keep going |
| 1001 | Token expired or bad | Get a fresh token from /api/auth/anonymous-token |
| 1002 | Session gone | Start a new session |
| 2001 | Out of credits | Anonymous users: show signup link with ?bind=<id>. Others: top up |
| 4001 | Wrong file type | List the accepted formats |
| 4002 | File too big | Tell them to trim or compress first |
| 400 | No X-Client-Id header | Generate one and resend |
| 402 | Export blocked on free tier | Not a credits problem — need to register or upgrade |
| 429 | Too many requests | Wait 30 seconds, try once more |

### Translating Backend GUI Instructions

The backend was built for a visual editor, so it sometimes refers to buttons and panels. Translate them:

| Backend says | What you do instead |
|---|---|
| "click [button]" or "点击" | Run the matching API call |
| "open [panel]" or "打开" | Fetch session state |
| "drag/drop" or "拖拽" | Send an edit command through SSE |
| "preview in timeline" | Print a track summary |
| "Export button" or "导出" | Run the export flow |

### SSE Stream Behavior

Text responses go to the user after GUI translation. Tool calls are internal only. Heartbeats and blank `data:` lines mean work is in progress — say "Still working on it..." every 2 minutes or so.

Around 30% of edits close the stream with no text output. If that happens, check `/api/state` to verify the edit landed, then summarize what changed.

**Draft structure shorthand**: `t` = tracks, `tt` = track type (0 = video, 1 = audio, 7 = text), `sg` = segments, `d` = duration in ms, `m` = metadata.

Track summary format:
```
Timeline (3 tracks): 1. Video: sunset beach (0-15s) 2. Audio: ambient waves (0-15s, 40%) 3. Text: "Golden Hour" (2-5s)
```

## Tips and Tricks

Be specific about what you want. "Fix the lighting" is okay but "add warm fill light from the left, keep shadows soft" gets much better results.

You can combine lighting with other edits in a single request — the backend handles multi-step operations.

Max upload is 500MB. Stick with MP4 or MOV for the smoothest experience. Output is always MP4.

## Quick Start

1. Upload your footage (drag and drop into the chat)
2. Describe the lighting: "make it look like golden hour with soft shadows"
3. Wait about 60-120 seconds
4. Download the finished MP4

No account needed for your first 100 credits. Works with MP4, MOV, AVI, WebM.
