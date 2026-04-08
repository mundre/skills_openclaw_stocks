---
name: free-ai-video-creator
version: "1.0.0"
displayName: "Free AI Video Creator — Generate Stunning Videos Without Spending a Dime"
description: >
  Turn your ideas, images, scripts, and raw clips into polished videos using free-ai-video-creator — a no-cost AI-powered video generation skill. Describe a concept, upload assets, or paste a script, and get back a structured, ready-to-publish video complete with scenes, captions, and pacing suggestions. Built for content creators, educators, small business owners, and social media managers who need professional-looking results without a production budget.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to Free AI Video Creator — where your ideas become fully structured, shareable videos without any budget or technical skills required. Tell me what kind of video you want to make and let's start building it right now!

**Try saying:**
- "I want to create a 60-second promotional video for my handmade candle business. I have a few product photos and want upbeat music. Can you write the script and scene breakdown?"
- "Turn this 800-word blog post about healthy meal prep into a YouTube video script with on-screen text suggestions and a hook for the first 5 seconds."
- "I need a short Instagram Reel explaining how to use my budgeting app. Make it punchy, under 30 seconds, with text overlays and a call-to-action at the end."

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Create Real Videos From Just an Idea

Most people assume video production requires expensive software, a camera crew, or hours of editing experience. Free AI Video Creator flips that assumption entirely. You bring the concept — a product launch, a tutorial idea, a short story, a social media campaign — and this skill helps you shape it into a complete video structure with scenes, narration cues, on-screen text, and visual direction.

Whether you're a solo creator bootstrapping a YouTube channel, a teacher building lesson content, or a small business owner who needs a promotional clip without hiring a studio, this tool meets you where you are. Paste a blog post and turn it into a video script. Describe a brand story and get a shot-by-shot breakdown. Upload a rough concept and receive a production-ready outline.

The goal isn't just to save money — it's to remove the intimidation barrier entirely. You don't need to know video editing terminology, rendering formats, or production timelines. Just describe what you want, and Free AI Video Creator handles the creative heavy lifting.

## Routing Your Video Generation Requests

Each prompt you submit is parsed for scene descriptors, style tokens, and duration parameters before being dispatched to the optimal free-tier rendering node.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering Backend Reference

The backend leverages distributed GPU clusters running diffusion-based video synthesis pipelines, queuing your text-to-video jobs across free-allocation compute slots. Rendered output is temporarily cached in cloud storage and delivered via a signed URL valid for 24 hours.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-ai-video-creator`
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

## Troubleshooting

**The output feels too generic:** This usually happens when the initial prompt is vague. Instead of 'make a video about fitness,' try 'make a 45-second Instagram video targeting busy moms who want 10-minute home workouts, with an energetic tone and three specific exercise callouts.' The more context you provide about audience, tone, and platform, the sharper the result.

**The script is too long or too short:** Specify your target duration upfront. Mention '30-second video' or '3-minute YouTube explainer' in your request. If the output still feels off, ask for a revised version with tighter pacing or expanded scene descriptions.

**Scene suggestions don't match my footage:** If you're working with specific existing clips or images, describe them explicitly — 'I have a clip of a coffee shop interior, a barista pouring latte art, and a customer smiling.' Free AI Video Creator will write scenes around your actual assets rather than assuming what you have.

**Captions feel robotic:** Request a specific tone. Words like 'conversational,' 'punchy,' 'warm and friendly,' or 'professional but approachable' directly shape how captions and narration are written.

## Common Workflows

**From Text to Video:** The most popular workflow starts with existing content — a blog post, email newsletter, or product description. Paste it in, specify the target platform (YouTube, TikTok, Instagram), and Free AI Video Creator restructures it into a scene-by-scene video script with narration, visual cues, and caption timing.

**From Scratch with Just an Idea:** Not everyone has existing content. If you only have a vague concept — 'I want a video about why small businesses should use email marketing' — the skill will generate a full video outline including hook, body sections, and a closing call-to-action tailored to your audience.

**Social Media Repurposing:** Have a long-form video or podcast transcript? Drop it in and request a cut-down version optimized for a specific platform. Free AI Video Creator will identify the strongest moments, suggest where to trim, and rewrite captions for shorter attention spans.

**Brand Storytelling:** Describe your brand's origin, values, or a customer success story and receive a structured narrative video script complete with emotional beats, visual scene suggestions, and voiceover direction.
