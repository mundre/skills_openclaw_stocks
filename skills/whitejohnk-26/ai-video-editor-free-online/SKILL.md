---
name: ai-video-editor-free-online
version: "1.0.0"
displayName: "AI Video Editor Free Online — Edit, Trim & Enhance Videos Instantly Without Downloads"
description: >
  Turn raw footage into polished, share-ready videos without installing a single app. This ai-video-editor-free-online skill lets you describe your editing goals in plain language — cut clips, add captions, adjust pacing, apply transitions, or reformat for different platforms — and get precise, actionable editing guidance or automated output instantly. Built for content creators, educators, small business owners, and social media managers who need professional results without a steep learning curve or a subscription paywall.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your video link, footage description, or editing goal and I'll give you a step-by-step edit plan or direct output. No video yet? Just describe the style and content you want.

**Try saying:**
- "I have a 12-minute interview recording. Help me cut it down to a 90-second highlight reel focused on the key insights, and suggest where to add captions."
- "I filmed a product unboxing in landscape mode but I need it in vertical 9:16 format for Instagram Reels — how do I reframe and trim it to under 60 seconds?"
- "Can you help me add auto-generated subtitles, a logo watermark in the corner, and a fade-to-black ending to my tutorial video before I upload it to YouTube?"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Edit Any Video with Just Your Words

Most people have footage sitting on their phones or drives that never gets used — because editing feels like too much work. This skill changes that. By combining AI-driven understanding of video structure with a free, browser-based approach, it lets you describe what you want and get results without touching a timeline or learning keyboard shortcuts.

Whether you're cutting a long interview down to the highlights, adding subtitles for accessibility, reformatting a landscape video into a vertical reel, or syncing clips to a beat — this skill walks you through each step or handles it directly. You don't need prior editing experience, and you don't need to pay for premium software.

This is designed for real-world use cases: a teacher turning a lecture recording into digestible segments, a small business owner creating a product demo from a phone video, or a creator repurposing a YouTube video into TikTok clips. Fast, free, and genuinely useful — that's the entire point.

## Routing Your Edit Requests

When you submit a trim, enhancement, or AI-generated effect, your request is parsed by the intent engine and dispatched to the appropriate cloud processing node based on operation type, file format, and current queue load.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

The backend leverages a distributed GPU pipeline to handle real-time video transcoding, frame interpolation, and AI upscaling entirely server-side — no local rendering required. Each API call passes your video stream through containerized processing workers that return a shareable output URL upon completion.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-editor-free-online`
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

## Performance Notes — What to Expect

This ai-video-editor-free-online skill works best when your input is clear and your goals are defined. Vague requests like 'make it better' will produce general suggestions, while specific requests like 'remove the first 45 seconds and add a jump cut at 2:10' will produce precise, actionable output.

For very long videos (over 30 minutes), consider working in segments rather than trying to process the entire file at once. Describe each section's purpose and the skill will help you build a coherent edit across all parts.

Browser-based processing means no large file uploads are required for planning and scripting your edit — you can get a full cut list, caption text, and transition notes before touching any export tool. When you're ready to render, the skill will point you to the right free online tool for your specific output format, whether that's a quick MP4 export, a GIF clip, or a captioned story video.

## Tips and Tricks for Getting the Best Edits

When describing your footage, be specific about what matters most — mention the platform you're editing for (YouTube, TikTok, Instagram), the target length, and the tone you want (punchy, calm, educational). The more context you give, the more precise the edit guidance will be.

If you're working with a long video, break it into goals: first ask for a cut list, then handle captions, then color or audio adjustments. Tackling one layer at a time produces cleaner results than trying to do everything at once.

For social media clips, always mention the aspect ratio upfront. A 1:1 square crop for LinkedIn behaves very differently than a 9:16 vertical for Reels, and knowing this early saves you from redoing work later. You can also ask for platform-specific pacing recommendations — TikTok audiences expect faster cuts than YouTube tutorial viewers, and this skill can help you match that rhythm without guesswork.
