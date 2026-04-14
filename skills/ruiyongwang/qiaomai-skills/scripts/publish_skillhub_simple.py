#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
荞麦饼 Skills - SkillHub.cn 发布脚本 (简化版)
作者: 度量衡
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def main():
    """主函数"""
    skill_path = Path(__file__).parent.parent
    build_dir = skill_path / "build"
    dist_dir = skill_path / "dist"
    
    print("=" * 60)
    print("荞麦饼 Skills - SkillHub.cn 发布构建")
    print("=" * 60)
    print()
    
    # 加载元数据
    with open(skill_path / "skillhub.json", 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    name = metadata['name']
    version = metadata['version']
    
    # 清理旧构建
    print("准备构建目录...")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    build_dir.mkdir(exist_ok=True)
    dist_dir.mkdir(exist_ok=True)
    
    # 复制文件
    print("复制文件...")
    files_to_copy = [
        "SKILL.md",
        "README_SKILLHUB.md", 
        "skillhub.json",
        ".metadata.json",
    ]
    
    for file in files_to_copy:
        src = skill_path / file
        if src.exists():
            shutil.copy2(src, build_dir / file)
            print(f"  [OK] {file}")
    
    # 复制目录
    for dir_name in ["core", "scripts"]:
        src_dir = skill_path / dir_name
        if src_dir.exists():
            shutil.copytree(src_dir, build_dir / dir_name)
            print(f"  [OK] {dir_name}/")
    
    # 创建发布包
    print("创建发布包...")
    package_name = f"{name}-{version}.zip"
    package_path = dist_dir / package_name
    
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in build_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(build_dir)
                zf.write(file_path, arcname)
    
    size = package_path.stat().st_size / 1024
    print(f"  [OK] {package_name} ({size:.1f} KB)")
    
    # 生成清单
    manifest = {
        "name": name,
        "version": version,
        "displayName": metadata['displayName'],
        "description": metadata['description'],
        "author": metadata['author'],
        "timestamp": datetime.now().isoformat(),
        "entry": metadata['entryPoint'],
        "platforms": metadata['platforms']
    }
    
    manifest_path = dist_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  [OK] manifest.json")
    
    print()
    print("=" * 60)
    print("构建完成!")
    print("=" * 60)
    print()
    print(f"技能名称: {metadata['displayName']}")
    print(f"版本: {version}")
    print(f"作者: {metadata['author']['displayName']}")
    print(f"标签: {metadata['author']['tagline']}")
    print()
    print("发布包位置:")
    print(f"  {package_path}")
    print()
    print("发布步骤:")
    print("1. 访问 https://skillhub.cn/developer")
    print("2. 登录 dlh365 账号")
    print("3. 点击'发布新技能'")
    print("4. 填写技能信息并上传发布包")
    print("5. 提交审核")
    print()
    print("详细指南: PUBLISH_SKILLHUB.md")
    print()

if __name__ == "__main__":
    main()
