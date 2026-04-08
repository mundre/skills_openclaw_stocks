---
name: ai-image-generator-free
version: "1.0.0"
displayName: "AI Image Generator Free — Create Stunning Visuals From Text Instantly"
description: >
  Tired of paying steep subscription fees just to bring a creative idea to life visually? The ai-image-generator-free skill lets anyone create high-quality, original images simply by describing what they want in plain text. Whether you're a blogger, social media creator, small business owner, or hobbyist, this tool removes the cost barrier entirely. Type a scene, a concept, or a mood — and watch it become a real image in seconds. No design skills needed, no software to install.
metadata: {"openclaw": {"emoji": "🎨", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to your free AI image studio — describe any scene, character, or concept and I'll generate a unique image for you instantly. Ready to create something? Just tell me what you want to see!

**Try saying:**
- "Generate a neon cyberpunk city scene"
- "Create a cute animal in watercolor style"
- "Make a product background for skincare"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Words Into Vivid Images — No Cost, No Limits

Creating original visuals used to mean hiring a designer, purchasing stock photos, or spending hours in complex software. The AI Image Generator Free skill changes that completely. By simply describing what you want — a sunset over a neon city, a cartoon dog wearing a chef's hat, or a minimalist product background — you get a unique, ready-to-use image in moments.

This skill is built for people who have ideas but not necessarily the tools or budget to execute them. Content creators can produce thumbnail art, marketers can prototype campaign visuals, and writers can generate cover concepts without ever opening a design app. The output isn't templated or recycled — every image is generated fresh from your description.

Whether you need one image or dozens, the process stays the same: describe it, generate it, use it. No paywalls, no watermarks, no creative compromise. This is visual storytelling made accessible to everyone.

## Prompt Routing and Request Handling

Each text prompt you submit is parsed for style tokens, subject descriptors, and resolution parameters before being dispatched to the appropriate diffusion model endpoint.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

AI Image Generator Free routes your generation requests through a distributed cloud inference backend, applying latent diffusion processing to convert your text prompt into a high-fidelity image. Model weights, CLIP encoding, and noise scheduling all run server-side, so no local GPU is required.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-image-generator-free`
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

## Common Workflows

Most users come to the AI Image Generator Free skill with one of a few common needs. Social media creators use it to produce eye-catching post visuals or thumbnail backgrounds without relying on stock photo sites. Small business owners generate product mockup backgrounds, promotional banners, or logo concept art on the fly.

Bloggers and writers use it to bring article headers and chapter illustrations to life — especially useful when the topic is abstract or niche and stock photos simply don't exist. Educators and presenters generate custom diagrams, metaphor visuals, or scene illustrations that make their content more engaging.

The key to great results is specificity in your prompt. Instead of 'a forest,' try 'a misty pine forest at dawn with golden light filtering through the trees and a dirt path leading into the distance.' The more vivid your description, the more accurate and compelling the generated image will be.

## Quick Start Guide

Getting your first image is straightforward. Start by thinking about the core subject — what is the main thing or scene you want to see? Then layer in details: the setting, the lighting, the style (photorealistic, cartoon, oil painting, flat design), and any mood or color palette you have in mind.

For example, instead of typing 'a dog,' try 'a golden retriever puppy sitting in a sunlit meadow, soft focus background, warm tones, photorealistic style.' Submit that as your prompt and the skill will return a generated image matching your description.

If the first result isn't quite right, refine your prompt. Add or remove adjectives, shift the style, or change the lighting description. Iteration is fast and free, so don't hesitate to experiment. You can also ask for variations — 'same scene but at night' or 'same subject in a cartoon style' — to explore different creative directions quickly.
