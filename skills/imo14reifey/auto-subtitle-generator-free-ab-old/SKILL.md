---
name: auto-subtitle-generator-free-ab-old
version: "1.0.0"
displayName: "Auto Subtitle Generator Free — Instantly Caption Any Video Without Paying a Dime"
description: >
  Drop a video and watch captions appear in seconds — no subscriptions, no hidden fees. This auto-subtitle-generator-free skill transcribes spoken audio and burns or exports accurate subtitles for mp4, mov, avi, webm, and mkv files. Whether you're captioning a YouTube tutorial, a social media reel, or a corporate training video, you get clean, timed text without wrestling with manual sync. Built for creators, educators, and marketers who need accessibility and engagement without the price tag.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to add subtitles to your video without spending anything? Upload your file and tell me what you need — whether it's burning captions directly into the video or exporting a separate subtitle file — and the auto-subtitle-generator-free skill will take care of the rest.

**Try saying:**
- "Generate subtitles for this mp4 interview video and export them as an SRT file."
- "Add burned-in captions to my YouTube tutorial — the speaker has a slight accent so please be accurate."
- "Create subtitles for this webinar recording and split lines so no caption stays on screen longer than 3 seconds."

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Captions for Every Video, Zero Cost Attached

Most subtitle tools hide their best features behind a paywall. This skill flips that entirely. The auto-subtitle-generator-free skill listens to the spoken content in your video, converts it into precisely timed captions, and gives you ready-to-use subtitles — all without asking for a credit card.

Upload your video, and the skill gets to work detecting speech, segmenting it into readable chunks, and aligning each line to the correct timestamp. The result is a clean subtitle track that matches the natural rhythm of conversation, not awkward walls of text that disappear before you can read them.

This is especially useful for content creators who publish across multiple platforms, educators building accessible course materials, and small business owners who can't justify expensive captioning services. Whether your video is a 30-second Instagram clip or a 90-minute webinar recording, the skill handles the heavy lifting so you can focus on the content itself.

## Routing Your Caption Requests

When you submit a video for auto subtitling, ClawHub parses your input—whether it's a direct upload, a URL, or a file path—and routes the transcription job to the appropriate NemoVideo processing endpoint based on file format, language hint, and subtitle output preference.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend uses speech-to-text inference to generate frame-accurate SRT, VTT, or burned-in subtitle tracks from your video's audio stream. Subtitle timing, punctuation restoration, and multi-language detection are all handled server-side, so no local processing power is required on your end.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `auto-subtitle-generator-free`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=auto-subtitle-generator-free&skill_version=1.0.0&skill_source=<platform>`

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

## Troubleshooting

If captions appear out of sync with the audio, the most common cause is background music or overlapping speech competing with the main voice track. Try uploading a version of the video with reduced background noise, or specify which speaker the subtitles should follow if there are multiple voices.

For videos with heavy accents, technical jargon, or industry-specific terminology, subtitle accuracy improves when you provide a brief context note — for example, mentioning that the video covers medical procedures or software engineering topics helps the skill prioritize correct terminology.

If subtitle lines feel too long or flash by too quickly, request a specific maximum character count per line (typically 42 characters works well for most screens) or a minimum display duration per caption. These small adjustments make a significant difference in readability across different screen sizes.

MKV and AVI files occasionally have audio tracks encoded in less common formats. If a file fails to process, converting it to mp4 first using any free converter usually resolves the issue immediately.

## Use Cases

Content creators use this skill to make Reels, TikToks, and YouTube Shorts more engaging — studies consistently show that captioned videos hold viewer attention longer, especially when autoplay is muted.

Educators and e-learning developers rely on the auto-subtitle-generator-free skill to meet accessibility requirements without purchasing expensive transcription software. Captioned lecture recordings and training videos are often legally required in academic and corporate settings.

Small business owners producing product demos, testimonial videos, or explainer content can caption their entire video library without outsourcing to a transcription service. Marketers repurposing long-form webinar content into short clips also benefit, since each clip gets its own accurate subtitle track automatically.

Non-English speakers producing content in languages other than English will find the skill useful for generating subtitles that can later be translated, making international content distribution significantly more straightforward.

## Common Workflows

The most common workflow starts with uploading a video file — mp4, mov, avi, webm, or mkv — and choosing whether you want subtitles burned into the video itself or exported as a standalone SRT or VTT file. Burned-in captions are ideal for social media platforms that don't support external subtitle tracks, while exported files work better for YouTube, Vimeo, or video players that handle them natively.

Another popular workflow involves batch processing: uploading multiple short clips from the same series and generating consistent subtitle styling across all of them. This is common for podcast highlight reels, course module videos, and social content repurposing.

For longer recordings like webinars or interviews, users often request subtitle segmentation adjustments — breaking lines at natural pauses rather than at fixed word counts. You can specify preferences like maximum characters per line or maximum seconds per caption block, and the skill will apply those rules throughout the entire video.
