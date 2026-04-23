#!/usr/bin/env python3
"""
非授权版本识别脚本
基于关键词匹配识别非授权商品（海外版、港版等）
"""

import json
import argparse
from typing import List, Dict, Any


# 违规关键词列表
VIOLATION_KEYWORDS = [
    '海外版',
    '港版',
    '美版',
    '欧版',
    '代购',
    '进口',
    '跨境',
    '原装进口',
    '直邮',
    '免税',
    '保税仓',
]


def detect_unauthorized(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    检测非授权版本商品

    Args:
        data: 商品数据列表

    Returns:
        非授权商品列表
    """
    unauthorized = []

    for item in data:
        title = item.get('title', '').lower()

        # 检查是否命中违规关键词
        for keyword in VIOLATION_KEYWORDS:
            if keyword.lower() in title:
                unauthorized.append({
                    'platform': item.get('platform', ''),
                    'shop': item.get('shop', ''),
                    'title': item.get('title', ''),
                    'reason': f'命中关键词: {keyword}',
                    'url': item.get('url', '')
                })
                break

    return unauthorized


def load_data(file_path: str) -> List[Dict[str, Any]]:
    """加载 JSON 数据文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data: List[Dict[str, Any]], file_path: str):
    """保存 JSON 数据文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='非授权版本识别')
    parser.add_argument('--data', required=True, help='原始数据文件 (JSON)')
    parser.add_argument('--output', required=True, help='输出文件 (JSON)')

    args = parser.parse_args()

    # 加载数据
    data = load_data(args.data)

    # 检测非授权商品
    unauthorized = detect_unauthorized(data)

    # 保存结果
    save_data(unauthorized, args.output)

    print(f"✅ 检测完成")
    print(f"📊 总商品数: {len(data)}")
    print(f"⚠️ 疑似非授权商品数: {len(unauthorized)}")
    print(f"💾 结果已保存到: {args.output}")


if __name__ == '__main__':
    main()
