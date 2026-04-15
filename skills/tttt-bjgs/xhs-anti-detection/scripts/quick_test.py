#!/usr/bin/env python3
"""
快速测试脚本
验证 xhs-anti-detection skill 的依赖和基本功能
"""

import sys
import subprocess
from pathlib import Path

# Skill 目录
SKILL_DIR = Path(__file__).parent.parent
REQUIREMENTS_FILE = SKILL_DIR / "requirements.txt"

def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """检查 Python 版本"""
    print_header("1. Python 版本检查")

    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 8:
        print("✅ Python 版本满足要求 (≥3.8)")
        return True
    else:
        print("❌ Python 版本过低，需要 ≥3.8")
        return False

def check_system_dependencies():
    """检查系统依赖"""
    print_header("2. 系统依赖检查")

    dependencies = {
        "exiftool": "exiftool -ver",
        "tesseract": "tesseract --version"
    }

    all_ok = True

    for name, cmd in dependencies.items():
        print(f"\n检查: {name}")
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # 提取版本信息
                version_line = result.stdout.strip().split('\n')[0]
                print(f"  ✅ 已安装: {version_line}")
            else:
                print(f"  ❌ 命令执行失败")
                all_ok = False

        except FileNotFoundError:
            print(f"  ❌ 未找到 {name}")
            print(f"     安装命令:")
            print(f"      macOS: brew install {name}")
            print(f"      Ubuntu: sudo apt-get install {name}")
            all_ok = False
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  命令超时")
            all_ok = False
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            all_ok = False

    return all_ok

def check_python_dependencies():
    """检查 Python 依赖"""
    print_header("3. Python 依赖检查")

    # 读取 requirements.txt
    if not REQUIREMENTS_FILE.exists():
        print(f"❌ 未找到 requirements.txt: {REQUIREMENTS_FILE}")
        return False

    with open(REQUIREMENTS_FILE, 'r') as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)

    print(f"需要安装的包: {', '.join(requirements)}")

    # 检查每个包
    all_ok = True
    for req in requirements:
        package_name = req.split('>=')[0].split('==')[0].split('~=')[0].strip()

        print(f"\n检查: {package_name}")
        try:
            module = __import__(package_name.replace('-', '_'))
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✅ 已安装: {version}")
        except ImportError:
            print(f"  ❌ 未安装")
            print(f"     安装: pip3 install '{req}'")
            all_ok = False

    return all_ok

def check_skill_structure():
    """检查 Skill 目录结构"""
    print_header("4. Skill 目录结构检查")

    required_files = [
        "SKILL.md",
        "USAGE.md",
        "requirements.txt",
        "scripts/process.py",
        "scripts/clean_metadata.py",
        "scripts/protect_text.py",
        "scripts/add_noise.py",
        "scripts/color_shift.py",
        "scripts/recompress.py",
        "scripts/verify.py",
        "scripts/quick_test.py",
        "references/safe_params.json",
        "hooks/post_generate.py"
    ]

    all_ok = True
    for file_path in required_files:
        full_path = SKILL_DIR / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (缺失)")
            all_ok = False

    return all_ok

def check_config_files():
    """检查配置文件"""
    print_header("5. 配置文件检查")

    config_file = SKILL_DIR / "references" / "safe_params.json"

    if not config_file.exists():
        print(f"❌ 配置文件缺失: {config_file}")
        return False

    import json
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"✅ 配置文件有效")
        print(f"   可用级别: {list(config.get('levels', {}).keys())}")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误: {e}")
        return False

def run_smoke_test():
    """运行冒烟测试"""
    print_header("6. 冒烟测试")

    # 创建一个测试图片
    test_image = SKLL_DIR / "test_input.png"
    test_output = SKILL_DIR / "test_output.jpg"

    try:
        import cv2
        import numpy as np

        print("创建测试图片...")
        # 创建 800x600 的测试图，包含文字
        img = np.ones((600, 800, 3), dtype=np.uint8) * 255  # 白色背景

        # 添加一些文字
        cv2.putText(img, "Test Image", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        cv2.putText(img, "Coffee Grind Comparison", (50, 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2)

        # 保存
        cv2.imwrite(str(test_image), img)
        print(f"  ✅ 测试图片创建: {test_image}")

        # 尝试导入处理模块
        print("\n导入处理模块...")
        sys.path.insert(0, str(SKILL_DIR))

        try:
            from scripts.clean_metadata import clean_metadata
            print("  ✅ clean_metadata 模块")
        except ImportError as e:
            print(f"  ❌ clean_metadata 导入失败: {e}")
            return False

        try:
            from scripts.add_noise import add_noise
            print("  ✅ add_noise 模块")
        except ImportError as e:
            print(f"  ❌ add_noise 导入失败: {e}")
            return False

        try:
            from scripts.color_shift import color_shift
            print("  ✅ color_shift 模块")
        except ImportError as e:
            print(f"  ❌ color_shift 导入失败: {e}")
            return False

        try:
            from scripts.recompress import recompress
            print("  ✅ recompress 模块")
        except ImportError as e:
            print(f"  ❌ recompress 导入失败: {e}")
            return False

        try:
            from scripts.verify import verify_image
            print("  ✅ verify 模块")
        except ImportError as e:
            print(f"  ❌ verify 导入失败: {e}")
            return False

        # 清理测试文件
        if test_image.exists():
            test_image.unlink()
        if test_output.exists():
            test_output.unlink()

        print("\n✅ 冒烟测试通过")
        return True

    except Exception as e:
        print(f"\n❌ 冒烟测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_summary(results):
    """打印总结"""
    print_header("测试总结")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"通过: {passed}/{total}")

    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"  {icon} {test_name}")

    if passed == total:
        print("\n🎉 Skill 就绪！可以使用了。")
        print("\n快速开始:")
        print("  python3 scripts/process.py --input <图片路径> --level medium")
        print("\n批量处理:")
        print("  python3 scripts/process.py --input-dir outputs/ --output-dir processed/")
        return True
    else:
        print("\n⚠️  请修复上述问题后再使用。")
        return False

def main():
    """主函数"""
    print("="*60)
    print("  xhs-anti-detection Skill 快速测试")
    print("="*60)

    results = {}

    # 运行各项检查
    results["Python 版本"] = check_python_version()
    results["系统依赖"] = check_system_dependencies()
    results["Python 依赖"] = check_python_dependencies()
    results["目录结构"] = check_skill_structure()
    results["配置文件"] = check_config_files()
    results["冒烟测试"] = run_smoke_test()

    # 总结
    success = print_summary(results)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
