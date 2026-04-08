---
name: image-to-video-ai-generator-free
version: "1.0.0"
displayName: "Image to Video AI Generator Free — Animate Still Photos into Dynamic Videos"
description: >
  Tell me what you need and I'll help you turn static images into captivating videos without spending a dime. This image-to-video-ai-generator-free skill walks you through the fastest free tools, prompt strategies, and workflows to animate photos, create slideshows with motion effects, or produce cinematic clips from a single still. Whether you're a content creator, small business owner, or social media enthusiast, get frame-by-frame guidance tailored to your project.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Drop your image or describe your photo and I'll tell you exactly which free AI tool to use and what prompt to write to generate a compelling video from it. No image yet? Just describe the scene and I'll guide you from scratch.

**Try saying:**
- "I have a product photo of a sneaker on a white background — what's the best free AI tool to animate it with subtle motion for an Instagram ad?"
- "I want to turn 10 vacation photos into a 30-second video with smooth transitions and background music using only free tools. How do I do that?"
- "I uploaded my portrait to Runway but the motion looks unnatural and glitchy — what prompt changes or settings should I try to fix it?"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# From Still Photo to Moving Story — For Free

Most people assume turning an image into a video requires expensive software or a professional editor. That assumption is outdated. A new wave of free AI tools can take a single photograph — a portrait, a product shot, a landscape — and breathe life into it with realistic motion, cinematic panning, or stylized animation.

This skill is your hands-on guide through that process. Instead of wading through tutorials scattered across the internet, you get a focused assistant that helps you choose the right free platform for your specific image type, craft the text prompts that produce the best motion results, and troubleshoot when outputs don't look the way you imagined.

Whether you want a looping background video for your website, an animated post for Instagram Reels, or a short cinematic clip from a family photo, this skill covers the full journey — from uploading your image to exporting a shareable video file — using only tools that cost nothing to start.

## Routing Animate Requests Intelligently

When you submit a still photo for animation, ClawHub parses your motion prompt, frame rate preference, and output duration to route your request to the optimal image-to-video inference pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

The free image-to-video backend leverages diffusion-based temporal synthesis models hosted on distributed GPU clusters, converting static frames into fluid motion sequences without local processing overhead. Each API call passes your source image alongside motion vectors and interpolation parameters to generate smooth keyframe transitions in the cloud.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `image-to-video-ai-generator-free`
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

## Integration Guide

Getting started with free image-to-video AI tools is straightforward once you know which platforms accept direct image uploads versus those that work from text prompts alone. Tools like Runway Gen-2, Kling AI (free tier), and Pika Labs all accept still images as a starting point and offer free credits or a freemium model to generate short video clips.

For workflow integration, you can export the generated video as an MP4 and drop it directly into tools like CapCut, DaVinci Resolve (free), or Canva to add text overlays, music, or color grading. If you're building a content pipeline, pairing an image-to-video generator with a free scheduler like Buffer lets you automate posting animated content to social platforms.

Always check resolution limits on free tiers — most cap exports at 720p. If you need 1080p, some tools offer a one-time free upscale or integrate with free upscalers like Topaz Gigapixel's trial version to boost quality before publishing.

## Common Workflows

The most popular workflow is the single-image cinematic pan: upload a wide landscape or architectural photo, write a prompt like 'slow dolly forward with gentle camera drift,' and export a 4-second loop. This works exceptionally well for website hero backgrounds and YouTube intro cards.

For e-commerce, a product-spin workflow is highly effective — upload a flat-lay product image, prompt the AI to rotate or zoom in gradually, and you get a dynamic product clip without a photoshoot. Combine several of these into one video using a free editor to create a full product showcase reel.

Portrait animation is another common use case. Tools like D-ID and HeyGen's free tier can take a headshot and add realistic facial movement or even lip-sync to an audio clip. This is popular for creating spokesperson videos from a single photo.

Finally, the photo slideshow with AI transitions workflow — importing a series of images into Pika or a similar tool and generating motion between each frame — produces polished results that rival paid video editors, entirely for free.
