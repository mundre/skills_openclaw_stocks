---
name: video-caption-generator-free-ab2o-0330
version: "1.0.0"
displayName: "Video Caption Generator Free — Auto-Transcribe & Subtitle Any Video Instantly"
description: >
  Tell me what you need and I'll generate accurate captions for your video — no subscriptions, no hidden fees. This video-caption-generator-free skill automatically transcribes spoken audio into timed subtitles, letting you add readable captions to any mp4, mov, avi, webm, or mkv file. Perfect for content creators, educators, and marketers who need accessible, searchable video content without the cost barrier. Outputs clean SRT or burned-in captions with adjustable styling.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you add free, accurate captions to your videos — just share your file or describe your captioning needs, and let's get your subtitles generated right away.

**Try saying:**
- "Generate captions for this mp4 interview video and give me an SRT file I can import into Premiere Pro"
- "Add burned-in subtitles to my webm tutorial video with white text and a dark background"
- "Transcribe the speech in this mov file and caption it in Spanish with English subtitles below"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn Any Video Into Captioned Content Instantly

Getting captions onto your videos shouldn't require a paid subscription or a complicated workflow. This skill was built for anyone who needs accurate, readable subtitles without jumping through hoops — whether you're a solo creator posting on social media, a teacher making course content accessible, or a business adding captions to training videos.

Upload your video file in any common format — mp4, mov, avi, webm, or mkv — and the skill listens to the audio, identifies speech, and produces timed caption text that matches what's being said on screen. You can choose to receive a downloadable SRT file to import into your editor, or have the captions burned directly into the video as permanent subtitles.

The result is a fully captioned video that's more accessible to deaf and hard-of-hearing viewers, easier to watch in sound-sensitive environments like offices or public spaces, and more likely to perform well on platforms that reward caption use. No technical setup required — just describe what you need and let the skill handle the rest.

## Routing Your Caption Requests

When you submit a video URL or upload a file, the skill automatically routes your transcription or subtitle request to the appropriate NemoVideo processing pipeline based on format, language detection, and caption output type.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend powers real-time speech-to-text transcription, auto-syncing burned-in or sidecar subtitles directly to your video timeline with frame-accurate timestamps. Supported outputs include SRT, VTT, and embedded caption formats for instant download or streaming.

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

## Integration Guide

Once your captions are generated, integrating them into your existing workflow is straightforward. If you requested an SRT file, you can import it directly into video editors like Adobe Premiere Pro, DaVinci Resolve, Final Cut Pro, or CapCut — each of these accepts standard SRT format without any conversion needed.

For platforms like YouTube and Vimeo, you can upload the SRT file in the video's caption settings, giving you the flexibility to edit timing or wording after the fact. If you chose burned-in captions, the output video is ready to upload anywhere without any additional steps.

When working with longer videos, consider splitting them into segments before uploading — this can improve transcription accuracy for content with multiple speakers or background noise. The skill supports mp4, mov, avi, webm, and mkv, so no pre-conversion is needed for most source files.

## Tips and Tricks

For the most accurate captions, use source videos with clear audio and minimal background noise. If your video has music overlapping dialogue, mention this upfront so the skill can prioritize speech detection accordingly.

If your video contains technical jargon, industry terms, or proper nouns, include a brief note with the correct spellings — this helps the transcription match your actual content rather than substituting phonetically similar common words.

Want captions in a different language? Specify the target language when making your request. The skill can transcribe audio and generate captions in multiple languages, making it especially useful for multilingual audiences or international content distribution.

For social media content, ask for captions with shorter line lengths and faster reading pace to match mobile viewing habits — short, punchy caption blocks tend to perform better on platforms like Instagram Reels and TikTok.

## Performance Notes

Caption accuracy is strongly tied to audio quality. Videos recorded in quiet environments with a close microphone will yield near-perfect transcription, while footage shot outdoors or in crowded spaces may require light editing of the generated captions.

File size and video length affect processing time. Short clips under five minutes typically return results quickly, while longer videos — such as full webinars or lectures — may take additional time to process. Uploading in mp4 or webm format tends to be the most efficient for processing speed.

The skill handles multi-speaker content well in most cases, but for roundtable discussions or interviews with overlapping speech, results may occasionally merge speaker lines. In those situations, reviewing the SRT output before final export is a good habit. Burned-in caption rendering is final, so always review an SRT file first if precision matters.
