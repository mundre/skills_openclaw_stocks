---
name: text-to-video-ai-2026
version: "1.0.0"
displayName: "Text-to-Video AI 2026 — Turn Written Prompts Into Stunning Videos Instantly"
description: >
  Tired of spending hours storyboarding, filming, and editing just to bring a simple idea to life? Text-to-video-ai-2026 lets you skip the production pipeline entirely — just type what you want to see, and watch it become a fully rendered video. Whether you're a marketer needing product demos, an educator building course content, or a creator scaling output, this skill taps into the latest 2026 AI video generation models to produce cinematic, narrated, or animated clips from plain text. Fast, flexible, and built for real workflows.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Paste your script, scene description, or video concept and I'll generate a fully rendered video using text-to-video-ai-2026 models. No footage? No problem — just describe what you want and I'll build it from scratch.

**Try saying:**
- "Create a 30-second product launch video for a wireless earbud brand using a sleek, dark cinematic style with upbeat background music and on-screen text callouts"
- "Generate a 60-second educational explainer video about how black holes form, using a space documentary visual style with a calm narrator voiceover and animated diagrams"
- "Turn this blog post intro into a vertical-format social media video with bold captions, fast cuts, and an energetic tone suitable for Instagram Reels"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# From Words on a Page to Video That Moves

Text-to-video-ai-2026 is built for anyone who has ever had a clear vision in their head but no crew, no camera, and no time to execute it. You write a prompt — a scene description, a script, a concept — and the skill translates it into a cohesive video with visuals, pacing, and optionally voiceover or captions baked in.

This isn't a basic slideshow generator. The 2026 generation of AI video models understands narrative structure, visual continuity, and stylistic tone. You can ask for a cinematic product reveal, a whiteboard explainer, a social media reel, or a news-style segment — and get back something that actually looks intentional, not stitched together.

The skill is designed to work iteratively. You can refine outputs by adjusting your prompt, changing the visual style, swapping the pacing, or requesting a different aspect ratio. Think of it as a creative collaborator that handles the heavy lifting while you stay focused on the message you're trying to deliver.

## Prompt Routing and Model Dispatch

Each text prompt is parsed for scene complexity, motion directives, and style tokens before being dispatched to the optimal diffusion pipeline in your connected model cluster.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Inference API Reference

Video generation requests are processed across distributed GPU nodes using latent diffusion with temporal attention layers, delivering rendered MP4 outputs via signed CDN URLs. Frame coherence, motion smoothing, and upscaling passes all run server-side — no local compute required.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `text-to-video-ai-2026`
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

## Best Practices

Start every text-to-video-ai-2026 session by defining three things: the audience, the platform, and the desired emotional response. A training video for enterprise employees needs a completely different visual language than a TikTok ad for Gen Z consumers — and the AI responds well to that kind of contextual framing in your prompt.

Iterate in layers. Get the structure and pacing right first, then refine the visual style, then polish the copy or voiceover. Trying to perfect everything in a single prompt often leads to over-constrained outputs that feel forced.

For brand consistency, include specific style references in your prompts — color hex codes, font style descriptors, or references to visual aesthetics (e.g., 'Wes Anderson symmetry', 'Apple product launch minimalism'). The 2026 models are trained on a wide enough visual corpus to interpret these references accurately and apply them with real coherence across a full video.

## Performance Notes

Text-to-video-ai-2026 models perform best when your input prompt is specific about visual style, duration, and intended platform. Vague prompts like 'make a video about coffee' will produce generic results, while prompts that specify mood, color palette, pacing, and subject framing consistently yield higher-quality outputs.

Longer videos (over 90 seconds) may require segmented generation — breaking your concept into scenes and stitching them together produces more visually coherent results than requesting a single long render. For complex narratives, providing a structured scene-by-scene breakdown dramatically improves output consistency.

Aspect ratio and resolution targets should be declared upfront. Specifying 9:16 for mobile, 16:9 for desktop, or 1:1 for feeds ensures the composition and subject framing are optimized for your delivery channel from the first render rather than requiring a crop or reformat afterward.
