#!/usr/bin/env python3
"""
睡眠脑波 API - Python 调用示例
模拟微信小程序调用

安装依赖：pip install requests
"""

import requests
import json
import sys

# API 基础地址（修改为你的电脑局域网IP，局域网内其他设备才能访问）
BASE_URL = "http://localhost:3092"


def health_check():
    """1. 健康检查"""
    resp = requests.get(f"{BASE_URL}/health")
    print("=== 健康检查 ===")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    print()


def list_audios(scene=None, severity=None, page=1):
    """2. 获取音频列表（可选过滤）"""
    params = {"page": page, "pageSize": 20}
    if scene:
        params["scene"] = scene
    if severity:
        params["severity"] = severity

    resp = requests.get(f"{BASE_URL}/api/audio/list", params=params)
    data = resp.json()
    print(f"=== 音频列表 (共 {data['data']['total']} 个) ===")
    for item in data["data"]["items"]:
        print(f"  [{item['audioId']}] {item['sleepSubtype']} | {item['useScene']} | {item['duration']}分钟 | {item['severity']}")
        print(f"    streamUrl: {item['streamUrl']}")
    print()
    return data["data"]["items"]


def match_audio(subtype, severity=None, duration=None, user_id=None):
    """3. 智能匹配音频"""
    params = {"subtype": subtype}
    if severity:
        params["severity"] = severity
    if duration:
        params["duration"] = duration
    if user_id:
        params["userId"] = user_id

    resp = requests.get(f"{BASE_URL}/api/audio/match", params=params)
    result = resp.json()

    if result["data"]:
        audio = result["data"]
        print("=== 智能匹配结果 ===")
        print(f"  睡眠类型: {audio['sleepSubtype']} ({audio['sleepSubtypeCode']})")
        print(f"  场景: {audio['useScene']} | 时长: {audio['duration']}分钟 | 程度: {audio['severity']}")
        print(f"  文件名: {audio['filename']}")
        print(f"  本地路径: {audio['file_path']}")
        print(f"  流媒体地址: {audio['streamUrl']}")
        print()
        return audio
    else:
        print(f"未找到匹配的音频: {result['message']}")
        return None


def get_stream_url(audio_id):
    """4. 获取指定音频的流媒体地址"""
    resp = requests.get(f"{BASE_URL}/api/audio/{audio_id}/url")
    result = resp.json()
    print("=== 音频地址信息 ===")
    if result["data"]:
        d = result["data"]
        print(f"  音频ID: {d['audioId']}")
        print(f"  本地路径: {d['localPath']}")
        print(f"  流媒体地址: {d['streamUrl']}")
        print(f"  时长: {d['duration']}分钟")
        print(f"  类型: {d['sleepSubtype']}")
    else:
        print(f"  错误: {result['message']}")
    print()


def update_profile(user_id, disorder_subtype, severity=None, age_group=None, gender=None):
    """5. 更新用户画像"""
    payload = {"userId": user_id, "disorderSubtype": disorder_subtype}
    if severity:
        payload["severity"] = severity
    if age_group:
        payload["ageGroup"] = age_group
    if gender:
        payload["gender"] = gender

    resp = requests.post(f"{BASE_URL}/api/profile", json=payload)
    print("=== 用户画像更新 ===")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    print()


def get_profile(user_id):
    """6. 获取用户画像"""
    resp = requests.get(f"{BASE_URL}/api/profile/{user_id}")
    print("=== 用户画像查询 ===")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    print()


def get_recommend(user_id, scene=None):
    """7. 智能推荐（根据用户画像）"""
    params = {}
    if scene:
        params["scene"] = scene

    resp = requests.get(f"{BASE_URL}/api/recommend/{user_id}", params=params)
    result = resp.json()
    print("=== 智能推荐 ===")
    if result["data"]["profile"]:
        print(f"  用户画像: {result['data']['profile']['disorderSubtype']} | {result['data']['profile']['severity']}")
    else:
        print(f"  {result['message']}")
    if result["data"]["audio"]:
        audio = result["data"]["audio"]
        print(f"  推荐音频: {audio['sleepSubtype']} | {audio['useScene']} | {audio['duration']}分钟")
        print(f"  流媒体地址: {audio['streamUrl']}")
    print()


def download_audio(audio_id, save_path=None):
    """8. 下载音频到本地文件"""
    stream_url = f"{BASE_URL}/audio-stream/{audio_id}"
    print(f"=== 正在下载音频: {audio_id} ===")
    print(f"  流媒体地址: {stream_url}")

    resp = requests.get(stream_url, stream=True)
    if resp.status_code != 200:
        print(f"  下载失败: HTTP {resp.status_code}")
        return

    if save_path is None:
        save_path = f"./{audio_id}.mp3"

    total = int(resp.headers.get("Content-Length", 0))
    downloaded = 0
    chunk_size = 8192

    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = downloaded * 100 // total
                    print(f"\r  下载进度: {pct}% ({downloaded}/{total} bytes)", end="", flush=True)

    print(f"\n  下载完成: {save_path}")
    print()


def main():
    print("=" * 50)
    print("睡眠脑波 API - Python 模拟小程序调用")
    print(f"API 地址: {BASE_URL}")
    print("=" * 50)
    print()

    # 1. 健康检查
    health_check()

    # 2. 列出睡前音频
    list_audios(scene="睡前")

    # 3. 匹配入睡困难音频
    match_audio("sleep_onset", severity="中度")

    # 4. 获取深睡不足流媒体地址
    get_stream_url("bw_deep_sleep_pre_30min_mild_delta_v1")

    # 5. 更新用户画像
    update_profile("user_001", "deep_sleep", severity="轻度", age_group="YOUNG_ADULT", gender="MALE")

    # 6. 查询用户画像
    get_profile("user_001")

    # 7. 智能推荐
    get_recommend("user_001", scene="睡前")

    # 8. 下载音频（可选，取消注释即可使用）
    # download_audio("bw_deep_sleep_pre_30min_mild_delta_v1")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"连接失败，请确认 API 服务已启动: {BASE_URL}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
