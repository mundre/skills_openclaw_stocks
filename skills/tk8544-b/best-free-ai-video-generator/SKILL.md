---
name: best-free-ai-video-generator
version: "1.0.0"
displayName: "Best Free AI Video Generator — Create Stunning Videos From Text or Images"
description: >
  Describe your idea, drop some images, or paste a script — and watch it become a fully produced video in seconds. This best-free-ai-video-generator skill helps creators, marketers, and educators turn raw concepts into polished video content without spending a dime. Generate text-to-video clips, animate still photos, add voiceovers, and produce social-ready formats across platforms like TikTok, YouTube, and Instagram.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your script, image, or video idea and I'll generate a polished AI video for you right now. No footage? Just describe the vibe, topic, or story you want and I'll handle the rest.

**Try saying:**
- "Create a 30-second promotional video for my handmade candle business using these product photos and this tagline: 'Light your world, naturally.'"
- "Generate a motivational YouTube Short with bold captions, upbeat background music, and a voiceover based on this quote about perseverance."
- "Turn this 200-word blog post about healthy meal prep into an engaging Instagram Reel with text overlays and smooth transitions."

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Any Idea Into a Finished Video Instantly

Whether you have a script, a single sentence, or just a rough concept, this skill transforms your input into watchable, shareable video content — no timeline editing, no expensive subscriptions, no steep learning curve required. It's built for people who need results fast and budgets that need to stay at zero.

The best-free-ai-video-generator skill works by understanding your intent and matching it with the right visual style, pacing, and structure. Want a 60-second product explainer? A motivational reel with captions? A slideshow with dynamic transitions and background music? Just describe it and the skill handles the creative heavy lifting.

This tool is especially useful for solo creators, small business owners, nonprofit teams, and students who need professional-looking video output without access to a design team or video production software. You bring the idea — this skill brings it to life.

## Routing Your Video Generation Requests

When you submit a text prompt or source image, ClawHub parses your input and routes it to the optimal free AI video generation engine based on your requested style, duration, and resolution parameters.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

Video synthesis runs on a distributed cloud backend that queues your text-to-video or image-to-video job, applies diffusion-based frame generation, and streams the rendered MP4 output back once processing completes. Latency varies by model load, clip length, and selected frame rate — lightweight 3-second clips typically render faster than extended 10-second sequences.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `best-free-ai-video-generator`
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

## Common Workflows With the Free AI Video Generator

Most users come to this skill with one of three starting points: a written script, a collection of images, or just a topic idea. Each path leads to a finished video, but the workflow looks a little different depending on what you bring.

If you have a script, paste it in and specify the target platform and length. The skill will match your words to visuals, add transitions, and suggest audio options. If you're starting from images, upload them in order or describe the sequence and the skill will animate, time, and style them into a cohesive clip.

For pure concept-to-video generation — where you only have a topic — describe the tone, audience, and goal. The skill will draft a visual storyboard, generate or source matching visuals, and produce a ready-to-export video. This workflow is especially popular for explainer videos, social content calendars, and educational clips.

## Quick Start Guide: Your First AI-Generated Video

Getting your first video out is straightforward. Start by deciding your output format: horizontal (16:9) for YouTube, vertical (9:16) for TikTok or Reels, or square (1:1) for general social use. Mention this upfront so the layout is optimized from the start.

Next, provide your core content. This can be a script (even bullet points work), a theme or topic, or a set of images with captions. The more specific you are about tone — cinematic, energetic, calm, corporate — the closer the first output will be to what you want.

Finally, specify any must-have elements: voiceover language, caption style, music mood, or brand colors. The skill will generate a draft video based on your inputs. You can then request adjustments like trimming a section, changing the pacing, swapping a visual, or updating the text overlay. Most users have a shareable video ready within two to three rounds of feedback.

## Troubleshooting Your AI Video Output

If your generated video feels off, the most common fix is adding more context to your original prompt. Vague inputs like 'make a cool video' produce generic results. Try specifying the audience, the emotion you want to trigger, the platform it's for, and the length.

If the visuals don't match your brand or topic, try describing the visual style more explicitly — for example, 'minimalist white background with bold sans-serif text' or 'warm golden-hour outdoor footage.' You can also upload reference images to anchor the aesthetic.

For voiceover issues, confirm the language, accent preference, and speaking pace in your request. If captions are appearing in the wrong position or font, describe your preferred style directly. And if the video feels too long or too fast, simply ask for a tighter cut or a slower pace — the skill can revise timing without regenerating the entire video from scratch.
