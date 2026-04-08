---
name: bytedance-seedance
version: "1.0.0"
displayName: "ByteDance Seedance — AI Video Generation Powered by Seedance 1.0"
description: >
  Tell me what you want to bring to life, and bytedance-seedance will turn your ideas into stunning AI-generated videos. Built on ByteDance's Seedance 1.0 model, this skill generates high-quality video content from text prompts or image inputs — with cinematic motion, consistent characters, and rich visual detail. Ideal for creators, marketers, and studios who need fast, expressive video without a camera or crew.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to the Seedance video generator — describe the scene, story, or concept you have in mind, and I'll produce a high-quality AI video using ByteDance's Seedance 1.0 model. Tell me what you're envisioning and let's start generating.

**Try saying:**
- "Generate a cinematic nature scene"
- "Create product video from description"
- "Animate this image into video"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# From Prompt to Video — Seedance Makes It Happen

ByteDance's Seedance 1.0 is one of the most capable video generation models available today, and this skill puts it directly in your workflow. Whether you're imagining a sweeping landscape, a product in motion, or a character walking through a scene, Seedance translates your words into fluid, high-fidelity video clips.

Unlike static image generation, Seedance understands temporal motion — meaning objects move naturally, lighting shifts realistically, and scenes feel alive rather than frozen. You can guide the output with detailed descriptions, set the mood, define the camera angle, or let the model surprise you with its own cinematic interpretation.

This skill is built for content creators, brand teams, indie filmmakers, game developers, and anyone who needs compelling video content fast. No studio, no equipment, no lengthy post-production — just a prompt and a result you can actually use.

## Routing Your Seedance Requests

When you submit a prompt, ClawHub parses your intent and routes it directly to the Seedance 1.0 inference pipeline, selecting the appropriate generation mode — text-to-video or image-to-video — based on your input.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance API Backend Reference

Seedance 1.0 runs on ByteDance's distributed cloud infrastructure, handling diffusion-based video synthesis at scale with low-latency frame rendering. Your generation jobs are queued, processed, and returned as downloadable video assets without any local compute required.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `bytedance-seedance`
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

## Best Practices for Seedance Video Generation

Getting the most out of bytedance-seedance comes down to how you write your prompts. Be specific about camera movement — terms like 'slow dolly in,' 'overhead drone shot,' or 'handheld close-up' give the model clear directorial cues that dramatically improve output quality.

Describe lighting and atmosphere explicitly. Seedance responds well to phrases like 'golden hour backlight,' 'foggy diffused daylight,' or 'hard neon contrast at night.' These details anchor the visual tone and help avoid generic-looking results.

Keep your subject action clear and grounded. Seedance handles motion best when the movement is physically plausible — a character walking, an object spinning, water flowing. Highly abstract or contradictory motion descriptions can reduce coherence. Start with one focused subject and build complexity from there once you see the baseline output.

## Use Cases — What You Can Build with Seedance

ByteDance Seedance is versatile enough to serve a wide range of real-world production needs. Marketing teams use it to generate concept videos for campaigns before committing to live shoots — testing visual directions quickly and cheaply. Social media creators use it to produce scroll-stopping clips for platforms like TikTok, Instagram Reels, and YouTube Shorts without needing filming equipment.

Game developers and concept artists use Seedance to visualize environments, characters in motion, and cinematic sequences during early production stages. Educators and trainers use it to create illustrative video content that explains processes or events that would be impossible or expensive to film.

Filmmakers and directors use it for pre-visualization — generating rough scene drafts to share with crews and clients before production begins. Whatever your use case, Seedance compresses the gap between imagination and a shareable video asset.
