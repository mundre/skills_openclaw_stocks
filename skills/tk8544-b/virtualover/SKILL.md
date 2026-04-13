---
name: virtualover
version: "1.0.0"
displayName: "VirtualOver — Overlay Virtual Elements Seamlessly onto Real Video Footage"
description: >
  Turn raw video clips into polished, layered productions with virtualover — a skill built for blending virtual graphics, overlays, and composited elements directly onto your footage. Whether you're adding branded lower-thirds, animated HUDs, or transparent PNG assets onto live video, virtualover handles the heavy lifting. Supports mp4, mov, avi, webm, and mkv formats. Ideal for content creators, marketers, and video editors who want professional overlay results without a steep learning curve.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! VirtualOver is ready to help you layer virtual graphics, overlays, and composited assets directly onto your video footage. Upload your clip and tell me what you'd like to overlay — let's build something that looks great.

**Try saying:**
- "Add a semi-transparent logo watermark to the bottom-right corner of my product demo video"
- "Overlay an animated lower-third title card that appears at the 5-second mark of my interview clip"
- "Place a virtual HUD display graphic over my drone footage to make it look like a live mission feed"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Blend the Virtual and Real Like a Pro

VirtualOver is designed for one specific job: taking your existing video footage and compositing virtual elements onto it with precision and ease. Whether that means dropping a motion graphic onto a talking-head video, layering a transparent logo watermark across a product demo, or placing an animated overlay on top of a screen recording — virtualover does it cleanly and quickly.

Unlike general-purpose video editors that bury overlay features under menus and timelines, virtualover puts the compositing workflow front and center. You describe what you want, upload your footage, and get back a result that looks intentional and polished — not slapped together.

Content creators building YouTube videos, social media managers producing branded reels, and indie filmmakers adding VFX touches will all find virtualover a natural fit. It works with the formats you already use — mp4, mov, avi, webm, and mkv — so there's no conversion step standing between you and your finished product.

## Routing Your Overlay Requests

When you describe a virtual element to composite — whether it's a 3D object, animated graphic, or tracked text — VirtualOver parses your intent and routes it to the appropriate NemoVideo rendering pipeline based on overlay type, anchor behavior, and footage context.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

VirtualOver runs on the NemoVideo backend, which handles real-time motion tracking, depth estimation, and alpha compositing to lock virtual elements convincingly onto moving footage. Every render call passes your clip metadata, overlay specs, and tracking parameters directly to NemoVideo's compositing engine.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `virtualover`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=virtualover&skill_version=1.0.0&skill_source=<platform>`

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

VirtualOver shines across a wide range of video production scenarios. Marketers use it to stamp branded overlays onto testimonial videos before publishing across social channels — keeping visual identity consistent without a full editing suite. YouTubers and streamers add lower-thirds, subscriber CTAs, and animated badges to their footage to give uploads a more produced feel.

Filmmakers and indie creators use virtualover to composite simple VFX elements — glowing screens, digital readouts, or sci-fi interface graphics — onto live-action footage without needing After Effects expertise. Corporate teams apply it to training videos, adding instructional callouts or highlight boxes that draw viewer attention to key moments.

Even podcasters producing video versions of their shows use virtualover to add chapter titles, speaker name cards, and sponsor graphics cleanly over their recordings. If your workflow involves putting something virtual on top of something real, virtualover is built for it.

## Troubleshooting

If your overlay appears in the wrong position, double-check how you described the placement. Terms like 'top-left', 'center-bottom', or specific pixel coordinates (e.g., '50px from the right edge, 30px from the bottom') give virtualover the clearest instructions and reduce placement guesswork.

If the overlay timing feels off — appearing too early or cutting out before expected — revisit your timecode instructions. Specifying start and end times in HH:MM:SS format tends to produce the most accurate results compared to vague descriptions like 'near the end'.

For transparency issues where a PNG overlay appears with a white or black background instead of being transparent, confirm that your source image file genuinely has an alpha channel. Not all PNG files exported from design tools preserve transparency correctly. Re-export from your design source with 'transparent background' explicitly enabled.

If output video quality looks degraded, mention your preferred output resolution or bitrate in your prompt — virtualover will respect quality parameters when they're clearly specified.

## Quick Start Guide

Getting started with virtualover takes less than a minute. First, upload your base video file — mp4, mov, avi, webm, and mkv are all supported. Then describe the overlay you want: specify what it is, where it should appear on the frame, when it should show up (timecode or duration), and any sizing or opacity preferences you have.

For image-based overlays like logos or PNG graphics, mention the file or describe the asset and virtualover will work with what you provide. For text overlays like lower-thirds or title cards, just describe the text content, font style preference, and position. The more specific your description, the closer the output will match your vision on the first pass.

Once processed, review the output and use follow-up prompts to fine-tune positioning, timing, or opacity. Iterating is fast — you don't need to re-upload the base footage each time you adjust overlay details.
