#!/usr/bin/env python3
"""
Game Launcher - 自动打开H5游戏网页
支持跨平台：macOS, Linux, Windows
"""

import sys
import subprocess
import platform

GAME_URL = "https://h5.play.cn/h5/home/index/recommond?caf=20000009&topRouterId=40383&content_Id=40382"


def detect_os():
    """检测当前操作系统"""
    return platform.system()


def open_url(url):
    """跨平台打开URL"""
    os_name = detect_os()

    if os_name == "Darwin":  # macOS
        cmd = ["open", url]
    elif os_name == "Linux":
        cmd = ["xdg-open", url]
    elif os_name == "Windows":
        # Windows 需要特殊处理
        print("🎮 正在打开游戏页面...")
        subprocess.run(["start", url], shell=True, check=True)
        print("✅ 游戏页面已在浏览器中打开")
        print(f"🔗 {url}")
        return
    else:
        print(f"❌ 不支持的操作系统: {os_name}")
        sys.exit(1)

    try:
        print("🎮 正在打开游戏页面...")
        if os_name == "Windows":
            subprocess.run(cmd[0], shell=True, check=True)
        else:
            subprocess.run(cmd, check=True)
        print("✅ 游戏页面已在浏览器中打开")
        print(f"🔗 {url}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 打开失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)


def main():
    """主函数"""
    global GAME_URL
    if len(sys.argv) > 1:
        # 支持自定义URL
        GAME_URL = sys.argv[1]

    open_url(GAME_URL)


if __name__ == "__main__":
    main()
