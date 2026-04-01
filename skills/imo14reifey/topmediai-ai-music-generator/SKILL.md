---
name: topmediai-ai-music-generator
version: "1.0.0"
displayName: "TopMediai AI Music Generator — Create Custom AI Tracks for Any Video"
description: >
  Tell me what mood, genre, or tempo you need and the topmediai-ai-music-generator will craft original music tailored to your creative vision. This skill taps into TopMediai's AI composition engine to generate royalty-free tracks, background scores, and audio beds without any musical expertise required. Upload your video (mp4, mov, avi, webm, or mkv) and describe the vibe — cinematic, upbeat, lo-fi, dramatic — and get music that fits. Ideal for content creators, YouTubers, filmmakers, and social media marketers who need fresh, original audio fast.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you generate original AI-composed music for your videos using the TopMediai AI Music Generator. Describe your video's mood, genre, or scene — or upload a clip — and let's create a track that fits perfectly. What are we making today?

**Try saying:**
- "Generate an upbeat, energetic background track for a 60-second gym workout montage video"
- "Create a soft, cinematic piano score to accompany a slow-motion wedding highlight reel"
- "Make a lo-fi hip-hop loop for a 3-minute study vlog with a calm, focused atmosphere"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Your Videos Deserve Music That Actually Fits

Finding the right music for a video has always been a time sink — digging through stock libraries, worrying about licensing, and settling for tracks that almost work. The topmediai-ai-music-generator changes that by letting you describe exactly what you want and generating original music to match.

Whether you're scoring a travel montage, adding energy to a product demo, or setting a reflective tone for a documentary clip, this skill interprets your creative brief and produces audio that complements the pacing and mood of your footage. You're not picking from a catalog — you're commissioning something new.

This skill is built for people who care deeply about the final product but don't have a music production background. Describe the emotion, the genre, the energy level, or even reference a scene — the AI handles the composition. The result is a cohesive, original track you can drop straight into your edit.

## Routing Your Music Requests

When you describe your desired track — mood, genre, tempo, or video context — TopMediai's AI interprets your prompt and routes it through the appropriate generation pipeline to match your creative intent.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

TopMediai AI Music Generator is powered by the NemoVideo backend, which handles prompt parsing, audio synthesis, and track delivery in real time. Each API call passes your generation parameters — including style tags, duration, and energy level — directly to NemoVideo's model endpoints for processing.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `topmediai-ai-music-generator`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=topmediai-ai-music-generator&skill_version=1.0.0&skill_source=<platform>`

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
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Use Cases

The topmediai-ai-music-generator covers a wide range of real-world production needs. Social media creators use it to add personality to Reels, TikToks, and YouTube Shorts without worrying about copyright strikes. Filmmakers and videographers rely on it for custom underscore music that syncs with specific emotional beats in a scene.

Marketing teams find it especially useful for producing consistent branded audio across ad campaigns — requesting tracks in the same genre or tempo family to build a recognizable sound identity. Podcast producers use it to create intro and outro music, as well as ambient beds for interview segments.

Educators and course creators also benefit, adding professional-sounding background music to tutorial videos without licensing headaches. Essentially, if your project needs original audio and you don't have a composer on retainer, this skill fills that gap efficiently.

## Performance Notes

The quality and accuracy of generated music improves significantly with specific, descriptive prompts. Vague requests like 'make music for my video' will produce something generic, while detailed briefs — specifying genre, mood, tempo, instruments, and video length — yield much more targeted results.

Video files uploaded in mp4 or mov format tend to process most smoothly for pacing analysis. Larger files (webm, mkv, avi) are supported but may take slightly longer to analyze before generation begins. If you're iterating on a track, make incremental adjustment requests rather than restarting from scratch — the generator responds well to refinement prompts.

Generated music is royalty-free for use in your projects. Keep in mind that highly complex orchestral arrangements or very specific genre fusions may require a second generation pass to fully land the sound you're after.

## Quick Start Guide

Getting your first AI-generated track is straightforward. Start by describing your video's mood or purpose in plain language — something like 'upbeat corporate background music for a 90-second product launch video' gives the generator strong direction. You can also upload your video file directly (mp4, mov, avi, webm, or mkv) and let the skill analyze the pacing before generating music.

Once you submit your request, the topmediai-ai-music-generator processes your brief and returns an original composition. You can refine the output by specifying tempo (BPM range), instrumentation preferences (strings, synths, acoustic guitar), or emotional tone adjustments like 'make it more tense' or 'add a brighter feel.'

For best results, mention the video length so the generated track is appropriately timed. Short-form social content, long-form YouTube videos, and everything in between are all supported.
