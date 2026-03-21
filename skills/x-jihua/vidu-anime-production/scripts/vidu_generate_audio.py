#!/usr/bin/env python3
"""
Vidu TTS语音合成脚本
调用Vidu audio-tts接口生成语音

授权方式: ApiKey
凭证Key: COZE_VIDU_API_7610322785025425408
"""

import os
import sys
import argparse
import json
from coze_workload_identity import requests


def generate_audio(
    text,
    voice_id,
    speed=1.0,
    volume=0,
    pitch=0,
    emotion=None,
    pronunciation_dict=None,
    payload=None
):
    """
    生成TTS语音

    Args:
        text (str): 需要合成语音的文本
        voice_id (str): 音色ID
        speed (float): 语速，默认1.0，范围[0.5, 2.0]
        volume (int): 音量，默认0，范围[0, 10]
        pitch (int): 语调，默认0，范围[-12, 12]
        emotion (str, optional): 情绪，可选值: happy, sad, angry, fearful, disgusted, surprised, calm
        pronunciation_dict (list, optional): 多音字发音规则
        payload (str, optional): 透传参数

    Returns:
        dict: 包含task_id、state、file_url的响应数据
    """
    # 获取凭证
    skill_id = "7610322785025425408"
    api_key = os.getenv("COZE_VIDU_API_" + skill_id)
    if not api_key:
        raise ValueError("缺少Vidu API凭证配置，请检查环境变量")

    # 构建请求
    url = "https://api.vidu.cn/ent/v2/audio-tts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {api_key}"
    }

    payload_data = {
        "text": text,
        "voice_setting_voice_id": voice_id,
        "voice_setting_speed": speed,
        "voice_setting_volume": volume,
        "voice_setting_pitch": pitch
    }

    if emotion:
        payload_data["voice_setting_emotion"] = emotion

    if pronunciation_dict:
        payload_data["pronunciation_dict_tone"] = pronunciation_dict

    if payload:
        payload_data["payload"] = payload

    # 发起请求
    try:
        response = requests.post(url, headers=headers, json=payload_data, timeout=60)

        # 检查HTTP状态码
        if response.status_code >= 400:
            raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, 响应内容: {response.text}")

        data = response.json()

        # 检查任务状态
        if data.get("state") == "failed":
            raise Exception(f"TTS生成失败: {data}")

        return data

    except requests.exceptions.RequestException as e:
        raise Exception(f"API调用失败: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Vidu TTS语音合成工具")
    parser.add_argument("--text", required=True, help="需要合成语音的文本")
    parser.add_argument("--voice_id", required=True, help="音色ID")
    parser.add_argument("--speed", type=float, default=1.0, help="语速，默认1.0，范围[0.5, 2.0]")
    parser.add_argument("--volume", type=int, default=0, help="音量，默认0，范围[0, 10]")
    parser.add_argument("--pitch", type=int, default=0, help="语调，默认0，范围[-12, 12]")
    parser.add_argument("--emotion", help="情绪，可选值: happy, sad, angry, fearful, disgusted, surprised, calm")
    parser.add_argument("--pronunciation_dict", help="多音字发音规则，JSON格式")
    parser.add_argument("--payload", help="透传参数")

    args = parser.parse_args()

    # 处理pronunciation_dict参数
    pronunciation_dict = None
    if args.pronunciation_dict:
        try:
            pronunciation_dict = json.loads(args.pronunciation_dict)
        except json.JSONDecodeError:
            raise ValueError("--pronunciation_dict 参数必须是有效的JSON格式")

    # 调用API
    result = generate_audio(
        text=args.text,
        voice_id=args.voice_id,
        speed=args.speed,
        volume=args.volume,
        pitch=args.pitch,
        emotion=args.emotion,
        pronunciation_dict=pronunciation_dict,
        payload=args.payload
    )

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
