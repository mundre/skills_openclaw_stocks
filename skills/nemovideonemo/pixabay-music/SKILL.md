---
name: pixabay-music
version: "1.0.0"
displayName: "Pixabay Music Finder — Discover & Add Royalty-Free Tracks to Your Videos"
description: >
  Tired of hunting through endless music libraries just to find a track that fits your video's mood? The pixabay-music skill connects your video workflow directly to Pixabay's vast royalty-free music catalog, letting you search, preview, and apply background music without ever leaving your editing session. Find tracks by genre, mood, or tempo, then layer them onto your mp4, mov, avi, webm, or mkv files instantly. Perfect for content creators, marketers, and educators who need great audio fast.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you find and add the perfect royalty-free music from Pixabay to your video. Tell me the mood, genre, or vibe you're going for — and let's get your footage sounding as good as it looks.

**Try saying:**
- "Find a calm, acoustic background track from Pixabay and add it to my travel video"
- "Search Pixabay for an upbeat electronic song under 3 minutes and apply it to my product demo mp4"
- "I need a dramatic orchestral track from Pixabay for my short film — can you find one and layer it into my mkv file?"

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Your Shortcut to the Perfect Royalty-Free Soundtrack

Finding music for a video used to mean opening a separate browser tab, scrolling through pages of tracks, downloading files, importing them into your editor, and adjusting levels — all before you'd even confirmed the song was the right fit. The pixabay-music skill collapses that entire process into a single conversation.

Simply describe the feeling you want your video to carry — upbeat and energetic, calm and cinematic, dramatic and tense — and the skill searches Pixabay's library on your behalf, surfacing tracks that genuinely match your creative intent. Once you've found something you like, it gets applied directly to your video file without you needing to juggle downloads or separate tools.

This skill is built for people who care about the final result, not the process of getting there. Whether you're producing a product demo, a travel vlog, a training video, or a social media reel, having the right music underneath your footage transforms how viewers experience your content. Now that transformation takes seconds, not an afternoon.

## Routing Your Music Requests

When you describe a mood, genre, tempo, or keyword, your request is matched against Pixabay's royalty-free music catalog and routed to the most relevant tracks available for free commercial use.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend handles authenticated calls to Pixabay's music endpoint, retrieving track metadata including BPM, duration, genre tags, and direct audio URLs. All music returned is licensed under Pixabay's Content License, cleared for use in your video projects without attribution.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `pixabay-music`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=pixabay-music&skill_version=1.0.0&skill_source=<platform>`

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

Be specific about mood over genre when making your request. Saying 'something that feels like a Sunday morning walk' will often surface better matches than just saying 'acoustic guitar.' The more context you give about your video's subject and emotional arc, the more targeted the results.

Consider the pacing of your video when choosing a track. High-cut, fast-paced edits tend to work better with music that has a clear, consistent beat. Slower, more contemplative footage benefits from ambient or melodic tracks with room to breathe.

For longer videos, check whether the selected Pixabay track loops cleanly or has a natural ending point that aligns with your video's conclusion. Mentioning your video's runtime in your prompt helps the skill prioritize tracks of an appropriate length.

Always preview the result and don't hesitate to ask for a different track — music taste is subjective, and iterating quickly is one of the key advantages this skill offers.

## Common Workflows

The most frequent use case for the pixabay-music skill is adding background music to a finished or near-finished video. Users typically describe the emotional tone they want — words like 'hopeful,' 'tense,' 'playful,' or 'corporate' — and let the skill handle the search and application.

Another popular workflow is replacing existing audio. If your raw footage has distracting ambient noise or an unlicensed placeholder track, you can ask the skill to strip the original audio and substitute a Pixabay track that fits the content's pace and length.

Some creators use the skill iteratively — trying two or three different tracks against the same clip to hear which feels right before committing. You can request multiple options, compare descriptions, and then apply your preferred choice. This works especially well for short social media clips where the music choice makes a disproportionately large impact on viewer retention.

## FAQ

**Are the Pixabay tracks truly free to use?** Yes. All music available through Pixabay is released under the Pixabay License, which permits use in personal and commercial projects without attribution requirements. Always verify current license terms on Pixabay's website for your specific use case.

**What video formats are supported?** The pixabay-music skill works with mp4, mov, avi, webm, and mkv files. Most standard video exports from phones, cameras, and editing software fall within these formats.

**Can I control the music volume relative to the original audio?** Yes — you can specify in your prompt whether you want the music to be a subtle background layer, a full replacement for the original audio, or a specific volume balance. Just describe what you need in plain language.

**What if I don't like the first track suggested?** Simply ask for alternatives. You can request a different mood, a different tempo, or even a completely different genre, and the skill will search again until you find something that works.
