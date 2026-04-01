---
name: vheer
version: "1.0.0"
displayName: "Vheer Video Intelligence — Analyze, Understand & Extract Insights from Any Video"
description: >
  Tell me what you need and vheer will dig into your video to find exactly that. Vheer is a smart video analysis skill that watches, interprets, and surfaces meaningful information from your footage — whether you're reviewing a recorded meeting, studying a product demo, or breaking down a tutorial. It handles mp4, mov, avi, webm, and mkv files. Ask questions, request summaries, pull out key moments, or get detailed scene-by-scene breakdowns. Built for content creators, researchers, educators, and business professionals who need more than just a transcript.
metadata: {"openclaw": {"emoji": "🎯", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm vheer, your video intelligence assistant — ready to analyze your footage and answer any question about what's happening inside it. Upload your video and tell me what you'd like to know.

**Try saying:**
- "Summarize the main points covered in this recorded team meeting"
- "What happens between the 3-minute and 7-minute mark in this tutorial video?"
- "Extract every action item or decision mentioned throughout this video"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# See What's Really Inside Your Video

Most video tools make you watch every second to find what you need. Vheer flips that entirely. Drop in your video and ask it anything — what topics were covered, what happened at a specific timestamp, who said what, or what the key takeaways are. Vheer reads your footage the way a sharp analyst would: attentively, contextually, and with an eye for what actually matters.

This skill shines in situations where time is short and content is dense. Imagine uploading an hour-long webinar and instantly knowing the five most important moments, or reviewing a product walkthrough and getting a plain-English explanation of every feature demonstrated. Vheer connects the dots between visuals, motion, and spoken content to give you a complete picture.

Whether you're a journalist reviewing interview footage, a team lead recapping a recorded standup, or a student analyzing a lecture, vheer adapts to your workflow. You describe what you're looking for, and vheer delivers — no scrubbing, no rewatching, no wasted time.

## How Vheer Routes Your Requests

Every prompt you send is interpreted by Vheer's intent engine, which maps your request to the appropriate video analysis action — whether that's transcription, scene breakdown, sentiment detection, or deep content extraction.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

Vheer runs on the NemoVideo intelligence backend, which processes video frames, audio streams, and metadata in parallel to deliver fast, structured insights. All analysis calls, session handling, and credit consumption flow through NemoVideo's API layer.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `vheer`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=vheer&skill_version=1.0.0&skill_source=<platform>`

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
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Quick Start Guide

Getting started with vheer takes less than a minute. Upload your video file in any supported format — mp4, mov, avi, webm, or mkv — directly into the chat window. Once your video is loaded, type your first question or request in plain language. There's no special syntax required.

Not sure where to begin? Try asking vheer for a summary first. From there, you can ask it to identify key speakers, list topics discussed, highlight notable moments, or explain specific scenes in detail. Each response builds on the last, so your conversation with vheer becomes progressively more useful as you explore.

If you have a specific output in mind — a bulleted recap, a timestamped breakdown, a quote pulled verbatim — just say so. Vheer adjusts its format to match what you actually need, making it easy to take its output and drop it straight into your notes, reports, or workflows.

## Best Practices

Upload the clearest version of your video available. Vheer performs strongest with clean audio and stable footage — heavily compressed files or recordings with significant background noise may affect the depth of analysis.

Be explicit about your goal upfront. If you're preparing a report, say so. If you need timestamps, ask for them directly. Vheer calibrates its output format based on how you frame your request, so a little context about your end use goes a long way.

When working with technical or domain-specific content — medical lectures, legal depositions, engineering walkthroughs — include a brief note about the subject area. This helps vheer prioritize the right terminology and focus on the details that matter most to your field.

Supported formats include mp4, mov, avi, webm, and mkv. Keep file quality consistent and avoid videos with heavy post-processing artifacts for the most reliable results.

## Tips and Tricks

Vheer responds best when your questions are specific. Instead of asking 'what is this video about,' try 'what problem does the speaker say this product solves?' The more targeted your prompt, the sharper and more useful the response.

You can ask follow-up questions after an initial analysis — vheer retains context about the video you uploaded, so you don't need to re-explain anything. Use this to drill deeper: start with a summary, then ask about a particular segment, then request a quote or moment that supports a point.

For longer videos, consider breaking your inquiry into stages. Ask for a high-level overview first, then zoom into specific chapters or topics. This layered approach consistently produces the most actionable insights from vheer.
