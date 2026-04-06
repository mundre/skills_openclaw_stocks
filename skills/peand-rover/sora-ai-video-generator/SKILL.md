---
name: sora-ai-video-generator
version: "1.0.0"
displayName: "Sora AI Video Generator — Create Stunning Videos from Text Prompts"
description: >
  Tired of spending hours storyboarding, filming, and editing just to produce a short video? The sora-ai-video-generator skill lets you turn plain text descriptions into polished, cinematic video clips without touching a camera or editing timeline. Describe a scene, a mood, or a story — and watch it come to life. Supports mp4, mov, avi, webm, and mkv output formats. Built for content creators, marketers, educators, and storytellers who want professional-quality video at the speed of an idea.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your Sora AI Video Generator — ready to transform your text descriptions into vivid, high-quality video clips. Tell me what scene, story, or concept you want to bring to life, and let's start creating.

**Try saying:**
- "Generate a 10-second video of a rainy Tokyo street at night with neon reflections on wet pavement and slow camera pan"
- "Create a product showcase video for a minimalist white sneaker on a clean studio background with soft lighting and a 360-degree rotation"
- "Make a short cinematic clip of a lone astronaut walking across a red desert planet at golden hour with dramatic wide-angle framing"

### Getting Connected

Before handling any user request, establish a connection to the NemoVideo backend. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/nemovideo/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Words Into Cinematic Video Moments Instantly

The Sora AI Video Generator skill bridges the gap between imagination and finished video content. Instead of wrangling cameras, actors, or complex editing software, you simply describe what you want to see — and the skill generates a video that matches your vision, tone, and style.

This is not a generic video template tool. Whether you want a sweeping aerial shot of a mountain at sunrise, a product demonstration in a sleek studio setting, or an animated explainer with a specific visual mood, the skill interprets natural language prompts with remarkable nuance. You can specify lighting conditions, camera movement, color palette, pacing, and narrative context all within your description.

Content creators producing social media reels, marketing teams building campaign assets, educators crafting visual lessons, and indie filmmakers prototyping scenes will all find immediate value here. The skill removes the production barrier entirely, letting you focus on the creative idea rather than the technical execution. Generate multiple variations from a single prompt and pick the one that resonates most with your audience.

## Prompt Routing and Request Handling

Each text-to-video request is parsed for scene descriptors, motion cues, aspect ratio, and duration before being dispatched to the appropriate Sora generation pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend API Reference

The NemoVideo backend orchestrates your Sora video generation jobs by queuing diffusion render tasks, managing frame synthesis, and returning a streamable MP4 output URL upon completion. Latency varies based on clip length, resolution tier, and current render queue depth.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `sora-ai-video-generator`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=sora-ai-video-generator&skill_version=1.0.0&skill_source=<platform>`

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

## Performance Notes

Generation time for the sora-ai-video-generator skill varies based on clip length, complexity of the scene, and the level of motion detail requested. Simple static or slow-motion scenes with minimal subjects typically render faster than complex multi-element scenes with rapid camera movement.

For best results, keep initial prompts under 300 characters and avoid combining too many conflicting visual styles in a single request — for example, asking for both a hand-drawn animation aesthetic and photorealistic textures simultaneously may produce inconsistent output.

Higher-resolution outputs and longer clip durations will naturally require more processing time. If you are generating video for a time-sensitive campaign, start with shorter clips to validate the visual direction before scaling up to longer sequences. The skill supports mp4, mov, avi, webm, and mkv formats, so specify your preferred container early to avoid unnecessary conversion steps downstream.

## Best Practices

Getting the most out of the sora-ai-video-generator skill comes down to the specificity and clarity of your prompts. Vague descriptions like 'make a cool video' produce generic results, while detailed scene descriptions unlock the full creative range of the skill.

Always include key visual parameters in your prompt: setting, time of day, lighting style, camera movement, subject action, and emotional tone. For example, instead of 'a forest scene,' try 'a misty old-growth forest at dawn with shafts of light filtering through tall redwoods and a slow forward dolly movement.'

If you need a specific output format such as mp4 for web delivery or mov for editing pipelines, mention it in your request. For iterative work, generate two or three variations of the same prompt with slight wording changes to compare results. Shorter, focused clips (5–15 seconds) tend to yield the most coherent and visually consistent output, especially for commercial or social media use cases.

## FAQ

**Can I use sora-ai-video-generator for commercial projects?** Yes. Videos generated through this skill can be used for marketing campaigns, social content, educational materials, and client deliverables. Always review the output for brand alignment before publishing.

**What video formats does the skill output?** The skill supports mp4, mov, avi, webm, and mkv. Specify your preferred format in your prompt or request, and the output will be prepared accordingly.

**Can I include voiceover or music in the generated video?** The skill focuses on the visual video generation layer. For audio — including voiceover, background music, or sound effects — you would combine the output with a dedicated audio tool in your workflow.

**How do I get consistent style across multiple clips?** Reuse the same descriptive language for lighting, color grading, and camera style across all your prompts within a project. Treating your style description like a reusable template keeps visual identity cohesive across a series of generated clips.
