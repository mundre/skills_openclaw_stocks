#!/usr/bin/env python3
"""
xhs-anti-detection: recompress.py

重新编码图像，改变压缩指纹，打破统计检测模式。
支持 PNG 和 JPEG 格式，可自定义输出格式。
"""

import sys
import json
import random
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image

CONFIG_PATH = Path(__file__).parent.parent / "references" / "safe_params.json"
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)


def recompress_image(input_path: Path, output_path: Optional[Path],
                     quality: int = 98, optimize: bool = True) -> Tuple[bool, Path]:
    """重新压缩图像，改变压缩指纹
    
    Args:
        input_path: 输入图像路径
        output_path: 输出图像路径（如果为 None，则自动生成）
        quality: JPEG 质量 (1-100)
        optimize: 是否优化编码
    
    Returns:
        (success, final_output_path)
    """
    print(f"[INFO] 重新编码: {input_path}")

    # 读取图像
    img = Image.open(input_path)
    
    # 保留所有元数据
    exif_data = img.getexif() if hasattr(img, 'getexif') else None
    png_text = img.text if hasattr(img, 'text') and img.text else None

    # 确定输出路径
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}.recomp{input_path.suffix}"

    # 确定输出格式 - 反检测处理应输出 JPEG 以减小文件大小并模拟相机照片
    # 如果用户指定了输出路径且为 .png，仍可保留 PNG，但建议使用 JPEG
    output_ext = output_path.suffix.lower()
    if output_ext in ['.jpg', '.jpeg']:
        output_format = 'JPEG'
        final_output_path = output_path
    elif output_ext == '.png':
        # 对于反检测场景，PNG 文件太大，建议转为 JPEG
        # 但保留用户指定的 PNG 输出（向后兼容）
        output_format = 'PNG'
        final_output_path = output_path
    else:
        output_format = 'JPEG'
        final_output_path = output_path.with_suffix('.jpg')

    # 如果需要将 PNG 转为 JPEG
    if input_path.suffix.lower() == '.png' and output_format == 'JPEG':
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

    # 设置保存参数
    save_kwargs = {
        'quality': quality,
        'optimize': optimize
    }

    if output_format == 'JPEG':
        save_kwargs['progressive'] = False
        # 随机子采样
        try:
            subsampling = random.choice([0, 2, 4])
            save_kwargs['subsampling'] = subsampling
        except Exception:
            subsampling = 'N/A'
        # 添加 EXIF 数据
        if exif_data:
            try:
                save_kwargs['exif'] = exif_data.tobytes()
            except Exception:
                pass
    else:
        subsampling = 'N/A'
        # PNG 格式：合并原始文本块 + 伪造相机信息
        try:
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            # 先添加原始文本块（保留所有原始信息）
            if png_text:
                for key, value in png_text.items():
                    pnginfo.add_text(key, str(value))
            # 再添加伪造的相机信息（覆盖或新增）
            pnginfo.add_text("Make", "iPhone")
            pnginfo.add_text("Model", "iPhone 15 Pro")
            pnginfo.add_text("Software", "Adobe Photoshop Lightroom Classic 13.0")
            save_kwargs['pnginfo'] = pnginfo
        except Exception as e:
            print(f"[WARN] PNG 文本块处理失败: {e}")

    # 保存
    img.save(final_output_path, format=output_format, **save_kwargs)

    print(f"[INFO] 重新编码完成: {final_output_path}")
    print(f"  格式: {output_format}, 质量: {quality}%" + 
          (f", 子采样: {subsampling}" if output_format == 'JPEG' else ""))

    return True, final_output_path


def process_image(input_path: Path, output_path: Optional[Path] = None,
                  strength: str = "medium") -> bool:
    """处理单个图像的重新编码（供 process.py 调用）"""
    config = CONFIG
    preset = config["strength_presets"].get(strength, config["strength_presets"]["medium"])

    quality = config["processing"]["recompression"]["quality"]
    # 强度影响质量
    if strength == "heavy":
        quality = max(90, quality - 5)
    elif strength == "light":
        quality = min(100, quality + 2)

    success, _ = recompress_image(input_path, output_path, quality=quality)
    return success


def main():
    if len(sys.argv) < 2:
        print("用法: python recompress.py --input <image> [--output <path>] [--strength light|medium|heavy]")
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

    # 根据强度调整质量
    quality = CONFIG["processing"]["recompression"]["quality"]
    if strength == "heavy":
        quality = max(90, quality - 5)
    elif strength == "light":
        quality = min(100, quality + 2)

    success, final_path = recompress_image(input_path, output_path, quality=quality)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
