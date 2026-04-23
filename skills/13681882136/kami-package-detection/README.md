# 📦 Kami Package Detection

> A free skill by **Kami SmartHome** — get notified the moment a package arrives at your door.

Monitor your RTSP camera feed for packages, parcels, backpacks, handbags, and suitcases using YOLOv8-World ONNX inference. When detected, outputs the object class and bounding box as structured JSON to stdout.

### Features

- 📦 Package & parcel detection
- 🧳 Suitcase / backpack / handbag recognition
- 🏠 Doorstep & reception monitoring
- ⏱ Configurable detection duration
- 🔔 JSON output for easy integration
- 🖥 CPU-only inference via `onnxruntime` — no GPU required
- 🐍 Isolated `.venv` — zero impact on system Python

### Scenarios

- Doorstep delivery waiting
- Office reception package management
- Warehouse cargo monitoring
- Temporary item watch

## Quick Start

```bash
# 1. Run setup (one-time)
bash setup.sh

# 2. Place your ONNX model file
cp /path/to/yolov8s-worldv2.onnx .

# 3. Run detection
.venv/bin/python yolo_world_onnx.py \
  --rtsp_url rtsp://192.168.1.100/live/camera01 \
  --conf_threshold 0.25 \
  --class_names parcel package "delivery box" person "Cardboard box" "Packaging Box" backpack handbag suitcase \
  --run_time 120
```

## Installation

```bash
bash setup.sh
```

The setup script automatically:
1. Detects system Python (`python3` or `python`), exits with error if not found
2. Creates an isolated virtual environment at `.venv/`
3. Installs Python dependencies from `requirements.txt`

> Idempotent — safe to run multiple times. Won't reinstall existing dependencies.

### Requirements

| Dependency | Version | Purpose |
|------------|---------|---------|
| `onnxruntime` | latest | ONNX model inference engine |
| `opencv-python-headless` | latest | Video capture and image processing |
| `numpy` | latest | Array operations |

### System Prerequisites

- **Python 3.8+** and **python3-venv** (`sudo apt install python3 python3-venv`)
- **ONNX model file**: `yolov8s-worldv2.onnx` in the skill directory
- **RTSP camera**: online and network-reachable

## Usage

### Basic Detection

```bash
.venv/bin/python yolo_world_onnx.py \
  --rtsp_url rtsp://127.0.0.1/live/TNPUSAQ-757597-DRFMY \
  --conf_threshold 0.25 \
  --class_names parcel package "delivery box" person "Cardboard box" "Packaging Box" backpack handbag suitcase \
  --run_time 60
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--rtsp_url` | string | No | `rtsp://127.0.0.1/live/TNPUSAQ-757597-DRFMY` | RTSP camera stream URL |
| `--conf_threshold` | float | No | `0.25` | Detection confidence threshold (0.0–1.0) |
| `--class_names` | string[] | No | `parcel package "delivery box" person "Cardboard box" "Packaging Box" backpack handbag suitcase` | Space-separated class names to detect |
| `--run_time` | int | No | `60` | Max run time in seconds. `0` = unlimited |

## Output Format

When a non-person target is detected, the skill outputs JSON to **stdout** and exits with code `0`:

```json
{
  "detections": [
    {
      "class_name": "parcel",
      "bbox": {"x1": 100, "y1": 200, "x2": 300, "y2": 400}
    }
  ]
}
```

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `detections` | array | List of detected objects |
| `detections[].class_name` | string | Detected object class |
| `detections[].bbox.x1` | int | Bounding box left x |
| `detections[].bbox.y1` | int | Bounding box top y |
| `detections[].bbox.x2` | int | Bounding box right x |
| `detections[].bbox.y2` | int | Bounding box bottom y |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Target detected and JSON output written |
| `1` | Model file missing, RTSP connection failure, or runtime error |
| `2` | Run time exceeded, no target detected (timeout) |

> Exit code `0` = detection success, `2` = timeout with no detection, `1` = error.

## Architecture

```
RTSP Camera → [yolo_world_onnx.py] → JSON stdout
                    │
                    ├── letterbox (preprocessing)
                    ├── ONNX inference (YOLOv8-World)
                    ├── parse_output + NMS (post-processing)
                    └── format_detection_result (JSON output)
```

The skill follows a single-pass detection model:
1. Read frames from RTSP stream
2. Preprocess each frame (letterbox resize to 320×320)
3. Run ONNX inference
4. Parse detections, apply NMS
5. On first non-person detection → output JSON → exit

## Error Handling

| Scenario | Behavior | Exit Code |
|----------|----------|-----------|
| Model file (`yolov8s-worldv2.onnx`) not found | Log error, exit immediately | `1` |
| RTSP stream cannot connect | Log error, exit immediately | `1` |
| Model load failure (corrupt ONNX) | Log error, exit immediately | `1` |
| Run time exceeded | Log timeout info, exit | `2` |
| Video stream ends (no more frames) | Log warning, exit | `2` |

## Troubleshooting

### Virtual environment not found
```
bash: .venv/bin/python: No such file or directory
```
**Fix**: Run `bash setup.sh` to initialize the environment.

### Model file missing
```
Model file not found: .../yolov8s-worldv2.onnx
```
**Fix**: Download or copy `yolov8s-worldv2.onnx` into the skill directory.

### RTSP connection failure
```
Cannot open video: rtsp://...
```
**Fix**: Verify the camera is online, check the `--rtsp_url` value, and confirm network connectivity.

### Low detection rate
- Try lowering `--conf_threshold` (e.g., `0.15`)
- Ensure the target object class is included in `--class_names`
- Check camera angle and lighting conditions

## File Structure

```
kami-package-detection/
├── .gitignore
├── requirements.txt          # onnxruntime, opencv-python-headless, numpy
├── setup.sh                  # Environment setup with Python auto-detection
├── SKILL.md                  # AI agent instructions + metadata
├── README.md                 # This file
├── yolo_world_onnx.py        # Main detection script
├── yolov8s-worldv2.onnx      # ONNX model file (not included, user-provided)
└── tests/
    └── test_parcel_detection.py
```

## License

MIT-0
