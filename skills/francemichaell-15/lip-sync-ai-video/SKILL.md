---
name: lip-sync-ai-video
version: "1.0.0"
displayName: "Lip Sync AI Video — Automatically Match Speech to Any Face in Video"
description: >
  Turn any video into a perfectly synced talking-head clip with lip-sync-ai-video technology that aligns mouth movements frame-by-frame to your audio track. Swap voices, dub into new languages, or animate still images to speak — all without reshooting. Ideal for content creators, marketers, educators, and localization teams who need natural-looking speech sync at scale. Supports custom audio uploads, multilingual dubbing, and realistic facial motion generation.
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome — you're one step away from perfectly synced speech in your video. Whether you're dubbing, localizing, or animating a face to match new audio, drop your video and audio details below and let's get started.

**Try saying:**
- "I have a 60-second product demo video in English and I want to dub it into French with matching lip sync — the French audio file is ready to upload."
- "Can you animate this headshot photo of our CEO to speak a 30-second welcome message I recorded? I need it to look like a real talking-head video."
- "My recorded voiceover doesn't match the on-screen presenter's mouth movements because we re-recorded the script after filming — can you re-sync the lips to the new audio?"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Make Any Face Speak Any Words, Instantly

Lip Sync AI Video takes the friction out of one of video production's most tedious challenges: getting a person's mouth movements to match the audio they're supposed to be saying. Whether you're dubbing a product explainer into Spanish, animating a spokesperson photo, or fixing a mismatch between recorded audio and on-camera delivery, this skill handles the frame-level alignment automatically.

The underlying process analyzes facial landmarks in each frame of your video, then regenerates the mouth region to match the phonetic rhythm and shape of your target audio. The result is a natural, fluid lip movement that holds up under normal viewing conditions — no uncanny valley, no obvious patching.

This skill is built for practical production workflows. Marketers use it to localize ad campaigns without recasting talent. Educators use it to update course videos when scripts change. Podcasters and YouTubers use it to animate static profile images into engaging talking avatars. Whatever your use case, the goal is the same: believable speech-to-face synchronization with minimal manual effort.

## Routing Your Lip Sync Requests

Each request — whether you're syncing a dubbed audio track, swapping dialogue, or animating a still face — gets parsed for target video, source audio, and face region before being dispatched to the appropriate lip sync pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

Lip sync processing runs on a GPU-accelerated cloud backend that handles facial landmark detection, mouth region isolation, and frame-by-frame phoneme-to-viseme rendering entirely server-side. You never need local compute — the API accepts your video and audio assets, queues the synthesis job, and streams back the composited output once rendering completes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `lip-sync-ai-video`
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

## Performance Notes

Lip sync quality is directly tied to the quality of your input files. Videos with a clear, front-facing or near-front-facing subject produce the most accurate mouth reconstruction — profiles beyond roughly 45 degrees will show reduced fidelity in the generated lip region. Lighting consistency across frames also matters; heavy flickering or extreme shadows near the mouth area can introduce artifacts.

For audio, clean mono or stereo recordings with minimal background noise yield the tightest phoneme mapping. Heavily compressed audio (low-bitrate MP3s) or recordings with significant reverb may cause slight timing drift on fast-speech segments. WAV or high-bitrate AAC files are preferred.

Processing time scales with video length and resolution. A 1080p, 2-minute clip typically completes in under 4 minutes. For batch localization jobs — syncing the same video to multiple language tracks — queuing them sequentially is more stable than simultaneous submissions.

## Quick Start Guide

Getting your first lip-sync-ai-video result takes three inputs: your source video, your target audio, and any preferences about output format or quality level.

**Step 1 — Prepare your video.** Export or locate your source clip. MP4 with H.264 encoding works best. Trim it to only the segment that needs syncing — don't include long silent intros or outros, as these add processing time without benefit.

**Step 2 — Prepare your audio.** Your replacement audio should match the intended duration of the video segment. If the new audio is longer or shorter than the original, let us know whether you want the video stretched, trimmed, or padded with silence.

**Step 3 — Submit and specify.** Share your files or links and describe the subject (single speaker, multiple speakers, animated avatar, etc.). Mention the target language if it differs from the source, and flag any sections where sync accuracy is especially critical, such as close-up shots.

You'll receive a download link to your synced output along with a brief quality summary.

## Best Practices

For the cleanest lip-sync-ai-video output, shoot or select source footage where the speaker's mouth is clearly visible and unobstructed — no hands near the face, no large mustaches covering the upper lip, and no motion blur from fast head movements.

When dubbing into another language, account for duration differences. Romance languages tend to run 15–20% longer than English for the same content. Either have your voice actor record a timed version matched to the original clip length, or allow for slight video speed adjustment in your brief.

If you're animating a still photo rather than a video, use a high-resolution image (at least 512×512px) with neutral expression and even lighting. Images where the subject is already mid-expression or laughing produce less natural results than a relaxed, closed-mouth or slightly open neutral pose.

For professional deliverables, always do a final review at 1x playback speed before publishing. Sync that looks slightly off at 2x speed is usually imperceptible at normal speed, but a real mismatch on a stressed syllable in a close-up will be noticeable — flag those moments for a targeted re-render.
