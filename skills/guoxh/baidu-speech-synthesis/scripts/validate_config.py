#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度语音合成配置验证脚本
验证环境变量配置、网络连通性、API权限
"""

import os
import sys
import requests
import json
from pathlib import Path

# 添加当前目录到路径，以便导入本地模块
sys.path.insert(0, str(Path(__file__).parent))

try:
    from baidu_tts import BaiduTTSClient
except ImportError as e:
    print(f"警告：无法导入 BaiduTTSClient: {e}")
    BaiduTTSClient = None

class ConfigValidator:
    """配置验证器"""
    
    # API端点
    TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    TTS_URL = "https://tsn.baidu.com/text2audio"
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def _add_result(self, test_name, success, message=""):
        """添加测试结果"""
        if success:
            self.passed += 1
            status = "✅ 通过"
        else:
            self.failed += 1
            status = "❌ 失败"
        
        result = {
            "test": test_name,
            "status": status,
            "message": message
        }
        self.results.append(result)
        return success
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("配置验证报告")
        print("=" * 60)
        
        for result in self.results:
            print(f"{result['status']} - {result['test']}")
            if result['message']:
                print(f"    {result['message']}")
        
        print("-" * 60)
        print(f"总计: {self.passed} 项通过, {self.failed} 项失败")
        
        if self.failed == 0:
            print("✅ 所有测试通过！配置有效。")
            return True
        else:
            print("❌ 存在配置问题，请检查上述失败项。")
            return False
    
    def check_environment_variables(self):
        """检查环境变量"""
        print("1. 检查环境变量...")
        
        # 检查 BAIDU_API_KEY
        api_key = os.environ.get("BAIDU_API_KEY")
        if not api_key:
            return self._add_result("BAIDU_API_KEY 存在", False, "环境变量 BAIDU_API_KEY 未设置")
        
        # 检查 BAIDU_SECRET_KEY
        secret_key = os.environ.get("BAIDU_SECRET_KEY")
        if not secret_key:
            return self._add_result("BAIDU_SECRET_KEY 存在", False, "环境变量 BAIDU_SECRET_KEY 未设置")
        
        # 验证密钥格式
        key_format_ok = True
        messages = []
        
        # API Key 格式检查（通常是24位字母数字）
        if len(api_key) != 24 or not api_key.isalnum():
            key_format_ok = False
            messages.append(f"API Key 格式可能无效 (长度: {len(api_key)}, 期望: 24位字母数字)")
        
        # Secret Key 格式检查（通常是32位字母数字）
        if len(secret_key) != 32 or not secret_key.isalnum():
            key_format_ok = False
            messages.append(f"Secret Key 格式可能无效 (长度: {len(secret_key)}, 期望: 32位字母数字)")
        
        if key_format_ok:
            return self._add_result("环境变量格式", True, f"API Key: {api_key[:4]}...{api_key[-4:]}, Secret Key: {secret_key[:4]}...{secret_key[-4:]}")
        else:
            return self._add_result("环境变量格式", False, "; ".join(messages))
    
    def check_network_connectivity(self):
        """检查网络连通性"""
        print("2. 检查网络连通性...")
        
        # 测试百度API端点
        endpoints = [
            ("百度鉴权接口", self.TOKEN_URL),
            ("百度TTS接口", self.TTS_URL)
        ]
        
        all_passed = True
        for name, url in endpoints:
            try:
                # 只测试连接，不发送实际请求
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code < 400:
                    self._add_result(f"连接到 {name}", True, f"{url} - 状态码: {response.status_code}")
                else:
                    all_passed = False
                    self._add_result(f"连接到 {name}", False, f"{url} - 状态码: {response.status_code}")
            except requests.exceptions.Timeout:
                all_passed = False
                self._add_result(f"连接到 {name}", False, f"{url} - 连接超时")
            except requests.exceptions.ConnectionError as e:
                all_passed = False
                self._add_result(f"连接到 {name}", False, f"{url} - 连接错误: {e}")
            except Exception as e:
                all_passed = False
                self._add_result(f"连接到 {name}", False, f"{url} - 未知错误: {e}")
        
        return all_passed
    
    def check_authentication(self):
        """检查API认证"""
        print("3. 检查API认证...")
        
        api_key = os.environ.get("BAIDU_API_KEY")
        secret_key = os.environ.get("BAIDU_SECRET_KEY")
        
        if not api_key or not secret_key:
            return self._add_result("API认证", False, "缺少API Key或Secret Key")
        
        # 尝试获取访问令牌
        try:
            params = {
                "grant_type": "client_credentials",
                "client_id": api_key,
                "client_secret": secret_key
            }
            
            response = requests.get(self.TOKEN_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    token = data["access_token"]
                    expires_in = data.get("expires_in", "未知")
                    
                    # 验证token格式（百度token通常以"1."开头）
                    if token.startswith("1."):
                        token_format = "有效格式 (以'1.'开头)"
                    else:
                        token_format = "非常规格式"
                    
                    return self._add_result("获取访问令牌", True, 
                        f"Token: {token[:10]}..., 有效期: {expires_in}秒, {token_format}")
                else:
                    error = data.get("error_description", data.get("error", "未知错误"))
                    return self._add_result("获取访问令牌", False, f"API返回错误: {error}")
            else:
                return self._add_result("获取访问令牌", False, f"HTTP状态码: {response.status_code}")
        
        except requests.exceptions.Timeout:
            return self._add_result("获取访问令牌", False, "请求超时")
        except requests.exceptions.ConnectionError as e:
            return self._add_result("获取访问令牌", False, f"连接错误: {e}")
        except json.JSONDecodeError:
            return self._add_result("获取访问令牌", False, "响应不是有效的JSON")
        except Exception as e:
            return self._add_result("获取访问令牌", False, f"未知错误: {e}")
    
    def check_tts_functionality(self):
        """检查TTS功能"""
        print("4. 检查TTS功能...")
        
        if BaiduTTSClient is None:
            return self._add_result("TTS功能", False, "无法导入BaiduTTSClient，跳过功能测试")
        
        try:
            # 创建客户端
            client = BaiduTTSClient()
            
            # 测试简单文本合成（短文本）
            test_text = "百度语音合成测试"
            
            # 注意：这需要有效的访问令牌
            # 我们尝试获取令牌，如果失败则跳过
            try:
                token = client.get_access_token()
                if not token:
                    return self._add_result("TTS功能", False, "无法获取访问令牌，请检查API Key和Secret Key")
                
                # 尝试合成短音频
                success, result = client.text_to_speech(
                    text=test_text,
                    voice=0,  # 度小美
                    speed=5,
                    pitch=5,
                    volume=5,
                    format=3  # mp3
                )
                
                if success:
                    return self._add_result("TTS功能", True, "成功合成测试音频")
                else:
                    return self._add_result("TTS功能", False, f"合成失败: {result}")
            
            except Exception as e:
                return self._add_result("TTS功能", False, f"TTS调用异常: {e}")
        
        except Exception as e:
            return self._add_result("TTS功能", False, f"客户端初始化失败: {e}")
    
    def run_all_checks(self):
        """运行所有检查"""
        print("开始百度语音合成配置验证")
        print("=" * 60)
        
        # 检查环境变量
        self.check_environment_variables()
        
        # 检查网络连通性
        self.check_network_connectivity()
        
        # 检查认证
        self.check_authentication()
        
        # 检查TTS功能（可选，如果前几步失败可能跳过）
        if self.failed == 0:
            self.check_tts_functionality()
        else:
            print("4. 跳过TTS功能检查（因前置检查失败）")
            self._add_result("TTS功能", False, "前置检查失败，跳过")
        
        # 打印摘要
        return self.print_summary()

def main():
    """主函数"""
    validator = ConfigValidator()
    success = validator.run_all_checks()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()