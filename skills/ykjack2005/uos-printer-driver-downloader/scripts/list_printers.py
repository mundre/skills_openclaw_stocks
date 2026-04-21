#!/usr/bin/env python3
"""
打印机驱动搜索脚本 - 第一部分
用于搜索打印机驱动列表，并将所有搜索结果保存到文件中，供第二个脚本选择下载

用法: python list_printers.py [打印机型号关键词]
示例: python list_printers.py LJ2405
"""

import json
import os
import sys
import requests
import urllib.parse


def search_drivers(keyword):
    """搜索打印机驱动"""
    url = "https://www.chinauos.com/driver-api/v1/driver/query/list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Referer": f"https://www.chinauos.com/resource/download-drivers/result?keyword={urllib.parse.quote(keyword)}",
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


def save_all_drivers(drivers, filename="driver_list.json"):
    """保存所有搜索到的驱动信息到JSON文件"""
    # 标准化每个驱动的信息
    normalized_drivers = []
    for item in drivers:
        driver_info = {
            "deb_id": item.get("deb_id"),
            "driver_id": item.get("driver_id"),
            "package": item.get("package"),
            "model": item.get("model"),
            "arch": item.get("arch"),
            "version": item.get("version")
        }
        normalized_drivers.append(driver_info)

    # 保存为列表格式
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(normalized_drivers, f, ensure_ascii=False, indent=2)

    return filename


def main():
    if len(sys.argv) > 1:
        keyword = sys.argv[1].strip()
        if not keyword:
            print("用法: python list_printers.py [打印机型号关键词]")
            print("示例: python list_printers.py LJ2405")
            return
    else:
        keyword = input("请输入打印机型号关键词 (例如 1102): ").strip()
        if not keyword:
            return

    print(f"正在搜索: {keyword}")
    drivers = search_drivers(keyword)

    if not drivers:
        print("没有找到驱动。")
        return

    # 打印表头
    header = f"\n{'序号':<4} | {'架构':<10} | {'驱动型号 (Model)':<50} | {'版本 (Version)':<15} | {'包名 (Package)'}"
    print(header)
    print("-" * 120)

    # 列出搜索结果，包名放在同一行
    for idx, item in enumerate(drivers):
        package = item.get('package', 'N/A')
        arch = item.get('arch', 'N/A')
        model = item.get('model', 'N/A')[:50]
        version = item.get('version', 'N/A')

        print(f"{idx + 1:<4} | {arch:<10} | {model:<50} | {version:<15} | {package}")

    # 保存所有驱动信息
    print(f"\n共找到 {len(drivers)} 个驱动")
    save_path = save_all_drivers(drivers)
    print(f"驱动列表已保存到: {save_path}")
    print("\n请运行第二个脚本下载驱动: python download_driver.py")


if __name__ == "__main__":
    main()
