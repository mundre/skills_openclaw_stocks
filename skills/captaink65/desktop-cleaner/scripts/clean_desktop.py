#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业桌面整理脚本
功能：
1. 扫描桌面文件，按类型分类整理
2. 检测并清理重复文件
3. 生成整理报告
"""

import os
import shutil
import hashlib
import json
from datetime import datetime

# 获取桌面路径
def get_desktop_path():
    if os.name == 'nt':  # Windows
        return os.path.join(os.path.expanduser('~'), 'Desktop')
    elif os.name == 'posix':  # macOS/Linux
        return os.path.join(os.path.expanduser('~'), 'Desktop')
    else:
        raise Exception("Unsupported OS")

# 按文件类型分类
def categorize_files(file_path):
    categories = {
        'Documents': ['.doc', '.docx', '.txt', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
        'Videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Executables': ['.exe', '.msi', '.app', '.dmg'],
        'Others': []
    }
    
    ext = os.path.splitext(file_path)[1].lower()
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return 'Others'

# 计算文件哈希值
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

# 主函数
def main():
    desktop_path = get_desktop_path()
    report = {
        'timestamp': datetime.now().isoformat(),
        'desktop_path': desktop_path,
        'files_processed': 0,
        'files_moved': 0,
        'duplicates_removed': 0,
        'categories': {}
    }
    
    # 创建分类文件夹
    for category in ['Documents', 'Images', 'Videos', 'Audio', 'Archives', 'Executables', 'Others']:
        category_path = os.path.join(desktop_path, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        report['categories'][category] = 0
    
    # 扫描桌面文件
    files = []
    for item in os.listdir(desktop_path):
        item_path = os.path.join(desktop_path, item)
        if os.path.isfile(item_path):
            files.append(item_path)
    
    report['files_processed'] = len(files)
    
    # 检测重复文件
    file_hashes = {}
    duplicates = []
    
    for file_path in files:
        # 跳过分类文件夹中的文件
        if os.path.basename(os.path.dirname(file_path)) in report['categories']:
            continue
        
        # 计算哈希值
        try:
            file_hash = get_file_hash(file_path)
            if file_hash in file_hashes:
                duplicates.append(file_path)
            else:
                file_hashes[file_hash] = file_path
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # 清理重复文件
    for duplicate in duplicates:
        try:
            os.remove(duplicate)
            report['duplicates_removed'] += 1
        except Exception as e:
            print(f"Error removing {duplicate}: {e}")
    
    # 整理文件
    for file_path in files:
        # 跳过分类文件夹中的文件和重复文件
        if (os.path.basename(os.path.dirname(file_path)) in report['categories'] or 
            file_path in duplicates):
            continue
        
        category = categorize_files(file_path)
        category_path = os.path.join(desktop_path, category)
        dest_path = os.path.join(category_path, os.path.basename(file_path))
        
        try:
            if not os.path.exists(dest_path):
                shutil.move(file_path, dest_path)
                report['files_moved'] += 1
                report['categories'][category] += 1
        except Exception as e:
            print(f"Error moving {file_path}: {e}")
    
    # 生成报告
    report_path = os.path.join(desktop_path, '整理报告.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("桌面整理完成！")
    print(f"处理文件数: {report['files_processed']}")
    print(f"移动文件数: {report['files_moved']}")
    print(f"删除重复文件数: {report['duplicates_removed']}")
    print(f"报告已保存至: {report_path}")

if __name__ == "__main__":
    main()