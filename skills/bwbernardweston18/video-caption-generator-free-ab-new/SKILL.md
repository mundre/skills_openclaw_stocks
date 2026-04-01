---
name: video-caption-generator-free-ab-new
version: "1.0.0"
displayName: "Video Caption Generator Free — Auto-Add Subtitles to Any Video Instantly"
description: >
  Tired of manually transcribing dialogue or paying for expensive captioning services? The video-caption-generator-free skill automatically detects speech in your video and generates accurate, time-synced captions without any cost. Upload mp4, mov, avi, webm, or mkv files and get readable subtitles burned in or exported as a subtitle file. Great for content creators, educators, marketers, and anyone making videos more accessible and engaging across social platforms.
metadata: {"openclaw": {"emoji": "💬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to add captions to your video without the hassle or the cost? Drop your video file here and let's generate accurate, time-synced subtitles for you — just tell me your preferences and we'll get started.

**Try saying:**
- "Add captions to this mp4 interview video and burn them into the footage"
- "Generate a subtitle file for my webinar recording so I can upload it to YouTube"
- "Create captions for this short social media clip and style them with bold white text"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Any Video Into a Captioned, Accessible Experience

Getting captions onto your videos used to mean hiring a transcriptionist, wrestling with auto-generated gibberish, or paying monthly fees for a captioning platform. This skill changes that entirely. Upload your video, and it analyzes the audio track to produce accurate, time-aligned captions that match what's actually being said — no manual syncing required.

Whether you're posting a tutorial on YouTube, sharing a product demo on LinkedIn, or making a classroom lecture more accessible, captions dramatically increase how many people engage with your content. Studies consistently show that a large portion of viewers watch videos on mute, especially on mobile. Captions keep those viewers watching.

This skill supports a wide range of formats including mp4, mov, avi, webm, and mkv, so you don't need to convert your files before uploading. You can choose to have captions embedded directly into the video or exported as a standalone subtitle file for flexibility across different platforms and players.

## Caption Request Routing Logic

When you submit a video for auto-subtitling, your request is routed through intent detection that identifies caption style, language, and burn-in preferences before dispatching to the appropriate transcription pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend powers all subtitle generation by running speech-to-text transcription against your video's audio track, then time-stamping and formatting captions into SRT, VTT, or hardcoded formats. Free-tier requests are processed through a shared queue, so render times may vary based on video length and current load.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-caption-generator-free`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=video-caption-generator-free&skill_version=1.0.0&skill_source=<platform>`

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

The video-caption-generator-free skill covers a surprisingly wide range of real-world needs. Social media creators use it to caption Instagram Reels, TikToks, and YouTube Shorts so their content performs well even when autoplay is muted. Educators and trainers use it to make recorded lectures and onboarding videos compliant with accessibility standards like WCAG and ADA guidelines.

Marketers add captions to product demos and testimonial videos to increase watch time and conversion rates on landing pages. Podcasters who repurpose audio content into video clips rely on this skill to add readable dialogue without a separate editing workflow.

For multilingual teams, the exported subtitle file can also serve as a starting point for translation, making it easier to localize content for international audiences without starting the transcription process from scratch.

## Performance Notes

Caption accuracy depends heavily on audio clarity. Videos with a single speaker, minimal background noise, and clear enunciation will produce the most accurate results. If your video has heavy background music, overlapping voices, or strong accents, you may want to review the generated captions and make minor edits before publishing.

Processing time scales with video length. Short clips under five minutes are typically processed quickly, while longer recordings like webinars or full-length courses may take more time. For best results, avoid uploading files with corrupted audio tracks or heavily compressed codecs, as these can reduce transcription quality.

Supported formats include mp4, mov, avi, webm, and mkv. If your file is in a less common format, converting it to mp4 before uploading will generally yield the smoothest experience.
