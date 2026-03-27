#!/usr/bin/env python3
"""
测试百度语音合成 API 认证
"""

import os
import sys
import requests

BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
if not BAIDU_API_KEY:
    print("❌ BAIDU_API_KEY 未设置")
    sys.exit(1)

print(f"使用的密钥（前30字符）: {BAIDU_API_KEY[:30]}...")
print(f"密钥长度: {len(BAIDU_API_KEY)}")
print(f"密钥格式猜测: {'bce-v3/' if BAIDU_API_KEY.startswith('bce-v3/') else '非 bce-v3'}")

# 测试 1: 直接作为 access_token 调用 TTS
print("\n=== 测试1: 直接作为 access_token ===")
params = {
    "tok": BAIDU_API_KEY,
    "tex": "测试",
    "per": 0,
    "spd": 5,
    "pit": 5,
    "vol": 5,
    "aue": 3,
    "cuid": "test",
}
try:
    resp = requests.post("https://aip.baidubce.com/text2audio", data=params, timeout=10)
    if resp.headers.get("Content-Type") == "audio/mp3":
        print("✅ 成功！返回音频长度:", len(resp.content))
    else:
        error = resp.json()
        print(f"❌ 错误: {error}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试 2: 尝试作为 client_id 获取 token（需要 secret_key）
print("\n=== 测试2: 尝试获取 token（假设密钥为 client_id）===")
token_url = "https://aip.baidubce.com/oauth/2.0/token"
params = {
    "grant_type": "client_credentials",
    "client_id": BAIDU_API_KEY,
    "client_secret": "",  # 未知
}
try:
    resp = requests.get(token_url, params=params, timeout=10)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ 获取 token 成功: {data.get('access_token')[:20]}...")
    else:
        print(f"❌ 失败: {resp.text}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试 3: 如果密钥是 bce-v3 格式，尝试解析
print("\n=== 测试3: 解析 bce-v3 格式 ===")
if BAIDU_API_KEY.startswith("bce-v3/"):
    parts = BAIDU_API_KEY.split("/")
    if len(parts) >= 3:
        print(f"  前缀: {parts[0]}")
        print(f"  中间部分: {parts[1]}")
        print(f"  后半部分: {parts[2][:20]}...")
        # 猜测中间部分是 access_key_id
        if parts[1].startswith("ALTAK-"):
            access_key = parts[1][6:]  # 去掉 ALTAK-
            print(f"  可能的 access_key_id: {access_key}")
            # 后半部分可能是 signature 或 secret?
            print(f"  可能的 secret_key 片段: {parts[2][:10]}...")
    else:
        print("  格式无法解析")

print("\n=== 总结 ===")
print("如果测试1成功，该密钥可直接作为 access_token 使用。")
print("否则需要单独的 API Key + Secret Key 对。")
print("请提供结果给用户以决定下一步。")