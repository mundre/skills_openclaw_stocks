#!/usr/bin/env python3
"""
百度 TTS 认证全面测试
测试三种认证方式：
1. access_token（以 "1." 开头）
2. IAM Key（以 "bce-v3/" 开头）
3. API Key + Secret Key（普通格式）
"""

import os
import sys
import json
import requests
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

try:
    from baidu_tts import BaiduTTSClient
except ImportError as e:
    print(f"导入失败: {e}")
    sys.exit(1)

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_iam_key():
    """测试 IAM Key（bce-v3/ 格式）"""
    print_header("测试 IAM Key (bce-v3/ 格式)")
    
    # 使用现有的 bce-v3/ 格式密钥
    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print("❌ BAIDU_API_KEY 未设置")
        return False
    
    print(f"使用密钥: {api_key[:50]}...")
    
    if not api_key.startswith("bce-v3/"):
        print("⚠️  密钥不是 bce-v3/ 格式，跳过 IAM 测试")
        return None
    
    try:
        # 测试客户端初始化
        client = BaiduTTSClient(api_key=api_key, secret_key="")
        print("✅ 客户端初始化成功")
        print(f"认证类型: {client.auth_type}")
        
        # 尝试合成短文本
        print("尝试合成短文本...")
        try:
            audio = client.synthesize_text("测试", per=0)
            print(f"✅ IAM 认证成功！音频长度: {len(audio)} bytes")
            return True
        except Exception as e:
            error_msg = str(e)
            print(f"❌ IAM 认证失败: {e}")
            
            # 分析错误
            if "tok, appid, apikey or iam-apikey is empty" in error_msg:
                print("⚠️  IAM Key 可能不适用于 TTS API")
                print("   建议创建专门的语音合成应用获取 API Key")
            elif "No permission" in error_msg:
                print("⚠️  无权限访问 TTS 服务")
                print("   请确保该 IAM Key 已授权语音合成服务")
            return False
            
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        return False

def test_token_auth():
    """测试 access_token 认证"""
    print_header("测试 access_token 认证")
    
    # 检查是否有可用的 access_token
    access_token = os.getenv("BAIDU_ACCESS_TOKEN")
    if not access_token:
        print("⚠️  BAIDU_ACCESS_TOKEN 未设置，跳过测试")
        return None
    
    print(f"使用 access_token: {access_token[:30]}...")
    
    try:
        # access_token 应该以 "1." 开头
        client = BaiduTTSClient(api_key=access_token, secret_key="")
        print("✅ 客户端初始化成功")
        print(f"认证类型: {client.auth_type}")
        
        # 尝试合成
        print("尝试合成短文本...")
        audio = client.synthesize_text("测试", per=0)
        print(f"✅ access_token 认证成功！音频长度: {len(audio)} bytes")
        return True
    except Exception as e:
        print(f"❌ access_token 认证失败: {e}")
        return False

def test_api_key_secret():
    """测试 API Key + Secret Key 认证"""
    print_header("测试 API Key + Secret Key 认证")
    
    api_key = os.getenv("BAIDU_API_KEY_FOR_TTS")
    secret_key = os.getenv("BAIDU_SECRET_KEY_FOR_TTS")
    
    if not api_key or not secret_key:
        print("⚠️  BAIDU_API_KEY_FOR_TTS 或 BAIDU_SECRET_KEY_FOR_TTS 未设置，跳过测试")
        return None
    
    # 检查是否为普通 API Key（非 bce-v3/ 格式）
    if api_key.startswith("bce-v3/"):
        print("⚠️  密钥是 bce-v3/ 格式，不是普通 API Key，跳过")
        return None
    
    print(f"使用 API Key: {api_key[:20]}...")
    print(f"使用 Secret Key: {secret_key[:10]}...")
    
    try:
        client = BaiduTTSClient(api_key=api_key, secret_key=secret_key)
        print("✅ 客户端初始化成功")
        print(f"认证类型: {client.auth_type}")
        
        # 获取 token
        token = client.get_access_token()
        print(f"✅ 获取 access_token 成功: {token[:30]}...")
        
        # 尝试合成
        print("尝试合成短文本...")
        audio = client.synthesize_text("测试", per=0)
        print(f"✅ API Key + Secret Key 认证成功！音频长度: {len(audio)} bytes")
        return True
    except Exception as e:
        print(f"❌ API Key + Secret Key 认证失败: {e}")
        return False

def check_baidu_api():
    """检查百度 API 端点"""
    print_header("检查百度 API 端点")
    
    endpoints = {
        "token_url": "https://openapi.baidu.com/oauth/2.0/token",
        "tts_url": "https://tsn.baidu.com/text2audio"
    }
    
    for name, url in endpoints.items():
        try:
            # 尝试 HEAD 请求检查可达性
            resp = requests.head(url, timeout=5)
            print(f"✅ {name}: {url} (状态: {resp.status_code})")
        except Exception as e:
            print(f"❌ {name}: {url} - 连接失败: {e}")

def main():
    """主测试函数"""
    print("百度 TTS 认证全面测试")
    print(f"工作目录: {os.getcwd()}")
    
    # 检查网络连接
    check_baidu_api()
    
    # 测试各种认证方式
    results = {}
    
    # 首先测试 IAM Key（使用现有的 BAIDU_API_KEY）
    results["iam"] = test_iam_key()
    
    # 测试 access_token
    results["token"] = test_token_auth()
    
    # 测试 API Key + Secret Key
    results["api_key_secret"] = test_api_key_secret()
    
    # 总结
    print_header("测试总结")
    
    success_count = sum(1 for r in results.values() if r is True)
    total_tests = sum(1 for r in results.values() if r is not None)
    
    print(f"测试完成: {success_count}/{total_tests} 成功")
    
    for auth_type, result in results.items():
        if result is None:
            status = "跳过"
        elif result:
            status = "✅ 成功"
        else:
            status = "❌ 失败"
        print(f"  {auth_type:15}: {status}")
    
    print("\n" + "="*60)
    print("重要提示:")
    print("1. 现有 bce-v3/ 格式 IAM Key 可能不适用于 TTS API")
    print("2. 需要创建专门的语音合成应用获取 API Key + Secret Key")
    print("3. 参考 ~/.openclaw/skills/baidu-speech-synthesis/references/api_setup.md")
    print("   获取详细的密钥申请指南")
    print("="*60)
    
    # 如果有成功的测试，返回 0，否则返回 1
    if success_count > 0:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())