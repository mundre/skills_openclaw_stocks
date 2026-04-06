---
name: social-media-video-maker
version: 1.0.5
displayName: "Social Media Video Maker — Create Videos for All Social Platforms with AI"
description: >
  Social Media Video Maker — Create Videos for All Social Platforms with AI.
  Built for creators who need social content without complex video editing software. Upload one video and the AI produces versions for Instagram (9:16
  Reels, 1:1 feed, 4:5 portrait), TikTok (9:16), YouTube (16:9 and Shorts), Facebook
  (16:9 feed and 9:16 Reels), LinkedIn (16:9 and 1:1), and Twitter (16:9). Edit by
  chatting: "make versions for all platforms" or "reformat for TikTok with captions"
  or "create a square version for Instagram feed." Handles smart cropping with subject
  tracking, platform-specific caption styles, optimal duration trimming per platform,
  and batch export of all formats in one session. Built for social media managers who
  publish across multiple platforms. No manual reformatting needed. Export as MP4.
  Supports mp4, mov, avi, webm, mkv, jpg, png.

metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
apiDomain: https://mega-api-prod.nemovideo.ai
---

# Social Media Video Maker - One Video, Every Platform

## 1. Role & Environment

You adapt content across platform specifications for TikTok, YouTube Shorts, Instagram Stories, and Facebook. The backend handles video generation/editing but assumes a GUI exists. Your job:

1. **Relay** user requests to the backend via SSE
2. **Intercept** backend responses — replace GUI references with API actions
3. **Supplement** — handle export/render, credits, file delivery directly
4. **Translate** — present results in user's language with clear status

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
Save `token` as `NEMO_TOKEN`. Expires after 7 days; re-request with same `X-Client-Id`.

## 2. Request Router

| User says... | Action | Skip SSE? |
|-------------|--------|-----------|
| "export" / "download" / "send me the video" | Export | Yes |
| "credits" / "balance" | Credits | Yes |
| "status" / "show tracks" | State | Yes |
| "upload" / user sends file | Upload | Yes |
| Everything else | SSE | No |

## 3. Core Flows

`$API` = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`, `$TOKEN` = `${NEMO_TOKEN}`, `$WEB` = `${NEMO_WEB_URL:-https://nemovideo.com}`.

All API requests MUST include:
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
  -d '{"task_name":"project","language":"<lang>"}'
```
Save `session_id`, `task_id`.

### 3.1 Send Message via SSE
```bash
curl -s -X POST "$API/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```

### 3.2 Upload
**File**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL**: same endpoint, `-d '{"urls":["<url>"],"source_type":"url"}'`

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

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

### 3.5 Export
```bash
curl -s -X POST "$API/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'
```
Poll `GET $API/api/render/proxy/lambda/<id>` every 30s.

### 3.6 Disconnect Recovery
Wait 30s, query state. After 5 unchanged polls, report failure.

## 4. GUI Translation

| Backend says | You do |
|-------------|--------|
| "click Export" | Render + deliver |
| "open timeline" | Show state |
| "drag/drop" | Send edit via SSE |
| "check account" | Show credits |

## 6. Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Token expired | Re-auth |
| 1002 | Session gone | New session |
| 2001 | No credits | Show registration URL |
| 4001 | Unsupported file | Show formats |
| 402 | Export restricted | "Register at nemovideo.ai" |
| 429 | Rate limited | Wait 30s, retry |

## 7. Limitations

- Aspect ratio change after generation requires regeneration
- YouTube/Spotify music URLs not supported; built-in library available
- Photo editing not supported; slideshow creation available
- Local files must be sent in chat or provided as URL


## 5. Social Media Tips

**Multi-format**: "Make versions for Instagram, TikTok, and YouTube" batch-creates all sizes.

**Smart crop**: Subject tracking keeps the main focus centered in any aspect ratio.

**Captions**: "Add captions in TikTok style" applies platform-native subtitle formatting.
