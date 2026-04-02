---
name: image-to-video-generator-free
version: "1.0.0"
displayName: "Image to Video Generator Free — Animate Your Photos Into Stunning Videos"
description: >
  Tired of static photos that fail to capture attention on social media or presentations? The image-to-video-generator-free skill transforms your still images into dynamic, engaging videos without any cost or complex software. Using this skill, you can breathe life into product photos, travel snapshots, or artwork by generating smooth animated video sequences. Whether you're a content creator, small business owner, or educator, image-to-video-generator-free gives everyone the power to produce scroll-stopping video content from photos they already own.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! Ready to turn your photos into eye-catching videos for free? Share your image and tell me the style or motion effect you'd like, and I'll generate your video right away!

**Try saying:**
- "Animate this product photo with a slow zoom-in effect so I can post it as a video ad on Instagram"
- "Create a slideshow video from these 5 travel photos with smooth crossfade transitions and a cinematic feel"
- "Turn my portrait photo into a short looping video with a subtle floating motion effect"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/image-to-video-generator-free/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Still Photos Into Captivating Videos Instantly

Most people have folders full of great photos that never get the attention they deserve simply because static images scroll by unnoticed. Video content consistently outperforms photos across every major platform — but producing video traditionally requires expensive tools, editing skills, and hours of work. That gap is exactly what this skill is built to close.

With the image-to-video-generator-free skill, you upload one or more images and describe the kind of video motion or style you want, and the skill handles the creative heavy lifting. Whether you want a gentle Ken Burns pan across a landscape photo, a dramatic zoom into a product shot, or a slideshow with smooth transitions set to a mood, the skill generates video output tailored to your request.

This skill is ideal for social media managers building reels, educators creating visual lesson content, e-commerce sellers showcasing products, and anyone who wants to repurpose existing photo libraries into fresh video content — all without spending a dollar or learning a new editing application.

## Routing Your Animation Requests

When you submit a photo for animation, your request is parsed for motion style, duration, and output resolution before being dispatched to the appropriate rendering pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

The free image-to-video backend leverages distributed GPU clusters to handle frame interpolation, motion synthesis, and video encoding entirely in the cloud — no local processing required. Rendered output is temporarily cached on the server and delivered as a streamable or downloadable video file upon job completion.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `image-to-video-generator-free`
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

## Troubleshooting Common Issues

If your generated video looks blurry or pixelated, the most likely cause is a low-resolution source image. Try uploading the highest resolution version of your photo available — at least 1080px on the shortest side is recommended for clean video output.

If the motion effect doesn't match what you described, try rephrasing your prompt with more specific directional language. Instead of 'make it move,' say 'slowly pan left to right across the full width of the image over 5 seconds.' Precision in your description directly improves result accuracy.

For multi-image slideshows, if transitions feel abrupt or the timing seems off, specify the duration you want each image to display and the transition style explicitly (e.g., 'show each photo for 3 seconds with a 1-second crossfade'). If a generated video file won't play on your device, request a different output format such as MP4 H.264, which has the broadest compatibility across platforms and devices.

## Use Cases for Image to Video Generator Free

The image-to-video-generator-free skill fits naturally into a wide range of real-world workflows. Social media creators use it to convert product or lifestyle photos into Reels, TikToks, and YouTube Shorts without needing a video camera or editing suite. Small business owners animate product images to create low-cost video advertisements that perform better than static posts.

Educators and trainers find it valuable for building visual presentations where photos need to feel dynamic rather than flat — adding motion to diagrams, historical images, or course thumbnails. Event photographers turn wedding or birthday galleries into shareable video highlights for clients.

Content marketers repurpose blog post images into teaser videos for newsletters and social campaigns. Even personal users create memorable animated keepsakes from family photos. The common thread is simple: you already have the images — this skill turns them into something people actually watch.

## Quick Start Guide

Getting started with image-to-video-generator-free takes less than two minutes. First, gather the image or images you want to animate — JPEG and PNG formats work best, and higher resolution photos produce sharper video output.

Next, describe the video style you want in plain language. Be specific: mention the type of motion (zoom, pan, parallax, fade), the mood (cinematic, energetic, calm), the intended platform (Instagram Reel, YouTube Short, presentation), and whether you want a single animated image or a multi-image slideshow. The more detail you provide, the closer the output will match your vision.

Once you submit your request, the skill processes your image and returns the generated video file or a preview link. You can then request adjustments — slower motion, different transitions, a different aspect ratio — in a follow-up message. Iteration is fast, so don't hesitate to refine until the video feels exactly right for your use case.
