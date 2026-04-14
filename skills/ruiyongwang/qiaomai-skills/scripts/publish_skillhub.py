#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
荞麦饼 Skills - SkillHub.cn 发布脚本
作者: 度量衡
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

class SkillHubPublisher:
    """SkillHub.cn 发布器"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.metadata_file = self.skill_path / "skillhub.json"
        self.build_dir = self.skill_path / "build"
        self.dist_dir = self.skill_path / "dist"
        
    def load_metadata(self) -> dict:
        """加载 SkillHub 元数据"""
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def prepare_build(self):
        """准备构建目录"""
        print("📦 准备构建目录...")
        
        # 清理旧构建
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            
        # 创建新目录
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
    def copy_files(self):
        """复制必要文件到构建目录"""
        print("📋 复制文件...")
        
        files_to_copy = [
            "SKILL.md",
            "README_SKILLHUB.md",
            "skillhub.json",
            ".metadata.json",
        ]
        
        # 复制核心文件
        for file in files_to_copy:
            src = self.skill_path / file
            if src.exists():
                shutil.copy2(src, self.build_dir / file)
                print(f"  ✓ {file}")
        
        # 复制核心模块
        core_dir = self.skill_path / "core"
        if core_dir.exists():
            shutil.copytree(core_dir, self.build_dir / "core")
            print(f"  ✓ core/")
        
        # 复制脚本
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            shutil.copytree(scripts_dir, self.build_dir / "scripts")
            print(f"  ✓ scripts/")
    
    def create_package(self) -> str:
        """创建发布包"""
        print("🗜️ 创建发布包...")
        
        metadata = self.load_metadata()
        name = metadata['name']
        version = metadata['version']
        
        package_name = f"{name}-{version}.zip"
        package_path = self.dist_dir / package_name
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.build_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.build_dir)
                    zf.write(file_path, arcname)
                    
        size = package_path.stat().st_size / 1024  # KB
        print(f"  ✓ {package_name} ({size:.1f} KB)")
        
        return str(package_path)
    
    def generate_manifest(self) -> dict:
        """生成发布清单"""
        metadata = self.load_metadata()
        
        manifest = {
            "name": metadata['name'],
            "version": metadata['version'],
            "displayName": metadata['displayName'],
            "description": metadata['description'],
            "author": metadata['author'],
            "timestamp": datetime.now().isoformat(),
            "files": {
                "main": "SKILL.md",
                "readme": "README_SKILLHUB.md",
                "metadata": "skillhub.json"
            },
            "entry": metadata['entryPoint'],
            "platforms": metadata['platforms']
        }
        
        manifest_path = self.dist_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ manifest.json")
        return manifest
    
    def print_publish_guide(self):
        """打印发布指南"""
        metadata = self.load_metadata()
        
        print("\n" + "="*60)
        print("🚀 SkillHub.cn 发布指南")
        print("="*60)
        print()
        print(f"技能名称: {metadata['displayName']}")
        print(f"版本: {metadata['version']}")
        print(f"作者: {metadata['author']['displayName']}")
        print(f"标签: {metadata['author']['tagline']}")
        print()
        print("📤 发布步骤:")
        print()
        print("1. 访问 SkillHub.cn 开发者中心")
        print("   https://skillhub.cn/developer")
        print()
        print("2. 登录您的开发者账号 (dlh365)")
        print()
        print('3. 点击"发布新技能"或"上传技能"')
        print()
        print("4. 填写技能信息:")
        print(f"   - 名称: {metadata['displayName']}")
        print(f"   - 英文名: {metadata['displayNameEn']}")
        print(f"   - 版本: {metadata['version']}")
        print(f"   - 描述: {metadata['description']}")
        print()
        print("5. 上传文件:")
        print(f"   - 主文件: dist/{metadata['name']}-{metadata['version']}.zip")
        print("   - 或单独上传 SKILL.md")
        print()
        print("6. 设置分类:")
        for cat in metadata['categories']:
            print(f"   - {cat}")
        print()
        print("7. 添加标签:")
        for tag in metadata['keywords'][:5]:
            print(f"   - {tag}")
        print()
        print("8. 提交审核")
        print()
        print("="*60)
        print()
        print("📁 发布包位置:")
        print(f"   {self.dist_dir}")
        print()
        print("✅ 准备就绪，可以发布了！")
        print()
    
    def build(self):
        """执行完整构建流程"""
        print("\n🌾 荞麦饼 Skills - SkillHub.cn 发布构建")
        print("="*60)
        print()
        
        self.prepare_build()
        self.copy_files()
        package_path = self.create_package()
        manifest = self.generate_manifest()
        
        print()
        print("✅ 构建完成！")
        print()
        
        self.print_publish_guide()
        
        return package_path, manifest


def main():
    """主函数"""
    # 获取技能目录
    skill_path = Path(__file__).parent.parent
    
    # 创建发布器
    publisher = SkillHubPublisher(skill_path)
    
    # 执行构建
    try:
        package_path, manifest = publisher.build()
        print(f"📦 发布包: {package_path}")
        print(f"📋 清单: {manifest}")
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        raise


if __name__ == "__main__":
    main()
