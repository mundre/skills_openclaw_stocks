---
name: nemo-subtitle
version: "1.8.12"
displayName: "NemoSubtitle - AI Subtitle: Add, Burn, Translate Subtitles to Video"
author: nemovideonemo
description: >
  NemoSubtitle - AI Subtitle: Add, Burn, Translate Subtitles to Video.
  Add subtitles, burn subtitles, and translate subtitles for any video through chat — the
  complete subtitle editing workflow. Transcribes speech with word-level timing, lets you
  review and adjust the text, then hardcode subtitles directly onto the footage or export
  as SRT and VTT files. Translates into 50+ languages for multilingual captions with
  per-language font and positioning. No timeline, no GUI — drop a video file and describe
  what you need. Handles accessibility captions, bilingual overlays, and batch processing
  across multiple clips. Supports mp4, mov, avi, webm, mkv.
metadata:
  primaryEnv: NEMO_TOKEN
  requires:
    env: ["NEMO_TOKEN"]
    configPaths:
      - "~/.config/nemovideo/"
  openclaw:
    emoji: 💬
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

# NemoSubtitle Skill

A subtitle-focused AI agent skill that automates caption generation, translation, SRT export, and subtitle burning for any video. Powered by the NemoVideo API.

## Description

Use NemoSubtitle when the user wants to **add subtitles**, **generate captions**, **transcribe video to text**, **translate subtitles**, **burn hardcoded captions**, or **export SRT/VTT files** from any video or audio. Powered by NemoVideo AI.

NemoSubtitle handles the complete subtitle and caption workflow end-to-end: auto-transcribe speech in any language, translate captions, export SRT / VTT / plain text, and burn styled subtitles directly into the video — no manual timecoding required.

**Trigger phrases:** add subtitles, generate captions, auto caption, transcribe video, video to text, subtitle translation, burn subtitles, hardcode captions, export SRT, SRT file, VTT file, bilingual subtitles, Chinese subtitles, subtitle generator, caption generator, video transcript, speech to text video, closed captions, open captions, subtitle burner, add captions to video, subtitle video, caption video

**Primary use cases:**
- Auto-generate subtitles from video/audio (any language, Whisper-powered ASR)
- Translate existing subtitles or auto-generated captions into any language
- Export subtitles as SRT, VTT, or plain text transcript
- Burn (hardcode) subtitles into video with full style control (font, size, position, color, background)
- Add Chinese subtitles to English videos (or vice versa) — bilingual caption overlay
- Clean up auto-generated captions (re-timing, punctuation fix, speaker diarization)
- Generate accessibility captions for social media (YouTube, TikTok, Instagram, Facebook)

**Not for:** generating new video from text, screen recording, or full video production workflows (see nemo-video skill for general editing).

---

## Setup

**Base URL:** `https://mega-api-prod.nemovideo.ai`

All requests require:
```
Authorization: Bearer <NEMOVIDEO_API_KEY>
Content-Type: application/json
```

Set `NEMOVIDEO_API_KEY` in your environment or OpenClaw secrets.

---

## Workflow Overview

```
Upload video/audio → Start subtitle job → Poll status → Get SRT/VTT/transcript
                                                      → Burn subtitles into video
```

---

## API Reference

### 1. Upload Media

Upload a video or audio file before processing.

```http
POST /v1/upload
Content-Type: multipart/form-data

file=<binary>
```

**Response:**
```json
{
  "file_id": "f_abc123",
  "filename": "interview.mp4",
  "duration_seconds": 182,
  "size_bytes": 45000000
}
```

Use `file_id` in subsequent requests.

---

### 2. Generate Subtitles (Transcription)

Transcribe speech and produce time-coded subtitles.

```http
POST /v1/subtitles/generate
Content-Type: application/json

{
  "file_id": "f_abc123",
  "language": "en",
  "output_formats": ["srt", "vtt", "txt"],
  "options": {
    "punctuate": true,
    "max_chars_per_line": 42,
    "max_lines": 2
  }
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | ✅ | Uploaded file ID |
| `language` | string | ✅ | Source language code (`en`, `zh`, `ja`, `ko`, `es`, `fr`, `de`, `auto`) — use `auto` for auto-detect |
| `output_formats` | array | ✅ | One or more of: `srt`, `vtt`, `txt`, `json` |
| `options.punctuate` | bool | ❌ | Auto-add punctuation (default: true) |
| `options.max_chars_per_line` | int | ❌ | Max characters per subtitle line (default: 42) |
| `options.max_lines` | int | ❌ | Max lines per subtitle block (default: 2) |

**Response:**
```json
{
  "job_id": "job_gen_789",
  "status": "queued",
  "estimated_seconds": 45
}
```

---

### 3. Translate Subtitles

Translate existing subtitles (from SRT/VTT file or a prior generation job) into a target language.

```http
POST /v1/subtitles/translate
Content-Type: application/json

{
  "source": {
    "type": "job_id",
    "value": "job_gen_789"
  },
  "target_language": "zh",
  "preserve_timing": true,
  "output_formats": ["srt"]
}
```

**Or translate from an uploaded SRT file:**
```json
{
  "source": {
    "type": "file_id",
    "value": "f_srt_456"
  },
  "target_language": "zh",
  "preserve_timing": true,
  "output_formats": ["srt", "vtt"]
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source.type` | string | ✅ | `job_id` or `file_id` |
| `source.value` | string | ✅ | Reference to subtitle source |
| `target_language` | string | ✅ | Target language code |
| `preserve_timing` | bool | ❌ | Keep original timestamps (default: true) |
| `output_formats` | array | ✅ | Output format(s) |

**Supported language codes:** `en`, `zh`, `zh-tw`, `ja`, `ko`, `es`, `fr`, `de`, `pt`, `ar`, `ru`, `hi`, `vi`, `th`, `id`

**Response:**
```json
{
  "job_id": "job_translate_321",
  "status": "queued",
  "estimated_seconds": 30
}
```

---

### 4. Burn Subtitles Into Video

Hardcode (burn) subtitles permanently into the video frame.

```http
POST /v1/subtitles/burn
Content-Type: application/json

{
  "file_id": "f_abc123",
  "subtitle_source": {
    "type": "job_id",
    "value": "job_gen_789"
  },
  "style": {
    "font": "Arial",
    "font_size": 28,
    "color": "#FFFFFF",
    "outline_color": "#000000",
    "outline_width": 2,
    "position": "bottom",
    "margin_bottom": 40
  },
  "output_format": "mp4"
}
```

**Or burn from an SRT file:**
```json
{
  "file_id": "f_abc123",
  "subtitle_source": {
    "type": "file_id",
    "value": "f_srt_456"
  },
  "style": { ... }
}
```

**Style parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `font` | `"Arial"` | Font family |
| `font_size` | `28` | Font size in pixels |
| `color` | `"#FFFFFF"` | Text color (hex) |
| `outline_color` | `"#000000"` | Outline/shadow color |
| `outline_width` | `2` | Outline thickness (0 = no outline) |
| `position` | `"bottom"` | `"top"` or `"bottom"` |
| `margin_bottom` | `40` | Pixels from bottom edge |
| `background_box` | `false` | Add semi-transparent background box |
| `background_opacity` | `0.5` | Box opacity (0.0–1.0) |

**Response:**
```json
{
  "job_id": "job_burn_654",
  "status": "queued",
  "estimated_seconds": 90
}
```

---

### 5. Bilingual Subtitles (Dual-Language Overlay)

Burn two subtitle tracks simultaneously (e.g., English on top, Chinese below).

```http
POST /v1/subtitles/burn-bilingual
Content-Type: application/json

{
  "file_id": "f_abc123",
  "primary": {
    "subtitle_source": { "type": "job_id", "value": "job_gen_789" },
    "style": {
      "font_size": 26,
      "color": "#FFFF00",
      "position": "bottom",
      "margin_bottom": 70
    }
  },
  "secondary": {
    "subtitle_source": { "type": "job_id", "value": "job_translate_321" },
    "style": {
      "font_size": 22,
      "color": "#FFFFFF",
      "position": "bottom",
      "margin_bottom": 30
    }
  },
  "output_format": "mp4"
}
```

**Response:**
```json
{
  "job_id": "job_bilingual_987",
  "status": "queued",
  "estimated_seconds": 120
}
```

---

### 6. Poll Job Status

All subtitle jobs are async. Poll until `status` is `completed` or `failed`.

```http
GET /v1/jobs/{job_id}
```

**Response (in progress):**
```json
{
  "job_id": "job_gen_789",
  "status": "processing",
  "progress": 0.62
}
```

**Response (completed):**
```json
{
  "job_id": "job_gen_789",
  "status": "completed",
  "outputs": {
    "srt": "https://cdn.nemovideo.ai/outputs/job_gen_789/subtitles.srt",
    "vtt": "https://cdn.nemovideo.ai/outputs/job_gen_789/subtitles.vtt",
    "txt": "https://cdn.nemovideo.ai/outputs/job_gen_789/transcript.txt"
  }
}
```

**Response (failed):**
```json
{
  "job_id": "job_gen_789",
  "status": "failed",
  "error": "Unsupported audio codec in input file"
}
```

**Polling strategy:**
- Check every 3–5 seconds for short files (<60s audio)
- Check every 10–15 seconds for longer files
- Timeout after 10 minutes; surface error to user

---

### 7. Download Output File

Download SRT, VTT, transcript, or rendered video from the URL in the job outputs.

```http
GET <output_url>
```

No auth required (CDN URLs are pre-signed, valid for 24 hours).

---

## Common Workflows

### Workflow A: Generate + Export SRT

```
1. Upload video → POST /v1/upload → file_id
2. Transcribe → POST /v1/subtitles/generate (language: "auto", formats: ["srt"])
3. Poll → GET /v1/jobs/{job_id} until completed
4. Download SRT from outputs.srt URL
5. Deliver SRT file to user
```

### Workflow B: Translate Existing Subtitles

```
1. Upload SRT file → POST /v1/upload → file_id
2. Translate → POST /v1/subtitles/translate (source: file_id, target_language: "zh")
3. Poll until completed
4. Download translated SRT
```

### Workflow C: Full Pipeline (Video → Chinese Hardcoded Subtitles)

```
1. Upload video → file_id
2. Generate subtitles (language: "en") → job_gen_id
3. Translate to Chinese → job_translate_id
4. Burn Chinese subtitles into video → job_burn_id
5. Poll burn job
6. Return final MP4 download URL
```

### Workflow D: Bilingual Video (EN + ZH)

```
1. Upload video → file_id
2. Generate EN subtitles → job_gen_id
3. Translate to ZH → job_translate_id
4. POST /v1/subtitles/burn-bilingual (primary: EN, secondary: ZH)
5. Poll → return MP4
```

---

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad request (missing params, invalid format) | Check request body; surface error to user |
| 401 | Invalid or missing API key | Prompt user to check `NEMOVIDEO_API_KEY` |
| 413 | File too large | Advise user: compress video or use a shorter clip |
| 422 | Unsupported format or language | List supported formats/languages to user |
| 429 | Rate limited | Wait 10s; retry with exponential backoff |
| 500/503 | Server error | Retry after 30s; if persistent, report to user |

For `job.status === "failed"`, always surface `error` message to user with a plain explanation.

---

## Behavior Notes

- **Language auto-detection:** Use `language: "auto"` when the source language is unknown. Detection adds ~5s to job time.
- **Chinese variants:** Use `zh` for Simplified Chinese, `zh-tw` for Traditional Chinese.
- **SRT vs VTT:** SRT is more universally compatible; VTT is needed for web players (HTML5 `<track>`). When in doubt, offer both.
- **Burn timing:** Burning subtitles re-encodes the video, which takes longer than SRT export alone. Set user expectations accordingly.
- **File limits:** Typical limit is 2GB per upload, 4 hours max duration. Very long files should be split first.
- **Output expiry:** CDN output URLs expire after 24 hours. If the user needs permanent storage, advise downloading promptly.

---

## Example Prompts → Actions

| User says | Action |
|-----------|--------|
| "Add subtitles to my video" | Upload → generate (language: auto) → burn → return MP4 |
| "Generate SRT for this video" | Upload → generate (formats: ["srt"]) → return SRT file |
| "Translate my subtitles to Spanish" | Upload SRT → translate (target: "es") → return SRT |
| "Add Chinese subtitles to this English video" | Upload → generate (en) → translate (zh) → burn → return MP4 |
| "Make bilingual English + Chinese subtitles" | Upload → generate (en) → translate (zh) → burn-bilingual → return MP4 |
| "Get the transcript from this podcast" | Upload → generate (formats: ["txt"]) → return transcript |
| "Export captions as VTT" | Upload → generate (formats: ["vtt"]) → return VTT |
| "Burn captions with white text, black outline" | Upload + provide SRT → burn (style: color #FFF, outline #000) → return MP4 |
