---
name: seedance-alternative
version: "1.0.0"
displayName: "Seedance Alternative — AI Video Generation Without the Waitlist or Limits"
description: >
  Drop a video concept, a script, or even a rough idea and watch it come to life without touching Seedance. This seedance-alternative skill on ClawHub lets you generate, remix, and animate video content using powerful AI — no queue, no restrictions. Whether you're a creator tired of waitlists, a marketer needing fast turnaround, or a filmmaker prototyping scenes, this tool delivers cinematic motion, style-matched clips, and prompt-driven video creation on demand.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to your go-to Seedance alternative — generate AI videos from text, images, or scripts in seconds. Drop your idea, reference clip, or scene description and let's start creating right now.

**Try saying:**
- "Generate a 10-second cinematic video of a lone astronaut walking across a red desert at golden hour with slow camera pan"
- "I have a product photo of a sneaker — create a dynamic video ad with motion blur and urban background transitions"
- "Turn this script into a short animated explainer video with a clean, modern visual style: 'Our app saves you 3 hours a week by automating your inbox.'"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Generate Stunning Videos Without Seedance's Constraints

If you've been using Seedance for AI video generation and hit a wall — whether it's usage caps, slow queues, or limited creative control — this skill was built for you. As a fully capable seedance-alternative, it lets you describe a scene, upload a reference, or paste a script and receive polished, motion-rich video output without the friction.

What sets this apart isn't just availability — it's creative range. You can generate realistic footage, stylized animations, product showcases, social media reels, and cinematic short clips all from the same interface. Describe the mood, the camera movement, the color grade, and the subject, and the AI interprets it with remarkable fidelity to your vision.

This skill is built for creators who move fast. Whether you're producing content for YouTube, TikTok, brand campaigns, or internal presentations, you get professional-grade video generation without waiting for access, managing API keys, or learning a new platform from scratch.

## Routing Your Generation Requests

Each prompt you submit gets parsed for motion style, duration, and resolution preferences before being dispatched to the appropriate Seedance-compatible inference endpoint.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Backend API Reference

Seedance Alternative routes all video synthesis jobs through a distributed cloud pipeline that handles frame interpolation, temporal consistency, and prompt adherence scoring without queuing delays. Your generation parameters — including seed values, aspect ratios, and motion intensity — are preserved end-to-end across the render session.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-alternative`
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

This seedance-alternative skill fits naturally into existing content production pipelines. If you're working in a marketing team, use it at the ideation and storyboarding stage — generate rough visual concepts from your brief before committing to a full production shoot. It dramatically cuts pre-production time and helps align stakeholders visually before resources are spent.

For solo creators, pair this skill with your existing editing tools. Export generated clips and bring them into DaVinci Resolve, Premiere Pro, or CapCut for final color grading, music layering, and caption overlays. The AI handles the heavy creative lift; your editor handles the polish.

If you're running a content agency, this tool scales with volume. Use consistent prompt templates for recurring content types — weekly product features, event recaps, testimonial visualizations — so your team can produce at speed without sacrificing visual consistency.

For e-commerce brands, integrate generated video content directly into product pages or ad sets by using product imagery as reference inputs, letting the AI animate and contextualize static assets into engaging short-form video without a full production budget.

## Tips and Tricks

Getting the best results from this seedance-alternative comes down to how you write your prompts. Instead of saying 'make a cool video,' describe the shot like a director would: specify the subject, setting, time of day, camera angle, and emotional tone. For example, 'close-up of a coffee cup steaming on a rainy windowsill, warm amber lighting, shallow depth of field' will produce dramatically better results than 'coffee video.'

If you're generating a video for social media, mention the aspect ratio upfront — vertical 9:16 for TikTok and Reels, square 1:1 for feed posts, or widescreen 16:9 for YouTube. This prevents unnecessary cropping after the fact.

For brand consistency, include color palette references or mood descriptors like 'muted tones,' 'high contrast,' or 'pastel and airy.' You can also reference visual styles like 'Wes Anderson symmetry' or 'documentary handheld feel' and the AI will interpret those creative shorthand cues effectively.

## Best Practices

When using this as your primary seedance-alternative workflow, treat each generation as an iteration rather than a final output. Generate a first version, review what landed and what didn't, then refine your prompt with specific adjustments. Saying 'same scene but slower camera movement and more fog' is far more efficient than rewriting the entire prompt from scratch.

For video ads or branded content, always start with the core message you want viewers to feel — not just what they'll see. Emotion-driven prompts like 'a sense of quiet confidence and minimalism' layer meaning into the visuals in ways that purely descriptive prompts miss.

Avoid overloading a single prompt with too many competing ideas. If you want a video with multiple scenes or transitions, break them into separate generations and sequence them in post. This gives you more control over pacing and ensures each segment gets the visual attention it deserves.

Always review generated clips for unintended artifacts before publishing, especially in close-up facial shots or text-heavy scenes where AI generation can occasionally introduce inconsistencies.
