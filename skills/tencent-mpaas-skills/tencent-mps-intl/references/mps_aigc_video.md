# AIGC Video Generation Parameters & Examples — `mps_aigc_video.py`

**Features**: AI video generation supporting text-to-video, image-to-video, and multi-shot storyboard generation with Hunyuan/Hailuo/Kling/Vidu/OS/GV models.
> ⚠️ Generated videos are stored for 12 hours by default. Please download them promptly.

## Parameter Reference

| Parameter | Description |
|------|------|
| `--prompt` | Video description text (max 2000 characters, required when no image is provided) |
| `--model` | Model: `Hunyuan` (default) / `Hailuo` / `Kling` / `Vidu` / `OS` / `GV` |
| `--model-version` | Model version, e.g., Kling `2.5`/`O1`, Hailuo `2.3`, Vidu `q2-pro` |
| `--scene-type` | Scene type: `motion_control` (Kling motion control) / `land2port` (Mingmou landscape-to-portrait) / `template_effect` (Vidu effect template) |
| `--multi-shot` | **Kling exclusive**. Enable multi-shot storyboard mode |
| `--multi-prompts-json` | **Kling exclusive**. Multi-shot configuration (JSON array), each shot contains `index`, `prompt`, `duration`. Limits: 1–6 shots, max 512 characters per prompt, total duration of all shots must equal the overall duration |
| `--negative-prompt` | Negative prompt |
| `--enhance-prompt` | Enable prompt enhancement |
| `--image-url` | Reference image (first frame) URL (single image, used for image-to-video) |
| `--last-image-url` | Reference image (last frame) URL (supported by some models, requires `--image-url` to be set as well) |
| `--image-cos-bucket` | COS Bucket for the first-frame image (mutually exclusive with `--image-url`) |
| `--image-cos-region` | COS Region for the first-frame image |
| `--image-cos-key` | COS Key for the first-frame image |
| `--last-image-cos-bucket` | COS Bucket for the last-frame image |
| `--last-image-cos-region` | COS Region for the last-frame image |
| `--last-image-cos-key` | COS Key for the last-frame image |
| `--ref-image-url` | Multi-image reference URL (can be specified multiple times, supported by GV/Vidu, max 3 images) |
| `--ref-image-type` | Multi-image reference type (corresponds one-to-one with `--ref-image-url`): `asset` (content reference) / `style` (style reference) |
| `--ref-image-cos-bucket` | COS Bucket for multi-image reference (can be specified multiple times) |
| `--ref-image-cos-region` | COS Region for multi-image reference (can be specified multiple times) |
| `--ref-image-cos-key` | COS Key for multi-image reference (can be specified multiple times) |
| `--duration` | Video duration (seconds). Supported ranges per model:<br>- Hunyuan: 5s (default)<br>- Hailuo: 6s (default) / 10s<br>- Kling: 5s / 10s (default)<br>- Vidu: 4s / 8s (default)<br>- OS: 5s (default) / 10s<br>- GV: 5s (default) / 10s |
| `--resolution` | Resolution: `720P` / `1080P` / `2K` / `4K` |
| `--aspect-ratio` | Aspect ratio (e.g., `16:9`, `9:16`, `1:1`, `4:3`, `3:4`) |
| `--no-logo` | Remove watermark (supported by Hailuo/Kling/Vidu) |
| `--enable-bgm` | Enable background music (supported by some model versions) |
| `--enable-audio` | Whether to generate audio for the video (supported by GV/OS, accepted values: `true`/`false`) |
| `--ref-video-url` | Reference video URL (Kling O1 only) |
| `--ref-video-type` | Reference video type: `feature` (feature reference) / `base` (video to be edited, default) |
| `--keep-original-sound` | Keep original audio: `yes` / `no` |
| `--ref-video-cos-bucket` | COS Bucket for reference video (can be specified multiple times) |
| `--ref-video-cos-region` | COS Region for reference video (can be specified multiple times) |
| `--ref-video-cos-key` | COS Key for reference video (can be specified multiple times) |
| `--off-peak` | Off-peak mode (Vidu only), task completes within 48 hours |
| `--additional-params` | Additional parameters in JSON format for model-specific extensions (e.g., Kling camera control) |
| `--no-wait` | Submit task only, do not wait for results |
| `--task-id` | Query the result of an existing task |
| `--cos-bucket-name` | COS Bucket for result storage (if not configured, MPS temporary storage is used for 12 hours) |
| `--cos-bucket-region` | COS Region for result storage |
| `--cos-bucket-path` | COS path prefix for result storage, default `/output/aigc-video/` |
| `--download-dir` | Download the generated video to a specified local directory after task completion (by default, only the pre-signed URL is printed) |
| `--operator` | Operator name (optional) |
| `--poll-interval` | Polling interval (seconds), default 10 |
| `--max-wait` | Maximum wait time (seconds), default 1800 |
| `--verbose` / `-v` | Output verbose information |
| `--region` | MPS service region (reads `TENCENTCLOUD_API_REGION` environment variable first, default `ap-guangzhou`) |
| `--dry-run` | Print parameters only, do not call the API |

## Mandatory Rules

- **AIGC scripts do not support the `--cos-object` parameter** — its use is prohibited. COS input must use dedicated parameters:
  - First-frame image: `--image-cos-bucket` + `--image-cos-region` + `--image-cos-key`
  - Last-frame image: `--last-image-cos-bucket` + `--last-image-cos-region` + `--last-image-cos-key`
  - Multi-image reference: `--ref-image-cos-bucket` + `--ref-image-cos-region` + `--ref-image-cos-key`
  - Reference video: `--ref-video-cos-bucket` + `--ref-video-cos-region` + `--ref-video-cos-key`
- When the user provides bucket/region/key, all three parameters must be passed in full — none may be omitted.

```bash
# COS image-to-video (explicitly specifying bucket/region/key)
python scripts/mps_aigc_video.py --prompt "Flowers swaying in the wind" \
    --image-cos-bucket mps-test-1234567 \
    --image-cos-region ap-guangzhou \
    --image-cos-key input/scene.jpg
```

## Multi-Shot Storyboard (Kling Exclusive)

### Single-Shot Mode (System Auto-Split)
```bash
python scripts/mps_aigc_video.py --prompt "Travel diary, capturing beautiful moments" --model Kling --multi-shot
```

### Multi-Shot Mode (Custom Per Shot)
```bash
python scripts/mps_aigc_video.py --model Kling --multi-shot --duration 12 \
    --multi-prompts-json '[
      {"index": 1, "prompt": "At sunrise, viewing the city skyline from the hotel window", "duration": "3"},
      {"index": 2, "prompt": "Enjoying breakfast at a café, pedestrians on the street outside", "duration": "4"},
      {"index": 3, "prompt": "Walking in the park, sunlight filtering through the leaves", "duration": "5"}
    ]'
```

**Validation rules**: 1–6 shots; max 512 characters per prompt; each duration ≥ 1 second; total of all durations must equal the overall duration.

## Example Commands

```bash
# Text-to-video (Hunyuan default)
python scripts/mps_aigc_video.py --prompt "A cat stretching lazily in the sunlight"

# Kling 2.5 + 10s + 1080P + 16:9 + no watermark + BGM
python scripts/mps_aigc_video.py --prompt "Cyberpunk city" --model Kling --model-version 2.5 \
    --duration 10 --resolution 1080P --aspect-ratio 16:9 --no-logo --enable-bgm

# Image-to-video (first-frame image + description)
python scripts/mps_aigc_video.py --prompt "Bring the scene to life" \
    --image-url https://example.com/photo.jpg

# First & last frame video generation (GV model)
python scripts/mps_aigc_video.py --prompt "Transition animation" --model GV \
    --image-url https://example.com/start.jpg --last-image-url https://example.com/end.jpg

# GV multi-image reference video generation (supports asset/style reference types)
python scripts/mps_aigc_video.py --prompt "Generate video with blended styles" --model GV \
    --ref-image-url https://example.com/img1.jpg --ref-image-type asset \
    --ref-image-url https://example.com/img2.jpg --ref-image-type style

# Kling O1 reference video + keep original audio
python scripts/mps_aigc_video.py --prompt "Stylize the video" --model Kling --model-version O1 \
    --ref-video-url https://example.com/video.mp4 --ref-video-type base --keep-original-sound yes

# Vidu off-peak mode
python scripts/mps_aigc_video.py --prompt "Natural scenery" --model Vidu --off-peak

# Submit task only without waiting
python scripts/mps_aigc_video.py --prompt "Promotional video" --no-wait

# Query task result
python scripts/mps_aigc_video.py --task-id abc123def456-aigc-video-20260328112000
```