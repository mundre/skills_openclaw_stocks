---
name: liblib-comfy-fusion
description: Generate product background fusion images via LiblibAI ComfyUI app API using signed AccessKey/SecretKey requests. Use when user asks for Liblib Comfy app generation, Feishu image + fusion, local or URL image input, task polling with generateUuid, or Feishu message URL extraction.
---

# Liblib Comfy Fusion Generation

Generate images with LiblibAI ComfyUI App API (template-based workflow). Supports **public image URL** or **local file**.

For **local files from Feishu**, the recommended flow is:

1) upload the local file to R2 (S3-compatible) to get a **public URL**  
2) use that public URL as the Liblib `LoadImage` input  
3) return the Liblib result `imageUrl` as **`MEDIA:https://...`** so Feishu displays it directly

## Prerequisites

Environment variables must be set:

- `LIB_ACCESS_KEY` — API access key
- `LIB_SECRET_KEY` — API secret key

## Usage

Run the CLI at `scripts/liblib_client.py`:

```bash
# Public URL input
python3 scripts/liblib_client.py run --image-url "https://example.com/input.jpg"

# Local file (Feishu inbound attachment) → upload to R2 → use public URL
python3 scripts/liblib_client.py run --local-image "/path/to/input.png" --basename "product-fusion"

# Local file (advanced): embed as data URI (only if Liblib accepts it)
python3 scripts/liblib_client.py run --local-image "/path/to/input.png" --local-image-mode data-uri

# Parse URL from Feishu message text
python3 scripts/liblib_client.py run --feishu-text "请处理这个图 https://example.com/input.jpg"

# Submit only (no poll)
python3 scripts/liblib_client.py run --local-image "./input.jpg" --no-poll

# Query task status
python3 scripts/liblib_client.py status <generateUuid>
```

### Output and Feishu 回传

- After a **successful** run (`generateStatus=5`), the script downloads `images[].imageUrl` into **`workspace/outputs/images/YYYY-MM-DD/<basename>.(png|jpg|...)`** (override with `--output-dir`).
- **stdout** prints a single line: `MEDIA:./outputs/images/YYYY-MM-DD/<file>` (relative to `workspace/`). Use this with OpenClaw Feishu channel so the image appears **in the current chat** without extra API calls.
- Full task JSON is printed to **stderr** for debugging.
- If `MEDIA:` is not supported in your channel, use **`feishu-uploader`** with `--receive-id-type chat_id` and the group `chat_id`, or `--open-id` for DM.

### Parameters (run)

| Flag | Meaning |
|------|--------|
| `--local-image` | Local path; takes priority over URL. Default mode uploads to R2 and uses public URL. |
| `--local-image-mode` | `r2` (default) or `data-uri`. |
| `--image-url` | Public URL the Liblib servers can fetch. |
| `--feishu-text` / `FEISHU_TEXT` | Extract first `http(s)` URL from text. |
| `--output-dir` | Default: `<workspace>/outputs/images`. |
| `--basename` | Filename stem (default `liblib-fusion`). |
| `--no-download` | Skip downloading result files. |
| `--no-print-media` | Do not print `MEDIA:` line; stdout prints absolute path of first saved file instead. |

## API Details

- Submit endpoint: `POST /api/generate/comfyui/app`
- Status endpoint: `POST /api/generate/comfy/status`
- Auth query params: `AccessKey`, `Signature`, `Timestamp`, `SignatureNonce`
- Signature algorithm:
  - content = `uriPath & Timestamp & SignatureNonce`
  - `HMAC-SHA1(secretKey, content)`
  - URL-safe Base64 without trailing `=`

## Async Pattern

1. Submit task to get `generateUuid`
2. Poll status endpoint until `generateStatus` is 5 (success) or 6 (failed)
3. Read `images[].imageUrl` when successful

## Notes

- **URL input**: must be publicly reachable by Liblib.
- **Local input**: default uses R2 upload to produce a public URL. Requires `boto3`.
- Returned image URLs are temporary (typically ~7 days).
- If API returns content review errors, try a different source image or URL.
