#!/usr/bin/env python3
"""
八爪鱼 RPA Webhook 调用工具
"""

import json
import hmac
import hashlib
import base64
import time
import argparse
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / 'config.json'

def show_help():
    print("""八爪鱼 RPA Webhook 调用工具

用法:
  python bazhuayu-webhook.py init              初始化配置
  python bazhuayu-webhook.py run [选项]        运行任务
  python bazhuayu-webhook.py config            查看当前配置
  python bazhuayu-webhook.py test              测试连接（dry-run）

run 选项:
  --param1=值 1    设置参数 1 的值
  --param2=值 2    设置参数 2 的值
  --dry-run        仅显示请求内容，不实际发送

示例:
  python bazhuayu-webhook.py run --param1=新值 1 --param2=新值 2
""")

def load_config():
    if not CONFIG_FILE.exists():
        print("错误：配置文件不存在，请先运行 init 初始化")
        sys.exit(1)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("配置已保存")

def init_config():
    print("=== 八爪鱼 RPA Webhook 初始化配置 ===\n")
    
    url = input("请输入 Webhook URL: ").strip()
    key = input("请输入签名密钥 (Key): ").strip()
    
    print("\n定义参数名称（逗号分隔，如：参数 1，参数 2）: ")
    params_input = input().strip()
    param_names = [p.strip() for p in params_input.split(',') if p.strip()]
    
    default_params = {}
    for name in param_names:
        value = input(f"请输入 [{name}] 的默认值：").strip()
        default_params[name] = value
    
    config = {
        'url': url,
        'key': key,
        'paramNames': param_names,
        'defaultParams': default_params
    }
    
    save_config(config)
    
    print("\n=== 配置完成 ===")
    print(f"Webhook URL: {url}")
    print(f"参数列表：{', '.join(param_names)}")

def show_config():
    config = load_config()
    print("=== 当前配置 ===")
    print(f"Webhook URL: {config['url']}")
    key = config['key']
    print(f"签名密钥：{key[:4]}...{key[-4:] if len(key) > 8 else key}")
    print(f"参数列表：{', '.join(config['paramNames'])}")
    print("默认参数值:")
    for name, value in config['defaultParams'].items():
        print(f"  {name} = {value}")

def calculate_sign(key, timestamp):
    """
    计算签名：HmacSHA256(timestamp + '\\n' + key) -> Base64
    
    根据八爪鱼文档示例，string_to_sign 作为 HMAC 的密钥，消息为空
    """
    string_to_sign = f"{timestamp}\n{key}"
    # string_to_sign 作为 HMAC 密钥，消息为空字节
    sign_data = hmac.new(
        string_to_sign.encode('utf-8'),
        b'',
        hashlib.sha256
    ).digest()
    return base64.b64encode(sign_data).decode('utf-8')

def run_task(override_params=None, dry_run=False):
    if override_params is None:
        override_params = {}
    
    config = load_config()
    
    # 合并参数：默认参数 + 覆盖参数
    params = {**config['defaultParams'], **override_params}
    
    timestamp = str(int(time.time()))
    sign = calculate_sign(config['key'], timestamp)
    
    payload = {
        'sign': sign,
        'params': params,
        'timestamp': timestamp
    }
    
    print("=== 准备发送请求 ===")
    print(f"URL: {config['url']}")
    print(f"时间戳：{timestamp}")
    print("参数:")
    for name, value in params.items():
        print(f"  {name} = {value}")
    
    if dry_run:
        print("\n[DRY RUN] 未实际发送请求")
        print("\n请求 Payload:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    
    print("\n正在发送请求...")
    
    try:
        import urllib.request
        import urllib.error
        
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            config['url'],
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            http_code = response.status
            result = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        http_code = e.code
        result = json.loads(e.read().decode('utf-8'))
    except Exception as e:
        print(f"\n=== 响应结果 ===")
        print(f"错误：{e}")
        sys.exit(1)
    
    print("\n=== 响应结果 ===")
    print(f"HTTP 状态码：{http_code}")
    
    if http_code == 200:
        print("✅ 调用成功!")
        if 'flowId' in result:
            print(f"应用 ID (flowId): {result['flowId']}")
        if 'flowProcessNo' in result:
            print(f"运行批次 (flowProcessNo): {result['flowProcessNo']}")
        if 'enterpriseId' in result:
            print(f"企业 ID: {result['enterpriseId']}")
    else:
        print("❌ 调用失败")
        if 'code' in result:
            print(f"错误码：{result['code']}")
        if 'description' in result:
            print(f"错误描述：{result['description']}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1]
    override_params = {}
    dry_run = False
    
    # 解析命令行参数
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '--dry-run':
            dry_run = True
        elif arg.startswith('--'):
            # 处理 --key=value 格式
            if '=' in arg:
                eq_pos = arg.index('=')
                key = arg[2:eq_pos]
                value = arg[eq_pos+1:]
                override_params[key] = value
            else:
                # 处理 --key value 格式（参数名和值分开）
                # 或者处理被空格拆分的 --参数 1=值 这种情况
                if i + 1 < len(args):
                    next_arg = args[i + 1]
                    if '=' in next_arg and not next_arg.startswith('--'):
                        # 下一个参数是 key=value 格式，说明当前参数名被空格拆分了
                        eq_pos = next_arg.index('=')
                        # 合并参数名时加回空格：--参数 + 1=值 -> 参数 1
                        key = arg[2:] + ' ' + next_arg[:eq_pos]
                        value = next_arg[eq_pos+1:]
                        override_params[key] = value
                        i += 1  # 跳过下一个参数
                    elif not next_arg.startswith('--'):
                        # 简单的 --key value 格式
                        override_params[arg[2:]] = next_arg
                        i += 1
        i += 1
    
    if command == 'init':
        init_config()
    elif command == 'config':
        show_config()
    elif command == 'run':
        run_task(override_params, dry_run)
    elif command == 'test':
        run_task({}, True)
    elif command in ('help', '-h', '--help'):
        show_help()
    else:
        print(f"未知命令：{command}\n")
        show_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
