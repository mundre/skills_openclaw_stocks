---
name: kami-package-detection
description: A free skill by Kami SmartHome. Get notified the moment a package arrives at your door. Detects packages, parcels, and bags from RTSP camera streams using AI vision.
version: 1.0.2
author: kami-smarthome
tags:
  - smart-home
  - object-detection
  - yolo
  - package-detection
  - parcel-detection
  - iot
  - camera
  - rtsp
  - onnx
  - edge-ai
  - delivery
  - monitoring
  - notification
triggers:
  - detect packages
  - detect parcels
  - check for deliveries
  - package detection
  - is there a package
  - monitor packages
  - check camera for packages
  - any deliveries at the door
metadata:
  openclaw:
    requires:
      bins:
        - python3
    emoji: "📦"
---

# Kami Package Detection

> Get notified the moment a package arrives at your door.

Monitor your camera feed for packages, parcels, backpacks, handbags, and suitcases. When detected, returns the object class and bounding box as JSON — ready for automation.

### Features

- 📦 Package & parcel detection
- 🧳 Suitcase / backpack / handbag recognition
- 🏠 Doorstep & reception monitoring
- ⏱ Configurable detection duration
- 🔔 JSON output for easy integration

### Scenarios

- Doorstep delivery waiting
- Office reception package management
- Warehouse cargo monitoring
- Temporary item watch

## Installation

```bash
bash setup.sh
```

Creates `.venv/` and installs `onnxruntime`, `opencv-python-headless`, `numpy`. Idempotent.

## Prerequisites

- `python3` and `python3-venv` installed
- `yolov8s-worldv2.onnx` model file in the skill directory
- RTSP camera online and reachable

### Model

The `yolov8s-worldv2.onnx` model file is included in the skill package. If missing, re-download this skill from ClawHub:

```bash
clawhub install kami-package-detection
```

## Parameter Confirmation

Before running, confirm these parameters with the user:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--rtsp_url` | `rtsp://127.0.0.1/live/TNPUSAQ-757597-DRFMY` | RTSP camera URL |
| `--conf_threshold` | `0.25` | Confidence threshold (0.0–1.0) |
| `--class_names` | `parcel package "delivery box" person "Cardboard box" "Packaging Box" backpack handbag suitcase` | Classes to detect |
| `--run_time` | `60` | Max seconds; `0` = unlimited |

**Ask the user: do any parameters need to be changed?**

## Usage

```bash
.venv/bin/python yolo_world_onnx.py \
  --rtsp_url rtsp://your-camera-address \
  --run_time 60
```

## Output (stdout JSON)

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

| Field | Type | Description |
|-------|------|-------------|
| `class_name` | string | Detected object class |
| `bbox.x1, y1, x2, y2` | int | Bounding box coordinates |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Target detected, JSON output written |
| `1` | Error (model missing, RTSP failure, runtime exception) |
| `2` | Timeout, no target detected within `--run_time` |

## Troubleshooting

- `bash: .venv/bin/python: No such file or directory` → Run `bash setup.sh`
- `Model file not found` → Place `yolov8s-worldv2.onnx` in the skill directory
- `Cannot open video` → Check camera is online and `--rtsp_url` is correct
