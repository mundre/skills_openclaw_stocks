---
name: video-caption-generator-ai-ab-old
version: "1.0.0"
displayName: "Video Caption Generator AI (A/B Legacy) — Auto-Generate Accurate Captions for Any Footage"
description: >
  Just drag your footage and the video-caption-generator-ai-ab-old skill gets to work transcribing speech, syncing timestamps, and formatting captions ready for export. Built on the legacy A/B testing model variant, it handles multilingual audio, overlapping speakers, and noisy background tracks better than standard auto-caption tools. Drop in a raw interview, a tutorial walkthrough, or a social clip and get clean, readable captions with proper line breaks and timing offsets. Ideal for content creators who need reliable subtitle files without manual correction passes.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to the Video Caption Generator AI (A/B Legacy) — paste a video link or upload your file and I'll generate accurate, synced captions ready to export. Drop your footage here to get started.

**Try saying:**
- "Generate captions for this 8-minute tutorial video and export them as an SRT file with accurate timestamps"
- "My interview footage has two speakers with some background noise — can you transcribe and caption it with speaker labels?"
- "Create captions for this Instagram Reel and format them as short 2-3 word bursts for on-screen display"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Captions That Actually Sync With Your Audio

Getting captions right is harder than it looks. Automated tools often mis-time lines, split sentences at awkward breaks, or completely fumble proper nouns and technical terms. The video-caption-generator-ai-ab-old skill was built specifically to address those gaps, using a model variant that was fine-tuned through A/B testing rounds to improve sync accuracy and readability across a wide range of video types.

Whether you're working with a talking-head interview, a screen recording with voiceover, or a fast-paced social video with background music, this skill processes the audio layer and produces captions that align tightly with spoken words. It handles filler words gracefully, doesn't hallucinate lines, and respects natural pauses when deciding where to break caption blocks.

The output is practical and portable — you get caption text with timestamps that can be dropped into editing timelines, uploaded as subtitle files, or reformatted for accessibility compliance. No post-processing gymnastics required. If you've ever spent an hour fixing auto-generated captions by hand, this is the workflow you've been looking for.

## Caption Request Routing Logic

Every caption request you submit gets parsed by the A/B Legacy dispatcher, which evaluates your footage metadata and queues it to the appropriate transcription pipeline based on language model version and frame rate compatibility.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Legacy API Backend Reference

The V2 legacy cloud processor handles all caption generation jobs through a distributed speech-to-text layer that timestamps each caption block at the frame level, syncing dialogue boundaries to your original timecode. Batch caption exports and SRT/VTT outputs are rendered server-side before being pushed back to your session workspace.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-caption-generator-ai-ab-old`
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

## Tips and Tricks

For best results with video-caption-generator-ai-ab-old, upload audio that's as clean as possible — even a basic noise reduction pass before submitting will noticeably improve transcription accuracy on clips recorded in echoey rooms or outdoors.

If your video contains technical jargon, product names, or uncommon proper nouns, include a short glossary or word list in your prompt. The skill will prioritize those spellings over its default phonetic guesses, which cuts down on correction time significantly.

When working with multi-speaker content, specify whether you want speaker labels in the output. The A/B legacy model handles overlapping dialogue better when it knows to look for turn-taking patterns, so flagging this upfront produces cleaner results than asking for labels after the fact.

For social-format captions — short punchy lines meant to appear as on-screen text — ask for a maximum of 4-5 words per caption block. The skill will re-segment the transcript to fit that constraint rather than just splitting the standard output.

## Performance Notes

The video-caption-generator-ai-ab-old variant performs strongest on English-language content with a single primary speaker, where timestamp sync accuracy typically lands within 200–400ms of the actual spoken word. For multilingual or code-switched audio, expect slightly longer processing time as the model identifies language boundaries before transcribing each segment.

Very long videos — anything over 45 minutes — may benefit from being split into chapters or segments before submission. The skill can process longer files, but chunking the input often produces more consistent caption quality across the full runtime rather than degradation toward the end of a long audio track.

Background music at moderate volume is handled well, but heavy bass-heavy soundtracks or audio where music volume matches speech volume will reduce accuracy. If your footage has this issue, a quick vocal isolation step beforehand is worth the extra minute. Caption export formats supported include SRT, VTT, and plain text with inline timestamps.
