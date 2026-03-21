#!/usr/bin/env python3
"""
Vidu生图脚本
调用Vidu reference2image/nano接口生成图片

授权方式: ApiKey
凭证Key: COZE_VIDU_API_7610322785025425408
"""

import os
import sys
import argparse
import json
import requests


def generate_image(prompt, images=None, aspect_ratio="16:9", resolution="1K", model="q2-pro"):
    """
    生成图片

    Args:
        prompt (str): 文本提示词，建议包含风格描述
        images (list, optional): 参考图片列表，支持Base64或URL，最多14张
        aspect_ratio (str): 比例，默认16:9，可选：9:16, 2:3, 3:4, 4:5, 1:1, 5:4, 4:3, 3:2, 16:9, 21:9
        resolution (str): 分辨率，默认1K，q2-pro可选：1K, 2K, 4K
        model (str): 模型版本，默认q2-pro，可选：q2-fast, q2-pro

    Returns:
        dict: 包含task_id和任务状态的响应数据
    """
    # 获取凭证
    api_key = os.getenv("VIDU_API_KEY")
    if not api_key:
        # Fallback to check COZE_VIDU_API_... if VIDU_API_KEY is not set
        skill_id = "7610322785025425408"
        api_key = os.getenv("COZE_VIDU_API_" + skill_id)
        
    if not api_key:
        raise ValueError("缺少Vidu API凭证配置，请设置环境变量 VIDU_API_KEY")

    # 构建请求
    url = "https://api.vidu.cn/ent/v2/reference2image/nano"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {api_key}"
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution
    }

    if images:
        payload["images"] = images

    # 发起请求
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        # 检查HTTP状态码
        if response.status_code >= 400:
            raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, 响应内容: {response.text}")

        data = response.json()

        # 检查任务状态
        if "task_id" not in data:
            raise Exception(f"API返回异常: {data}")

        return data

    except requests.exceptions.RequestException as e:
        raise Exception(f"API调用失败: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Vidu生图工具")
    parser.add_argument("--prompt", required=True, help="文本提示词")
    parser.add_argument("--images", help="参考图片列表，JSON格式，支持Base64或URL")
    parser.add_argument("--aspect_ratio", default="16:9", help="比例，默认16:9")
    parser.add_argument("--resolution", default="1K", help="分辨率，默认1K")
    parser.add_argument("--model", default="q2-pro", help="模型版本，默认q2-pro")

    args = parser.parse_args()

    # 处理图片参数
    images = None
    if args.images:
        try:
            images = json.loads(args.images)
        except json.JSONDecodeError:
            raise ValueError("--images 参数必须是有效的JSON格式")

    # 调用API
    result = generate_image(
        prompt=args.prompt,
        images=images,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        model=args.model
    )

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
