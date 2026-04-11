---
name: seedance-video
description: >
  使用字节跳动 Seedance 生成 AI 视频：文生视频、图生视频（首帧/首尾帧/参考图）、
  异步任务查询。支持 Seedance 2.0（多模态输入、视频续生、视频编辑）等多个模型。
  Use when: (1) 用户说"生成视频"/"做个视频"/"AI视频"/"text to video",
  (2) 用户要求根据图片生成视频/动画/"图生视频"/"image to video",
  (3) 用户提到 Seedance/字节视频生成,
  (4) 用户说"帮我做段视频"/"生成一段动画"。
  NOT for: 从已有视频中抽帧/截图（用 video-frames）、
  视频剪辑/转码/格式转换（用 ffmpeg 直接操作）、实拍视频处理。
version: 1.0.0
category: file-generation
argument-hint: "[text prompt or task ID]"
---

# Seedance Video Generation

Generate AI videos using ByteDance Seedance models via the Volcengine Ark API.

## Prerequisites

Set the `ARK_API_KEY` environment variable before making API calls (the API rejects unauthenticated requests):

```bash
export ARK_API_KEY="your-api-key-here"
```

**Base URL**: `https://ark.cn-beijing.volces.com/api/v3`

## Supported Models

| Model | Model ID | Capabilities |
|-------|----------|-------------|
| **Seedance 2.0** | `doubao-seedance-2-0-260128` | **Multimodal input (text+image+video+audio), Video extension, Video editing** |
| Seedance 2.0 Fast | `doubao-seedance-2-0-fast-260128` | Same as 2.0, faster generation |
| Seedance 1.5 Pro | `doubao-seedance-1-5-pro-251215` | Text-to-video, Image-to-video (first frame, first+last frame), Audio support, Draft mode |
| Seedance 1.0 Pro | `doubao-seedance-1-0-pro-250528` | Text-to-video, Image-to-video (first frame, first+last frame) |
| Seedance 1.0 Pro Fast | `doubao-seedance-1-0-pro-fast-251015` | Text-to-video, Image-to-video (first frame only) |
| Seedance 1.0 Lite T2V | `doubao-seedance-1-0-lite-t2v-250428` | Text-to-video only |
| Seedance 1.0 Lite I2V | `doubao-seedance-1-0-lite-i2v-250428` | Image-to-video (first frame, first+last frame, reference images 1-4) |

**Default model**: `doubao-seedance-1-5-pro-251215` (stable, supports audio)

> 💡 Seedance 2.0 (`doubao-seedance-2-0-260128`) 已上线但需在方舟控制台激活，激活后改 seedance.py 的 DEFAULT_MODEL 即可切换。

## Execution (Recommended: Python CLI Tool)

A Python CLI tool is provided at `~/.claude/skills/seedance-video/seedance.py` for robust execution with proper error handling, automatic retries, and local image base64 conversion. **Prefer using this tool over raw curl commands.**

### Quick Examples with Python CLI

```bash
# Text-to-video (create + wait + download)
python3 ~/.claude/skills/seedance-video/seedance.py create --prompt "小猫对着镜头打哈欠" --wait --download ~/Desktop

# Image-to-video from local file
python3 ~/.claude/skills/seedance-video/seedance.py create --prompt "人物缓缓转头微笑" --image /path/to/photo.jpg --wait --download ~/Desktop

# Image-to-video from URL
python3 ~/.claude/skills/seedance-video/seedance.py create --prompt "风景画面缓缓推进" --image "https://example.com/image.jpg" --wait --download ~/Desktop

# First + last frame
python3 ~/.claude/skills/seedance-video/seedance.py create --prompt "花朵从含苞到盛开" --image first.jpg --last-frame last.jpg --wait --download ~/Desktop

# Reference images (Lite I2V)
python3 ~/.claude/skills/seedance-video/seedance.py create --prompt "[图1]的人物在跳舞" --ref-images ref1.jpg ref2.jpg --model doubao-seedance-1-0-lite-i2v-250219 --wait --download ~/Desktop

# Custom parameters
python3 ~/.claude/skills/seedance-video/seedance.py create --prompt "城市夜景延时摄影" --ratio 21:9 --duration 8 --resolution 1080p --generate-audio false --wait --download ~/Desktop

# Draft mode (cheaper preview)
python3 ~/.claude/skills/seedance-video/seedance.py create --prompt "海浪拍打沙滩" --draft true --wait --download ~/Desktop

# Generate final video from draft
python3 ~/.claude/skills/seedance-video/seedance.py create --draft-task-id <DRAFT_TASK_ID> --resolution 720p --wait --download ~/Desktop

# Query task status
python3 ~/.claude/skills/seedance-video/seedance.py status <TASK_ID>

# Wait for an existing task
python3 ~/.claude/skills/seedance-video/seedance.py wait <TASK_ID> --download ~/Desktop

# List tasks
python3 ~/.claude/skills/seedance-video/seedance.py list --status succeeded

# Delete/cancel task
python3 ~/.claude/skills/seedance-video/seedance.py delete <TASK_ID>
```

## Alternative: Raw curl Commands

### Step 1: Create Video Generation Task

Determine the generation mode based on user input, then call the API.

#### Mode A: Text-to-Video

```bash
TASK_RESULT=$(curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      {
        "type": "text",
        "text": "YOUR_PROMPT_HERE"
      }
    ],
    "ratio": "16:9",
    "duration": 5,
    "resolution": "720p",
    "generate_audio": true
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

#### Mode B: Image-to-Video (First Frame)

The user provides one image as the first frame. The image can be a URL or local file path (convert to base64).

**With image URL:**
```bash
TASK_RESULT=$(curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      {
        "type": "text",
        "text": "YOUR_PROMPT_HERE"
      },
      {
        "type": "image_url",
        "image_url": { "url": "IMAGE_URL_HERE" },
        "role": "first_frame"
      }
    ],
    "ratio": "adaptive",
    "duration": 5,
    "resolution": "720p",
    "generate_audio": true
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

**With local image file (convert to base64):**
```bash
IMG_PATH="/path/to/image.png"
IMG_EXT="${IMG_PATH##*.}"
IMG_EXT_LOWER=$(echo "$IMG_EXT" | tr '[:upper:]' '[:lower:]')
IMG_BASE64=$(base64 < "$IMG_PATH" | tr -d '\n')
IMG_DATA_URL="data:image/${IMG_EXT_LOWER};base64,${IMG_BASE64}"

TASK_RESULT=$(curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      {
        "type": "text",
        "text": "YOUR_PROMPT_HERE"
      },
      {
        "type": "image_url",
        "image_url": { "url": "'"$IMG_DATA_URL"'" },
        "role": "first_frame"
      }
    ],
    "ratio": "adaptive",
    "duration": 5,
    "resolution": "720p",
    "generate_audio": true
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

#### Mode C: Image-to-Video (First + Last Frame)

Requires two images. Supported by: Seedance 1.5 Pro, 1.0 Pro, 1.0 Lite I2V.

```bash
TASK_RESULT=$(curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      {
        "type": "text",
        "text": "YOUR_PROMPT_HERE"
      },
      {
        "type": "image_url",
        "image_url": { "url": "FIRST_FRAME_IMAGE_URL" },
        "role": "first_frame"
      },
      {
        "type": "image_url",
        "image_url": { "url": "LAST_FRAME_IMAGE_URL" },
        "role": "last_frame"
      }
    ],
    "ratio": "adaptive",
    "duration": 5,
    "resolution": "720p",
    "generate_audio": true
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

#### Mode D: Reference Image-to-Video (Seedance 1.0 Lite I2V only)

Provide 1-4 reference images. Use `[图1]`, `[图2]` in prompt to reference specific images.

```bash
TASK_RESULT=$(curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-0-lite-i2v-250219",
    "content": [
      {
        "type": "text",
        "text": "[图1]的人物在跳舞"
      },
      {
        "type": "image_url",
        "image_url": { "url": "REF_IMAGE_URL_1" },
        "role": "reference_image"
      }
    ],
    "ratio": "16:9",
    "duration": 5,
    "resolution": "720p"
  }')

TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Task created: $TASK_ID"
```

### Step 2: Poll for Task Completion

Video generation is asynchronous. Poll the task status until it completes.

```bash
echo "Waiting for video generation to complete..."
while true; do
  STATUS_RESULT=$(curl -s -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/${TASK_ID}" \
    -H "Authorization: Bearer $ARK_API_KEY")

  STATUS=$(echo "$STATUS_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")

  if [ "$STATUS" = "succeeded" ]; then
    echo "Video generation succeeded!"
    VIDEO_URL=$(echo "$STATUS_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['content']['video_url'])")
    echo "Video URL: $VIDEO_URL"
    break
  elif [ "$STATUS" = "failed" ]; then
    ERROR_MSG=$(echo "$STATUS_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message','Unknown error'))" 2>/dev/null || echo "Unknown error")
    echo "Video generation failed: $ERROR_MSG"
    break
  elif [ "$STATUS" = "expired" ]; then
    echo "Video generation task expired."
    break
  else
    echo "Status: $STATUS - still processing..."
    sleep 15
  fi
done
```

### Step 3: Download and Open Video

```bash
OUTPUT_PATH="$HOME/Desktop/seedance_video_$(date +%Y%m%d_%H%M%S).mp4"
curl -s -o "$OUTPUT_PATH" "$VIDEO_URL"
echo "Video saved to: $OUTPUT_PATH"
open "$OUTPUT_PATH"
```

## Optional Parameters Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `doubao-seedance-1-5-pro-251215` | Model ID to use |
| `ratio` | string | `16:9` (text2vid) / `adaptive` (img2vid) | Aspect ratio: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`, `adaptive` |
| `duration` | integer | `5` | Video duration in seconds (4-12 for 1.5 Pro, 2-12 for others). Set `-1` for auto (1.5 Pro only) |
| `resolution` | string | `720p` | Resolution: `480p`, `720p`, `1080p` |
| `seed` | integer | `-1` | Random seed for reproducibility. -1 = random |
| `camera_fixed` | boolean | `false` | Fix camera position |
| `watermark` | boolean | `false` | Add watermark to video |
| `generate_audio` | boolean | `true` | Generate synchronized audio (Seedance 1.5 Pro only) |
| `draft` | boolean | `false` | Generate draft/preview video at lower cost (Seedance 1.5 Pro only, forces 480p) |
| `return_last_frame` | boolean | `false` | Return last frame image URL (for chaining consecutive videos) |
| `service_tier` | string | `default` | `default` (online) or `flex` (offline, 50% cheaper, slower) |
| `execution_expires_after` | integer | `172800` | Task timeout in seconds (3600-259200) |

## Additional Operations

### Query Task Status

```bash
curl -s -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/${TASK_ID}" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -m json.tool
```

### List Tasks

```bash
# List all tasks (paginated)
curl -s -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks?page_num=1&page_size=10" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -m json.tool

# Filter by status
curl -s -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks?page_num=1&page_size=10&filter.status=succeeded" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -m json.tool
```

### Cancel or Delete Task

```bash
curl -s -X DELETE "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/${TASK_ID}" \
  -H "Authorization: Bearer $ARK_API_KEY"
```

Note: `queued` tasks will be cancelled; `succeeded`/`failed`/`expired` tasks will be deleted from history.

### Generate Consecutive Videos (Using Last Frame)

Set `return_last_frame: true` on the first task, then use the returned `last_frame_url` as the first frame of the next task.

```bash
# Get last frame URL from completed task
LAST_FRAME_URL=$(curl -s -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/${TASK_ID}" \
  -H "Authorization: Bearer $ARK_API_KEY" | python3 -c "import sys,json; print(json.load(sys.stdin)['content']['last_frame_url'])")

# Use it as first frame for the next video
# ... (use Mode B with LAST_FRAME_URL as the image URL)
```

### Draft Mode (Seedance 1.5 Pro)

Generate a cheap preview first, then produce the final video if satisfied:

```bash
# Step 1: Create draft
DRAFT_RESULT=$(curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      { "type": "text", "text": "YOUR_PROMPT_HERE" }
    ],
    "draft": true,
    "resolution": "480p"
  }')
DRAFT_TASK_ID=$(echo "$DRAFT_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Step 2: After draft succeeds, generate final video from draft
FINAL_RESULT=$(curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      {
        "type": "draft_task",
        "draft_task": { "id": "'"$DRAFT_TASK_ID"'" }
      }
    ],
    "resolution": "720p"
  }')
```

## Image Requirements

- Formats: jpeg, png, webp, bmp, tiff, gif (1.5 Pro also supports heic, heif)
- Aspect ratio (width/height): between 0.4 and 2.5
- Dimensions: 300-6000 px per side
- Max file size: 30 MB

## 通过飞书发送视频文件（OpenClaw）

详见 [how_to_send_video_via_feishu_app.md](how_to_send_video_via_feishu_app.md)

## Rules

1. **检查 API Key**：调用前验证 `ARK_API_KEY` 已设置 — API 会直接拒绝未认证请求
2. **默认模型**：Seedance 1.5 Pro (`doubao-seedance-1-5-pro-251215`)，除非用户指定其他模型
3. **文生视频默认参数**：720p, 16:9, 5 秒, 带音频
4. **图生视频默认参数**：自适应比例（根据输入图片自动适配）
5. **轮询间隔**：每 15 秒检查一次任务状态
6. **视频 URL 24 小时过期** — 生成后立即下载，否则链接会失效需要重新生成
7. **任务历史保留 7 天** — 超期后无法查询
8. 本地图片文件需转为 base64 data URL 格式后再发送
9. 展示 task ID 给用户，方便后续查询状态
10. 生成失败时清晰展示错误信息并建议修复方案
