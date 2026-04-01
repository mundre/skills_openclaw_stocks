---
name: video-caption-generator-free-ab-old
version: "1.0.0"
displayName: "Video Caption Generator Free — Auto-Add Subtitles to Any Video Instantly"
description: >
  Turn raw footage into fully captioned videos without spending a dime. This video-caption-generator-free skill automatically transcribes speech and burns accurate subtitles directly into your video — no manual syncing, no expensive software. Upload your mp4, mov, avi, webm, or mkv file and get back a captioned version ready to share. Built for content creators, educators, social media managers, and anyone who wants accessible, engaging video without the hassle.
metadata: {"openclaw": {"emoji": "💬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to add captions to your video for free? Upload your mp4, mov, avi, webm, or mkv file and I'll generate accurate subtitles and embed them directly — just tell me your video and any caption preferences to get started.

**Try saying:**
- "Add captions to my interview video and make the font large enough to read on mobile"
- "Generate subtitles for this tutorial clip and position them at the bottom center of the frame"
- "Transcribe and caption my product demo video — keep the style clean and minimal"

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Captions for Every Video, Zero Cost Involved

Getting captions onto your videos used to mean paying for transcription services, wrestling with subtitle editors, or spending hours syncing text frame by frame. This skill changes that entirely. Upload your video, and it handles the heavy lifting — detecting spoken words, generating accurate caption text, and embedding those subtitles directly into your footage.

Whether you're posting a tutorial on YouTube, sharing a product demo on LinkedIn, or making a short clip accessible for hearing-impaired viewers, captions make a measurable difference in how your content performs and who it reaches. Studies consistently show that captioned videos hold viewer attention longer and perform better in feeds where autoplay runs silently.

This skill supports the most common video formats — mp4, mov, avi, webm, and mkv — so you don't need to convert anything before uploading. The result is a clean, captioned video file you can download and publish immediately. No subscriptions, no watermarks, no technical setup required.

## Caption Request Routing Logic

When you submit a video URL or upload a file, the skill automatically detects your intent — whether you need auto-subtitles, SRT export, burned-in captions, or multi-language transcription — and routes your request to the matching NemoVideo endpoint.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend powers all subtitle generation by running speech-to-text transcription, frame-synced caption alignment, and optional style rendering server-side — so no local processing is required. Supported formats include SRT, VTT, ASS, and hardcoded MP4 output with configurable font and placement settings.

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

## Performance Notes

Caption accuracy depends heavily on audio quality in your source video. Clear speech with minimal background noise produces the best transcription results — think recorded voiceovers, studio interviews, or screen recordings with system audio. Videos with heavy background music, overlapping speakers, or strong accents may produce captions that need light review before publishing.

Longer videos take more processing time than short clips. For a 5-minute video, expect a quick turnaround. For videos over 30 minutes, give the skill a moment to work through the full transcription before the captioned file is ready. Supported formats include mp4, mov, avi, webm, and mkv — files outside these formats should be converted before uploading to ensure smooth processing.

## Best Practices

For the sharpest captions, trim your video before uploading — removing long silences or dead air at the start and end helps the transcription engine focus on the actual spoken content. If your video contains technical jargon, product names, or industry-specific terms, mention them when submitting your request so caption output can be reviewed with those terms in mind.

Choose a caption style that suits your platform. Bold white text with a subtle drop shadow reads well on most backgrounds and works across mobile and desktop. If you're captioning for social media, shorter caption lines with faster refresh rates tend to feel more natural to viewers scrolling quickly through a feed.

Always watch the captioned output once before publishing. Even highly accurate auto-captions occasionally mishear a word, and a quick review catches anything that needs a small correction before your video goes live.
