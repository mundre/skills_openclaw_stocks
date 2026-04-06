---
name: ai-text-to-video-generator-free
version: "1.0.1"
displayName: "AI Text to Video Generator Free — Turn Words Into Stunning Videos Instantly"
description: >
  Type a script, a story idea, or even a single sentence — and watch it become a fully animated video in seconds. This ai-text-to-video-generator-free skill transforms plain text into visual content complete with scenes, transitions, and pacing built around your words. Perfect for content creators, educators, marketers, and social media managers who need professional-looking videos without a budget or a film crew. No editing experience required.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome! You're one text prompt away from a finished video — this skill turns your words, scripts, or story ideas into real video content using AI, completely free. Paste your script or describe your video concept to get started right now.

**Try saying:**
- "Turn my script into a video"
- "Generate scenes from this text"
- "Create a promo video from description"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# From Blank Page to Finished Video — Instantly

Most people have ideas but no way to turn them into video. Hiring editors is expensive. Learning software takes weeks. And staring at a blank timeline is frustrating when all you have is a good script and a deadline. This skill exists to close that gap entirely.

With the AI Text to Video Generator Free skill, you write your message — a product pitch, a how-to guide, a short story, a social media hook — and the AI handles the visual storytelling. It interprets your text, builds a scene structure, selects appropriate visual flow, and assembles a cohesive video that matches your tone and intent.

Whether you're producing explainer content for a startup, educational clips for a classroom, or quick promo videos for Instagram and TikTok, this skill gives you a fast, zero-cost path from idea to finished video. No subscriptions, no timeline dragging, no rendering headaches — just text in, video out.

## Prompt Routing and Video Dispatch

When you submit a text prompt, the skill parses your scene descriptors, style tags, and duration parameters before routing the generation request to the optimal AI rendering pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

The free-tier video synthesis backend processes your text-to-video requests through a distributed diffusion model cluster, handling keyframe interpolation, voiceover synthesis, and scene transitions entirely in the cloud — no local GPU required. Rendered video assets are temporarily cached on the CDN edge node closest to your region for fast preview and download.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-text-to-video-generator-free`
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

## Best Practices for AI Text to Video Generation

The quality of your output is directly tied to the clarity of your input. Vague prompts like 'make a video about health' produce generic results. Instead, specify your audience, tone, video length, and purpose — for example: 'A 45-second upbeat video for millennials about meal prepping on a budget.'

Break your text into logical segments if you're working with longer scripts. The AI performs best when it can map distinct ideas to distinct scenes. Think in chunks: hook, problem, solution, call to action.

For social media content, always mention the platform. A LinkedIn explainer video has a very different pacing and tone than a TikTok. Naming the platform helps the AI calibrate visual energy, text density, and scene length appropriately.

Finally, include emotional cues when relevant. Words like 'urgent,' 'inspiring,' 'calm,' or 'playful' guide the AI toward the right visual atmosphere for your message.

## Troubleshooting Common Issues

If your generated video structure feels off or scenes don't match your intent, the most common cause is an ambiguous prompt. Re-read your input and ask: could this be interpreted multiple ways? If yes, tighten the language and resubmit.

If the AI is generating too many scenes for a short video, explicitly state your target duration and scene count — for example: '3 scenes, under 30 seconds, fast-paced.' Constraints help the model stay focused.

When working with technical or niche topics, avoid heavy jargon without context. The AI may misinterpret industry-specific terms. Either define them briefly in your prompt or use plain-language equivalents.

If your output feels generic despite a detailed prompt, try reframing your input as a story rather than a list of facts. Narrative structure — character, conflict, resolution — consistently produces more dynamic and engaging video concepts than bullet-point style descriptions.

## FAQ — AI Text to Video Generator Free

**Do I need any video editing experience to use this?** No. This skill is built for people who have never touched a timeline. You provide text; the AI handles all structural and visual decision-making.

**What types of videos can I generate?** Explainers, social media shorts, product demos, educational content, storytelling videos, promotional clips, and more. If it can be scripted, it can be generated.

**Is there a word or character limit for my input text?** For best results, keep your input focused — roughly equivalent to a 30 to 90 second spoken script. Longer inputs can be broken into multiple generation requests.

**Can I use this for commercial projects?** Yes. The generated video concepts, scripts, and scene structures are yours to use, adapt, and produce commercially. Always review final output to ensure it aligns with your brand voice before publishing.
