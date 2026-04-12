---
name: online-video-editor
version: 3.0.2
displayName: "Online Video Editor — Edit, Trim & Export Polished Videos Without Software"
description: >
  Turn raw, uncut footage into share-ready videos without installing a single app. This online-video-editor skill handles trimming, cutting, captioning, transitions, and format conversion through simple chat commands. Whether you're producing social content, training videos, or event highlights, you get precise editing guidance and output-ready instructions tailored to your platform and audience.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
apiDomain: https://mega-api-prod.nemovideo.ai
---

## Getting Started

> Welcome to your online video editor assistant — whether you're trimming a clip, adding captions, or building a full highlight reel, I'm ready to help you get it done. Tell me what footage you're working with and what you want the final video to look like!

**Try saying:**
- "I have a 15-minute interview recording and need to cut it down to a 2-minute highlight reel for LinkedIn. The guest talks about remote work culture — which parts should I keep?"
- "Can you help me add animated captions to my cooking tutorial video so it works without sound on Instagram Reels? The video is 45 seconds long."
- "I recorded a birthday event on my phone in portrait mode but I need a horizontal version for YouTube. How do I reframe and export it correctly?"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Edit Any Video From Your Browser, Instantly

Most video editing tools demand a steep learning curve, expensive subscriptions, or a powerful desktop machine. This skill flips that entirely. By working through natural conversation, you can describe exactly what you want your video to look like — and get step-by-step guidance, edit plans, or ready-to-execute instructions without ever opening a timeline editor.

The online video editor skill is built for creators who move fast. Need to cut a 10-minute interview down to a punchy 90-second highlight reel? Want to add captions in a specific font style for Instagram Reels? Trying to stitch together clips from different devices into one cohesive piece? Describe it, and the skill maps out exactly how to get there.

This isn't a one-size-fits-all approach. Every edit recommendation accounts for your target platform, aspect ratio, audience, and tone. From YouTube long-form to TikTok vertical clips to corporate presentation videos, the skill adapts its guidance to match what you're actually making.

## Routing Edits to the Right Tool

When you submit a request — whether it's trimming a clip, adding captions, applying a color grade, or exporting in a specific codec — ClawHub parses your intent and routes it to the matching video processing endpoint automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

All timeline edits, transitions, and export jobs run through a distributed cloud rendering backend, so your browser never handles the heavy transcoding work. Requests are queued, processed frame-accurately, and returned as a streamable or downloadable output file without requiring any local software.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `online-video-editor`
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

## Use Cases — What You Can Build With This Skill

Content creators use this skill to repurpose long-form YouTube videos into short clips for Shorts, Reels, and TikTok — getting a complete cut list without manually scrubbing through footage.

Small business owners use it to turn product demo recordings into polished explainer videos, complete with caption suggestions, background music cues, and call-to-action overlays timed to key moments.

Educators and course creators rely on it to restructure lecture recordings, remove filler sections, and plan chapter markers that make long videos easier to navigate on platforms like Teachable or Kajabi.

Event videographers use the skill to plan highlight reels from wedding or conference footage — identifying the strongest emotional beats, sequencing clips for narrative flow, and choosing appropriate transition styles for the event's tone.

## Tips and Tricks for Faster, Better Edits

When describing your footage, include the platform you're publishing to upfront. A video destined for TikTok needs different pacing, aspect ratio, and caption placement than one going to YouTube or a company website. Mentioning this early saves multiple rounds of revision.

For trimming requests, give timestamps or describe the content at each section rather than just saying 'cut the boring parts.' The more context you provide — like 'the speaker repeats themselves between minutes 3 and 5' — the more precise the edit plan you'll receive.

If you're working with multiple clips that need to be stitched together, list them in order with a one-line description of each. This lets the skill suggest the best transition types, pacing adjustments, and whether a title card or intro sequence would help the final video feel cohesive.

## Troubleshooting Common Online Video Editing Problems

If your exported video looks pixelated or blurry, the issue is almost always export resolution or bitrate settings, not the edit itself. Describe your source footage quality and the platform you're uploading to, and the skill will recommend the correct export settings for that destination.

Audio sync issues — where the video and audio drift apart mid-clip — typically happen when mixing footage from different devices or frame rates. Share the specs of each clip (frame rate, recording device) and you'll get a clear plan for normalizing them before editing begins.

If captions appear misaligned or overflow the frame on mobile, it's usually a font size or safe-zone issue. The skill can recommend caption positioning rules for each major platform so your text never gets cropped by a phone's interface elements.

For videos that feel too long but you're unsure what to cut, describe the goal of the video in one sentence — the skill will use that as a filter to identify which sections directly serve that goal and which are safe to remove.
