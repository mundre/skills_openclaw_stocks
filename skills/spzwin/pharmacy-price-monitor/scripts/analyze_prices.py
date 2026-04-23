#!/usr/bin/env python3
"""
价格合规性检查脚本
识别低于标准价的违规商品
"""

import json
import argparse
from typing import List, Dict, Any


def analyze_prices(data: List[Dict[str, Any]], standard_price: float) -> List[Dict[str, Any]]:
    """
    分析商品价格，识别违规商品

    Args:
        data: 商品数据列表，每个商品包含 platform, shop, title, price, url
        standard_price: 标准价格

    Returns:
        违规商品列表
    """
    violations = []

    for item in data:
        try:
            price = float(item.get('price', 0))
            if price < standard_price:
                violations.append({
                    'platform': item.get('platform', ''),
                    'shop': item.get('shop', ''),
                    'title': item.get('title', ''),
                    'actual_price': price,
                    'standard_price': standard_price,
                    'diff': round(price - standard_price, 2),
                    'url': item.get('url', '')
                })
        except (ValueError, TypeError):
            continue

    return violations


def load_data(file_path: str) -> List[Dict[str, Any]]:
    """加载 JSON 数据文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data: List[Dict[str, Any]], file_path: str):
    """保存 JSON 数据文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='价格合规性检查')
    parser.add_argument('--data', required=True, help='原始数据文件 (JSON)')
    parser.add_argument('--price', type=float, required=True, help='标准价格')
    parser.add_argument('--output', required=True, help='输出文件 (JSON)')

    args = parser.parse_args()

    # 加载数据
    data = load_data(args.data)

    # 分析价格
    violations = analyze_prices(data, args.price)

    # 保存结果
    save_data(violations, args.output)

    print(f"✅ 分析完成")
    print(f"📊 总商品数: {len(data)}")
    print(f"⚠️ 违规商品数: {len(violations)}")
    print(f"💾 结果已保存到: {args.output}")


if __name__ == '__main__':
    main()
