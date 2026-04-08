---
name: vheer-ai-video-generator
version: "1.0.0"
displayName: "Vheer AI Video Generator — Create Stunning Videos from Text & Images"
description: >
  Drop a concept, image, or script and watch it transform into a polished video — that's the power of vheer-ai-video-generator. This skill taps into Vheer's generative video engine to turn your ideas into cinematic clips, product showcases, social reels, and more. Key features include text-to-video generation, image-to-video animation, style customization, and scene sequencing. Built for content creators, marketers, and storytellers who want professional-grade video output without a production team.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to Vheer AI Video Generator — your shortcut from idea to finished video. Tell me what you want to create and I'll generate it using Vheer's AI engine. Share a prompt, an image, or a concept to get started right now.

**Try saying:**
- "Generate video from my product photo"
- "Create a cinematic text-to-video clip"
- "Animate this image into a reel"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Turn Words and Images Into Real Video

Vheer AI Video Generator brings your creative ideas to life without requiring a camera, editing suite, or production crew. Whether you start with a written prompt, a product photo, or a rough storyboard concept, this skill converts your input into a fully rendered video sequence using Vheer's generative AI engine.

The skill is designed for people who need video content fast — social media managers working against a posting schedule, e-commerce brands building product demos, indie creators crafting short films, or marketers who need explainer videos without the agency budget. You describe the scene, set the tone, and Vheer handles the visual heavy lifting.

Beyond simple generation, the skill supports iterative refinement. Don't love the first output? Adjust the mood, swap the visual style, change the pacing, or rework the narrative arc. The result is a flexible, conversational video production workflow that meets you where your creative process already lives.

## Routing Your Vheer Video Requests

Each prompt, image upload, or style selection you submit is parsed and dispatched to the appropriate Vheer generation pipeline — whether that's text-to-video, image-to-video, or motion synthesis.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Vheer Cloud API Reference

Vheer processes all generation jobs on its distributed GPU cloud backend, queuing your render request and streaming the output back once the video frames are synthesized and encoded. Latency varies by resolution, motion complexity, and current cluster load.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `vheer-ai-video-generator`
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

Vheer AI Video Generator fits naturally into content workflows that already rely on AI-assisted creation. If you're running a social media content pipeline, you can use this skill as the video production step — taking copy or campaign briefs that were written elsewhere and converting them directly into video assets ready for scheduling.

For e-commerce teams, the skill pairs well with product photography workflows. Export your product images from your photo editing tool, bring them here, and generate animated product videos suitable for listings, ads, or email campaigns without any additional software.

Agencies and freelancers can use the skill to rapidly prototype video concepts for client presentations. Generate multiple style variations from the same brief in minutes, present options to the client, and then refine the chosen direction — all within the same conversation thread. This removes the back-and-forth typically associated with early-stage video production and compresses the approval cycle significantly.

## Quick Start Guide

Getting your first video out of Vheer AI Video Generator takes less than a minute. Start by describing your video in plain language — include the subject, mood, movement style, and intended platform if you have one. The more specific your prompt, the closer the output will match your vision on the first attempt.

If you have a source image — a product shot, a landscape photo, a character illustration — you can drop it directly into the chat alongside your description. The skill will use it as a visual anchor for the generated video, animating and extending it into a full clip.

For best results, mention the aspect ratio you need upfront (vertical for Reels and TikTok, horizontal for YouTube, square for feeds). You can also specify duration, color palette preferences, and camera movement style such as slow zoom, pan, or static. Once the video is generated, simply describe any changes you want and the skill will revise accordingly.
