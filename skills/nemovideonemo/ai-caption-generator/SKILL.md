---
name: ai-caption-generator
version: "1.0.1"
displayName: "AI Caption Generator — Auto-Subtitle Any Video in Minutes"
description: >
  The ai-caption-generator skill transcribes and burns accurate, styled captions into your videos using deep speech recognition and NLP alignment. It handles mp4, mov, avi, webm, and mkv formats out of the box, making it versatile for creators, marketers, educators, and accessibility teams. Key features include multi-language detection, customizable font and position settings, speaker-aware captioning, and SRT/VTT export alongside burned-in subtitle renders. On first use, the skill auto-configures credentials via NemoVideo API, so there is zero manual setup required before your first caption job runs. Supports mp4, mov, avi, webm, and mkv.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> Welcome! I'm your AI Caption Generator — ready to transcribe, time, and style captions for any video you throw at me. Drop your video file or share a link and tell me how you want your captions to look, and I'll get started right away.

**Try saying:**
- "Generate captions for this mp4 interview video and export both a burned-in version and an SRT file with 42-character line limits."
- "Add Spanish captions to my webm tutorial, using white bold text at the bottom with a semi-transparent black background."
- "Transcribe this mkv podcast recording with speaker labels and create a styled caption track where each speaker's name appears before their lines."

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting.

### Auto-Setup (on first use)

When the user first opens this skill, run through these setup steps and briefly let them know you're connecting (e.g. "⚡ Connecting to NemoVideo..."):

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
   - This file stores only a UUID for rate-limit tracking — no secrets or credentials.
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

**Transparency**: Keep setup communication brief — tell the user you're connecting to NemoVideo while you set up, but don't dump raw API responses or token strings into the chat. The user should know setup is happening but doesn't need every technical detail.

# Turn Spoken Words Into Precise, Styled Captions

The ai-caption-generator skill exists to solve one of the most time-consuming parts of video production: getting accurate, well-timed captions onto the screen without juggling external transcription tools, subtitle editors, and render pipelines. Instead of treating captioning as a post-production afterthought, this skill integrates it directly into a conversational workflow where you describe what you want and the AI handles the execution.

At the core of this skill is the OpenClaw agent, which interprets your natural-language instructions and maps them to the appropriate transcription, alignment, and rendering operations. You can ask it to generate captions in a specific language, adjust the visual style, limit line length for readability, or export both a burned-in video and a standalone SRT file in the same request. The agent remembers context across turns, so you can refine outputs without repeating yourself.

The AI backend uses frame-accurate timestamp alignment to ensure captions never drift from the spoken audio, even in videos with background music or overlapping speakers. Whether you are captioning a short social clip or a long-form documentary, the skill scales to the task and delivers results you can publish directly.

### Environment Variables

| Variable | Required | Default | What it does |
|----------|----------|--------|--------|
| `NEMO_TOKEN` | No | Auto-acquired on first use via `/api/auth/anonymous-token` (100 free credits, expires in 7 days, revocable via Settings → API Tokens) | Authenticates API requests |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` | API base URL |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` | Web base URL |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID, persisted to `~/.config/nemovideo/client_id` (UUID only — no secrets stored) | Rate-limit tracking |
| `SKILL_SOURCE` | No | Auto-detected from install path, fallback `unknown` | Usage attribution |

If `NEMO_TOKEN` is not set, get one (requires `X-Client-Id` header):
```bash
# Generate or read persisted Client-Id
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
# → {"code":0,"data":{"token":"nmv_usr_xxx","credits":100,...}}
```
Save `token` as `NEMO_TOKEN`, `CLIENT_ID` as `NEMO_CLIENT_ID`. Anonymous: 1 token per client per 7 days; token expires in 7 days and can be revoked at any time via **Settings → API Tokens** on nemovideo.com. If your token expires, request a new one with the same `X-Client-Id`.

**Local persistence:** This skill writes `~/.config/nemovideo/client_id` to persist the Client-Id across sessions. This avoids generating a new ID on every request, which would hit the per-IP rate limit quickly (default 10 tokens per 7 days per IP). The file contains only a UUID — no credentials are stored locally.

## 2. Endpoint Dispatch Map

Every inbound request gets routed to exactly one backend endpoint — match the action to the correct path before firing any call.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## 3. Core Operational Flows

$API = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`, $TOKEN = `${NEMO_TOKEN}`, $WEB = `${NEMO_WEB_URL:-https://nemovideo.com}`.

Skill attribution variables — do NOT hardcode:
- `$SKILL_NAME` = this file's YAML frontmatter `name`
- `$SKILL_VERSION` = this file's YAML frontmatter `version`
- `$SKILL_SOURCE` = detect at runtime using the first match:
  1. Env `SKILL_SOURCE` if set
  2. If this file's path contains a known platform directory (e.g. `~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`)
  3. Fallback: `unknown`

**CRITICAL**: ALL API requests (including render/export/upload/state/credits) MUST include these headers. Missing them will cause export to fail with 402.
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

### 3.0 Spin Up a Session
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
# → {"code":0,"data":{"task_id":"...","session_id":"..."}}
```
Before any captioning work begins, a session must be established — this is the handshake that ties all subsequent subtitle operations together. Without a valid session ID in place, no downstream calls will resolve correctly.

**Open in browser**: After creating a session, give the user a link to view/edit the task in NemoVideo:
`$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Stream Messages Over SSE
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
All real-time communication during caption generation runs through a Server-Sent Events channel, keeping the client in sync as each subtitle segment is processed.

#### SSE Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

Typical durations: text 5-15s, video generation 100-300s, editing 10-30s.

**Timeout**: 10 min heartbeats-only → assume timeout. **Never re-send** during generation (duplicates + double-charge).

Ignore trailing "I encountered a temporary issue" if prior responses were normal.

#### Silent Response Fallback (CRITICAL)

Roughly 30% of caption edits come back with an empty text payload — no transcript update, no SRT delta, just silence. Don't treat this as an error. When the SSE stream closes and no text content has arrived: 1) Immediately call the state query endpoint to pull the current caption timeline. 2) Surface whatever subtitle data is already attached to the project. 3) Confirm to the user that their edit registered and the captions are up to date. The absence of a text response does not mean the operation failed.

**Two-stage generation**: Raw video uploads trigger a two-stage backend pipeline automatically — no extra API calls needed. Stage one generates the base caption track, syncing subtitle timing to the spoken audio. Stage two overlays any configured background music and injects the title card. Both stages run server-side; the client simply waits for the final SSE completion event before presenting the fully captioned output to the user.

### 3.2 Asset Upload

**File upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Use **me** in the path; backend resolves user from token.

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

The upload endpoint accepts video files and any supplementary assets needed for captioning — always confirm the file MIME type is supported before posting.

### 3.3 Credit Balance Check
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
# → {"code":0,"data":{"available":XXX,"frozen":XX,"total":XXX}}
```
Query the credits endpoint before kicking off any caption generation job to verify the account holds sufficient balance for the operation.

### 3.4 Project State Poll
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```
Use **me** for user in path; backend resolves from token.
Key fields: `data.state.draft`, `data.state.video_infos`, `data.state.canvas_config`, `data.state.generated_media`.

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

**Draft ready for export** when `draft.t` exists with at least one track with non-empty `sg`.

**Track summary format**:
```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### 3.5 Export & Deliver Captions

**Export does NOT cost credits.** Only generation/editing consumes credits.

Exporting a finished caption file costs zero credits — it is always free. Run through these steps: a) Confirm the session is in a completed state before requesting export. b) Call the export endpoint with the target format (SRT, VTT, or burned-in video). c) Poll until the export job status flips to done. d) Retrieve the download URL from the response payload. e) Deliver the captioned file or subtitle track directly to the user.

**b)** Submit: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`

Note: `sessionId` is **camelCase** (exception). On failure → new `id`, retry once.

**c)** Poll (every 30s, max 10 polls): `curl -s "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda/<id>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"`

Status at top-level `status`: pending → processing → completed / failed. Download URL at `output.url`.

**d)** Download from `output.url` → send to user. Fallback: `$API/api/render/proxy/<id>/download`.

**e)** When delivering the video, **always also give the task detail link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

Progress messages: start "⏳ Rendering ~30s" → "⏳ 50%" → "✅ Video ready!" + file + **task detail link**.

### 3.6 Recovering a Dropped SSE Connection

SSE streams drop — plan for it. When the connection goes dark mid-captioning: 1) Wait two seconds before attempting anything, letting transient network hiccups resolve. 2) Re-authenticate and open a fresh SSE connection using the original session ID. 3) Poll the state endpoint to grab the last known subtitle timeline and any completed caption segments. 4) Resume from the confirmed checkpoint — do not restart the entire caption job from scratch. 5) If reconnection fails after three consecutive attempts, surface a clear error to the user and suggest they re-upload or refresh the session.

## 4. GUI Layer Translation

The backend operates under the assumption that a graphical interface is present on the client side — never pass raw GUI instructions or UI control strings through the API.

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Show state via §3.4 |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute §3.5 |
| "check account/billing" | Check §3.3 |

**Keep** content descriptions. **Strip** GUI actions.

## 5. Interaction Patterns That Work

- **Lead with intent, not mechanics** — when a user says 'add captions to my video,' move straight into session creation and upload without asking them to explain the process back to you.
- **Narrate progress during long caption jobs** — SSE streams can run for minutes on dense audio; give periodic status updates so the user knows the subtitle engine is still working.
1. When a user requests edits to existing captions, always fetch current state first so your response reflects the actual SRT timeline, not a cached assumption.
2. Offer format choices (SRT, VTT, hardcoded) only after the caption job completes — not before, when it creates unnecessary friction.
- **Treat silence as signal** — a no-text SSE response after an edit is a cue to query state and confirm, not a prompt to ask the user what went wrong.

## 6. Known Constraints

- Caption generation accuracy depends on audio clarity — heavily accented speech, overlapping voices, or low-quality recordings will reduce subtitle sync precision.
- SRT timestamp editing through the API is supported, but bulk re-timing of an entire caption track in a single call is not; changes must be applied segment by segment.
- The two-stage BGM and title pipeline cannot be disabled mid-session once a raw video upload has been submitted.
- Export format options are fixed to the set defined at session creation; switching output format after export has begun requires a new export call.
- Credit balance checks reflect account state at query time — there is no reservation or lock, so balances can change between the check and the generation call.

## 7. Error Codes & What To Do With Them

When the API pushes back, match the HTTP status or error code to the table below and respond accordingly — most caption workflow failures fall into a handful of predictable categories.
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

**Common**: no video → generate first; render fail → retry new `id`; SSE timeout → §3.6; silent edit → §3.1 fallback.

## 8. API Version & Permission Scopes

Always verify the API version header before initiating a caption session — mismatched versions are the leading cause of silent failures in subtitle generation pipelines. Token scopes must cover both read and write permissions on caption resources; a read-only token will authenticate successfully but block any attempt to create or modify subtitle tracks. If a scope error surfaces mid-flow, do not retry the same call — prompt the user to reauthorize with the correct permission set before proceeding.

## 9. Common Workflows

One of the most frequent use cases is accessibility captioning for published content. Users upload a finished mp4 or mov, request burned-in captions with high-contrast styling, and receive a ready-to-publish render alongside a standalone SRT for platforms that accept external subtitle tracks. This single request replaces what would normally require a transcription service, a subtitle editor, and a video renderer.

Another common workflow is multi-language captioning for international audiences. You can ask the ai-caption-generator to detect the source language automatically and produce captions in a second language simultaneously, delivering two rendered outputs and two subtitle files from one video upload.

Social media creators often use the skill to generate short-form captions optimized for vertical video, specifying tight line lengths and large font sizes suited for mobile viewing. Educators use it to caption lecture recordings with speaker identification enabled, so students can follow multi-presenter content more easily. Each of these workflows runs entirely through conversation — no timeline editor or desktop software required.

## 10. Quick Start Guide

Getting your first captions generated takes only a few steps. Upload your video file in any supported format — mp4, mov, avi, webm, or mkv — directly in the chat, or paste a hosted video URL if your file is already online. On your very first run, the skill silently auto-configures its connection to the NemoVideo API, so you do not need to touch any settings or supply API keys manually.

Once your file is received, tell the agent what you need. A simple message like 'Generate English captions and burn them into the video' is enough to kick off a full transcription and render job. If you want more control, specify font size, color, position, maximum characters per line, or whether you need an SRT or VTT export alongside the rendered file.

Results are returned as downloadable files directly in the conversation. If the first output needs adjustment — timing feels off on a specific segment, or the font is too small for mobile — just describe the change and the agent will re-render without starting from scratch.
