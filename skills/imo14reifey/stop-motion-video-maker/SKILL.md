---
name: stop-motion-video-maker
version: "1.0.0"
displayName: "Stop Motion Video Maker — Bring Still Images to Life with Animation"
description: >
  Turn a sequence of photos or video frames into a fluid stop-motion-video-maker animation in minutes. Upload your images or footage in mp4, mov, avi, webm, or mkv format and control frame rate, playback speed, and loop behavior to craft everything from quirky clay-figure animations to product showcases and timelapse-style reels. Built for artists, educators, content creators, and hobbyists who want polished stop-motion results without complex software.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! 🎞️ Ready to turn your photos or footage into a stop-motion animation? Upload your images or video file and tell me your preferred frame rate or style — let's build something frame-worthy together!

**Try saying:**
- "I have 120 JPEG photos of a clay figure I animated on my desk — can you turn them into a stop-motion video at 12 frames per second?"
- "Convert this timelapse MOV file into a stop-motion style video with a slightly choppy, hand-crafted look at 8 fps."
- "I want to make a stop-motion product reveal using 60 still images of a rotating sneaker — output it as an MP4 that loops cleanly."

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Frame by Frame, Your Story Comes Alive

Stop-motion animation has a charm that no smooth CGI can replicate — the slight imperfections, the tactile feel, the sense that human hands crafted every single frame. This skill is built specifically to help you harness that magic without needing a film school degree or expensive editing software.

Upload a batch of photos you've shot on your phone, a timelapse clip, or even a short video you want to re-sequence as a stop-motion piece. You control the frame rate to set the pace — slow and dreamy or fast and snappy — and the skill stitches everything together into a clean, exportable animation ready for social media, presentations, or personal projects.

Whether you're animating LEGO figures on your kitchen table, documenting a painting coming together stroke by stroke, or building a product reveal for your brand, this tool gives you a straightforward path from a pile of still images to a finished stop-motion video that actually looks intentional and polished.

## Routing Your Animation Requests

Each request — whether you're sequencing frames, adjusting frame rate, or exporting your flipbook animation — is parsed and routed to the matching stop motion pipeline endpoint automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

The NemoVideo backend stitches your uploaded still images into a timed frame sequence, applying your chosen fps and transition settings to render the final stop motion output. Every frame order, dwell time, and export format you specify flows directly through the NemoVideo API.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `stop-motion-video-maker`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=stop-motion-video-maker&skill_version=1.0.0&skill_source=<platform>`

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

**Large image sets:** Uploading sequences of 200+ high-resolution images will take longer to process. For faster results, resize images to 1920×1080 or lower before uploading — stop-motion animation rarely requires 4K source frames to look great at typical playback sizes.

**Frame rate and file size:** Lower frame rates (8–12 fps) produce smaller output files and are stylistically appropriate for most stop-motion aesthetics. Higher frame rates (18–24 fps) increase file size and processing time but create smoother motion, which suits product photography or nature timelapse conversions.

**Video source files:** When converting an existing mp4, mov, avi, webm, or mkv file into a stop-motion style, the skill extracts individual frames and re-sequences them at your target fps. Very long source videos (over 5 minutes) may be trimmed or require you to specify a clip range to keep processing manageable.

**Export format:** The default output is mp4 (H.264), which offers broad compatibility across devices, platforms, and social media upload tools.

## Frequently Asked Questions

**What file types can I upload?** You can upload images in common formats (JPG, PNG) as a sequence, or existing video files in mp4, mov, avi, webm, or mkv that you'd like re-rendered as stop-motion.

**How many frames do I need for a good stop-motion video?** It depends on your desired length and frame rate. At 12 fps, 60 images gives you a 5-second clip. For smoother motion at 24 fps, plan for more frames. The skill works well anywhere from 8 fps (classic choppy stop-motion) to 24 fps (fluid animation).

**Can I add music or a voiceover?** Currently the skill focuses on the visual stop-motion assembly — frame sequencing, timing, and export. Audio layering is best handled in a secondary editing step after export.

**Will the output loop?** Yes — you can request a seamless loop output, which is especially useful for social media posts, GIFs converted from the video, or display installations.
