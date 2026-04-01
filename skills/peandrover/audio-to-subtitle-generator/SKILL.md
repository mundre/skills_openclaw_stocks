---
name: audio-to-subtitle-generator
version: "1.0.0"
displayName: "Audio to Subtitle Generator — Instantly Convert Speech into Accurate Subtitles"
description: >
  Tell me what you need and I'll turn your spoken audio into clean, time-synced subtitles in minutes. This audio-to-subtitle-generator skill transcribes dialogue from your video files and produces ready-to-use subtitle tracks with precise timestamps. Upload your mp4, mov, avi, webm, or mkv file and get SRT or VTT output formatted for direct use in editing tools, streaming platforms, or accessibility compliance. Built for content creators, educators, journalists, and businesses who need accurate captions without manual transcription work.
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you generate accurate, time-synced subtitles from your video's audio track. Upload your video file and tell me your preferred subtitle format or any specific requirements — let's get your captions ready to go!

**Try saying:**
- "Generate subtitles for this mp4 interview video and export them as an SRT file"
- "Create captions for my webinar recording — the speaker has a slight accent so please be extra careful with accuracy"
- "I have a 45-minute mkv documentary — can you produce a VTT subtitle file with line breaks kept under 42 characters?"

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Turn Every Word Spoken Into Readable, Synced Subtitles

Whether you're publishing a YouTube tutorial, captioning a corporate training video, or making a documentary accessible to deaf and hard-of-hearing audiences, getting subtitles right matters. This skill listens to the audio in your video file and converts every spoken word into a properly timed subtitle file — no manual typing, no tedious timestamp adjustments, and no expensive transcription services required.

The audio-to-subtitle-generator works by analyzing the speech track in your uploaded video, segmenting it into readable lines, and attaching precise start and end timestamps to each segment. The result is a subtitle file you can drop directly into your video editor, upload to YouTube or Vimeo, or embed into your website player.

This is especially valuable for multilingual teams, solo creators working at scale, or anyone who needs to repurpose recorded content across multiple formats. Instead of spending hours scrubbing through a timeline, you get a complete subtitle draft in a fraction of the time — ready to review, edit if needed, and publish with confidence.

## Routing Your Transcription Requests

Each subtitle generation request is parsed for audio source, language preference, and caption format, then routed to the appropriate transcription pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend handles speech-to-text processing by analyzing audio waveforms, detecting speaker segments, and outputting time-coded subtitle tracks in SRT, VTT, or plain text formats. Requests are authenticated via bearer token and processed asynchronously, with subtitle files returned once the transcription job completes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `audio-to-subtitle-generator`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=audio-to-subtitle-generator&skill_version=1.0.0&skill_source=<platform>`

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

## Best Practices

For the most accurate subtitle output, start with the cleanest audio possible. Videos with minimal background noise, consistent microphone placement, and clear speech will produce subtitles that need little to no manual correction after generation.

If your video features technical jargon, brand names, or industry-specific terminology, mention key terms upfront so they can be handled with greater care during transcription. This is particularly useful for medical, legal, or technology-focused content where a misheard word can change meaning significantly.

Keep subtitle line lengths readable — aim for no more than two lines on screen at a time and avoid breaking sentences mid-thought when possible. When reviewing your generated subtitles, pay special attention to speaker transitions and moments with overlapping dialogue, as these are the most common areas where timing may need a small manual nudge before publishing.

## Quick Start Guide

Getting started with the audio-to-subtitle-generator is straightforward. Begin by uploading your video file in one of the supported formats: mp4, mov, avi, webm, or mkv. Once uploaded, specify your preferred output format — SRT is the most universally compatible, while VTT works best for web-based players and HTML5 video.

If your video contains multiple speakers, mention that upfront so subtitles can be segmented clearly between voices. You can also specify a maximum characters-per-line limit if your platform has display constraints — 42 characters per line is a common broadcast standard.

Once processing is complete, you'll receive your subtitle file ready for download. You can import it directly into Adobe Premiere Pro, DaVinci Resolve, Final Cut Pro, or upload it alongside your video on YouTube, Vimeo, or any streaming platform that accepts external caption files.

## Use Cases

The audio-to-subtitle-generator serves a wide range of real-world workflows. Content creators on YouTube and TikTok use it to add captions that boost watch time and reach viewers who watch without sound — a habit that now represents over 85% of mobile video consumption.

Educators and e-learning developers rely on it to make course videos ADA and WCAG compliant, ensuring students with hearing impairments have full access to lecture content. Legal and medical professionals use it to transcribe recorded depositions, patient consultations, or training sessions where accuracy and timestamping are critical for documentation.

Journalists and podcast producers convert recorded interviews into subtitle files that double as searchable transcripts. Corporate communications teams use it to caption internal town halls, product demos, and onboarding videos — making content reusable across global teams regardless of language or hearing ability.
