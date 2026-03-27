#!/usr/bin/env python3
"""
百度 TTS 认证诊断工具
快速检查认证配置并提供修复建议
"""

import os
import sys

def diagnose_auth():
    print("🔍 百度 TTS 认证诊断")
    print("="*60)
    
    # 检查环境变量
    api_key = os.getenv("BAIDU_API_KEY")
    secret_key = os.getenv("BAIDU_SECRET_KEY")
    access_token = os.getenv("BAIDU_ACCESS_TOKEN")
    
    print("1. 检查环境变量:")
    print(f"   BAIDU_API_KEY: {'✅ 已设置' if api_key else '❌ 未设置'}")
    if api_key:
        print(f"     值（前30字符）: {api_key[:30]}...")
        print(f"     格式检测: ", end="")
        if api_key.startswith("1."):
            print("✅ 可能是 access_token（以 '1.' 开头）")
        elif api_key.startswith("bce-v3/"):
            print("⚠️  IAM Key 格式（bce-v3/）")
            print("     注意：此密钥可能不适用于语音合成")
        else:
            print("📋 普通 API Key 格式")
    
    print(f"   BAIDU_SECRET_KEY: {'✅ 已设置' if secret_key else '❌ 未设置'}")
    if secret_key:
        print(f"     值（前10字符）: {secret_key[:10]}...")
    
    print(f"   BAIDU_ACCESS_TOKEN: {'✅ 已设置' if access_token else '❌ 未设置'}")
    if access_token:
        print(f"     值（前30字符）: {access_token[:30]}...")
    
    print("\n2. 认证配置分析:")
    
    if not api_key and not access_token:
        print("   ❌ 未找到任何认证凭证")
        print("\n   解决方案:")
        print("   1. 创建语音合成应用获取 API Key + Secret Key")
        print("   2. 或设置 BAIDU_API_KEY 环境变量")
        return False
    
    # 分析配置
    if api_key:
        if api_key.startswith("1."):
            print("   ✅ 配置为 access_token 模式")
            print("     将使用 tok 参数认证")
        elif api_key.startswith("bce-v3/"):
            print("   ⚠️  配置为 IAM Key 模式")
            print("     将使用 iam-apikey 参数认证")
            print("\n     警告: 现有 bce-v3/ALTAK‑... 密钥可能不适用于语音合成")
            print("     若遇到 'tok, appid, apikey or iam‑apikey is empty' 错误")
            print("     请创建语音合成专用应用获取 API Key + Secret Key")
        else:
            # 普通 API Key
            if secret_key:
                print("   ✅ 配置为 API Key + Secret Key 模式")
                print("     将自动获取 access_token")
            else:
                print("   ❌ 普通 API Key 需要同时设置 BAIDU_SECRET_KEY")
                print("\n   解决方案:")
                print("   1. 设置 BAIDU_SECRET_KEY 环境变量")
                print("   2. 或改用 access_token（以 '1.' 开头）")
                return False
    
    print("\n3. 建议:")
    
    if api_key and api_key.startswith("bce-v3/"):
        print("   ⚠️  检测到可能不兼容的 IAM Key")
        print("   建议创建语音合成专用应用:")
        print("   1. 访问 https://console.bce.baidu.com/ai/")
        print("   2. 创建语音合成应用")
        print("   3. 获取 API Key + Secret Key")
        print("   4. 更新环境变量")
    
    elif api_key and not api_key.startswith(("1.", "bce-v3/")) and secret_key:
        print("   ✅ 配置正确（API Key + Secret Key）")
        print("   可以开始使用 baidu_tts.py")
    
    elif api_key and api_key.startswith("1."):
        print("   ✅ 配置正确（access_token）")
        print("   可以开始使用 baidu_tts.py")
    
    else:
        print("   ❓ 配置不完整，请参考以下步骤:")
        print("   1. 获取语音合成 API 密钥")
        print("   2. 设置正确的环境变量")
        print("   3. 运行测试命令:")
        print("      python scripts/baidu_tts.py --text '测试' --output test.mp3")
    
    print("\n" + "="*60)
    print("📚 详细指南请参考:")
    print("   ~/.openclaw/skills/baidu-speech-synthesis/references/api_setup.md")
    
    return True

if __name__ == "__main__":
    try:
        success = diagnose_auth()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"诊断过程中出错: {e}")
        sys.exit(1)