---
name: ai-video-creator-free
version: "1.0.0"
displayName: "AI Video Creator Free — Turn Text, Images & Ideas Into Polished Videos"
description: >
  Drop a script, a handful of images, or even just a rough idea, and watch it transform into a shareable video — no editing software, no subscription wall, no steep learning curve. This ai-video-creator-free skill handles the heavy lifting: sequencing visuals, matching pacing, generating captions, and structuring your content into a cohesive clip. Built for creators, educators, small business owners, and social media managers who need quality video output without the cost or complexity of traditional tools.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your topic, script, or a few bullet points and I'll turn it into a complete video outline with scenes, captions, and pacing. No content yet? Just describe the video you have in mind and I'll start from there.

**Try saying:**
- "Create a 30-second product promo video script for my handmade candle shop, targeting Instagram Reels with upbeat pacing and on-screen text callouts"
- "I have 8 photos from our company event — build me a video storyboard with scene order, caption suggestions, and a recommended background music mood"
- "Write a scene-by-scene breakdown for a 2-minute YouTube explainer video about how to start composting at home, aimed at beginners"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# From Raw Idea to Ready-to-Share Video, Instantly

Most people have content worth sharing — a product story, a tutorial, a quick announcement — but hit a wall when it comes to actually making the video. Editing timelines, sourcing music, syncing visuals, writing captions: it stacks up fast. This skill cuts through all of that.

With the AI Video Creator Free skill, you describe what you want or hand over your raw materials — text, bullet points, image descriptions, a script — and it builds the structure, narrative flow, and visual plan for your video. Whether you're making a 15-second Instagram reel concept or a 3-minute explainer, the output is practical, formatted, and ready to produce or hand off to a simple video tool.

This is especially useful for solo creators and small teams who can't justify expensive software or agency rates. You get the creative direction, scene-by-scene breakdowns, suggested visuals, on-screen text, and pacing guidance — all free, all fast, all tailored to your specific message and audience.

## Routing Your Video Requests

When you submit a prompt, image, or script, AI Video Creator Free parses your input and routes it to the appropriate generation pipeline — text-to-video, image-to-video, or idea expansion — based on the detected content type and chosen output style.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

AI Video Creator Free offloads all rendering to a distributed cloud backend, where your assets are queued, processed through diffusion-based video synthesis models, and returned as a downloadable MP4 or shareable link. Render times vary by resolution, clip length, and current queue load — lightweight 720p clips typically complete in under two minutes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-creator-free`
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

## Tips and Tricks for Getting the Best Results

The more context you give, the sharper the output. Instead of saying 'make a video about my bakery,' try: 'make a 45-second TikTok video for my sourdough bakery, targeting local customers, with a warm and rustic tone.' Platform, length, tone, and audience all shape how scenes are structured and how captions are written.

If you already have a rough script or bullet points, paste them in — the skill will reformat and enhance them rather than starting from scratch, which saves time and keeps your voice intact.

For image-based videos, describe each photo or asset briefly (e.g., 'photo of a latte on a wooden table, morning light'). This helps generate accurate scene descriptions and transition suggestions even without uploading files directly.

Finally, ask for variations. If the first video outline feels too formal or too fast-paced, just say so. You can request a shorter cut, a different hook, or a version optimized for silent autoplay — the skill adapts quickly.

## Performance Notes — What to Expect

This skill is optimized for planning, scripting, and structuring video content — it outputs scene-by-scene breakdowns, on-screen text suggestions, voiceover scripts, caption copy, and pacing notes. It does not render or export actual video files, but its output is designed to work seamlessly with free tools like CapCut, Canva Video, or DaVinci Resolve.

Response quality is strongest for videos under 5 minutes. For longer formats like full tutorials or documentary-style content, break the request into segments (intro, body, outro) for cleaner, more focused output.

The skill handles a wide range of formats: vertical (9:16 for Reels/TikTok), square (1:1 for feeds), and horizontal (16:9 for YouTube). Specifying your format upfront ensures the scene structure and text placement suggestions match the actual screen dimensions you're working with.

Expect turnaround in seconds. Each output is a complete creative brief you can act on immediately.
