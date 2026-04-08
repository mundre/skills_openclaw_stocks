---
name: free-lip-sync-ai
version: "1.0.0"
displayName: "Free Lip Sync AI — Automatically Match Mouth Movements to Any Audio Track"
description: >
  Turn any video into a perfectly synced masterpiece without spending a cent. This free-lip-sync-ai skill analyzes audio waveforms and facial movements to realign mouth animations frame-by-frame, making dubbed content, translated videos, and animated characters look naturally spoken. Ideal for content creators, educators, filmmakers, and social media producers who need professional lip sync results without costly software subscriptions.
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to your free lip sync AI workspace — where out-of-sync audio and awkward dubbed footage become a thing of the past. Share your video and audio files to get started, or describe your lip sync challenge and I'll walk you through it.

**Try saying:**
- "Sync mouth movements to new audio"
- "Fix drifting lip sync in video"
- "Remap dubbed dialogue to face"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Sync Every Word Without Touching the Timeline

Getting lip sync right has traditionally required expensive software, a skilled editor, and hours of frame-by-frame adjustments. This free-lip-sync-ai skill changes that entirely — just bring your video and your audio, and let the AI handle the alignment automatically.

The skill works by detecting facial landmarks in your footage, analyzing the phoneme structure of your audio track, and remapping mouth movements so they match what's being said. Whether you're dubbing a foreign-language film, syncing a voiceover to an animated character, or fixing a recording where audio and video drifted apart, the result is a natural, believable performance that holds up under scrutiny.

This is built for creators who move fast and can't afford to lose hours on technical corrections. Social media producers, indie filmmakers, YouTube educators, and localization teams will find this skill especially useful. No prior video editing knowledge is required — describe your project, share your files, and get synced output ready to publish.

## Routing Sync Requests Intelligently

When you submit an audio track, your lip sync request is parsed for phoneme timing, speaker count, and output format before being dispatched to the optimal processing node.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

The backend runs a phoneme-to-viseme mapping pipeline that analyzes your audio waveform in real time, generating frame-accurate mouth shape sequences at up to 60fps. All rendering jobs are queued through a distributed cloud engine, so heavy files won't stall your session.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-lip-sync-ai`
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

Getting free-lip-sync-ai into your existing production workflow is straightforward. For individual creators, the simplest path is to export your video and audio as separate files from your editing timeline — most NLEs like DaVinci Resolve, Premiere Pro, or Final Cut Pro support this natively — then pass both files to this skill for sync processing before reimporting the result.

For teams handling batch localization work, you can describe multiple video-audio pairs in a single session and receive queued processing instructions. The skill supports common video formats including MP4, MOV, and WebM, and accepts audio in MP3, WAV, and AAC formats.

Once synced output is returned, it drops directly back into your timeline as a replacement clip with no additional reformatting needed. For recurring workflows — such as a weekly dubbed video series — you can save your project parameters as a prompt template and reuse them each session to maintain consistent output settings across episodes.

## Performance Notes

Free-lip-sync-ai performs best when the source video contains a clearly visible, front-facing or near-front-facing subject with unobstructed mouth visibility. Heavily side-angled shots, extreme close-ups of non-facial areas, or footage with persistent occlusion (hands over the mouth, masks, heavy beards) may reduce landmark detection accuracy and result in less precise sync.

For audio, clean mono or stereo tracks with minimal background noise produce the sharpest phoneme mapping. Heavily compressed audio or tracks with significant reverb can cause the AI to misread consonant boundaries, slightly affecting timing precision on fast speech passages.

Video resolution of 720p or higher is recommended for reliable facial landmark tracking. Lower-resolution footage is still processable but may yield softer sync accuracy, particularly around subtle mouth shapes like 'f', 'v', and 'th' sounds. Processing time scales with clip length — shorter clips under 3 minutes typically return results significantly faster.

## Use Cases

Free-lip-sync-ai covers a wide range of practical production scenarios that come up constantly for modern creators. The most common use case is video localization — when a video is dubbed into another language, the translated audio rarely matches the original mouth timing, and this skill re-syncs the face to the new track seamlessly.

Content creators who record voiceovers separately from their on-camera footage use this skill to fix natural drift that occurs when audio and video are captured on different devices or edited independently. Even a 200ms offset is noticeable to viewers, and this skill corrects it in one pass.

Animation studios and indie game developers use free-lip-sync-ai to apply dialogue audio to character models without manual keyframe animation. Podcast producers who record video alongside audio and experience sync issues during export also benefit heavily. It's equally useful for corporate training videos, e-learning modules, and accessibility-focused re-dubbing projects where clear, believable speech presentation matters.
