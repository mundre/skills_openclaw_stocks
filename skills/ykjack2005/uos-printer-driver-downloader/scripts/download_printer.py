#!/usr/bin/env python3
"""
自动下载打印机驱动脚本
用法: python download_printer.py <打印机型号> [下载目录] [--arch <架构>]
示例: python download_printer.py "联想 LJ2405" /Users/yangkaijian/Desktop --arch arm64
"""

import sys
import os
import json
import requests


def search_drivers(keyword):
    """搜索打印机驱动"""
    url = "https://www.chinauos.com/driver-api/v1/driver/query/list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Referer": "https://www.chinauos.com/resource/download-drivers",
        "Accept": "application/json"
    }
    params = {
        "keyword": keyword,
        "source": "2",
        "pageIndex": "1",
        "pageSize": "20"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("result") and data.get("data"):
            return data["data"]["list"]
        else:
            print(f"未找到相关结果: {data.get('msg')}")
            return []
    except Exception as e:
        print(f"搜索出错: {e}")
        return []


def download_driver(driver_info, download_dir="."):
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
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Referer": "https://www.chinauos.com/resource/download-drivers"
        }

        # 第一步：获取真实下载链接
        resp = requests.get(download_api, headers=headers, timeout=10)
        resp.raise_for_status()
        result_data = resp.json()

        if not result_data.get('result'):
            print(f"API返回错误: {result_data.get('msg')}")
            return False

        actual_url = result_data['data']['url']

        # 第二步：从真实 URL 下载文件
        file_resp = requests.get(actual_url, headers=headers, stream=True, timeout=60)
        file_resp.raise_for_status()

        # 构造文件名
        filename = f"{package}_{version}_{arch}.deb"
        filepath = os.path.join(download_dir, filename)

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
    args = sys.argv[1:]
    if not args:
        print("用法: python download_printer.py <打印机型号> [下载目录] [--arch <架构>]")
        print("示例: python download_printer.py \"联想 LJ2405\" /Users/yangkaijian/Desktop --arch arm64")
        sys.exit(1)

    printer_model = args[0]
    download_dir = "."
    preferred_arch = "amd64"

    i = 1
    while i < len(args):
        if args[i] == "--arch" and i + 1 < len(args):
            preferred_arch = args[i + 1]
            i += 2
        else:
            # 非 --arch 参数视为下载目录
            download_dir = args[i]
            i += 1

    # 确保下载目录存在
    if not os.path.exists(download_dir):
        os.makedirs(download_dir, exist_ok=True)

    print(f"搜索打印机驱动: {printer_model}")
    drivers = search_drivers(printer_model)

    if not drivers:
        print(f"没有找到与 '{printer_model}' 相关的驱动")
        sys.exit(1)

    # 显示搜索结果
    print(f"\n共找到 {len(drivers)} 个驱动:")
    print(f"{'序号':<4} | {'架构':<10} | {'驱动型号 (Model)':<50} | {'版本 (Version)':<15} | {'包名 (Package)'}")
    print("-" * 120)

    for idx, item in enumerate(drivers):
        package = item.get('package', 'N/A')
        arch = item.get('arch', 'N/A')
        model = item.get('model', 'N/A')[:50]
        version = item.get('version', 'N/A')
        print(f"{idx + 1:<4} | {arch:<10} | {model:<50} | {version:<15} | {package}")

    # 让用户选择驱动
    try:
        if len(drivers) == 1:
            choice = 1
            print(f"\n只有一个驱动可用，自动选择序号 1")
        else:
            # 尝试自动选择指定架构的驱动
            matched = [i for i, d in enumerate(drivers) if d.get('arch') == preferred_arch]
            if matched:
                choice = matched[0] + 1
                print(f"\n检测到 {preferred_arch} 架构驱动，自动选择序号 {choice}")
            else:
                # 让用户手动选择
                print(f"\n请选择要下载的驱动 (1-{len(drivers)})")
                choice_input = input("请输入序号 (按回车选择第一个): ").strip()
                if not choice_input:
                    choice = 1
                else:
                    choice = int(choice_input)

        if choice < 1 or choice > len(drivers):
            print("序号超出范围，使用第一个驱动")
            choice = 1

    except (ValueError, KeyboardInterrupt):
        print("输入无效，使用第一个驱动")
        choice = 1

    selected_driver = drivers[choice - 1]

    print(f"\n选择的驱动:")
    print(f"  型号: {selected_driver.get('model')}")
    print(f"  包名: {selected_driver.get('package')}")
    print(f"  架构: {selected_driver.get('arch')}")
    print(f"  版本: {selected_driver.get('version')}")
    print(f"  下载目录: {download_dir}")

    # 确认下载
    confirm = input("\n确认下载？(y/n): ").strip().lower()
    if confirm != 'y':
        print("下载已取消")
        sys.exit(0)

    # 执行下载
    success = download_driver(selected_driver, download_dir)

    if success:
        print(f"\n驱动下载成功！")
    else:
        print(f"\n驱动下载失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
