#!/usr/bin/env python3
"""
Vidu参考生视频脚本
调用Vidu reference2video接口生成视频

授权方式: ApiKey
"""

import os
import sys
import argparse
import json
import requests


def generate_video(
    images,
    prompt,
    videos=None,
    model="viduq3",
    duration=5,
    bgm=False,
    seed=0,
    aspect_ratio="16:9",
    resolution="720p",
    movement_amplitude="auto",
    off_peak=False,
    watermark=False,
    audio=True
):
    """
    生成视频（支持 viduq3 和 viduq2）

    Args:
        images (list): 参考图片列表，支持Base64或URL
        prompt (str): 分镜提示词
        videos (list, optional): 参考视频列表
        model (str): 模型名称，可选：viduq3, viduq2
        duration (int): 视频时长（秒），viduq3可选3-16，q2系列可选1-10
        bgm (bool): 是否添加背景音乐，默认False（q3不生效）
        seed (int): 随机种子，默认0
        aspect_ratio (str): 比例，默认16:9
        resolution (str): 分辨率，默认720p
        movement_amplitude (str): 运动幅度，默认auto（q2/q3不生效）
        off_peak (bool): 是否使用错峰模式，默认False
        watermark (bool): 是否添加水印，默认False
        audio (bool): 是否生成音频（仅q3生效），默认True

    Returns:
        dict: 包含task_id和任务状态的响应数据
    """
    
    # 获取凭证
    api_key = os.getenv("VIDU_API_KEY")
    if not api_key:
        raise ValueError("缺少Vidu API凭证配置(VIDU_API_KEY)，请检查环境变量")

    # 构建请求
    url = "https://api.vidu.cn/ent/v2/reference2video"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {api_key}"
    }

    # 基础payload
    payload = {
        "model": model,
        "images": images,
        "prompt": prompt,
        "duration": duration,
        "seed": seed,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "off_peak": off_peak,
        "watermark": watermark
    }

    # 可选参数处理
    if videos:
        payload["videos"] = videos
    
    # q3 特有/不生效参数处理
    if model == "viduq3":
        payload["audio"] = audio
        # q3 不支持 bgm, movement_amplitude
    else:
        # q2 系列参数
        payload["bgm"] = bgm
        # movement_amplitude: q2和q3系列模型不支持该参数，仅保留旧模型兼容或移除
        # 根据最新文档，q2/q3不支持，故不传
        # payload["movement_amplitude"] = movement_amplitude
        # q2 不支持 audio 参数

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
    parser = argparse.ArgumentParser(description="Vidu参考生视频工具")
    parser.add_argument("--images", required=True, help="参考图片列表，JSON格式，支持Base64或URL")
    parser.add_argument("--prompt", required=True, help="文本提示词")
    parser.add_argument("--videos", help="参考视频列表，JSON格式")
    parser.add_argument("--model", default="viduq3", help="模型名称，默认viduq3，可选：viduq3, viduq2")
    parser.add_argument("--duration", type=int, default=5, help="视频时长（秒），默认5")
    parser.add_argument("--bgm", action="store_true", help="是否添加背景音乐（仅q2生效）")
    parser.add_argument("--seed", type=int, default=0, help="随机种子，默认0")
    parser.add_argument("--aspect_ratio", default="16:9", help="比例，默认16:9")
    parser.add_argument("--resolution", default="720p", help="分辨率，默认720p")
    parser.add_argument("--movement_amplitude", default="auto", help="运动幅度，默认auto")
    parser.add_argument("--off_peak", action="store_true", help="是否使用错峰模式")
    parser.add_argument("--watermark", action="store_true", help="是否添加水印")
    parser.add_argument("--no_audio", action="store_true", help="禁用音频生成（仅q3生效）")

    args = parser.parse_args()

    # 处理图片和视频参数
    try:
        images_data = json.loads(args.images)
    except json.JSONDecodeError:
        # 尝试作为单个URL处理
        if args.images.startswith("http"):
            images_data = [args.images]
        else:
            raise ValueError("--images 参数必须是有效的JSON格式或URL")

    videos_data = None
    if args.videos:
        try:
            videos_data = json.loads(args.videos)
        except json.JSONDecodeError:
            if args.videos.startswith("http"):
                videos_data = [args.videos]
            else:
                raise ValueError("--videos 参数必须是有效的JSON格式或URL")

    # 调用API
    try:
        result = generate_video(
            images=images_data,
            prompt=args.prompt,
            videos=videos_data,
            model=args.model,
            duration=args.duration,
            bgm=args.bgm,
            seed=args.seed,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            movement_amplitude=args.movement_amplitude,
            off_peak=args.off_peak,
            watermark=args.watermark,
            audio=not args.no_audio
        )
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
