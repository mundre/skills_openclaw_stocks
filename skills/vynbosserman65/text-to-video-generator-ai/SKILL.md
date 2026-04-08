---
name: text-to-video-generator-ai
version: "1.0.0"
displayName: "Text-to-Video Generator AI — Turn Written Prompts Into Stunning Videos"
description: >
  Type a scene, a story idea, or a product pitch — and watch it become a video. This text-to-video-generator-ai skill transforms plain text descriptions into fully rendered video content, complete with visuals, pacing, and style matching. Whether you're a content creator, marketer, or educator, it handles the heavy lifting so you skip straight from concept to finished clip.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome — you're one text prompt away from a generated video. Describe your scene, concept, or story and this text-to-video generator will build it into visual content for you. Drop your prompt below to get started.

**Try saying:**
- "Generate a 30-second promotional video for a coffee brand using a warm, cinematic morning aesthetic with soft lighting and close-up shots of a steaming cup"
- "Create a short explainer video about how solar panels work, aimed at middle school students, using simple animations and an upbeat visual style"
- "Turn this product description into a 15-second social media video clip with bold text overlays and high-energy pacing: 'Our new running shoe is built for speed, comfort, and all-terrain grip'"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# From Words on a Page to Video That Moves

Most video creation tools assume you already have footage. This one doesn't. The text-to-video-generator-ai skill starts with nothing but your words — a sentence, a paragraph, a creative brief — and builds video content around them from scratch.

Describe a product launch, a short story, a social media ad, or an explainer concept, and the skill interprets your intent, selects appropriate visual styles, and assembles a coherent video sequence. You control the tone, the subject matter, and the narrative arc. The skill handles the visual translation.

This is especially useful for teams that move fast and need video assets without a full production pipeline. Marketers can prototype ad concepts before committing to a shoot. Educators can generate illustrative clips for lessons. Indie creators can visualize scripts before filming. Whatever your workflow, this skill fits in as the step between idea and execution.

## Prompt Routing and Model Dispatch

Each text prompt you submit is parsed for scene complexity, motion descriptors, and style tags before being dispatched to the optimal diffusion model pipeline for rendering.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Video Synthesis API Reference

All video generation jobs run on distributed GPU clusters via an asynchronous cloud rendering backend, with frame synthesis, temporal coherence processing, and output encoding handled server-side. Your generated video assets are stored in a secure session bucket and delivered via signed CDN URL upon job completion.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `text-to-video-generator-ai`
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

## Quick Start Guide

Getting your first video generated is straightforward. Start by writing a clear, specific text prompt describing what you want the video to show. Include details like subject matter, visual tone, intended audience, and approximate length if you have a target in mind.

For example, instead of typing 'make a video about dogs,' try 'create a 20-second upbeat video about golden retriever puppies playing in a park, suitable for a pet adoption campaign.' The more context you provide, the closer the output will match your vision.

Once you submit your prompt, the skill processes your description and returns a generated video or a preview sequence. You can then refine by adjusting your prompt — tightening the mood, changing the pacing description, or specifying a different visual style. Iteration is fast, so don't hesitate to run multiple variations.

## Performance Notes

Video generation quality scales directly with prompt specificity. Vague prompts produce generic results; detailed prompts produce targeted, usable content. If your first output feels off-brand or misaligned, the most effective fix is almost always a more descriptive prompt rather than regenerating with the same input.

Longer videos with complex scene transitions take more processing time than short, single-scene clips. If speed matters, break a longer concept into shorter segments and generate them individually before combining.

Text-heavy scenes — like those with on-screen titles, captions, or data visualizations — benefit from explicitly stating font style preferences and placement in your prompt. Without guidance, the skill defaults to standard visual layouts, which may not match your brand guidelines.

## Best Practices

Lead with the end goal. Before describing visuals, state the purpose of the video — is it to sell, educate, entertain, or inspire? This framing shapes how the skill interprets everything that follows.

Use reference anchors when possible. Phrases like 'cinematic documentary style,' 'fast-cut social media reel,' or 'minimalist whiteboard animation' give the generator clear stylistic targets that dramatically improve output consistency.

Avoid overloading a single prompt with too many competing ideas. If your concept has multiple distinct segments — an intro, a product demo, and a call-to-action — describe each section separately or structure your prompt with clear scene breaks. This produces cleaner transitions and more coherent pacing across the full video.
