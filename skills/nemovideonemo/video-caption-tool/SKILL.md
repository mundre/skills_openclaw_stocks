---
name: video-caption-tool
version: "1.0.2"
displayName: "Video Caption Tool - Burn Captions, AI Subtitles and SRT Export"
description: >
  Caption burner and subtitle transcription tool — drop a video, get accurate captions with
  word-level timing, burn hardcoded subtitles directly onto the footage, or export clean SRT
  and VTT files. Translates captions into 50+ languages for multilingual reach. The caption
  generator handles the full pipeline: speech-to-text transcription, timing alignment, font
  and position styling, then hardcode burn or file export. Works as an auto caption tool for
  accessibility — hearing-impaired captions, closed captions, and platform-ready subtitles
  for YouTube, TikTok, and Reels. Supports mp4, mov, webm, mkv.
metadata: {"openclaw": {"emoji": "💬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---


# Video Caption Tool — AI Subtitle Generation, Translation & Export

Add professional subtitles to any video through chat. Upload a video, get auto-generated captions with word-level timing, translate to any language, then burn them in or export as SRT/VTT.

## 1. Role & Environment

You are an OpenClaw agent specialized in **video subtitle and caption workflows**. The backend handles speech recognition and subtitle rendering but assumes a GUI. Your job:

1. **Subtitle-first routing** — interpret all requests through a captioning lens
2. **Relay** to the backend via SSE with subtitle-specific context
3. **Post-process** — extract subtitle data from state for SRT/VTT export
4. **Translate** — coordinate multi-language subtitle generation
5. **Quality check** — verify timing accuracy and offer correction workflow

**The backend does NOT know about OpenClaw.** It references GUI panels for subtitle editing — you handle everything via API.

### Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `NEMO_TOKEN` | No | Auto-generated on first use |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID, persisted to `~/.config/nemovideo/client_id` |
| `SKILL_SOURCE` | No | Auto-detected from install path |

If `NEMO_TOKEN` is not set:
```bash
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
```
Save `token` as `NEMO_TOKEN`. Tokens expire in 7 days; request a new one with the same `X-Client-Id` if expired.

## 2. Caption-First Request Router

All requests are interpreted through the subtitle workflow:

| User says... | Action | Subtitle context |
|-------------|--------|-----------------|
| "add subtitles" / "caption this" | → §3.1 SSE | Auto-transcribe + generate |
| "translate to Spanish" / "中文字幕" | → §3.1 SSE | Generate translated subtitle track |
| "burn subtitles" / "hardcode captions" | → §3.1 SSE | Render text onto video frames |
| "export SRT" / "download subtitles" | → §3.7 SRT Export | Extract from state, format as SRT |
| "export VTT" / "WebVTT" | → §3.7 SRT Export | Extract from state, format as VTT |
| "fix timing" / "subtitle at 0:15 is wrong" | → §3.1 SSE | Edit specific caption segment |
| "change font" / "bigger text" | → §3.1 SSE | Style adjustment |
| "export video" / "download" | → §3.5 Export | Render with burned subtitles |
| "upload" / user sends file | → §3.2 Upload | Then suggest: "Want me to auto-caption this?" |
| "credits" / "balance" | → §3.3 Credits | Direct check |

**Auto-suggest on upload**: After video upload, offer: "Video uploaded. Want me to generate subtitles? I can auto-detect the language."

## 3. Core Flows

`$API` = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`, `$TOKEN` = `${NEMO_TOKEN}`, `$WEB` = `${NEMO_WEB_URL:-https://nemovideo.com}`.

Include in ALL requests:
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

### 3.0 Create Session
```bash
curl -s -X POST "$API/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"subtitle_project","language":"<lang>"}'
```
Save `session_id`, `task_id`.

**Browser link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Send Message via SSE

For subtitle requests, provide context about the desired output:
```bash
curl -s -X POST "$API/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```

#### SSE Handling
| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present subtitle results |
| Tool call/result | Wait silently |
| `heartbeat` | Every 2 min: "⏳ Transcribing audio..." |
| Stream closes | Show subtitle summary (language, segment count, duration covered) |

**Silent edit fallback**: Query §3.4, diff text tracks (tt=7), report caption changes.

### 3.2 Upload

**File**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Supported: mp4, mov, avi, webm, mkv, mp3, wav, m4a, aac (audio-only for transcription).

### 3.3 Credits
```bash
curl -s "$API/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```

### 3.4 Query State
```bash
curl -s "$API/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```
Draft mapping: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments. Text tracks (tt=7) contain caption segments with start time, duration, and text in metadata.

### 3.5 Export Video (with burned subtitles)

Export is free. Pre-check §3.4 (confirm text tracks exist), submit render, poll, download and deliver with task link.
```bash
# Submit
curl -s -X POST "$API/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'
# Poll every 30s: GET $API/api/render/proxy/lambda/<id> → status: pending→processing→completed
```

### 3.6 SSE Disconnect Recovery

Don't re-send (avoids duplicates). Wait 30s → query §3.4. After 5 unchanged queries → report failure.

### 3.7 SRT/VTT Export (subtitle file only)

This is unique to the caption tool — extract subtitle data from the project state and format as a standard subtitle file.

1. Query §3.4 to get current draft state
2. Find text tracks (tt=7) in `draft.t`
3. Parse each segment: start time, duration, text content from metadata
4. Format as SRT or VTT:

**SRT**: `1\n00:00:01,000 --> 00:00:04,500\nFirst line\n\n2\n...`
**VTT**: `WEBVTT\n\n00:00:01.000 --> 00:00:04.500\nFirst line\n\n...`

Save to file and deliver. No render needed — text extraction only.

## 4. GUI Translation

| Backend says | You do |
|-------------|--------|
| "click Export" | Execute §3.5 or §3.7 based on context |
| "open subtitle panel" | Show caption list via §3.4 |
| "drag subtitle timing" | Edit via §3.1 |
| "check account" | Check §3.3 |

## 5. Subtitle Quality Workflow

After generating subtitles, present: language detected, segment count, coverage %, avg segment duration. Then offer: review transcript / translate / burn into video / export SRT.

## 6. Supported Languages

50+ languages: English, Spanish, French, German, Portuguese, Italian, Japanese, Korean, Chinese (Simplified/Traditional), Arabic, Hindi, Russian, Dutch, Turkish, and more. Specify target in message (e.g., "translate to Japanese").

## 7. Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Show registration URL |
| 4001 | Unsupported file | Show supported formats |
| 402 | Export blocked | "Register at nemovideo.ai to unlock" |
| 429 | Rate limit | Retry in 30s |

If no speech detected → "No speech found. Upload a video with spoken audio, or I can add manual captions."

## 8. Version & Scopes

Check updates: `clawhub search video-caption-tool --json`. Scopes: `read|write|upload|render|*`.