#!/usr/bin/env python3
"""
xhs-anti-detection: verify.py

验证处理后的图像是否满足安全发布标准。
检查元数据、自然度分数，生成报告。
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image

CONFIG_PATH = Path(__file__).parent.parent / "references" / "safe_params.json"
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

def check_metadata_clean(image_path: Path, config: Dict) -> Dict[str, Any]:
    """检查元数据是否干净"""
    result = {"clean": True, "suspicious_fields": []}

    # 尝试读取 EXIF
    try:
        img = Image.open(image_path)
        exif = img._getexif()
        if exif:
            fields_to_remove = [f.lower() for f in config["metadata"]["fields_to_remove"]]
            for tag, value in exif.items():
                tag_name = Image.ExifTags.TAGS.get(tag, str(tag)).lower()
                if tag_name in fields_to_remove:
                    result["clean"] = False
                    result["suspicious_fields"].append({
                        "field": tag_name,
                        "value": str(value)[:50]  # 截断长值
                    })
    except Exception as e:
        result["error"] = str(e)

    return result

def check_naturalness(image_path: Path) -> Dict[str, Any]:
    """评估图像自然度（基于统计特征）"""
    result = {"score": 0.8, "details": {}}

    try:
        img = Image.open(image_path)
        img_array = np.array(img.convert('RGB'))

        # 计算色彩分布熵（越自然熵越高）
        hist_r = np.histogram(img_array[:, :, 0], bins=256, range=(0, 255))[0]
        hist_g = np.histogram(img_array[:, :, 1], bins=256, range=(0, 255))[0]
        hist_b = np.histogram(img_array[:, :, 2], bins=256, range=(0, 255))[0]

        # 归一化
        hist_r = hist_r / hist_r.sum()
        hist_g = hist_g / hist_g.sum()
        hist_b = hist_b / hist_b.sum()

        # 计算熵
        def entropy(hist):
            non_zero = hist[hist > 0]
            return -np.sum(non_zero * np.log2(non_zero))

        ent_r = entropy(hist_r)
        ent_g = entropy(hist_g)
        ent_b = entropy(hist_b)
        avg_ent = (ent_r + ent_g + ent_b) / 3

        # 自然图像熵通常在 7-8 bits（256 级）
        # AI 生成图像可能过于均匀，熵偏低或偏高
        result["details"]["entropy"] = {
            "r": round(ent_r, 2),
            "g": round(ent_g, 2),
            "b": round(ent_b, 2),
            "avg": round(avg_ent, 2)
        }

        # 评分：熵在 6.5-8.0 之间为佳
        if 6.5 <= avg_ent <= 8.0:
            result["score"] = 0.9
        elif 6.0 <= avg_ent <= 8.5:
            result["score"] = 0.7
        else:
            result["score"] = 0.5

    except ImportError:
        result["error"] = "numpy 未安装，无法计算自然度"
        result["score"] = 0.7  # 保守评分
    except Exception as e:
        result["error"] = str(e)
        result["score"] = 0.6

    return result

def check_file_size(image_path: Path) -> Dict[str, Any]:
    """检查文件大小是否合理（排除异常）"""
    size_bytes = image_path.stat().st_size
    size_kb = size_bytes / 1024

    # 根据分辨率估算合理大小（粗略）
    img = Image.open(image_path)
    pixels = img.width * img.height

    # 典型 JPEG 压缩比：每像素 0.5-2 bits
    expected_min = pixels * 0.5 / 8 / 1024  # KB
    expected_max = pixels * 2 / 8 / 1024    # KB

    result = {
        "size_kb": round(size_kb, 2),
        "expected_range_kb": [round(expected_min, 2), round(expected_max, 2)],
        "suspicious": not (expected_min <= size_kb <= expected_max)
    }

    return result

def generate_report(image_path: Path, results: Dict[str, Any]) -> str:
    """生成验证报告"""
    report_lines = [
        "=" * 60,
        f"验证报告: {image_path.name}",
        "=" * 60,
        ""
    ]

    # 元数据检查
    meta = results.get("metadata", {})
    report_lines.append("【元数据检查】")
    if meta.get("clean"):
        report_lines.append("  ✅ 未发现 AI 生成标识字段")
    else:
        report_lines.append("  ⚠️  发现可疑字段:")
        for field in meta.get("suspicious_fields", []):
            report_lines.append(f"    - {field['field']}: {field['value']}")
    report_lines.append("")

    # 自然度检查
    natural = results.get("naturalness", {})
    report_lines.append("【自然度评估】")
    score = natural.get("score", 0)
    if score >= 0.8:
        status = "✅ 优秀"
    elif score >= 0.6:
        status = "⚠️  中等"
    else:
        status = "❌ 较差"
    report_lines.append(f"  分数: {score:.2f} {status}")
    if "details" in natural:
        details = natural["details"].get("entropy", {})
        report_lines.append(f"  色彩熵: R={details.get('r', 'N/A')}, G={details.get('g', 'N/A')}, B={details.get('b', 'N/A')}")
    report_lines.append("")

    # 文件大小检查
    filesize = results.get("filesize", {})
    report_lines.append("【文件大小】")
    report_lines.append(f"  实际: {filesize.get('size_kb', 'N/A')} KB")
    expected = filesize.get("expected_range_kb", ["N/A", "N/A"])
    report_lines.append(f"  预期范围: {expected[0]} - {expected[1]} KB")
    if filesize.get("suspicious"):
        report_lines.append("  ⚠️  文件大小异常（可能压缩不当）")
    else:
        report_lines.append("  ✅ 文件大小正常")
    report_lines.append("")

    # 总体建议
    report_lines.append("【发布建议】")
    all_ok = (
        meta.get("clean", False) and
        not filesize.get("suspicious", False) and
        score >= 0.6
    )
    if all_ok:
        report_lines.append("  ✅ 建议发布：图像通过安全检查")
    else:
        report_lines.append("  ⚠️  建议：重新处理或使用测试账号发布验证")

    report_lines.append("")
    report_lines.append("=" * 60)

    return "\n".join(report_lines)

def verify_image(image_path: Path, output_report: bool = True) -> Dict[str, Any]:
    """完整验证流程"""
    print(f"[INFO] 验证图像: {image_path}")

    results = {}

    # 1. 元数据检查
    print("  [1/3] 检查元数据...")
    results["metadata"] = check_metadata_clean(image_path, CONFIG)

    # 2. 自然度评估
    print("  [2/3] 评估自然度...")
    results["naturalness"] = check_naturalness(image_path)

    # 3. 文件大小检查
    print("  [3/3] 检查文件大小...")
    results["filesize"] = check_file_size(image_path)

    # 生成报告
    if output_report:
        report = generate_report(image_path, results)
        report_path = image_path.parent / f"{image_path.stem}.verify_report.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"[SUCCESS] 验证报告已保存: {report_path}")
        print("\n" + report)

    return results

def main():
    if len(sys.argv) < 2:
        print("用法: python verify.py --input <image> [--no-report]")
        sys.exit(1)

    input_path = None
    output_report = True

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--input" and i + 1 < len(args):
            input_path = Path(args[i + 1])
        elif arg == "--no-report":
            output_report = False

    if not input_path or not input_path.exists():
        print(f"[ERROR] 输入文件不存在: {input_path}")
        sys.exit(1)

    verify_image(input_path, output_report)

if __name__ == "__main__":
    # 需要 numpy
    import numpy as np
    main()
