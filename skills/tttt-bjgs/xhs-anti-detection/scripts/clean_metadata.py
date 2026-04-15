#!/usr/bin/env python3
"""
xhs-anti-detection: clean_metadata.py

清除或伪造图像的 EXIF/元数据，移除 AI 生成标识，伪造相机信息。
支持 JPEG (EXIF) 和 PNG (tEXt 块)。
"""

import sys
import json
import random
from pathlib import Path
from typing import Dict, Optional

try:
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pyexiv2
    PYEXIV2_AVAILABLE = True
except Exception as e:
    PYEXIV2_AVAILABLE = False
    print(f"[DEBUG] pyexiv2 不可用: {type(e).__name__}: {e}")

# 加载配置
CONFIG_PATH = Path(__file__).parent.parent / "references" / "safe_params.json"
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)


def load_metadata(image_path: Path) -> Dict:
    """加载图像的元数据"""
    metadata = {}

    if PYEXIV2_AVAILABLE:
        try:
            exif = pyexiv2.ImageMetadata(str(image_path))
            exif.read()
            metadata = dict(exif.exif_items)
            metadata.update(exif.iptc_items)
            return metadata
        except Exception as e:
            print(f"[WARN] pyexiv2 读取失败: {e}, 回退到 PIL")

    if PIL_AVAILABLE:
        try:
            img = Image.open(image_path)
            exif_data = img.getexif()
            if exif_data:
                metadata = {tag_id: value for tag_id, value in exif_data.items()}
        except Exception as e:
            print(f"[WARN] PIL 读取失败: {e}")

    return metadata


def clean_metadata(metadata: Dict, config: Dict) -> Dict:
    """清理元数据：移除 AI 标识字段"""
    cleaned = metadata.copy()
    fields_to_remove = config["metadata"]["fields_to_remove"]

    for field in fields_to_remove:
        for key in list(cleaned.keys()):
            if isinstance(key, str) and key.lower() == field.lower():
                del cleaned[key]
            # 对于 tag ID 形式的键，跳过（不影响）

    return cleaned


def fake_camera_metadata(metadata: Dict, config: Dict) -> Dict:
    """伪造相机元数据"""
    fake = {}
    camera_models = config["metadata"]["fake_camera_models"]
    fake_camera = random.choice(camera_models)

    # 伪造 Make 和 Model
    fake["Make"] = fake_camera.split()[0]
    fake["Model"] = fake_camera

    # 伪造软件信息（移除 AI 痕迹）
    fake["Software"] = "Adobe Photoshop Lightroom Classic 13.0"

    # 伪造拍摄时间（过去 1-30 天随机）
    from datetime import datetime, timedelta
    fake_time = datetime.now() - timedelta(
        days=random.randint(1, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    fake["DateTimeOriginal"] = fake_time.strftime("%Y:%m:%d %H:%M:%S")
    fake["DateTimeDigitized"] = fake_time.strftime("%Y:%m:%d %H:%M:%S")

    # 伪造白平衡和色彩配置
    fake["WhiteBalance"] = 0
    fake["ColorSpace"] = 1

    return fake


def write_metadata(image_path: Path, metadata: Dict) -> bool:
    """将伪造的元数据写入图像文件
    
    支持格式：
    - JPEG: 使用 EXIF
    - PNG: 使用 tEXt 块（存储为文本字段）
    """
    success = False
    suffix = image_path.suffix.lower()

    if PYEXIV2_AVAILABLE and suffix in ['.jpg', '.jpeg']:
        try:
            exif = pyexiv2.ImageMetadata(str(image_path))
            exif.read()
            exif.clear()
            exif.update(metadata)
            exif.write()
            success = True
            print("[INFO] 使用 pyexiv2 写入元数据成功")
        except Exception as e:
            print(f"[WARN] pyexiv2 写入失败: {e}")
            success = False

    if not success and PIL_AVAILABLE:
        try:
            img = Image.open(image_path)

            if suffix in ['.jpg', '.jpeg']:
                # JPEG: 使用 EXIF
                exif = img.getexif()
                TAG_MAP = {
                    'Make': 271, 'Model': 272, 'Software': 305,
                    'DateTimeOriginal': 36867, 'DateTimeDigitized': 36868,
                    'WhiteBalance': 4197, 'ColorSpace': 40961,
                }
                for key, value in metadata.items():
                    if key in TAG_MAP:
                        exif[TAG_MAP[key]] = value
                img.save(image_path, exif=exif.tobytes(), quality=95, optimize=True)
                success = True
                print("[INFO] 使用 PIL 写入 EXIF 成功")

            elif suffix == '.png':
                # PNG: 使用 PngInfo 文本块
                pnginfo = PngInfo()

                # 映射字段到 PNG 文本键
                field_mapping = {
                    'Make': 'Make',
                    'Model': 'Model',
                    'Software': 'Software',
                    'DateTimeOriginal': 'DateTimeOriginal',
                    'DateTimeDigitized': 'DateTimeDigitized',
                }

                for key, value in metadata.items():
                    if key in field_mapping:
                        pnginfo.add_text(field_mapping[key], str(value))

                img.save(image_path, pnginfo=pnginfo, quality=95, optimize=True)
                success = True
                print("[INFO] 使用 PIL 写入 PNG 文本块成功")

            else:
                print(f"[WARN] 不支持的格式: {suffix}")

        except Exception as e:
            print(f"[WARN] PIL 写入元数据失败: {e}")

    if not success:
        print("[WARN] 无法写入元数据")
        print("        建议: 安装 pyexiv2 以支持完整 EXIF 操作")

    return success


def process_image(input_path: Path, output_path: Optional[Path] = None,
                  strength: str = "medium") -> bool:
    """处理单个图像的元数据"""
    print(f"[INFO] 处理元数据: {input_path}")

    # 加载配置
    config = CONFIG
    if strength in config["strength_presets"]:
        preset = config["strength_presets"][strength]
        print(f"[INFO] 使用强度预设: {strength}")

    # 读取元数据
    metadata = load_metadata(input_path)
    if not metadata:
        print("[WARN] 未找到元数据或无法读取")

    # 清理
    cleaned = clean_metadata(metadata, config)
    print(f"[INFO] 移除了 {len(metadata) - len(cleaned)} 个字段")

    # 伪造
    faked = fake_camera_metadata(cleaned, config)
    print(f"[INFO] 伪造相机: {faked.get('Make', 'Unknown')} {faked.get('Model', '')}")

    # 输出路径
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}.clean{input_path.suffix}"

    # 复制文件并写入元数据
    import shutil
    shutil.copy2(input_path, output_path)

    written = write_metadata(output_path, faked)
    if written:
        print(f"[SUCCESS] 元数据已清理并保存到: {output_path}")
    else:
        print(f"[PARTIAL] 元数据已清理（内存中），但未写入文件")
        print(f"          输出文件已复制: {output_path}")

    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python clean_metadata.py --input <image> [--output <path>] [--strength light|medium|heavy]")
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


if __name__ == "__main__":
    main()
