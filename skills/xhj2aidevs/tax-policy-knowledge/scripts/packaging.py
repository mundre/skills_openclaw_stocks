#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财税政策知识库 Skill 打包脚本
作者：墨渊
功能：将 Skill 打包为标准通用的安装文件
"""
import os
import shutil
import zipfile
import json
import datetime
from pathlib import Path
def create_install_package():
    """创建安装包"""
    print("🎯 开始打包财税政策知识库 Skill...")
    
    # 基础路径
    skill_dir = Path(".")
    output_dir = skill_dir / "dist"
    output_dir.mkdir(exist_ok=True)
    
    # 生成版本信息
    version = "1.0.0"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"tax-policy-knowledge-v{version}-{timestamp}"
    
    # 1. 创建 zip 安装包
    zip_path = output_dir / f"{package_name}.zip"
    print(f"📦 创建安装包: {zip_path.name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加所有必要文件
        include_patterns = [
            "*.md", "*.yaml", "*.py",
            "assets/*", "references/*", "scripts/*"
        ]
        
        files_added = 0
        for pattern in include_patterns:
            for file_path in skill_dir.glob(pattern):
                if file_path.is_file():
                    arcname = str(file_path.relative_to(skill_dir))
                    zipf.write(file_path, arcname)
                    files_added += 1
                    print(f"  📄 添加: {arcname}")
    
    # 2. 创建安装说明文件
    install_guide = output_dir / "INSTALL.md"
    install_content = f"""# 财税政策知识库 Skill 安装指南
## 📦 安装包信息
- **包名**: {package_name}.zip
- **版本**: {version}
- **打包时间**: {timestamp}
- **文件数量**: {files_added} 个文件
- **适用平台**: Windows/macOS/Linux
## 🔧 安装方法
### 方法一：AiPy 直接安装
1. 解压 `{package_name}.zip` 文件
2. 将 `tax-policy-knowledge` 文件夹复制到 AiPy 的 skills 目录
   - Windows: `%APPDATA%\\.aipyapp\\skills\\`
   - macOS/Linux: `~/.aipyapp/skills/`
3. 重启 AiPy 应用
4. 在对话中使用关键词触发：财税政策、增值税、企业所得税、个人所得税等
### 方法二：独立使用计算工具
1. 解压 `{package_name}.zip` 文件
2. 进入解压后的目录
3. 运行计算工具：
```bash
cd tax-policy-knowledge/scripts
python tax_policy_calculator.py vat --sales 150000
```
## 📁 包含文件
```
tax-policy-knowledge/
├── SKILL.md                          # 技能核心文档
├── skill.yaml                        # 技能配置文件
├── README.md                         # 项目说明文档
├── assets/                           # 静态资源
│   ├── wechat-qr.png                # 微信二维码
│   ├── policy-overview.html         # 政策概览页面
│   └── wechat-qr-preview.html       # 二维码预览
├── references/                       # 参考资料
│   └── tax-policy-database.md       # 财税政策详细数据库
└── scripts/                          # 脚本工具
    ├── tax_policy_calculator.py     # 财税计算器
    └── test_calculator.py           # 测试脚本
```
## 🎯 功能特性
✅ 政策法规查询（增值税、企业所得税、个人所得税等）
✅ 政策解读分析
✅ 优惠资格判定
✅ 合规风险提示
✅ 申报操作指导
✅ 4种税务计算工具
## 📞 技术支持
如有安装问题，请联系：
- QQ: 1817694478
- 微信扫码: 见 assets/wechat-qr.png
---
**打包时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**打包工程师**: 墨渊
"""
    
    with open(install_guide, 'w', encoding='utf-8') as f:
        f.write(install_content)
    print(f"📝 生成安装指南: {install_guide.name}")
    
    # 3. 创建校验文件
    checksum_file = output_dir / "CHECKSUM.md5"
    import hashlib
    with open(zip_path, 'rb') as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()
    
    checksum_content = f"""# 文件校验信息
文件名: {zip_path.name}
MD5: {md5_hash}
文件大小: {zip_path.stat().st_size} 字节
打包时间: {timestamp}
版本: {version}
校验命令:
```bash
# Windows
certutil -hashfile "{zip_path.name}" MD5
# macOS/Linux
md5sum "{zip_path.name}"
```
"""
    
    with open(checksum_file, 'w', encoding='utf-8') as f:
        f.write(checksum_content)
    print(f"🔍 生成校验文件: {checksum_file.name}")
    
    # 4. 创建 package.json 用于 npm 风格安装
    package_json = {
        "name": "tax-policy-knowledge",
        "version": version,
        "description": "基于国家相关官方政策法规库近三年有效财税政策的专业知识库Skill",
        "main": "SKILL.md",
        "author": "AiPy Team",
        "license": "MIT",
        "keywords": ["tax", "policy", "china", "vat", "corporate-tax", "income-tax"],
        "files": [
            "SKILL.md",
            "skill.yaml",
            "README.md",
            "assets/",
            "references/",
            "scripts/"
        ],
        "install": "copy to ~/.aipyapp/skills/",
        "created": timestamp
    }
    
    package_json_path = output_dir / "package.json"
    with open(package_json_path, 'w', encoding='utf-8') as f:
        json.dump(package_json, f, indent=2, ensure_ascii=False)
    print(f"📋 生成 package.json: {package_json_path.name}")
    
    # 5. 创建一键安装脚本
    install_script = output_dir / "install.sh"
    install_script_content = """#!/bin/bash
# 财税政策知识库 Skill 一键安装脚本
echo "🔧 开始安装财税政策知识库 Skill..."
echo "=========================================="
# 检测系统类型
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    # Linux 或 macOS
    SKILLS_DIR="$HOME/.aipyapp/skills"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash)
    SKILLS_DIR="$APPDATA/.aipyapp/skills"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi
# 创建技能目录
mkdir -p "$SKILLS_DIR"
# 复制文件
echo "📁 复制文件到: $SKILLS_DIR/tax-policy-knowledge"
cp -r tax-policy-knowledge "$SKILLS_DIR/"
# 设置权限
chmod -R 755 "$SKILLS_DIR/tax-policy-knowledge/scripts"/*.py 2>/dev/null
echo "✅ 安装完成！"
echo ""
echo "🎯 使用方法:"
echo "1. 重启 AiPy 应用"
echo "2. 在对话中使用关键词触发:"
echo "   - 财税政策"
echo "   - 增值税"
echo "   - 企业所得税"
echo "   - 个人所得税"
echo "3. 或运行计算工具:"
echo "   cd $SKILLS_DIR/tax-policy-knowledge/scripts"
echo "   python tax_policy_calculator.py vat --sales 150000"
echo ""
echo "📞 技术支持: QQ 1817694478"
"""
    
    with open(install_script, 'w', encoding='utf-8') as f:
        f.write(install_script_content)
    # 设置执行权限
    if os.name != 'nt':  # 非 Windows 系统
        os.chmod(install_script, 0o755)
    print(f"⚡ 生成一键安装脚本: {install_script.name}")
    
    # 6. 创建 Windows 批处理安装脚本
    install_bat = output_dir / "install.bat"
    install_bat_content = """@echo off
REM 财税政策知识库 Skill Windows 安装脚本
echo 🔧 开始安装财税政策知识库 Skill...
echo ==========================================
REM 设置技能目录
set "SKILLS_DIR=%APPDATA%\\.aipyapp\\skills"
REM 创建目录
if not exist "%SKILLS_DIR%" mkdir "%SKILLS_DIR%"
REM 复制文件
echo 📁 复制文件到: %SKILLS_DIR%\\tax-policy-knowledge
xcopy /E /I /Y tax-policy-knowledge "%SKILLS_DIR%\\tax-policy-knowledge"
echo ✅ 安装完成！
echo.
echo 🎯 使用方法:
echo 1. 重启 AiPy 应用
echo 2. 在对话中使用关键词触发:
echo    - 财税政策
echo    - 增值税
echo    - 企业所得税
echo    - 个人所得税
echo 3. 或运行计算工具:
echo    cd %SKILLS_DIR%\\tax-policy-knowledge\\scripts
echo    python tax_policy_calculator.py vat --sales 150000
echo.
echo 📞 技术支持: QQ 1817694478
pause
"""
    
    with open(install_bat, 'w', encoding='utf-8') as f:
        f.write(install_bat_content)
    print(f"🪟 生成 Windows 安装脚本: {install_bat.name}")
    
    # 最终统计
    print("\n" + "="*60)
    print("🎉 打包完成！")
    print("="*60)
    print(f"📦 安装包: {zip_path.name}")
    print(f"📏 大小: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"📄 文件数: {files_added} 个")
    print(f"📁 输出目录: {output_dir.absolute()}")
    print("\n📋 生成的文件:")
    for file in output_dir.iterdir():
        size_kb = file.stat().st_size / 1024
        print(f"  • {file.name} ({size_kb:.1f} KB)")
    
    return {
        "package_name": package_name,
        "zip_path": zip_path,
        "files_added": files_added,
        "output_dir": output_dir
    }
if __name__ == "__main__":
    try:
        result = create_install_package()
        print("\n✅ 打包工程师 墨渊 已完成任务！")
        print("📦 安装包已准备好，可以直接分发使用。")
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()