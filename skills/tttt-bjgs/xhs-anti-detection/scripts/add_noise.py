#!/usr/bin/env python3
"""
xhs-anti-detection: add_noise.py

添加噪声和纹理：高斯噪声 + 颗粒纹理，打破统计检测特征。
"""

import sys
import json
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image

CONFIG_PATH = Path(__file__).parent.parent / "references" / "safe_params.json"
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)


def add_gaussian_noise(img_array: np.ndarray, sigma: float = 2.0) -> np.ndarray:
    """添加高斯噪声"""
    noise = np.random.normal(0, sigma, img_array.shape)
    result = img_array.astype(np.float32) + noise
    result = np.clip(result, 0, 255)
    return result.astype(np.uint8)


def add_grain_texture(rgb: np.ndarray, amount: float = 0.3) -> np.ndarray:
    """添加颗粒纹理（模拟胶片颗粒）"""
    # 生成随机噪声
    noise = np.random.uniform(0, 255, rgb.shape).astype(np.float32)
    # 混合
    result = rgb.astype(np.float32) * (1 - amount) + noise * amount
    return np.clip(result, 0, 255).astype(np.uint8)


def process_image(input_path: Path, output_path: Optional[Path] = None,
                  strength: str = "medium") -> bool:
    """处理单个图像的噪声添加"""
    print(f"[INFO] 添加噪声: {input_path}")

    # 加载强度配置
    config = CONFIG
    preset = config["strength_presets"].get(strength, config["strength_presets"]["medium"])
    sigma = preset.get("noise_sigma", config["processing"]["noise_sigma"])
    grain_amount = preset.get("grain_amount", config["processing"]["texture"]["grain_amount"])

    print(f"[INFO] 噪声强度: sigma={sigma}, grain={grain_amount}")

    # 读取图像
    img = Image.open(input_path)
    if img.mode not in ('RGB', 'RGBA', 'L'):
        img = img.convert('RGB')
    
    # 保留所有元数据
    exif_data = img.getexif() if hasattr(img, 'getexif') else None
    png_text = img.text if hasattr(img, 'text') and img.text else None

    img_array = np.array(img)

    # 步骤 1: 高斯噪声
    noisy = add_gaussian_noise(img_array, sigma)
    print(f"[INFO] 已添加高斯噪声 (σ={sigma})")

    # 步骤 2: 颗粒纹理（仅对彩色图像）
    if len(noisy.shape) == 3 and noisy.shape[2] >= 3:
        if noisy.shape[2] == 4:  # RGBA
            rgb = noisy[:, :, :3]
            alpha = noisy[:, :, 3]
            # grain_amount 从百分比转换为小数 (5% → 0.05)
            grain_factor = grain_amount / 100.0
            grainy = add_grain_texture(rgb, grain_factor)
            result_array = np.dstack([grainy, alpha])
        else:
            # grain_amount 从百分比转换为小数
            grain_factor = grain_amount / 100.0
            result_array = add_grain_texture(noisy, grain_factor)
        print(f"[INFO] 已添加颗粒纹理 (amount={grain_amount}%, factor={grain_factor:.3f})")
    else:
        result_array = noisy

    # 转换回图像
    result_img = Image.fromarray(result_array, mode=img.mode)

    # 输出路径
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}.noisy{input_path.suffix}"

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
    print(f"[SUCCESS] 噪声处理完成: {output_path}")

    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python add_noise.py --input <image> [--output <path>] [--strength light|medium|heavy]")
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
