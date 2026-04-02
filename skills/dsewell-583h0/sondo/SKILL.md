---
name: sondo
version: "1.0.0"
displayName: "Sondo AI Video Skill — Intelligent Audio-Visual Sync and Sound Design for Your Clips"
description: >
  Tell me what you need and sondo will handle the rest — whether you're matching beats to cuts, layering ambient sound, or syncing dialogue to motion. Sondo is a ClawHub AI skill built for creators who want their video and audio to feel inseparable. It analyzes your footage and aligns sound elements with precision, supporting mp4, mov, avi, webm, and mkv formats. Perfect for filmmakers, content creators, and social media editors who want professional-grade audio-visual cohesion without a full studio setup.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm sondo — ready to help you sync, layer, and shape the audio experience of your video. Drop your clip and tell me what you're hearing in your head, and let's make it real.

**Try saying:**
- "Sync the music drops to the action cuts in my skateboarding clip"
- "Add subtle ambient background sound to make my indoor interview feel warmer and less clinical"
- "Match the beat of this upbeat track to the transitions in my product launch video"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Where Sound Meets Vision — Perfectly, Every Time

Sondo is built around one idea: that great video isn't just seen, it's felt. The gap between amateur and professional content often comes down to how well the audio and visuals move together — and sondo closes that gap automatically.

Upload your clip and describe what you're going for. Want the music to hit exactly when the subject turns to camera? Need ambient room tone to carry through a cut without jarring the viewer? Sondo reads the structure of your footage and applies audio-visual alignment logic that would normally take hours of manual timeline work.

Whether you're cutting a travel vlog, a product showcase, a short film, or a social reel, sondo adapts to the mood and pacing of your content. It's not a one-size-fits-all audio stamper — it's a responsive skill that treats each video as its own creative challenge, giving your final cut the kind of sonic texture that makes people watch twice.

## Routing Your Sondo Requests

Every prompt you send — whether it's syncing a beat drop to a cut, layering ambient texture, or generating a full sound design pass — gets parsed by Sondo's intent engine and routed to the matching audio-visual pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

Sondo runs on the NemoVideo API, which handles frame-accurate audio analysis, waveform-to-timeline binding, and generative sound rendering for your clips. All session state, stem data, and sync markers are managed server-side through NemoVideo's processing layer.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `sondo`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=sondo&skill_version=1.0.0&skill_source=<platform>`

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

## Tips and Tricks

When working with sondo, the more specific your prompt, the better your results. Instead of saying 'make it sound good,' try describing the emotional tone — 'I want it to feel tense and cinematic right before the 0:45 mark.' Sondo responds well to emotional and contextual cues, not just technical instructions.

If you're providing your own music track, trim it to roughly match your video length before uploading. Sondo works best when it isn't guessing how much of a track to use — giving it a close-length audio file lets it focus on precision alignment rather than structural decisions.

For multi-scene videos, consider breaking your clip into segments and describing each section's audio needs separately. This gives sondo clearer creative direction per scene and tends to produce more nuanced, intentional results than treating the whole video as one uniform block.

## Common Workflows

One of the most popular ways creators use sondo is for beat-matched editing — uploading a clip alongside a music track and asking sondo to align visual cuts to rhythmic peaks. This is especially effective for sports highlights, dance videos, and fast-paced brand content where timing is everything.

Another frequent workflow is ambient layering. Many creators shoot in environments that sound too clean or too noisy straight out of camera. Sondo can introduce or adjust ambient texture — a coffee shop hum, light outdoor wind, or neutral room tone — to make a scene breathe naturally without distracting from the main audio.

Dialogue-heavy videos like interviews, tutorials, and vlogs benefit from sondo's ability to smooth audio across cuts, reducing the jarring effect of mismatched room acoustics between takes. Instead of manually fading every edit point, you describe the feel you want and sondo handles the transitions.
