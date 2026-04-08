---
name: image-to-video-generator-ai-free
version: "1.0.0"
displayName: "Image to Video Generator AI Free — Animate Still Photos Into Dynamic Videos Instantly"
description: >
  Tired of static images that fail to capture attention in a scroll-happy world? The image-to-video-generator-ai-free skill transforms your still photos into fluid, engaging video clips without any cost or complex software. Upload a single image or a series of photos and watch them come alive with motion, transitions, and cinematic effects. Perfect for content creators, marketers, small business owners, and social media enthusiasts who need eye-catching video content fast.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome! I can turn your still photos into captivating videos using the image-to-video-generator-ai-free skill — no editing skills or software needed. Upload your image and tell me the style or mood you're going for, and let's create something worth watching!

**Try saying:**
- "I have a product photo of my handmade candle — can you turn it into a short atmospheric video with slow zoom and warm lighting effects for Instagram?"
- "I want to create a memorial slideshow video from 8 family photos with gentle transitions and a soft, emotional feel. Can you help me set that up?"
- "Can you animate my landscape photo of a mountain sunset into a cinematic video clip with a slow pan effect and dramatic music-ready pacing?"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn Your Photos Into Stunning Videos for Free

Still images tell a story, but videos make people stop and watch. This skill bridges the gap between your photo library and compelling video content — no editing experience required. Whether you have a single product shot, a portrait, a landscape, or a collection of event photos, this tool breathes motion into them and delivers a polished video ready to share.

Using advanced AI animation techniques, the image-to-video-generator-ai-free skill applies smooth movement, zoom effects, parallax depth, and stylistic transitions to your images. You can specify the mood, pacing, and style you want — from a slow, cinematic drift to an energetic slideshow with punchy cuts. The result feels intentional and professionally crafted, not like an auto-generated slideshow from a decade-old app.

This is built for real use cases: launching a product on Instagram, creating a memorial video, animating a logo for a YouTube intro, or turning travel photos into a shareable reel. You describe what you want, upload your image or images, and the skill handles the rest — completely free.

## Routing Your Animation Requests

When you submit a still photo, the skill parses your motion prompt and frame parameters before dispatching the job to the appropriate AI video synthesis pipeline based on resolution, duration, and animation style.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

The backend leverages a distributed diffusion-based video generation API that processes keyframe interpolation and temporal coherence rendering entirely in the cloud, so no local GPU is required. Requests are queued, encoded, and returned as a streamable video file or downloadable MP4 once the inference pass completes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `image-to-video-generator-ai-free`
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

## Performance Notes

The image-to-video-generator-ai-free skill performs best with portrait or landscape-oriented images in standard aspect ratios (16:9, 9:16, or 1:1). Unusual crops or extreme panoramic images may require manual aspect ratio guidance when you submit your request.

Animation complexity affects processing time. A simple Ken Burns zoom on a single image is near-instant, while a multi-image sequence with layered transitions and depth effects takes longer to render. For time-sensitive projects, mention your deadline so the skill can prioritize effect simplicity or suggest pre-optimized templates.

Images with busy backgrounds or low subject contrast may produce less precise motion effects, since AI depth estimation relies on clear foreground-background separation. For portraits and product shots, this skill performs exceptionally well. For abstract or highly textured images, expect more stylized, painterly motion rather than realistic parallax.

## Common Workflows

The most common workflow is single-image animation: you upload one photo, describe the desired motion (zoom, drift, parallax), specify the output length (typically 3–15 seconds), and receive a video clip ready for social media or presentation use.

A second popular workflow is photo slideshow creation. Users submit 5–20 images with a theme (wedding, travel, product launch) and request a sequenced video with timed transitions, consistent styling, and an appropriate pacing for the platform. This is especially useful for Instagram carousels converted to Reels or event recap videos.

A third workflow involves logo and graphic animation — taking a static brand asset and adding entrance motion, subtle looping animation, or a cinematic reveal effect. This turns a flat PNG into a dynamic intro bumper or branded social post. Simply describe the brand feel and the type of motion you want, and the skill handles the animation logic from there.

## Best Practices for Image-to-Video Generation

For the best results with the image-to-video-generator-ai-free skill, start with high-resolution images — ideally 1080p or higher. Low-resolution or heavily compressed photos will produce blurry or pixelated video output, especially when zoom or pan effects are applied.

When describing the effect you want, be specific about motion style. 'Slow zoom in on the subject' produces a very different result than 'parallax depth effect with background separation.' The more detail you provide about mood, pacing, and intended platform (Instagram Reels, YouTube, TikTok), the more targeted the output will be.

For multi-image slideshows, keep a consistent visual theme across your photos — similar lighting, color palette, or subject matter. Wildly mismatched images create jarring transitions even with the smoothest AI effects. Grouping photos by scene or color tone before submitting will give your final video a cohesive, professional look.
