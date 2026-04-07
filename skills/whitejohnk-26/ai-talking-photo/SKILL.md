---
name: ai-talking-photo
version: "1.0.0"
displayName: "AI Talking Photo — Animate Still Images Into Lifelike Speaking Portraits"
description: >
  Bring any still photo to life with ai-talking-photo, the skill that syncs facial animation to audio and makes portraits speak, sing, or narrate. Upload a face image and a voice clip — or just a script — and watch the photo animate with natural lip movements, blinking, and subtle expressions. Perfect for memorial videos, social content creators, educators, marketers, and anyone who wants to tell a story through a face rather than a talking-head video.
metadata: {"openclaw": {"emoji": "🗣️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome! With AI Talking Photo, you can turn any portrait into a speaking, animated video in moments. Upload your photo and audio clip (or tell me what you'd like the subject to say) and let's bring it to life!

**Try saying:**
- "Animate this portrait with my audio"
- "Make my headshot say this script"
- "Create talking photo for social reel"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Make Any Photo Speak With One Upload

Static photos hold stories that never get told. AI Talking Photo changes that by turning a single still image into an animated, speaking portrait — no camera, no studio, no video shoot required. Whether it's a historical figure, a product mascot, a family member, or your own headshot, this skill breathes voice and movement into the image in seconds.

The process is straightforward: provide a clear face photo and either an audio file or a text script you want spoken. The skill analyzes the facial geometry, maps lip movements to the audio waveform, and generates a short video where the subject appears to genuinely speak. Subtle head motion, eye blinks, and micro-expressions are layered in to avoid the uncanny stiffness of early deepfake tools.

Creators use this for memorial tribute videos, branded spokesperson content, educational history lessons, social media reels, and interactive storytelling. If you can photograph a face, you can give it a voice — that's the core promise of AI Talking Photo.

## Routing Animate Portrait Requests

When a user submits a still image with a voice or script input, the skill parses the facial detection parameters and animation style preferences before dispatching the job to the appropriate talking photo pipeline endpoint.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Talking Photo API Reference

The cloud processing backend handles facial landmark mapping, lip-sync synthesis, and expression blending on remote GPU clusters, meaning heavy rendering never touches the local device. Completed animated portrait outputs are returned as video streams or downloadable clips once the synthesis job finalizes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-talking-photo`
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

## Best Practices

The quality of your output is almost entirely determined by the quality of your input photo. Avoid images with heavy filters, strong side-lighting, or partial face occlusion — these confuse the facial landmark detection and produce jittery or misaligned lip movements. A neutral expression in the source photo gives the animation engine the most flexibility to map a wide range of speech sounds accurately.

Keep audio clips clean and free of background music during the lip-sync generation phase. If your final video needs music, add it as a separate layer after the talking photo is rendered. This prevents the model from misreading musical frequencies as speech phonemes.

For emotional impact — especially in memorial or tribute videos — choose audio that is paced naturally and not too fast. Rapid speech compresses lip movements and reduces the realism of the animation. A speaking rate of 120–150 words per minute tends to yield the most convincing results. Finally, always review the generated video before publishing; small manual trims at the start and end of the clip can remove any initialization frames where the face hasn't yet settled into the animation.

## Integration Guide

Getting started with AI Talking Photo requires just two inputs: a face image and an audio source. For best results, use a front-facing photo where the subject's mouth and eyes are clearly visible, unobstructed by hands, masks, or extreme angles. JPEG and PNG formats work well; aim for at least 512×512 pixels to preserve animation quality.

For audio, you can supply an MP3, WAV, or M4A file up to 60 seconds, or simply paste a text script and select a voice style — the skill will synthesize the speech internally before animating the photo. If you're embedding the output in a website or presentation, request the export in MP4 format with a transparent-background option for overlay use.

When building workflows — such as auto-generating spokesperson videos from a CMS or producing personalized video messages at scale — pass the image URL and script text as variables. The skill returns a video URL or file you can route directly into your delivery pipeline, email platform, or social scheduler.
