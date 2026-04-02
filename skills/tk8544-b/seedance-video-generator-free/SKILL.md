---
name: seedance-video-generator-free
version: "1.0.0"
displayName: "Seedance Video Generator Free — Create AI Videos From Text or Images"
description: >
  Drop an image or type a scene description and watch it transform into a smooth, dynamic video clip — no editing software, no subscriptions required. The seedance-video-generator-free skill taps into Seedance's powerful AI video model to animate stills, generate motion from prompts, and produce shareable clips in seconds. Built for creators, marketers, and storytellers who want cinematic results without the cost barrier.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to the Seedance Video Generator Free skill — your shortcut from idea to animated video clip in seconds! Drop an image or describe a scene you want to bring to life, and let's generate your video right now.

**Try saying:**
- "Animate my product photo now"
- "Generate a cinematic landscape clip"
- "Turn this image into video"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Words and Images Into Moving Video Instantly

The seedance-video-generator-free skill brings Seedance's AI video generation directly into your workflow — no accounts to juggle, no paywalls to hit. Whether you're starting from a single photograph or a written description of a scene, this skill converts your input into a fluid, realistic video clip that feels crafted rather than generated.

This is especially powerful for creators who need quick visual content without the overhead of traditional video production. Imagine animating a product photo for an ad, bringing a concept sketch to life for a pitch deck, or generating a dramatic cinematic scene from a one-line prompt. The skill handles motion, lighting transitions, and scene continuity automatically.

Designed for social media creators, indie filmmakers, small business owners, and curious experimenters, seedance-video-generator-free removes the friction between your idea and a finished video. You describe it, you get it — fast, free, and ready to share.

## Routing Text and Image Prompts

When you submit a request, ClawHub detects whether you're passing a raw text prompt or a reference image and routes it to the appropriate Seedance generation pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance Cloud API Reference

Seedance Video Generator Free processes all diffusion inference on remote cloud GPUs, meaning render jobs are queued, executed, and returned as downloadable video URLs without any local compute required. Generation latency depends on current queue depth and your selected resolution or motion intensity settings.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-video-generator-free`
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

If your generated video looks static or barely animated, the most common cause is a prompt that lacks motion cues. Add explicit action words — 'flowing,' 'rotating,' 'expanding,' 'flickering' — to give the model clear direction.

Images with very busy backgrounds or extreme close-ups sometimes confuse depth estimation, resulting in unnatural warping. Try cropping to a cleaner composition before uploading, or describe the subject more narrowly in your prompt.

If the output clips feel too short or cut off abruptly, specify a duration preference in your prompt (e.g., 'generate a 4-second clip'). While the free tier has generation limits, rephrasing your prompt and resubmitting usually resolves inconsistent outputs without needing to start over from scratch.

## Tips and Tricks

To get the most out of seedance-video-generator-free, be specific with your motion descriptions. Instead of saying 'make it move,' try 'slow zoom into the center with light flickering on the left.' The more directional detail you give, the more intentional the output feels.

When uploading images, high-contrast and well-lit photos produce noticeably smoother animations. Avoid heavily compressed or low-resolution images — the model reads pixel detail to infer depth and motion paths.

For text-only prompts, think in cinematic terms: camera angle, lighting mood, subject movement, and background activity. Phrases like 'handheld camera feel,' 'golden hour glow,' or 'slow-motion water splash' steer the output toward a specific visual style. Iterating with small prompt changes between runs is the fastest way to dial in exactly what you're after.

## Use Cases

The seedance-video-generator-free skill shines across a surprisingly wide range of real-world applications. E-commerce sellers use it to animate product images into attention-grabbing social clips without hiring a videographer. A static sneaker photo becomes a rotating showcase; a candle image blooms with flickering flame and drifting smoke.

Content creators on TikTok, Instagram Reels, and YouTube Shorts use it to produce scroll-stopping intros or B-roll from a single descriptive prompt — filling gaps in a production schedule without picking up a camera.

Educators and presenters use it to visualize abstract concepts: a prompt like 'cells dividing under a microscope with blue fluorescent glow' becomes an illustrative clip that no stock library would have. Game developers and concept artists use it to rapidly prototype environment moods before committing to full production assets.
