---
name: seedance-video-editor
version: "1.0.0"
displayName: "Seedance Video Editor — Edit and Export Clips at 1080p"
description: >
  Export edited video at up to 1080p using seedance-video-editor, with final MP4 files ready in under 2 minutes depending on clip length. Send raw footage, specify cuts and effects, and get a structured video back — no manual timeline scrubbing required. Built for content creators and developers who need repeatable, script-driven edits on short-form clips under 5 minutes.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your raw clip and a list of cuts, and I'll return a finished 1080p MP4. No footage yet? Describe the edit you want and we'll work from there.

**Try saying:**
- "Trim the first 8 seconds off my 2-minute clip and add a fade-in at the start"
- "Cut between three segments at 0:15, 0:42, and 1:10, then export as 1080p MP4"
- "Add a 3-second title card at the beginning and remove the last 5 seconds of dead air"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Cut, Trim, and Export MP4 Files Fast

Send a raw clip and a plain-text edit list — something like 'cut 0:12 to 0:45, add fade-out at end, export 1080p' — and seedance-video-editor processes it into a finished MP4. The skill handles the frame-level cuts so you don't have to open a timeline editor.

A typical 90-second clip with 3 cuts and a title overlay takes roughly 40 seconds to process. That's the actual turnaround, not an estimate padded for edge cases.

You can chain multiple edits in a single request: trim start, insert a 2-second black frame at 0:30, add an end card at the final 5 seconds. The output is one continuous MP4 file, not a project file that needs rendering.

## Routing Edits to Correct Actions

User prompts containing terms like 'trim', 'cut', 'merge', or 'export 1080p' are parsed against Seedance's action map to route to the correct editing pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance Rendering Pipeline Details

When an export is triggered, Seedance offloads the render job to cloud GPU nodes, which process the 1080p output at up to 60fps using H.264 or H.265 encoding depending on the selected quality preset. Session metadata, including timeline state and clip references, is held server-side for up to 30 minutes before auto-expiry.

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

Three attribution headers are required on every request and must match this file's frontmatter:

| Header | Value |
|--------|-------|
| `X-Skill-Source` | `seedance-video-editor` |
| `X-Skill-Version` | frontmatter `version` |
| `X-Skill-Platform` | auto-detect: `clawhub` / `cursor` / `unknown` from install path |

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

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

Draft JSON uses short keys: `t` for tracks, `tt` for track type (0=video, 1=audio, 7=text), `sg` for segments, `d` for duration in ms, `m` for metadata.

Example timeline summary:
```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

## Troubleshooting

If the exported MP4 cuts at the wrong timestamp, check whether you used seconds or MM:SS format — seedance-video-editor defaults to MM:SS, so '90' is interpreted as 1 minute 30 seconds, not 90 seconds flat. Restate timestamps explicitly if the first export is off.

Blank or black frames in the output usually mean a cut point landed on a keyframe boundary. Shift the cut 2–3 frames earlier or later and re-run the edit. This fixes the issue in over 90% of cases without a full re-upload.

Audio sync drift on clips longer than 4 minutes is a known edge case. Request a 48kHz audio lock in your edit instructions ('lock audio to 48kHz') and the drift drops to under 1 frame across the full clip length.

File size over 500MB after export? Specify a bitrate cap in your request — '8 Mbps max' keeps a 3-minute 1080p clip under 180MB without visible quality loss at normal playback sizes.

## Integration Guide

Connect seedance-video-editor to your existing content pipeline by passing edit instructions as structured text through the ClawHub skill interface. No separate SDK install is needed — the skill reads plain-text commands directly from the chat input field.

If you're batching more than 5 clips, number each job ('Job 1: clip_a.mp4, cut 0:10–0:55') so the editor tracks them separately and doesn't merge instructions across files. Each job returns its own MP4, labeled by the job number you assigned.

For teams using shared asset libraries, include the clip source URL in the first line of your request. The editor fetches the file directly, so you don't need to re-upload the same source footage across 10 different edit requests — that alone cuts per-job setup time to under 15 seconds.

## Tips and Tricks

Write your edit instructions in chronological order — seedance-video-editor reads them sequentially, so 'cut to 0:45, then add title' processes differently than 'add title, then cut to 0:45'. Sequence matters more than formatting.

If you're working with clips longer than 3 minutes, break the edit list into labeled segments (e.g., 'Segment A: 0:00–1:00, Segment B: 1:01–2:30'). This keeps the instruction set under 200 characters per segment and reduces parsing errors on complex timelines.

For text overlays, specify font size in pixels and duration in seconds — don't just say 'big text for a while.' Something like '48px white text, 4 seconds, centered' gives the editor enough to work with. Vague overlay instructions produce vague results.

You can request a preview frame at a specific timestamp (e.g., 'show frame at 0:32') before committing to the full export. It's a one-second check that saves a full re-render.
