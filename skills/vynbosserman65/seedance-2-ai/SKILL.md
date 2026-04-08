---
name: seedance-2-ai
version: "1.0.0"
displayName: "Seedance 2 AI — Generate Cinematic AI Videos from Text & Images"
description: >
  Tired of spending hours trying to produce professional-quality video content with clunky tools that never quite capture your vision? seedance-2-ai brings ByteDance's powerful Seedance 2 video generation model directly to your workflow. Describe a scene, upload a reference image, or combine both — and watch fully animated, cinematic video clips come to life in seconds. Built for creators, marketers, and storytellers who demand motion quality that actually impresses.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to Seedance 2 AI — your shortcut to generating cinematic, motion-rich video clips from simple text descriptions or images. Tell me what scene you want to create and I'll bring it to life right now.

**Try saying:**
- "Generate a slow-motion video of golden hour light sweeping across a misty mountain valley with cinematic camera pan"
- "Create a product showcase video for a sleek black smartwatch rotating on a dark reflective surface with dramatic lighting"
- "Use this image of a city skyline at night and animate it with light rain, moving car headlights, and subtle camera drift"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Words and Images Into Stunning AI Video

Seedance 2 AI is a next-generation video creation skill that harnesses one of the most capable AI video models available today. Whether you're a solo content creator, a marketing team on a deadline, or a filmmaker exploring new ideas, this skill lets you generate high-fidelity, motion-rich video clips simply by describing what you want to see — or by feeding it a starting image.

Unlike basic text-to-video tools that produce choppy or generic results, Seedance 2 is built for visual coherence, smooth motion, and cinematic composition. You can generate product showcases, narrative scenes, abstract visuals, social media clips, and much more without touching a single video editing timeline.

The real power here is flexibility. Combine a detailed text prompt with a reference image to guide the visual style, or go purely text-driven for conceptual scenes. The model understands camera motion, lighting mood, subject behavior, and scene transitions — giving you outputs that feel intentional, not accidental.

## Routing Your Seedance Requests

Each prompt or image you submit is parsed for intent — text-to-video, image-to-video, or cinematic style transfer — and dispatched to the appropriate Seedance 2 AI generation pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance 2 API Reference

Seedance 2 AI processes all generation jobs on ByteDance's cloud inference cluster, meaning your text prompts and reference images are sent securely to remote diffusion models for rendering — local compute is never required. Generation times vary based on resolution, motion complexity, and current queue load.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-2-ai`
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

## Use Cases

Seedance 2 AI fits naturally into a wide range of creative and commercial workflows. Social media managers use it to produce scroll-stopping short-form video content without hiring a video production team. E-commerce brands generate polished product animations directly from product photos, turning static listings into engaging visual experiences.

Filmmakers and creative directors use it for rapid concept visualization — testing a scene's mood, lighting, or composition before committing to a full shoot. Game developers and worldbuilders generate environmental or character motion references. Even educators and presenters use it to create visually compelling explainer clips that hold attention far better than static slides.

Whether you need a single atmospheric clip or a batch of varied scene concepts, Seedance 2 AI handles it with consistent visual quality across genres and styles.

## Performance Notes

Seedance 2 AI generates video clips that are optimized for quality and motion coherence, but generation time will vary depending on the complexity of your prompt and the length of the output clip. Highly detailed scenes with multiple moving subjects or intricate lighting may take slightly longer to render than simple single-subject clips.

For the sharpest results, use high-resolution reference images when doing image-to-video generation — low-resolution or heavily compressed inputs can reduce output clarity. Text prompts benefit from specificity: named visual styles, lighting descriptors, and explicit motion cues consistently outperform vague or abstract instructions.

If your first output isn't quite right, small prompt adjustments — changing a lighting descriptor, swapping a camera motion term, or adding a mood word — can meaningfully shift the result. Think of it as iterative directing rather than a single-shot process.

## Quick Start Guide

Getting your first Seedance 2 AI video is straightforward. Start by writing a clear, descriptive prompt — include subject, setting, lighting, mood, and any camera behavior you want (e.g., 'slow push-in', 'aerial drift', 'static wide shot'). The more specific your description, the more precisely the output matches your vision.

If you have a reference image, attach it alongside your prompt. Seedance 2 will use it as a visual anchor, preserving key elements like color palette, subject appearance, or composition while adding motion and life to the scene.

For best results, avoid vague prompts like 'make a cool video.' Instead, try something like: 'A barista pouring latte art in slow motion, warm café lighting, shallow depth of field, gentle steam rising.' Treat your prompt like a mini director's note — describe what the camera sees, not just what exists in the scene.
