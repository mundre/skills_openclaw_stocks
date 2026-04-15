#!/usr/bin/env python3
"""
xhs-anti-detection: color_shift.py

色彩偏移处理：轻微改变图像的色相和饱和度，打破 AI 检测模型的统计特征。
"""

import sys
import json
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import cv2
from PIL import Image

CONFIG_PATH = Path(__file__).parent.parent / "references" / "safe_params.json"
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)


def shift_hue_saturation(rgb: np.ndarray, hue_shift_deg: float, sat_factor: float) -> np.ndarray:
    """偏移色相和饱和度（基于 HSV 空间）"""
    # 转换为 HSV
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    
    # 色相偏移（度 → 0-255 范围）
    hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift_deg * (255/360)) % 255
    
    # 饱和度调整
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat_factor, 0, 255)
    
    # 转回 RGB
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    return result


def process_image(input_path: Path, output_path: Optional[Path] = None,
                  strength: str = "medium") -> bool:
    """处理单个图像的色彩偏移"""
    print(f"[INFO] 色彩偏移处理: {input_path}")

    # 加载强度配置
    config = CONFIG
    preset = config["strength_presets"].get(strength, config["strength_presets"]["medium"])
    hue_shift = preset.get("color_shift_hue_deg", config["processing"]["color_shift"]["hue_deg"])
    sat_factor = 1 + (preset.get("color_shift_saturation_pct", config["processing"]["color_shift"]["saturation_pct"]) / 100.0)

    print(f"[INFO] 色相偏移: ±{hue_shift}°, 饱和度系数: {sat_factor:.2f}")

    # 读取图像
    img = Image.open(input_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    
    # 保留所有元数据
    exif_data = img.getexif() if hasattr(img, 'getexif') else None
    png_text = img.text if hasattr(img, 'text') and img.text else None

    img_array = np.array(img)

    # 处理色彩
    if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
        rgb = img_array[:, :, :3]
        shifted = shift_hue_saturation(rgb, hue_shift, sat_factor)

        # 如果有 alpha 通道，保留
        if img_array.shape[2] == 4:
            result_array = np.dstack([shifted, img_array[:, :, 3]])
        else:
            result_array = shifted
    else:
        result_array = img_array

    result_img = Image.fromarray(result_array, mode=img.mode)

    # 输出路径
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}.color{input_path.suffix}"

    # 保存（合并所有元数据）
    save_kwargs = {'quality': 95, 'optimize': True}
    if exif_data:
        try:
            save_kwargs['exif'] = exif_data.tobytes()
        except Exception:
            pass
    
    # 合并 PNG 文本块
    if png_text:
        try:
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            for key, value in png_text.items():
                pnginfo.add_text(key, str(value))
            pnginfo.add_text("Make", "iPhone")
            pnginfo.add_text("Model", "iPhone 15 Pro")
            pnginfo.add_text("Software", "Adobe Photoshop Lightroom Classic 13.0")
            save_kwargs['pnginfo'] = pnginfo
        except Exception as e:
            print(f"[WARN] PNG 文本块处理失败: {e}")

    result_img.save(output_path, **save_kwargs)
    print(f"[SUCCESS] 色彩偏移完成: {output_path}")

    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python color_shift.py --input <image> [--output <path>] [--strength light|medium|heavy]")
        sys.exit(1)

    input_path = None
    output_path = None
    strength = "medium"

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--input" and i + 1 < len(args):
            input_path = Path(args[i + 1])
        elif arg == "--output" and i + 1 < len(args):
            output_path = Path(args[i + 1])
        elif arg == "--strength" and i + 1 < len(args):
            strength = args[i + 1]

    if not input_path or not input_path.exists():
        print(f"[ERROR] 输入文件不存在: {input_path}")
        sys.exit(1)

    process_image(input_path, output_path, strength)
    sys.exit(0)


if __name__ == "__main__":
    main()
