# AIGC Image Generation Parameters & Examples — `mps_aigc_image.py`

**Features**: AI image generation, supporting text-to-image and image-to-image, with Hunyuan/GEM/Qwen model support.
> ⚠️ Generated images are stored for 12 hours by default. Please download them promptly.

## Parameter Reference

| Parameter | Description |
|------|------|
| `--prompt` | Image description text (max 1000 characters, required when no reference image is provided) |
| `--model` | Model: `Hunyuan` (default) / `GEM` / `Qwen` |
| `--model-version` | Model version, e.g., GEM `2.5` / `3.0` |
| `--negative-prompt` | Negative prompt |
| `--enhance-prompt` | Enable prompt enhancement |
| `--image-url` | Reference image URL (can be specified multiple times, GEM supports up to 3 images) |
| `--image-ref-type` | Reference image type (corresponds one-to-one with `--image-url`): `asset` (content reference) / `style` (style reference) |
| `--image-cos-bucket` | COS Bucket of the reference image (can be specified multiple times, mutually exclusive with `--image-url`) |
| `--image-cos-region` | COS Region of the reference image (can be specified multiple times) |
| `--image-cos-key` | COS Key of the reference image (can be specified multiple times) |
| `--additional-parameters` | Additional parameters (JSON string, model-specific extension parameters) |
| `--aspect-ratio` | Aspect ratio (e.g., `16:9`, `1:1`). Supported: `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `--resolution` | Resolution: `720P` / `1080P` / `2K` / `4K` |
| `--no-wait` | Submit the task only, without waiting for results |
| `--task-id` | Query the result of an existing task |
| `--cos-bucket-name` | COS Bucket for result storage (if not configured, MPS temporary storage is used for 12 hours) |
| `--cos-bucket-region` | COS Region for result storage |
| `--cos-bucket-path` | COS path prefix for result storage, default `/output/aigc-image/` |
| `--download-dir` | Download generated images to a specified local directory after task completion (by default, only pre-signed URLs are printed) |
| `--operator` | Operator name (optional) |
| `--poll-interval` | Polling interval (seconds), default 5 |
| `--max-wait` | Maximum wait time (seconds), default 300 |
| `--verbose` / `-v` | Output detailed information |
| `--region` | MPS service region (reads `TENCENTCLOUD_API_REGION` environment variable first, default `ap-guangzhou`) |
| `--dry-run` | Print parameters only, do not call the API |

## Mandatory Rules

- **AIGC scripts do not support the `--cos-object` parameter**; its use is prohibited. COS reference images must use the dedicated parameters:
  - `--image-cos-bucket` + `--image-cos-region` + `--image-cos-key` (can be specified multiple times)
- When the user provides bucket/region/key, all three parameters must be passed in completely; none may be omitted.

```bash
# Image-to-image from COS (explicitly specifying bucket/region/key)
python scripts/mps_aigc_image.py --prompt "city night scene" \
    --image-cos-bucket mps-test-1234567 \
    --image-cos-region ap-guangzhou \
    --image-cos-key input/ref.jpg
```

## Example Commands

```bash
# Text-to-image (Hunyuan default)
python scripts/mps_aigc_image.py --prompt "a cute orange tabby cat napping in the sunshine"

# GEM 3.0 + negative prompt + 16:9 + 2K
python scripts/mps_aigc_image.py --prompt "cyberpunk city night scene" --model GEM --model-version 3.0 \
    --negative-prompt "people" --aspect-ratio 16:9 --resolution 2K

# Image-to-image (reference image + description)
python scripts/mps_aigc_image.py --prompt "transform this photo into an oil painting style" \
    --image-url https://example.com/photo.jpg

# GEM multi-image reference (supports asset/style reference types)
python scripts/mps_aigc_image.py --prompt "blend these elements" --model GEM \
    --image-url https://example.com/img1.jpg --image-ref-type asset \
    --image-url https://example.com/img2.jpg --image-ref-type style

# Submit task only without waiting
python scripts/mps_aigc_image.py --prompt "product poster" --no-wait

# Query task result
python scripts/mps_aigc_image.py --task-id abc123def456-aigc-image-20260328112000
```