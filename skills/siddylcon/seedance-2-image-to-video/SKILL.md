---
name: seedance-2-image-to-video
version: "1.0.0"
displayName: "Seedance 2 Image to Video — Animate Still Photos Into Fluid AI Videos"
description: >
  Drop a still image and watch it breathe. Seedance-2-image-to-video transforms static photos, illustrations, and artwork into smooth, cinematic video clips using ByteDance's Seedance 2 model. Whether you're animating product shots, portraits, landscapes, or digital art, this skill brings motion to moments that were never meant to stay still. Built for creators, marketers, and storytellers who want fast, high-quality results.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome! I can transform any still image into a smooth, cinematic video clip using Seedance 2 — just share your photo and tell me how you'd like it to move.

**Try saying:**
- "Animate this photo with subtle motion"
- "Make my product image into video"
- "Add wind and movement to landscape"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Any Still Image Into a Living, Moving Scene

Some images are too good to stay frozen. Seedance 2 Image to Video takes the photos, illustrations, or renders you already have and transforms them into fluid, high-fidelity video clips — complete with natural motion, atmospheric movement, and cinematic feel.

Powered by ByteDance's Seedance 2 model, this skill interprets the content of your image and generates motion that feels intentional rather than glitchy or artificial. A portrait subject might subtly turn their head. A landscape might show wind moving through the grass. A product shot might slowly orbit to reveal all angles. The result is video that looks like it was always meant to move.

This skill is ideal for social media creators who want eye-catching content without shooting new footage, e-commerce teams animating product imagery, digital artists adding life to their illustrations, and marketers who need compelling visuals at speed. Upload your image, describe the motion you want, and let Seedance 2 handle the rest.

## Routing Your Animation Requests

When you submit a still image with a motion prompt, ClawHub parses your intent and routes the request directly to the Seedance 2 image-to-video pipeline, matching your specified duration, aspect ratio, and motion intensity to the correct generation endpoint.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance 2 API Reference

Seedance 2 image-to-video processing runs entirely on ByteDance's cloud inference backend, where your source frame is encoded, temporally extended via latent diffusion, and decoded into a fluid MP4 output — no local GPU required. Generation typically completes within 60–120 seconds depending on resolution and motion complexity.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-2-image-to-video`
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

**E-commerce Product Animation:** Upload a clean product photo with a neutral background and prompt a slow rotation or floating effect. This turns standard catalog imagery into scroll-stopping video for ads or product pages — no studio shoot required.

**Social Media Content Creation:** Take a single hero photo from a shoot and generate multiple animated versions with different motion styles — one with a slow zoom, one with atmospheric background movement, one with a cinematic pan. You get a week's worth of content from a single image.

**Digital Art and Illustration Bring-To-Life:** Artists can upload finished illustrations and animate characters with breathing, blinking, or subtle environmental motion — turning static portfolio pieces into living previews for clients or platforms like Instagram and ArtStation.

**Presentation and Pitch Deck Enhancement:** Replace static slides with animated image clips to add visual energy to investor decks, brand presentations, or event screens. A 4-second animated visual lands far harder than a JPG.

## FAQ

**What kinds of images work best with Seedance 2 Image to Video?**
Most image types work well — photographs, digital illustrations, product renders, and even stylized artwork. Images with clear subjects and defined backgrounds tend to produce the most coherent motion. Very abstract or heavily cluttered compositions may produce less predictable results.

**Can I control what kind of motion gets applied?**
Yes. You can describe the motion in your prompt — things like 'slow camera pan left,' 'hair blowing in wind,' 'water rippling,' or 'subject turns toward the camera.' The more specific your description, the closer the output will match your intent.

**How long are the generated video clips?**
Seedance 2 typically generates short clips in the range of 3–6 seconds, which are ideal for social media, looping content, or embedding in longer productions.

**Does the original image get altered?**
No — the output is a new video file. Your original image remains unchanged.

## Best Practices

**Start with a high-resolution, well-lit image.** Seedance 2 produces better motion when it has clean visual information to work with. Blurry, low-contrast, or heavily compressed images can lead to artifacts in the animated output.

**Be specific about motion direction and intensity.** Instead of saying 'make it move,' try 'slowly zoom in toward the subject's face' or 'gentle ocean waves in the background.' Directional and descriptive language gives the model clearer guidance.

**Use images with natural motion cues.** Photos of hair, fabric, water, fire, clouds, or foliage animate particularly well because the model recognizes these as elements that move in the real world. Rigid objects like furniture or architecture may require more explicit motion instructions.

**Iterate on prompts.** If the first result isn't quite right, adjust the motion description rather than changing the image. Small prompt tweaks — like adding 'subtle' or 'dramatic' — can meaningfully shift the output style.
