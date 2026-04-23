#!/usr/bin/env python3
"""
Markdown 报告生成脚本
汇总分析结果并生成结构化报告
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter, defaultdict


def load_data(file_path: str) -> List[Dict[str, Any]]:
    """加载 JSON 数据文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_summary(violations: List[Dict], unauthorized: List[Dict],
                     all_data: List[Dict]) -> Dict[str, Any]:
    """生成汇总统计数据"""
    # 平台分布
    violation_by_platform = Counter([v['platform'] for v in violations])
    unauthorized_by_platform = Counter([u['platform'] for u in unauthorized])

    # 总商品数
    total_by_platform = Counter([d['platform'] for d in all_data])

    return {
        'total_violations': len(violations),
        'total_unauthorized': len(unauthorized),
        'total_products': len(all_data),
        'violation_by_platform': dict(violation_by_platform),
        'unauthorized_by_platform': dict(unauthorized_by_platform),
        'total_by_platform': dict(total_by_platform),
    }


def generate_markdown(summary: Dict, violations: List[Dict], unauthorized: List[Dict],
                      drug_name: str, spec: str, standard_price: float, platforms: List[str]) -> str:
    """生成 Markdown 报告"""

    md = f"""# 药品电商价格监控报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 一、目标与结论

### 调研目标
- **药品名称**: {drug_name}
- **规格**: {spec or '未指定'}
- **标准价格**: {standard_price} 元
- **监控平台**: {', '.join(platforms)}

### 核心结论
- ✅ 低价违规店铺：**{summary['total_violations']} 家**
- 📍 平台分布：{', '.join([f'{k} {v} 家' for k, v in summary['violation_by_platform'].items()]) or '无'}
- ⚠️ 疑似非授权商品：**{summary['total_unauthorized']} 件**

---

## 二、总体情况

| 平台   | 商品数量 | 违规数量 | 非授权数量 |
|--------|----------|----------|------------|
"""

    # 平台汇总表
    all_platforms = set(summary['total_by_platform'].keys()) | set(platforms)
    for platform in sorted(all_platforms):
        total = summary['total_by_platform'].get(platform, 0)
        violation = summary['violation_by_platform'].get(platform, 0)
        unauthorized = summary['unauthorized_by_platform'].get(platform, 0)
        md += f"| {platform}   | {total}        | {violation}        | {unauthorized}          |\n"

    md += f"| **总计** | **{summary['total_products']}**  | **{summary['total_violations']}**    | **{summary['total_unauthorized']}**      |\n"

    md += "\n---\n\n"

    # 问题分析
    md += "## 三、问题分析\n\n"

    # 价格违规情况
    md += "### 价格违规情况\n\n"
    if summary['total_violations'] > 0:
        violation_rate = round(summary['total_violations'] / summary['total_products'] * 100, 1)
        md += f"- 违规率：**{violation_rate}%**（{summary['total_violations']}/{summary['total_products']}）\n"
        md += f"- 主要平台：{', '.join([f'{k}（{v} 家）' for k, v in summary['violation_by_platform'].items()])}\n"
    else:
        md += "- ✅ 无价格违规商品\n"

    md += "\n"

    # 非授权商品情况
    md += "### 非授权商品\n\n"
    if summary['total_unauthorized'] > 0:
        md += f"- 疑似非授权商品：**{summary['total_unauthorized']} 件**\n"
        md += f"- 主要平台：{', '.join([f'{k}（{v} 件）' for k, v in summary['unauthorized_by_platform'].items()])}\n"
    else:
        md += "- ✅ 无疑似非授权商品\n"

    md += "\n---\n\n"

    # 详细数据 - 违规商品清单
    if violations:
        md += "## 四、详细数据\n\n"

        md += "### 违规商品清单\n\n"
        md += "| 平台   | 店铺名称 | 商品名称 | 实际售价 | 标准价格 | 差价 | 链接 |\n"
        md += "|--------|----------|----------|----------|----------|------|------|\n"

        for v in violations:
            md += f"| {v['platform']}   | {v['shop']} | {v['title']} | {v['actual_price']} | {v['standard_price']} | {v['diff']} | [{v['url']}]({v['url']}) |\n"

        md += "\n---\n\n"

    # 非授权商品清单
    if unauthorized:
        md += "### 非授权商品清单\n\n"
        md += "| 平台   | 店铺名称 | 商品标题 | 判定依据 | 链接 |\n"
        md += "|--------|----------|----------|----------|------|\n"

        for u in unauthorized:
            md += f"| {u['platform']}   | {u['shop']} | {u['title']} | {u['reason']} | [{u['url']}]({u['url']}) |\n"

        md += "\n---\n\n"

    md += "---\n\n"
    md += "*本报告由 OpenClaw 药品电商价格监控系统自动生成*\n"

    return md


def save_report(markdown: str, file_path: str):
    """保存 Markdown 报告"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown)


def main():
    parser = argparse.ArgumentParser(description='生成 Markdown 报告')
    parser.add_argument('--violations', help='违规商品数据文件 (JSON)')
    parser.add_argument('--unauthorized', help='非授权商品数据文件 (JSON)')
    parser.add_argument('--all-data', help='原始商品数据文件 (JSON)')
    parser.add_argument('--output', required=True, help='输出报告文件 (Markdown)')
    parser.add_argument('--drug-name', default='未知药品', help='药品名称')
    parser.add_argument('--spec', default='', help='药品规格')
    parser.add_argument('--price', type=float, required=True, help='标准价格')
    parser.add_argument('--platforms', nargs='+', default=['京东', '淘宝', '拼多多'],
                        help='监控平台列表')

    args = parser.parse_args()

    # 加载数据
    violations = load_data(args.violations) if args.violations else []
    unauthorized = load_data(args.unauthorized) if args.unauthorized else []
    all_data = load_data(args.all_data) if args.all_data else []

    # 生成汇总统计
    summary = generate_summary(violations, unauthorized, all_data)

    # 生成 Markdown 报告
    markdown = generate_markdown(summary, violations, unauthorized,
                                  args.drug_name, args.spec, args.price, args.platforms)

    # 保存报告
    save_report(markdown, args.output)

    print(f"✅ 报告生成完成")
    print(f"📊 违规商品数: {summary['total_violations']}")
    print(f"⚠️ 非授权商品数: {summary['total_unauthorized']}")
    print(f"💾 报告已保存到: {args.output}")


if __name__ == '__main__':
    main()
