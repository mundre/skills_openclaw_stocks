---
name: video-caption-generator-ai
version: "1.0.0"
displayName: "Video Caption Generator AI — Auto-Create Accurate Subtitles & Captions for Any Video"
description: >
  Tired of manually transcribing dialogue and syncing captions frame by frame? The video-caption-generator-ai skill automates the entire captioning workflow — from speech detection to timestamped subtitle export. Generate SRT, VTT, or plain-text captions for YouTube videos, reels, interviews, webinars, and more. Supports multiple languages, speaker detection, and custom styling cues. Built for content creators, video editors, educators, and marketing teams who need accurate, publish-ready captions without the tedious manual effort.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm your Video Caption Generator AI — ready to turn your video's spoken content into clean, timestamped captions. Drop in your video details, transcript, or audio description and let's get your captions created right now.

**Try saying:**
- "Generate an SRT caption file for a 5-minute product demo video with these timestamps and dialogue..."
- "Create bilingual captions in English and Spanish for this interview transcript, formatted for YouTube upload"
- "Write styled captions with speaker labels for a two-person podcast video, exported in WebVTT format"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/video-caption-generator-ai/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Any Video Into Fully Captioned Content Instantly

Creating captions for video content used to mean hours of rewinding, typing, and manually adjusting timestamps — a workflow that slows down even the most experienced video producers. The video-caption-generator-ai skill changes that entirely by intelligently processing spoken audio and generating synchronized, accurate captions ready for publishing.

Whether you're producing short-form social content, long-form educational videos, corporate training materials, or podcast recordings converted to video, this skill adapts to your content type. You can request captions in multiple languages, ask for speaker-labeled transcripts, or generate caption files in specific formats like SRT or WebVTT that plug directly into your editing software or hosting platform.

The result is a dramatically faster post-production pipeline. Instead of captioning being a bottleneck at the end of your workflow, it becomes a one-prompt task. Content teams can caption entire video libraries in the time it previously took to caption a single clip — making accessibility and SEO optimization achievable at scale.

## Caption Request Routing Logic

When you submit a video file or URL, the skill parses your input to determine whether to trigger transcription, translation, subtitle formatting, or a burn-in caption export pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Transcription API Reference

The backend leverages a speech-to-text cloud engine that processes audio streams frame-by-frame, aligning word-level timestamps to generate SRT, VTT, or ASS caption files with speaker diarization support. Large video files are chunked into segments for parallel processing, reducing turnaround time on long-form content.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-caption-generator-ai`
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

Captions generated by the video-caption-generator-ai skill are designed to slot directly into the most common video production and publishing workflows. SRT files are compatible with Adobe Premiere Pro, DaVinci Resolve, Final Cut Pro, and most cloud-based video editors — simply import the caption file as a subtitle track.

For YouTube and Vimeo uploads, request WebVTT or SRT format and upload the file directly through each platform's subtitle management panel. Both platforms support manual caption file uploads, giving you full control over caption appearance and timing.

If you're embedding video on a website, ask for captions in WebVTT format, which pairs with the HTML5 video element's native track tag. For accessibility compliance workflows, you can also request captions formatted to meet WCAG 2.1 AA standards, including proper punctuation, sound effect descriptions, and speaker identification cues built into the output.

## Performance Notes

The video-caption-generator-ai skill performs best when provided with clear audio descriptions, existing rough transcripts, or detailed dialogue input. Caption accuracy is closely tied to the quality and clarity of the source material you provide — clean dialogue with minimal crosstalk yields the most precise timestamp alignment.

For longer videos exceeding 30 minutes, consider breaking content into logical segments (by scene, chapter, or speaker turn) before submitting. This improves output coherence and makes it easier to review or edit captions in sections rather than as one large block.

When requesting multilingual captions, specify the target language and any regional dialect preferences upfront. The skill handles translation and caption formatting simultaneously, but flagging technical terminology, brand names, or proper nouns in your prompt helps preserve accuracy across language outputs.

## Troubleshooting

If generated captions appear misaligned with your expected timing, double-check that the timestamps or timecodes you provided in your prompt match the actual video duration and pacing. Even small discrepancies in start times can cascade across a full caption file.

For captions that truncate mid-sentence or split awkwardly across lines, include a note in your prompt specifying your preferred maximum characters per caption line (typically 42 characters for broadcast standards or 32 for mobile-first content). This gives the skill the formatting constraints it needs to break lines naturally.

If speaker labels are missing or incorrect in a multi-person video, provide a brief speaker roster in your prompt — names, approximate voice descriptions, or turn-taking cues. This context dramatically improves attribution accuracy in interview or panel-style video content.
