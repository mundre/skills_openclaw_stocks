---
name: digen-ai
description: "DigenAI image and video generation for OpenClaw. Supports text-to-image, image-to-video, and text-to-video. Image generation via api.digen.ai; video generation via new API with Bearer token. Triggers on: generate image, generate video, Digen AI, text to image, image to video, text to video. API key available via Telegram bot @digen_skill_bot (send /key)."
---

# DigenAI Skill

Generate images from text prompts and videos from images or text via DigenAI API.

## ⚠️ First Time Users: Get Your Free API Key

**Video generation requires a free API key.**

### How to Get Your API Key

1. Open our Telegram bot: **https://t.me/digen_skill_bot**
2. Send the command: `/key`
3. Copy your API key (starts with `dg_`)

Your API key is used as:
```
Authorization: Bearer YOUR_API_KEY
```

---

## Quick Start

```python
from digen_ai_client import DigenAIClient

# Image generation (old API) — requires DIGEN_TOKEN + DIGEN_SESSION_ID
client = DigenAIClient(
    old_api_token="your_token",
    old_api_session="your_session"
)

# Video generation (new API) — requires API Key
client = DigenAIClient(api_key="ak_xxxxxxxxxxxxxxxxxxxx")
```

---

## Image Generation (Old API)

**Uses `api.digen.ai` with DIGEN_TOKEN + DIGEN_SESSION_ID**

### Available Models
| Model | Description |
|-------|-------------|
| `default` | High quality model |

### Resolutions
| Ratio | Size |
|-------|------|
| Multiple | Standard resolutions supported |

### Example

```python
from digen_ai_client import DigenAIClient

client = DigenAIClient(
    old_api_token="your_digen_token",
    old_api_session="your_digen_session"
)

result = client.generate_image_sync(
    prompt="futuristic cyberpunk city at night, neon lights, rainy streets, highly detailed, 8K",
    model="default",
    resolution="1:1"
)

if result["success"]:
    print(f"✅ Image: {result['images'][0]}")
else:
    print(f"❌ Error: {result.get('error')}")
```

---

## Video Generation (New API)

**Uses new API with Bearer API Key**

### Available Models
| `default` | High quality, fast generation | 10s |

### Modes
- **Text-to-Video**: text prompt only
- **Image-to-Video**: image URL with optional motion prompt

### Example: Image-to-Video

```python
from digen_ai_client import DigenAIClient

client = DigenAIClient(api_key="ak_xxxxxxxxxxxxxxxxxxxx")

result = client.generate_video_sync(
    image_url="https://your-image.jpg",
    prompt="gentle camera pan left, neon lights twinkling",
    model="default",
    duration=5,
    aspect_ratio="1:1"
)

if result["success"]:
    print(f"✅ Video: {result['video_url']}")
    print(f"   Thumbnail: {result['thumbnail_url']}")
else:
    print(f"❌ Error: {result.get('error')}")
```

### Example: Text-to-Video

```python
client = DigenAIClient(api_key="ak_xxxxxxxxxxxxxxxxxxxx")

result = client.generate_video_sync(
    prompt="A cute cat playing piano in a cozy room, soft lighting",
    model="default",
    duration=5,
    aspect_ratio="1:1"
)
```

---

## API Key Management (New API)

### Check API Key Info

```python
client = DigenAIClient(api_key="ak_xxx")
info = client.get_api_key_info()
print(info)
# {'success': True, 'data': {'api_key': 'ak_xxx', 'status': 1, 'created_at': '...'}}
```

### Upload Image

```python
result = client.upload_image(file_path="/path/to/image.jpg")
if result["success"]:
    print(f"Image URL: {result['url']}")
```

---

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DIGEN_TOKEN` | Old API token for image generation |
| `DIGEN_SESSION_ID` | Old API session ID for image generation |
| `DIGEN_API_KEY` | New API key (ak_xxx) for video generation |

### Setup

```bash
# Image generation (old API)
export DIGEN_TOKEN="your_token"
export DIGEN_SESSION_ID="your_session"

# Video generation (new API)
export DIGEN_API_KEY="ak_xxxxxxxxxxxxxxxxxxxx"
```

---

## Error Handling

### No API Key Error (Video)

```
❌ API Key Not Found!
Join our Discord: https://discord.gg/4shAQahd
Go to #api-key channel → send !key
```

### Error Codes (New API)

| HTTP Code | Error Code | Description |
|-----------|------------|-------------|
| 400 | invalid_request | Invalid or missing parameters |
| 401 | invalid_api_key | Invalid or missing API key |
| 402 | insufficient_credits | Not enough credits |
| 404 | not_found | Resource not found |
| 500 | internal_error | Internal server error |

---

## API Reference

### New API Endpoints (Video)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/b/v1/api-key` | Get API key info |
| `POST` | `/b/v1/upload` | Upload image file |
| `POST` | `/b/v1/video/generate` | Generate video |
| `GET` | `/b/v1/video/{id}` | Get video status |

Base URL: `[New API endpoint]`

### Old API Endpoints (Image)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v2/tools/text_to_image` | Generate image |
| `POST` | `/v6/video/get_task_v2` | Get image status |

Base URL: `https://api.digen.ai`

---

## Scripts

- `scripts/digen_ai_client.py` - Python client with sync/async support
- `scripts/batch_generate.py` - Batch image generation utility

## Tips

- Image generation: poll every 3 seconds, timeout 120s
- Video generation: poll every 5 seconds, timeout 300s
- Resolution: 720p or 1080p
