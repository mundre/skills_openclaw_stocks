#!/usr/bin/env python3
"""
xhs-anti-detection: post_generate.py

自动触发钩子：在 image-generation skill 生成图片后自动调用。
检测到新生成的图片，自动应用反检测处理。
"""

import sys
import json
import time
from pathlib import Path
from typing import Optional

# 假设 image-generation skill 的输出目录
DEFAULT_OUTPUT_DIR = Path.home() / ".deskclaw" / "nanobot" / "workspace" / "outputs"

def watch_and_process(output_dir: Path, strength: str = "medium") -> None:
    """
    监控输出目录，对新生成的图片自动处理

    注意：这是一个简化版本。实际集成需要与 image-generation skill
    的钩子系统对接，或通过文件系统事件监控。
    """
    print(f"[INFO] 监控目录: {output_dir}")
    print(f"[INFO] 处理强度: {strength}")
    print("[INFO] 等待新图片生成...（按 Ctrl+C 停止）")

    try:
        while True:
            # 查找最新的未处理图片
            images = list(output_dir.glob("*.png")) + \
                     list(output_dir.glob("*.jpg")) + \
                     list(output_dir.glob("*.jpeg"))

            for img_path in images:
                # 跳过已处理的（.safe 后缀）
                if img_path.stem.endswith(".safe"):
                    continue

                # 检查是否已有对应的 .safe 文件
                safe_path = img_path.parent / f"{img_path.stem}.safe{img_path.suffix}"
                if safe_path.exists():
                    continue

                # 发现未处理的新图片
                print(f"[INFO] 发现新图片: {img_path.name}")
                print("[INFO] 开始反检测处理...")

                # 调用 process.py
                import subprocess
                cmd = [
                    "python3",
                    str(Path(__file__).parent / "process.py"),
                    "--input", str(img_path),
                    "--strength", strength,
                    "--no-verify"  # 自动模式下跳过验证以加快速度
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"[SUCCESS] 自动处理完成: {safe_path}")
                else:
                    print(f"[ERROR] 自动处理失败: {result.stderr}")

            time.sleep(5)  # 每 5 秒检查一次

    except KeyboardInterrupt:
        print("\n[INFO] 监控已停止")

def auto_process_latest(output_dir: Path, count: int = 1, strength: str = "medium") -> None:
    """
    自动处理最新的 N 张图片（非监控模式，单次执行）
    """
    print(f"[INFO] 自动处理最新 {count} 张图片")

    images = list(output_dir.glob("*.png")) + \
             list(output_dir.glob("*.jpg")) + \
             list(output_dir.glob("*.jpeg"))

    # 按修改时间排序
    images.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    latest = images[:count]
    for img_path in latest:
        if img_path.stem.endswith(".safe"):
            continue
        safe_path = img_path.parent / f"{img_path.stem}.safe{img_path.suffix}"
        if safe_path.exists():
            print(f"[SKIP] 已处理: {img_path.name}")
            continue

        print(f"[INFO] 处理: {img_path.name}")
        import subprocess
        cmd = [
            "python3",
            str(Path(__file__).parent / "process.py"),
            "--input", str(img_path),
            "--strength", strength
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] 完成")
        else:
            print(f"[FAIL] {result.stderr}")

def main():
    if len(sys.argv) < 2:
        print("用法: python post_generate.py --watch [--dir <目录>] [--strength light|medium|heavy]")
        print("       python post_generate.py --latest <数量> [--dir <目录>] [--strength light|medium|heavy]")
        print("")
        print("模式:")
        print("  --watch           监控目录，自动处理新图片（持续运行）")
        print("  --latest N        处理最新的 N 张图片（单次执行）")
        print("")
        print("选项:")
        print("  --dir PATH        图片目录（默认: outputs/）")
        print("  --strength LEVEL  处理强度: light/medium/heavy")
        exit(1)

    mode = None
    watch = False
    latest_count = 0
    output_dir = DEFAULT_OUTPUT_DIR
    strength = "medium"

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--watch":
            watch = True
            mode = "watch"
        elif arg == "--latest":
            latest_count = int(args[i + 1])
            mode = "latest"
            i += 1
        elif arg == "--dir":
            output_dir = Path(args[i + 1])
            i += 1
        elif arg == "--strength":
            strength = args[i + 1]
            i += 1
        i += 1

    if mode is None:
        print("[ERROR] 必须指定模式: --watch 或 --latest")
        exit(1)

    if not output_dir.exists():
        print(f"[ERROR] 目录不存在: {output_dir}")
        exit(1)

    if mode == "watch":
        watch_and_process(output_dir, strength)
    elif mode == "latest":
        auto_process_latest(output_dir, latest_count, strength)

if __name__ == "__main__":
    main()
