#!/usr/bin/env python3
"""
xhs-anti-detection: protect_text.py

文字区域保护：对图像中的文字区域进行锐化，背景轻微模糊，
使 AI 检测模型难以识别文字内容。
"""

import sys
import json
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

# 检查 OpenCV 可用性
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

CONFIG_PATH = Path(__file__).parent.parent / "references" / "safe_params.json"
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)


def detect_text_regions_cv2(img_array: np.ndarray) -> Optional[np.ndarray]:
    """使用 OpenCV 检测文字区域（简化版）"""
    if not CV2_AVAILABLE:
        return None
    
    try:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        # 使用 Canny 边缘检测
        edges = cv2.Canny(gray, 50, 150)
        # 膨胀操作连接边缘
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        return dilated
    except Exception as e:
        print(f"[WARN] 文字检测失败: {e}")
        return None


def protect_text_areas(img: Image.Image, text_mask: Optional[Image.Image] = None) -> Image.Image:
    """保护文字区域：锐化文字，轻微模糊背景"""
    result = img.copy()
    
    if text_mask is None:
        # 没有掩码时，轻微锐化整张图
        result = result.filter(ImageFilter.SHARPEN)
        return result
    
    # 有掩码时：分别处理
    # 文字区域：锐化
    sharpened = result.filter(ImageFilter.SHARPEN)
    # 背景区域：轻微高斯模糊
    background = result.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # 合成：掩码为255的地方用 sharpened，否则用 background
    mask_array = np.array(text_mask)
    result_array = np.array(result)
    sharpened_array = np.array(sharpened)
    background_array = np.array(background)
    
    # 创建结果
    final_array = np.where(
        mask_array[:, :, np.newaxis] > 128,
        sharpened_array,
        background_array
    )
    
    return Image.fromarray(final_array.astype(np.uint8), mode=img.mode)


def process_image(input_path: Path, output_path: Optional[Path] = None,
                  strength: str = "medium") -> bool:
    """处理单个图像的文字保护"""
    print(f"[INFO] 文字区域保护: {input_path}")

    # 读取图像
    img = Image.open(input_path)
    
    # 保留所有元数据
    exif_data = img.getexif() if hasattr(img, 'getexif') else None
    png_text = img.text if hasattr(img, 'text') and img.text else None

    # 检测文字区域
    if CV2_AVAILABLE:
        img_array = np.array(img.convert('RGB'))
        mask_array = detect_text_regions_cv2(img_array)
        if mask_array is not None:
            mask_img = Image.fromarray(mask_array, mode='L')
        else:
            mask_img = None
    else:
        mask_img = None

    # 应用保护
    result = protect_text_areas(img, mask_img)
    print(f"[INFO] 文字区域已保护（锐化），背景已轻微模糊")

    # 输出路径
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}.text{input_path.suffix}"

    # 保存（合并所有元数据）
    save_kwargs = {'quality': 95, 'optimize': True}
    if exif_data:
        try:
            save_kwargs['exif'] = exif_data.tobytes()
        except Exception:
            pass
    
    # 合并 PNG 文本块：保留原始 + 添加伪造
    if png_text:
        try:
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            # 先添加原始文本块
            for key, value in png_text.items():
                pnginfo.add_text(key, str(value))
            # 再添加伪造的相机信息（会覆盖重复键）
            pnginfo.add_text("Make", "iPhone")
            pnginfo.add_text("Model", "iPhone 15 Pro")
            pnginfo.add_text("Software", "Adobe Photoshop Lightroom Classic 13.0")
            save_kwargs['pnginfo'] = pnginfo
        except Exception as e:
            print(f"[WARN] PNG 文本块处理失败: {e}")

    result.save(output_path, **save_kwargs)
    print(f"[SUCCESS] 文字保护完成: {output_path}")

    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python protect_text.py --input <image> [--output <path>] [--strength light|medium|heavy]")
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
