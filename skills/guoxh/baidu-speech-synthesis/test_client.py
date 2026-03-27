#!/usr/bin/env python3
"""
测试更新后的百度 TTS 客户端
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from scripts.baidu_tts import BaiduTTSClient

def test_token_mode():
    """测试 access_token 模式（bce-v3/...）"""
    print("=== 测试 token 模式 ===")
    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print("❌ BAIDU_API_KEY 未设置")
        return False
    
    print(f"使用密钥（前30字符）: {api_key[:30]}...")
    
    try:
        # 初始化客户端（不传 secret_key）
        client = BaiduTTSClient(api_key=api_key, secret_key="")
        print("✅ 客户端初始化成功")
        
        # 尝试合成短文本
        print("尝试合成短文本...")
        audio = client.synthesize_text("测试", per=0)
        print(f"✅ 合成成功，音频长度: {len(audio)} bytes")
        return True
    except Exception as e:
        print(f"❌ 合成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_key_secret_mode():
    """测试 API Key + Secret Key 模式"""
    print("\n=== 测试 API Key + Secret Key 模式 ===")
    api_key = os.getenv("BAIDU_API_KEY")
    secret_key = os.getenv("BAIDU_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("⚠️  需要 BAIDU_API_KEY 和 BAIDU_SECRET_KEY，跳过")
        return None
    
    try:
        client = BaiduTTSClient(api_key=api_key, secret_key=secret_key)
        print("✅ 客户端初始化成功")
        
        # 获取 token
        token = client.get_access_token()
        print(f"✅ 获取 token 成功: {token[:20]}...")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

if __name__ == "__main__":
    # 设置环境变量（如果未设置）
    if not os.getenv("BAIDU_API_KEY"):
        # 从 openclaw.json 读取？简单起见，直接使用已知值
        os.environ["BAIDU_API_KEY"] = "bce-v3/ALTAK-xhakLZ9EzPn8ItVfKsorz/d6cb949f8c48cd120c0392389b978a90aa29490b"
    
    success = test_token_mode()
    if success:
        print("\n✅ Token 模式测试通过！")
    else:
        print("\n❌ Token 模式测试失败，可能需要单独的 API Key + Secret Key")
    
    # 如果有 Secret Key 则测试第二种模式
    result = test_key_secret_mode()
    if result is not None:
        if result:
            print("✅ API Key + Secret Key 模式测试通过")
        else:
            print("❌ API Key + Secret Key 模式测试失败")
    
    sys.exit(0 if success else 1)