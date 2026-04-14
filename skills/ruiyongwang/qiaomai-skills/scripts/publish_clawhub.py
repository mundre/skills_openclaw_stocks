#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
荞麦饼 Skills - ClawHub 发布脚本
作者: 度量衡
版本: 1.0.0
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# 技能信息
SKILL_INFO = {
    "name": "qiaomai-skills",
    "display_name": "荞麦饼 Skills",
    "version": "1.0.0",
    "author": "度量衡",
    "tagline": "标准源自最佳实践",
    "description": "下一代智能体操作系统，八大维度全面优化"
}

def print_header():
    """打印标题"""
    print("\n" + "="*60)
    print("  荞麦饼 Skills - ClawHub 发布构建")
    print("="*60)
    print()

def print_success(msg):
    """打印成功信息"""
    print(f"[OK] {msg}")

def print_error(msg):
    """打印错误信息"""
    print(f"[ERROR] {msg}")

def print_info(msg):
    """打印信息"""
    print(f"[INFO] {msg}")

def get_skill_dir():
    """获取技能目录"""
    return Path(__file__).parent.parent

def create_dist_dir(skill_dir):
    """创建构建目录"""
    dist_dir = skill_dir / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    return dist_dir

def copy_files(skill_dir, build_dir):
    """复制文件到构建目录"""
    files_to_copy = [
        "SKILL.md",
        "README_CLAWHUB.md",
        "clawhub.json",
        ".metadata.json",
    ]
    
    dirs_to_copy = [
        "core",
        "scripts",
        "data",
        "docs",
    ]
    
    # 复制文件
    for file in files_to_copy:
        src = skill_dir / file
        if src.exists():
            shutil.copy2(src, build_dir / file)
            print_success(f"复制 {file}")
        else:
            print_info(f"跳过 {file} (不存在)")
    
    # 复制目录
    for dir_name in dirs_to_copy:
        src = skill_dir / dir_name
        if src.exists():
            shutil.copytree(src, build_dir / dir_name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            print_success(f"复制 {dir_name}/")

def create_manifest(build_dir, skill_info):
    """创建清单文件"""
    manifest = {
        "name": skill_info["name"],
        "version": skill_info["version"],
        "author": skill_info["author"],
        "tagline": skill_info["tagline"],
        "description": skill_info["description"],
        "entry": "SKILL.md",
        "files": [
            "SKILL.md",
            "README_CLAWHUB.md",
            "clawhub.json",
            ".metadata.json",
            "core/",
            "scripts/",
            "data/",
            "docs/"
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    manifest_path = build_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print_success("创建 manifest.json")
    return manifest

def create_zip(build_dir, dist_dir, skill_info):
    """创建发布包"""
    zip_name = f"{skill_info['name']}-{skill_info['version']}.zip"
    zip_path = dist_dir / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in build_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(build_dir)
                zf.write(file_path, arcname)
    
    size_kb = zip_path.stat().st_size / 1024
    print_success(f"创建 {zip_name} ({size_kb:.1f} KB)")
    
    return zip_path

def generate_publish_guide(skill_dir, skill_info, zip_path):
    """生成发布指南"""
    guide_path = skill_dir / "PUBLISH_CLAWHUB.md"
    
    guide_content = f"""# 🌾 荞麦饼 Skills - ClawHub 发布指南

> **作者：{skill_info['author']} | {skill_info['tagline']}**

---

## 📦 发布信息

| 项目 | 内容 |
|------|------|
| **包名** | {skill_info['name']} |
| **显示名称** | {skill_info['display_name']} |
| **版本** | {skill_info['version']} |
| **作者** | {skill_info['author']} |
| **标签** | {skill_info['tagline']} |
| **发布包** | `{zip_path.name}` |

---

## 🚀 发布步骤

### 方式一：使用 ClawHub CLI (推荐)

```bash
# 1. 安装 ClawHub CLI
npm install -g clawhub

# 2. 登录 ClawHub
clawhub login

# 3. 进入技能目录
cd {skill_dir}

# 4. 发布技能
clawhub publish
```

### 方式二：手动上传

1. **访问** https://clawhub.ai/publish-skill
2. **登录** GitHub 账号
3. **点击** "Publish New Skill"
4. **填写信息：**
   - Package Name: `{skill_info['name']}`
   - Display Name: `{skill_info['display_name']}`
   - Version: `{skill_info['version']}`
   - Description: {skill_info['description']}
   - Author: {skill_info['author']}
5. **上传** 发布包: `{zip_path}`
6. **添加标签：**
   - ai-agent
   - knowledge-graph
   - memory-system
   - visualization
   - report-generation
   - easy-to-use
7. **提交** 发布

---

## 📋 表单内容

### 基本信息
- **Package Name**: `{skill_info['name']}`
- **Display Name**: `{skill_info['display_name']}`
- **Version**: `{skill_info['version']}`
- **Description**: {skill_info['description']}，让智能像荞麦饼一样营养全面、易于消化、百搭实用。

### 详细描述
```
荞麦饼 Skills 是从 oclaw-hermes v5.0.0 进化而来的下一代智能体操作系统。

【八大核心优化】
1. 易用性优化 - 自然语言交互 + 一键配置向导
2. 智能执行优化 - 自适应引擎 v2.0 + 预测性执行
3. 智能数据库优化 - 向量+图+关系混合架构
4. 智能记忆体优化 - 八层记忆架构 (OctoMemory)
5. 报告系统优化 - 多格式智能生成 + 自适应模板
6. 类案检索优化 - 语义+规则混合检索
7. 知识拓扑优化 - 动态知识图谱 (DynamicKG)
8. 可视化优化 - 交互式仪表盘 + 3D 知识空间

【性能表现】
- 启动时间: 200ms (提升 47%)
- 响应延迟: 80ms (提升 42%)
- 并发处理: 100 (提升 100%)
- 易用性评分: 5/5

【设计理念】
"让智能像荞麦饼一样，营养全面、易于消化、百搭实用。"
```

### 标签
```
ai-agent, knowledge-graph, memory-system, visualization, report-generation, case-search, easy-to-use, multi-agent
```

---

## 📁 文件清单

```
{skill_info['name']}-{skill_info['version']}.zip
├── SKILL.md              # 技能主文档
├── README_CLAWHUB.md     # ClawHub 专用 README
├── clawhub.json          # ClawHub 元数据
├── .metadata.json        # OpenClaw 元数据
├── manifest.json         # 清单文件
├── core/                 # 8大核心模块
├── scripts/              # 工具脚本
├── data/                 # 数据存储
└── docs/                 # 文档
```

---

## 🔗 相关链接

- **ClawHub**: https://clawhub.ai
- **发布页面**: https://clawhub.ai/publish-skill
- **项目主页**: https://github.com/dlh365/qiaomai-skills

---

**让智能更简单，让创造更自由。**

🌾 {skill_info['author']} | {skill_info['tagline']}
"""
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print_success(f"生成发布指南: {{guide_path}}")
    return guide_path

def main():
    """主函数"""
    print_header()
    
    # 获取技能目录
    skill_dir = get_skill_dir()
    print_info(f"技能目录: {{skill_dir}}")
    
    # 创建构建目录
    build_dir = skill_dir / "build_clawhub"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    
    # 创建发布目录
    dist_dir = create_dist_dir(skill_dir)
    
    # 复制文件
    print("\\n复制文件...")
    copy_files(skill_dir, build_dir)
    
    # 创建清单
    print("\\n创建清单...")
    manifest = create_manifest(build_dir, SKILL_INFO)
    
    # 创建发布包
    print("\\n创建发布包...")
    zip_path = create_zip(build_dir, dist_dir, SKILL_INFO)
    
    # 生成发布指南
    print("\\n生成发布指南...")
    guide_path = generate_publish_guide(skill_dir, SKILL_INFO, zip_path)
    
    # 清理构建目录
    shutil.rmtree(build_dir)
    
    # 打印完成信息
    print("\\n" + "="*60)
    print("  构建完成!")
    print("="*60)
    print()
    print(f"技能名称: {{SKILL_INFO['display_name']}}")
    print(f"版本: {{SKILL_INFO['version']}}")
    print(f"作者: {{SKILL_INFO['author']}}")
    print(f"标签: {{SKILL_INFO['tagline']}}")
    print()
    print(f"发布包位置:")
    print(f"  {{zip_path}}")
    print()
    print("发布步骤:")
    print("1. 访问 https://clawhub.ai/publish-skill")
    print("2. 登录 GitHub 账号")
    print("3. 点击'Publish New Skill'")
    print("4. 填写技能信息并上传发布包")
    print("5. 提交发布")
    print()
    print(f"详细指南: {{guide_path}}")
    print()

if __name__ == "__main__":
    main()
