#!/usr/bin/env python3
"""
检查OpenClaw环境变量设置
"""

import os
import json

print("🔍 检查环境变量")
print("=" * 60)

# 检查所有以PATENT开头的环境变量
for key, value in os.environ.items():
    if key.startswith('PATENT_'):
        print(f"{key}: {value[:20]}...{value[-20:] if len(value) > 40 else ''} (长度: {len(value)})")

# 检查OpenClaw相关的环境变量
openclaw_vars = [
    'PATENT_API_TOKEN',
    'OPENCLAW_SKILL_NAME',
    'OPENCLAW_SKILL_METADATA',
    'OPENCLAW_SKILL_CONFIG'
]

print(f"\n🔧 检查特定变量:")
for var in openclaw_vars:
    if var in os.environ:
        print(f"✅ {var}: 已设置")
        if var == 'OPENCLAW_SKILL_METADATA' or var == 'OPENCLAW_SKILL_CONFIG':
            try:
                data = json.loads(os.environ[var])
                print(f"   内容: {json.dumps(data, ensure_ascii=False)[:200]}...")
            except:
                print(f"   内容: {os.environ[var][:200]}...")
        else:
            print(f"   内容: {os.environ[var][:50]}...")
    else:
        print(f"❌ {var}: 未设置")

# 检查当前工作目录
print(f"\n📁 工作目录: {os.getcwd()}")
print(f"📁 脚本目录: {os.path.dirname(os.path.abspath(__file__))}")

# 检查配置文件是否存在
config_files = ['config.json', '.env', 'config.example.json']
print(f"\n📄 配置文件检查:")
for config_file in config_files:
    if os.path.exists(config_file):
        print(f"✅ {config_file}: 存在")
        if config_file == 'config.json':
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if 'token' in config:
                        print(f"   包含token: {config['token'][:20]}...")
            except:
                print(f"   无法读取或解析")
    else:
        print(f"❌ {config_file}: 不存在")