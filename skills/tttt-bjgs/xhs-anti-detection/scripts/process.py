#!/usr/bin/env python3
"""
xhs-anti-detection: process.py

主处理流程：按顺序调用所有处理步骤，生成安全图片。
"""

import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from PIL import Image

CONFIG_PATH = Path(__file__).parent.parent / "references" / "safe_params.json"
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

def run_step(step_name: str, script_name: str, input_path: Path,
             output_path: Path, strength: str) -> bool:
    """执行单个处理步骤"""
    script_path = Path(__file__).parent / script_name

    if not script_path.exists():
        print(f"[ERROR] 脚本不存在: {script_path}")
        return False

    cmd = [
        "python3", str(script_path),
        "--input", str(input_path),
        "--output", str(output_path),
        "--strength", strength
    ]

    print(f"  [{step_name}] 执行: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] {step_name} 失败:")
        print(result.stderr)
        return False

    # 打印脚本输出（去掉每行前面的 [INFO] 等标记）
    for line in result.stdout.splitlines():
        if line.strip():
            print(f"    {line}")

    return True

def process_image(input_path: Path, output_path: Optional[Path] = None,
                  strength: str = "medium", verify: bool = True) -> bool:
    """
    完整处理流程

    顺序：
    1. 元数据清理 → 2. 文字保护 → 3. 色彩偏移 → 4. 添加噪声 → 5. 重新编码 → 6. 验证
    """
    print(f"[INFO] 开始完整处理: {input_path}")
    print(f"[INFO] 强度: {strength}")

    # 确定输出路径
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}.safe{input_path.suffix}"

    # 使用临时文件链
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        current = input_path

        steps = [
            ("1/5 元数据清理", "clean_metadata.py", "step1"),
            ("2/5 文字保护", "protect_text.py", "step2"),
            ("3/5 色彩偏移", "color_shift.py", "step3"),
            ("4/5 添加噪声", "add_noise.py", "step4"),
            ("5/5 重新编码", "recompress.py", "step5"),
        ]

        for step_name, script, step_id in steps:
            # 确定此步骤的输出文件扩展名
            # recompress 步骤应输出 JPEG 格式以减小文件大小
            if step_id == "step5":
                next_file = tmpdir / f"{step_id}.jpg"
            else:
                next_file = tmpdir / f"{step_id}{input_path.suffix}"
            
            next_file_jpg = tmpdir / f"{step_id}.jpg"  # 备用

            if not run_step(step_name, script, current, next_file, strength):
                print(f"[ERROR] 处理失败于步骤: {step_name}")
                return False

            # 检查实际生成的文件（某些步骤可能改变扩展名）
            if next_file_jpg.exists():
                current = next_file_jpg
            elif next_file.exists():
                current = next_file
            else:
                print(f"[ERROR] 步骤 {step_name} 未生成输出文件")
                return False

        # 最终文件复制到目标位置
        import shutil
        shutil.copy2(current, output_path)
        print(f"[INFO] 最终文件: {output_path}")

    # 验证
    if verify:
        print("[INFO] 运行验证...")
        verify_script = Path(__file__).parent / "verify.py"
        cmd = ["python3", str(verify_script), "--input", str(output_path), "--no-report"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"[WARN] 验证过程出错: {result.stderr}")

    print(f"[SUCCESS] 处理完成: {output_path}")
    return True

def main():
    if len(sys.argv) < 2:
        print("用法: python process.py --input <image> [--output <path>] [--strength light|medium|heavy] [--no-verify]")
        sys.exit(1)

    input_path = None
    output_path = None
    strength = "medium"
    verify = True

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--input" and i + 1 < len(args):
            input_path = Path(args[i + 1])
        elif arg == "--output" and i + 1 < len(args):
            output_path = Path(args[i + 1])
        elif arg == "--strength" and i + 1 < len(args):
            strength = args[i + 1]
        elif arg == "--no-verify":
            verify = False

    if not input_path or not input_path.exists():
        print(f"[ERROR] 输入文件不存在: {input_path}")
        sys.exit(1)

    if strength not in ["light", "medium", "heavy"]:
        print(f"[ERROR] 强度必须是: light, medium, heavy（当前: {strength}）")
        sys.exit(1)

    success = process_image(input_path, output_path, strength, verify)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
