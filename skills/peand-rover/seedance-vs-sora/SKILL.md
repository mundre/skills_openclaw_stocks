---
name: seedance-vs-sora
version: "1.0.0"
displayName: "Seedance vs Sora Comparison — Find the Right AI Video Generator for Your Project"
description: >
  Cut through the hype and get a clear, side-by-side breakdown of Seedance and Sora for your specific creative needs. This seedance-vs-sora skill analyzes motion quality, prompt fidelity, output resolution, generation speed, and pricing so you can make an informed choice. Whether you're a filmmaker, marketer, or content creator, stop guessing which tool fits your workflow.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome! Whether you're deciding between Seedance and Sora for a campaign, a short film, or rapid content production, this skill gives you a direct, honest comparison. Tell me what you're working on and I'll help you pick the right tool.

**Try saying:**
- "I need to generate 15-second product ads with consistent branding — which is better, Seedance or Sora?"
- "Compare how Seedance and Sora handle cinematic camera pans and realistic lighting for a short film I'm producing."
- "I have a limited budget and need fast turnaround on AI video clips for social media — break down the cost and speed differences between Seedance and Sora."

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Stop Guessing — Pick the Right AI Video Tool

Choosing between Seedance and Sora isn't just a spec sheet exercise — it's a decision that shapes your entire production pipeline. Seedance leans into fast, stylized motion with strong prompt adherence for short-form content, while Sora pushes cinematic realism and complex scene continuity for longer, narrative-driven clips. Both are powerful, but they shine in very different scenarios.

This skill walks you through the real differences that matter: how each model handles camera movement, lighting transitions, character consistency across frames, and the kinds of prompts each responds to best. You'll also get a clear picture of where each tool struggles — so you're not burned by unexpected outputs mid-project.

Whether you're producing social media ads, experimental short films, product demos, or AI-assisted storytelling, this comparison gives you a concrete recommendation based on your actual use case — not a generic pros-and-cons list.

## Routing Seedance and Sora Requests

When you submit a prompt, ClawHub detects whether you're targeting Seedance's motion-optimized pipeline or Sora's cinematic diffusion engine and routes your generation request to the appropriate model endpoint automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## API Backend Reference Guide

Both Seedance and Sora generations run through ClawHub's cloud inference layer, which handles frame scheduling, temporal consistency processing, and output rendering without requiring local GPU resources. Seedance calls hit ByteDance's video diffusion API while Sora requests are proxied through OpenAI's video generation endpoint, each with their own latency and credit cost profiles.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-vs-sora`
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

## Troubleshooting

If you're getting inconsistent character appearances across frames in Seedance, try anchoring your prompt with more explicit physical descriptors and reduce clip length to under 8 seconds. Seedance performs more reliably when prompts are dense with visual detail rather than abstract or narrative.

With Sora, common issues include slow queue times during peak usage and occasional over-smoothing of fast-motion sequences. If your Sora output looks too cinematic or 'floaty' for a fast-cut edit, try prompting with explicit motion speed cues like 'quick cut,' 'handheld,' or 'fast pan.'

For both tools, avoid ambiguous spatial language (e.g., 'nearby,' 'in the background') — replace with precise positional cues. If outputs from either model don't match your creative vision after two iterations, this skill can help you rewrite your prompt structure from scratch.

## Performance Notes

Seedance typically excels at generating stylized, high-motion clips in under 60 seconds, making it well-suited for rapid iteration on social content and music videos. Its prompt-to-motion mapping is tight for short durations (under 10 seconds), but longer sequences can show drift in subject consistency.

Sora, by contrast, handles extended scenes (10–20+ seconds) with stronger spatial and temporal coherence. Camera logic — things like smooth dollies, rack focus, and realistic depth — tends to hold up better in Sora outputs. However, generation times are longer and access has historically been more restricted.

For high-volume, fast-turnaround workflows, Seedance has an edge. For prestige projects where realism and scene complexity matter more than speed, Sora is the stronger choice. Benchmark your specific prompt types against both before committing to a pipeline.
