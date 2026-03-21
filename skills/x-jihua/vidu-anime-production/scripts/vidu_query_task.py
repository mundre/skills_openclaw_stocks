#!/usr/bin/env python3
"""
Vidu查询任务脚本
查询Vidu异步任务的生成结果

授权方式: ApiKey
凭证Key: COZE_VIDU_API_7610322785025425408
"""

import os
import sys
import argparse
import time
import json
import requests


def query_task(task_id):
    """
    查询任务状态和结果

    Args:
        task_id (str): 任务ID

    Returns:
        dict: 包含任务状态和生成物的响应数据
    """
    # 获取凭证
    api_key = os.getenv("VIDU_API_KEY")
    if not api_key:
        skill_id = "7610322785025425408"
        api_key = os.getenv("COZE_VIDU_API_" + skill_id)
        
    if not api_key:
        raise ValueError("缺少Vidu API凭证配置，请检查环境变量 VIDU_API_KEY")

    # 构建请求
    url = f"https://api.vidu.cn/ent/v2/tasks/{task_id}/creations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {api_key}"
    }

    # 发起请求
    try:
        response = requests.get(url, headers=headers, timeout=30)

        # 检查HTTP状态码
        if response.status_code >= 400:
            raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, 响应内容: {response.text}")

        data = response.json()

        # 检查错误码
        if data.get("err_code"):
            raise Exception(f"任务错误: err_code={data.get('err_code')}, state={data.get('state')}")

        return data

    except requests.exceptions.RequestException as e:
        raise Exception(f"API调用失败: {str(e)}")


def wait_for_completion(task_id, max_wait_time=600, poll_interval=5):
    """
    等待任务完成（轮询）

    Args:
        task_id (str): 任务ID
        max_wait_time (int): 最大等待时间（秒），默认600秒（10分钟）
        poll_interval (int): 轮询间隔（秒），默认5秒

    Returns:
        dict: 完成后的任务结果

    Raises:
        Exception: 任务失败或超时
    """
    start_time = time.time()

    while True:
        # 检查是否超时
        elapsed = time.time() - start_time
        if elapsed > max_wait_time:
            raise Exception(f"任务超时：等待时间超过 {max_wait_time} 秒")

        # 查询任务状态
        result = query_task(task_id)
        state = result.get("state")

        print(f"[{int(elapsed)}s] 任务状态: {state}")

        # 检查是否完成
        if state == "success":
            return result
        elif state == "failed":
            raise Exception(f"任务失败: {result}")
        elif state in ["created", "queueing", "processing"]:
            # 继续等待
            time.sleep(poll_interval)
        else:
            raise Exception(f"未知任务状态: {state}")


def main():
    parser = argparse.ArgumentParser(description="Vidu查询任务工具")
    parser.add_argument("--task_id", required=True, help="任务ID")
    parser.add_argument("--wait", action="store_true", help="是否等待任务完成（轮询模式）")
    parser.add_argument("--max_wait_time", type=int, default=600, help="最大等待时间（秒），默认600")
    parser.add_argument("--poll_interval", type=int, default=5, help="轮询间隔（秒），默认5")

    args = parser.parse_args()

    # 执行查询
    if args.wait:
        # 轮询等待完成
        print(f"开始等待任务 {args.task_id} 完成...")
        result = wait_for_completion(
            task_id=args.task_id,
            max_wait_time=args.max_wait_time,
            poll_interval=args.poll_interval
        )
        print("\n任务完成！")
    else:
        # 单次查询
        result = query_task(args.task_id)

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
