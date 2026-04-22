#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山引擎豆包语音播客生成器
基于 PodcastTTS API，输入主题文本自动生成双人对话播客音频。
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path

import websockets

# 加载 protocols
sys.path.insert(0, str(Path(__file__).parent))
from protocols import (
    EventType,
    MsgType,
    finish_connection,
    finish_session,
    receive_message,
    start_connection,
    start_session,
    wait_for_event,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("PodcastTTS")

ENDPOINT = "wss://openspeech.bytedance.com/api/v3/sami/podcasttts"
DEFAULT_RESOURCE_ID = "volc.service_type.10050"
DEFAULT_ENCODING = "mp3"
DEFAULT_SAMPLE_RATE = 24000


class PodcastGenerator:
    """火山引擎播客语音合成客户端"""

    def __init__(
        self,
        appid: str,
        access_token: str,
        app_key: str = "aGjiRDfUWi",
        resource_id: str = DEFAULT_RESOURCE_ID,
        endpoint: str = ENDPOINT,
    ):
        self.appid = appid
        self.access_token = access_token
        self.app_key = app_key
        self.resource_id = resource_id
        self.endpoint = endpoint

    async def generate(
        self,
        text: str,
        output_dir: str = "output",
        encoding: str = DEFAULT_ENCODING,
        use_head_music: bool = True,
        use_tail_music: bool = False,
        only_nlp_text: bool = False,
        return_audio_url: bool = False,
        speaker_info: dict = None,
        speech_rate: int = 0,
        skip_round_audio_save: bool = False,
    ) -> dict:
        """
        生成播客音频

        Args:
            text: 输入主题文本
            output_dir: 输出目录
            encoding: 音频格式 mp3 / wav / pcm
            use_head_music: 是否加片头音乐
            use_tail_music: 是否加片尾音乐
            only_nlp_text: 只返回文本不生成音频
            return_audio_url: 返回音频 URL 而非流式下发
            speaker_info: 说话人配置，如 {"random_order": false}
            speech_rate: 语速，默认 0
            skip_round_audio_save: 跳过分段保存

        Returns:
            dict: 包含 output_files, duration, texts, usage 等信息
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        headers = {
            "X-Api-App-Id": self.appid,
            "X-Api-App-Key": self.app_key,
            "X-Api-Access-Key": self.access_token,
            "X-Api-Resource-Id": self.resource_id,
            "X-Api-Connect-Id": str(uuid.uuid4()),
        }

        req_params = {
            "input_id": f"podcast_{int(time.time())}",
            "input_text": text,
            "nlp_texts": None,
            "prompt_text": "",
            "action": 0,
            "use_head_music": use_head_music,
            "use_tail_music": use_tail_music,
            "input_info": {
                "input_url": "",
                "return_audio_url": return_audio_url,
                "only_nlp_text": only_nlp_text,
            },
            "speaker_info": speaker_info or {"random_order": False},
            "audio_config": {
                "format": encoding,
                "sample_rate": DEFAULT_SAMPLE_RATE,
                "speech_rate": speech_rate,
            }
        }

        is_podcast_round_end = True
        audio_received = False
        last_round_id = -1
        task_id = ""
        websocket = None
        retry_num = 5
        podcast_audio = bytearray()
        audio = bytearray()
        voice = ""
        current_round = 0
        podcast_texts = []
        output_files = []
        total_duration = 0.0
        usage_total = {"input_text_tokens": 0, "output_audio_tokens": 0, "total_tokens": 0}

        try:
            while retry_num > 0:
                logger.info(f"连接服务器: {self.endpoint}")
                websocket = await websockets.connect(
                    self.endpoint,
                    additional_headers=headers
                )
                logger.info("WebSocket 连接成功")

                if not is_podcast_round_end:
                    req_params["retry_info"] = {
                        "retry_task_id": task_id,
                        "last_finished_round_id": last_round_id
                    }

                await start_connection(websocket)
                await wait_for_event(websocket, MsgType.FullServerResponse, EventType.ConnectionStarted)

                session_id = str(uuid.uuid4())
                if not task_id:
                    task_id = session_id

                await start_session(websocket, json.dumps(req_params).encode(), session_id)
                await wait_for_event(websocket, MsgType.FullServerResponse, EventType.SessionStarted)
                await finish_session(websocket, session_id)

                while True:
                    msg = await receive_message(websocket)

                    if msg.type == MsgType.AudioOnlyServer and msg.event == EventType.PodcastRoundResponse:
                        if not audio_received and audio:
                            audio_received = True
                        audio.extend(msg.payload)
                        logger.debug(f"音频数据接收: {len(msg.payload)} 字节")

                    elif msg.type == MsgType.Error:
                        raise RuntimeError(f"服务器错误: {msg.payload.decode()}")

                    elif msg.type == MsgType.FullServerResponse:
                        if msg.event == EventType.PodcastRoundStart:
                            data = json.loads(msg.payload.decode())
                            if data.get("text"):
                                filtered = {"text": data.get("text"), "speaker": data.get("speaker")}
                                podcast_texts.append(filtered)
                            voice = data.get("speaker", "")
                            current_round = data.get("round_id", -1)
                            if current_round == -1:
                                voice = "head_music"
                            if current_round == 9999:
                                voice = "tail_music"
                            is_podcast_round_end = False
                            logger.info(f"轮次开始 [{current_round}] {voice}: {data.get('text', '')[:50]}...")

                        elif msg.event == EventType.PodcastRoundEnd:
                            data = json.loads(msg.payload.decode())
                            if data.get("is_error"):
                                logger.error(f"轮次错误: {data}")
                                break
                            is_podcast_round_end = True
                            last_round_id = current_round
                            duration = data.get("audio_duration", 0)
                            total_duration += duration
                            if audio:
                                filename = f"{voice}_{current_round}.{encoding}"
                                filepath = output_path / filename
                                if not skip_round_audio_save:
                                    with open(filepath, "wb") as f:
                                        f.write(audio)
                                    output_files.append(str(filepath))
                                    logger.info(f"分段音频已保存: {filepath} ({duration:.2f}s)")
                                podcast_audio.extend(audio)
                                audio.clear()

                        elif msg.event == EventType.PodcastEnd:
                            data = json.loads(msg.payload.decode())
                            logger.info(f"播客全部生成完毕")

                        elif msg.event == EventType.UsageResponse:
                            data = json.loads(msg.payload.decode())
                            usage = data.get("usage", {})
                            for k in usage_total:
                                usage_total[k] += usage.get(k, 0)

                    if msg.event == EventType.SessionFinished:
                        break

                if not audio_received and not only_nlp_text:
                    raise RuntimeError("未收到任何音频数据")

                await finish_connection(websocket)
                await wait_for_event(websocket, MsgType.FullServerResponse, EventType.ConnectionFinished)

                if is_podcast_round_end:
                    final_files = []
                    if podcast_audio and not only_nlp_text:
                        final_name = f"podcast_final_{int(time.time())}.{encoding}"
                        final_path = output_path / final_name
                        with open(final_path, "wb") as f:
                            f.write(podcast_audio)
                        final_files.append(str(final_path))
                        logger.info(f"✅ 最终完整音频已保存: {final_path}")

                    if only_nlp_text and podcast_texts:
                        text_path = output_path / "podcast_texts.json"
                        with open(text_path, "w", encoding="utf-8") as f:
                            json.dump(podcast_texts, f, ensure_ascii=False, indent=2)
                        final_files.append(str(text_path))
                        logger.info(f"文本已保存: {text_path}")

                    return {
                        "success": True,
                        "output_dir": str(output_path.absolute()),
                        "segment_files": output_files,
                        "final_files": final_files,
                        "duration": round(total_duration, 2),
                        "texts": podcast_texts,
                        "usage": usage_total,
                    }
                else:
                    logger.warning(f"播客未完成，从轮次 {last_round_id} 继续重试...")
                    retry_num -= 1
                    await asyncio.sleep(1)
                    if websocket:
                        await websocket.close()
        finally:
            if websocket:
                await websocket.close()

        return {"success": False, "error": "重试次数耗尽，播客生成失败"}


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="火山引擎豆包语音播客生成器")
    parser.add_argument("text", help="输入主题文本")
    parser.add_argument("-o", "--output", default="output", help="输出目录 (默认: output)")
    parser.add_argument("-f", "--format", default="mp3", choices=["mp3", "wav", "pcm"], help="音频格式")
    parser.add_argument("--no-head-music", action="store_true", help="不加片头音乐")
    parser.add_argument("--tail-music", action="store_true", help="加片尾音乐")
    parser.add_argument("--only-text", action="store_true", help="只生成文本不生成音频")
    parser.add_argument("--appid", default=os.getenv("VOLC_APPID"), help="App ID (或环境变量 VOLC_APPID)")
    parser.add_argument("--token", default=os.getenv("VOLC_ACCESS_TOKEN"), help="Access Token (或环境变量 VOLC_ACCESS_TOKEN)")
    parser.add_argument("--app-key", default=os.getenv("VOLC_APP_KEY", "aGjiRDfUWi"), help="App Key")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细日志")

    args = parser.parse_args()

    if not args.appid or not args.token:
        print("错误: 必须提供 --appid 和 --token，或通过环境变量 VOLC_APPID / VOLC_ACCESS_TOKEN 设置")
        sys.exit(1)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    gen = PodcastGenerator(
        appid=args.appid,
        access_token=args.token,
        app_key=args.app_key,
    )

    result = await gen.generate(
        text=args.text,
        output_dir=args.output,
        encoding=args.format,
        use_head_music=not args.no_head_music,
        use_tail_music=args.tail_music,
        only_nlp_text=args.only_text,
    )

    if result["success"]:
        print(f"\n✅ 播客生成成功！")
        print(f"   时长: {result['duration']} 秒")
        print(f"   输出目录: {result['output_dir']}")
        print(f"   最终文件: {', '.join(result['final_files'])}")
        print(f"   Token 消耗: {result['usage']}")
    else:
        print(f"\n❌ 生成失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
