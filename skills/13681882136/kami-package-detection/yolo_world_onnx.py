import cv2
import numpy as np
import onnxruntime as ort
import time
import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta, timezone
import re

DEFAULT_DATE = "2000-01-01"  # Default date for time-only strings


def parse_time(time_str: str) -> datetime:
    """
    Parse a time string and return a timezone-aware datetime object.
    Supports three formats:
      1) ISO UTC: "2024-03-25T06:00:00Z"
      2) CST local: "14:00:00 2024-03-25"  (UTC+8)
      3) Time only: "14:00:00"             (default date + CST)
    """
    # Format 1: ISO UTC ending with Z
    if time_str.endswith('Z') and 'T' in time_str:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    # Format 2: CST local "HH:MM:SS YYYY-MM-DD"
    pattern_full = r'^(\d{2}):(\d{2}):(\d{2}) (\d{4})-(\d{2})-(\d{2})$'
    match = re.match(pattern_full, time_str)
    if match:
        h, m, s, y, mo, d = map(int, match.groups())
        cst_tz = timezone(timedelta(hours=8))
        return datetime(y, mo, d, h, m, s, tzinfo=cst_tz)

    # Format 3: Time only "HH:MM:SS" (default date + CST)
    pattern_time = r'^(\d{2}):(\d{2}):(\d{2})$'
    match = re.match(pattern_time, time_str)
    if match:
        h, m, s = map(int, match.groups())
        cst_tz = timezone(timedelta(hours=8))
        y, mo, d = map(int, DEFAULT_DATE.split('-'))
        return datetime(y, mo, d, h, m, s, tzinfo=cst_tz)

    raise ValueError(f"Unsupported time format: {time_str}")


# ==================== Logging Configuration ====================
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "yolo_world_onnx_log.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ------------------ Helper Functions ------------------
def letterbox(img, new_shape=320, color=(114, 114, 114)):
    shape = img.shape[:2]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
    dw /= 2
    dh /= 2
    if shape[::-1] != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img, r, (dw, dh)


def parse_output(output, conf_threshold=0.25, class_names=None):
    if len(output.shape) == 3:
        output = output.transpose(0, 2, 1)[0]
    else:
        output = output[0]
    boxes = []
    scores = []
    class_ids = []
    num_classes = len(class_names) if class_names is not None else output.shape[1] - 4
    for pred in output:
        bbox = pred[:4]
        cls_scores = pred[4:4+num_classes]
        max_score = np.max(cls_scores)
        if max_score > conf_threshold:
            class_id = np.argmax(cls_scores)
            boxes.append(bbox)
            scores.append(max_score)
            class_ids.append(class_id)
    return np.array(boxes), np.array(scores), np.array(class_ids)


def xywh2xyxy(x):
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2
    y[..., 1] = x[..., 1] - x[..., 3] / 2
    y[..., 2] = x[..., 0] + x[..., 2] / 2
    y[..., 3] = x[..., 1] + x[..., 3] / 2
    return y


def scale_boxes(boxes, orig_shape, ratio, pad):
    if len(boxes) == 0:
        return boxes
    boxes = xywh2xyxy(boxes)
    boxes[:, [0, 2]] -= pad[0]
    boxes[:, [1, 3]] -= pad[1]
    boxes /= ratio
    boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, orig_shape[1])
    boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, orig_shape[0])
    return boxes.astype(int)


def nms(boxes, scores, iou_threshold):
    if len(boxes) == 0:
        return []
    indices = cv2.dnn.NMSBoxes(boxes.tolist(), scores.tolist(), 0.0, iou_threshold)
    if len(indices) > 0:
        return indices.flatten()
    return []


def get_color(class_id):
    colors = [
        (255, 0, 0),    # blue
        (0, 255, 0),    # green
        (0, 0, 255),    # red
        (255, 255, 0),  # cyan
        (255, 0, 255),  # magenta
        (0, 255, 255)   # yellow
    ]
    return colors[class_id % len(colors)]


def format_detection_result(class_name: str, bbox: list) -> dict:
    """Format a single detection result as a dictionary."""
    return {
        "class_name": class_name,
        "bbox": {"x1": int(bbox[0]), "y1": int(bbox[1]), "x2": int(bbox[2]), "y2": int(bbox[3])}
    }


# ------------------ Configuration ------------------
def parse_args():
    parser = argparse.ArgumentParser(description='YOLO-World ONNX Object Detection')
    parser.add_argument('--rtsp_url', type=str, default="rtsp://127.0.0.1/live/TNPUSAQ-757597-DRFMY",
                        help='RTSP camera URL')
    parser.add_argument('--conf_threshold', type=float, default=0.25,
                        help='Confidence threshold')
    parser.add_argument('--class_names', type=str, nargs='+',
                        default=["parcel", "package", "delivery box", "person", "Cardboard box", "Packaging Box", "backpack", "handbag", "suitcase"],
                        help='List of class names to detect')
    parser.add_argument('--run_time', type=int, default=60,
                        help='Max run time in seconds, 0 for unlimited')
    return parser.parse_args()


def main():
    args = parse_args()

    VIDEO_PATH = args.rtsp_url
    ONNX_MODEL = os.path.join(script_dir, "yolov8s-worldv2.onnx")
    CONF_THRESHOLD = args.conf_threshold
    IOU_THRESHOLD = 0.45
    INPUT_SIZE = 320
    CLASS_NAMES = args.class_names
    max_run_time = args.run_time

    logger.info("===== Detection started =====")
    logger.info(f"RTSP URL: {VIDEO_PATH}")
    logger.info(f"Model path: {ONNX_MODEL}")
    logger.info(f"Confidence threshold: {CONF_THRESHOLD}")
    logger.info(f"IOU threshold: {IOU_THRESHOLD}")
    logger.info(f"Input size: {INPUT_SIZE}")
    logger.info(f"Class names: {CLASS_NAMES}")
    if max_run_time > 0:
        logger.info(f"Max run time: {max_run_time} seconds")
    else:
        logger.info("Run time: unlimited")

    # ------------------ Initialize ONNX Runtime ------------------
    if not os.path.exists(ONNX_MODEL):
        logger.error(f"Model file not found: {ONNX_MODEL}")
        sys.exit(1)

    logger.info(f"Loading model: {ONNX_MODEL}")
    try:
        session = ort.InferenceSession(ONNX_MODEL, providers=['CPUExecutionProvider'])
        input_name = session.get_inputs()[0].name
        logger.info("Model loaded successfully")
        logger.info(f"Input shape: {session.get_inputs()[0].shape}")
        logger.info(f"Output shape: {session.get_outputs()[0].shape}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        sys.exit(1)

    # ------------------ Open Video ------------------
    logger.info(f"Opening video source: {VIDEO_PATH}")
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {VIDEO_PATH}")
        sys.exit(1)

    logger.info("Video opened successfully")
    logger.info(f"Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    logger.info(f"Total frames: {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}")
    logger.info("Starting detection")

    # ------------------ Main Loop ------------------
    frame_count = 0
    total_fps = 0
    start_program_time = time.time()

    try:
        while True:
            # Check timeout (only when run_time > 0)
            if max_run_time > 0 and (time.time() - start_program_time) > max_run_time:
                logger.info(f"Run time reached {max_run_time} seconds, exiting")
                break

            ret, frame = cap.read()
            if not ret:
                logger.warning("Cannot read frame, video may have ended")
                break

            frame_count += 1
            start_time = time.time()
            orig_shape = frame.shape[:2]

            # Preprocessing
            img, ratio, pad = letterbox(frame, INPUT_SIZE)
            img = img[:, :, ::-1].transpose(2, 0, 1)
            img = np.ascontiguousarray(img)
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0)

            # Inference
            outputs = session.run(None, {input_name: img})

            # Parse output
            if len(outputs) > 0:
                boxes, scores, class_ids = parse_output(outputs[0], CONF_THRESHOLD, CLASS_NAMES)

                if len(boxes) > 0:
                    boxes_scaled = scale_boxes(boxes, orig_shape, ratio, pad)
                    keep = nms(boxes_scaled, scores, IOU_THRESHOLD)

                    for i in keep:
                        x1, y1, x2, y2 = boxes_scaled[i]
                        conf = scores[i]
                        cls_id = class_ids[i]

                        # Output JSON and exit when non-person target detected
                        if CLASS_NAMES[cls_id].lower() != "person":
                            logger.info(f"Target detected - frame:{frame_count}, class:{CLASS_NAMES[cls_id]}, confidence:{conf:.2f}")
                            detection = format_detection_result(
                                CLASS_NAMES[cls_id], [x1, y1, x2, y2]
                            )
                            result = {"detections": [detection]}
                            print(json.dumps(result, ensure_ascii=False))
                            cap.release()
                            avg_fps = total_fps / frame_count if frame_count > 0 else 0
                            logger.info(f"Done! Total frames: {frame_count}, Avg FPS: {avg_fps:.2f}")
                            logger.info("===== Program exit =====")
                            sys.exit(0)

            # Calculate FPS
            fps = 1.0 / (time.time() - start_time)
            total_fps += fps

            # Print progress every 30 frames
            if frame_count % 30 == 0:
                avg_fps = total_fps / frame_count
                logger.info(f"Frame {frame_count}, Avg FPS: {avg_fps:.2f}")

    finally:
        cap.release()

    # Normal exit stats (timeout or video ended)
    avg_fps = total_fps / frame_count if frame_count > 0 else 0
    logger.info(f"Done! Total frames: {frame_count}, Avg FPS: {avg_fps:.2f}")
    logger.info("===== Program exit (timeout/no detection) =====")
    sys.exit(2)


if __name__ == "__main__":
    main()
