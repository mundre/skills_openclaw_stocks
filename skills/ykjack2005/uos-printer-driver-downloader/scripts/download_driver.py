#!/usr/bin/env python3
"""
打印机驱动下载脚本 - 第二部分
使用第一个脚本保存的 driver_list.json，从列表中选择并下载驱动文件
"""

import json
import os
import requests


def load_driver_list(filename="driver_list.json"):
    """从JSON文件加载驱动列表信息"""
    if not os.path.exists(filename):
        print(f"错误：找不到驱动列表文件 '{filename}'")
        print("请先运行 list_printers.py 搜索并保存驱动列表。")
        return None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 兼容旧格式（单个对象）
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            print("错误：驱动列表格式无效。")
            return None

    except Exception as e:
        print(f"读取驱动列表文件失败：{e}")
        return None


def display_driver_list(drivers):
    """显示驱动列表供用户选择"""
    print("\n" + "=" * 120)
    header = f"\n{'序号':<4} | {'架构':<10} | {'驱动型号 (Model)':<50} | {'版本 (Version)':<15} | {'包名 (Package)'}"
    print(header)
    print("-" * 120)

    for idx, item in enumerate(drivers):
        package = item.get('package', 'N/A')
        arch = item.get('arch', 'N/A')
        model = item.get('model', 'N/A')[:50]
        version = item.get('version', 'N/A')

        print(f"{idx + 1:<4} | {arch:<10} | {model:<50} | {version:<15} | {package}")


def download_driver(driver_info, output_dir="."):
    """根据 driver_info 中的 deb_id 和 driver_id 下载驱动"""
    deb_id = driver_info.get('deb_id')
    driver_id = driver_info.get('driver_id')

    if not deb_id or not driver_id:
        print("错误：缺少必要的下载参数 (deb_id 或 driver_id)")
        return False

    # 构造下载链接
    download_api = f"https://www.chinauos.com/driver-api/v1/driver/download?deb_id={deb_id}&driver_id={driver_id}"

    package = driver_info.get('package', 'unknown')
    model = driver_info.get('model', 'unknown')
    arch = driver_info.get('arch', 'unknown')
    version = driver_info.get('version', 'unknown')

    print(f"\n开始下载驱动...")
    print(f"  型号：{model}")
    print(f"  包名：{package}")
    print(f"  架构：{arch}")
    print(f"  版本：{version}")

    try:
        # 使用 stream=True 避免大文件占用过多内存
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Referer": "https://www.chinauos.com/resource/download-drivers"
        }
        # 首先获取下载URL
        resp = requests.get(download_api, headers=headers, timeout=60)
        resp.raise_for_status()
        result_data = resp.json()
        if not result_data.get('result'):
            print(f"API返回错误: {result_data.get('msg')}")
            return False
        actual_url = result_data['data']['url']
        # 从实际URL下载文件
        file_resp = requests.get(actual_url, headers=headers, stream=True, timeout=60)
        file_resp.raise_for_status()

        # 构造文件名
        filename = f"{package}_{version}_{arch}.deb"
        filepath = os.path.join(output_dir, filename)

        # 获取文件大小（如果响应头中有）
        total_size = int(file_resp.headers.get('content-length', 0))
        if total_size > 0:
            print(f"文件大小：{total_size / 1024 / 1024:.2f} MB")

        downloaded_size = 0

        with open(filepath, 'wb') as f:
            for chunk in file_resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    # 显示下载进度
                    if total_size > 0:
                        percent = (downloaded_size / total_size) * 100
                        print(f"\r进度：{percent:.1f}% ({downloaded_size / 1024 / 1024:.2f} MB / {total_size / 1024 / 1024:.2f} MB)", end='', flush=True)

        print("\n")

        print(f"下载完成！")
        print(f"文件保存位置：{os.path.abspath(filepath)}")
        print(f"文件大小：{downloaded_size / 1024 / 1024:.2f} MB")

        return True

    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误：{e}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误：{e}")
        return False
    except requests.exceptions.Timeout:
        print("下载超时，请检查网络连接。")
        return False
    except Exception as e:
        print(f"下载失败：{e}")
        return False


def main():
    print("=" * 60)
    print("打印机驱动下载脚本")
    print("=" * 60)

    # 加载驱动列表
    list_file = "driver_list.json"
    drivers = load_driver_list(list_file)

    if drivers is None:
        return

    print(f"\n已加载 {len(drivers)} 个驱动")

    # 显示列表并让用户选择
    display_driver_list(drivers)

    print("\n" + "=" * 120)
    try:
        choice = int(input("请输入要下载的序号 (输入 0 退出)："))
        if choice == 0:
            print("已退出。")
            return
        elif 1 <= choice <= len(drivers):
            selected = drivers[choice - 1]

            # 确认下载
            print("\n准备下载的驱动信息：")
            print(f"  型号：{selected.get('model')}")
            print(f"  包名：{selected.get('package')}")
            print(f"  架构：{selected.get('arch')}")
            print(f"  版本：{selected.get('version')}")
            print(f"  DEB ID：{selected.get('deb_id')}")
            print(f"  DRIVER ID：{selected.get('driver_id')}")

            confirm = input("\n确认下载？(y/n)：").strip().lower()
            if confirm != 'y':
                print("已取消下载。")
                return

            # 执行下载
            success = download_driver(selected, "/Users/yangkaijian/Desktop")

            if success:
                print("\n驱动下载成功！")
            else:
                print("\n驱动下载失败，请重试。")

        else:
            print("序号超出范围。")

    except ValueError:
        print("输入无效，请输入数字序号。")


if __name__ == "__main__":
    main()
