#!/usr/bin/env python3
"""Assemble model prompts from collected context."""

from __future__ import annotations

import json

from config import CLS_COLUMNS
from normalize import normalize_text
from schemas import ReportContext


def build_report_prompt(context: ReportContext) -> str:
    framework = context.framework.get("content", "")
    framework_name = context.framework.get("name", "")
    framework_source = context.framework.get("source", "")
    news_payload = {
        key: {
            "query": bundle.query,
            "provider": bundle.provider,
            "answer": bundle.answer,
            "results": [item.to_dict() for item in bundle.results],
            "error": bundle.error,
        }
        for key, bundle in context.news.items()
    }
    telegraph_payload = context.telegraph
    assets_payload = {key: asset.to_dict() for key, asset in context.assets.items()}

    instructions = [
        "请基于以下上下文直接输出中文 Markdown 报告。",
        "遵守技能文档要求，但不要复述规则本身。",
        "优先使用已给出的事实与证据，不要臆造来源。",
        "如证据不足，直接说明证据不足，再给出谨慎推演。",
        "必须把原油与天然气分开分析。",
        "尽量区分：事实、市场信号、推演。",
        f"当前上下文已按过去 {context.meta.get('lookback_hours', 18)} 小时时窗筛选。",
    ]

    return "\n\n".join(
        [
            "\n".join(instructions),
            f"框架文件: {framework_name} | 来源: {framework_source}",
            "分析框架摘录:\n" + framework,
            "新闻与搜索结果:\n" + json.dumps(news_payload, ensure_ascii=False, indent=2),
            "市场快讯流（CLS + Jin10）:\n" + json.dumps(telegraph_payload, ensure_ascii=False, indent=2),
            "风险资产:\n" + json.dumps(assets_payload, ensure_ascii=False, indent=2),
            "元信息:\n" + json.dumps(context.meta, ensure_ascii=False, indent=2),
        ]
    )


def build_fallback_markdown(context: ReportContext) -> str:
    framework_excerpt = _compact_framework_excerpt(context.framework.get("content", ""))
    search_lines = _build_search_lines(context)
    telegraph_lines = _build_telegraph_lines(context, limit=12)
    asset_lines = _build_asset_lines(context)

    lines = [
        "# 伊朗局势跟踪简报",
        "",
        f"- 生成时间: {context.generated_at}",
        f"- 框架来源: {context.framework.get('source', '')}",
        f"- 搜索方式: {context.meta.get('search_method', '')}",
        f"- 时效窗口: 过去 {context.meta.get('lookback_hours', 18)} 小时",
        f"- 新闻窗口内结果: {context.meta.get('news_results_in_window', 0)}",
        f"- 新闻缺失时间戳: {context.meta.get('news_missing_timestamp', 0)}",
        f"- 电报窗口前总量: {context.meta.get('telegraph_total_before_window', 0)}",
        f"- 电报窗口内数量: {context.meta.get('telegraph_items_in_window', len(context.telegraph))}",
        "",
        "## 分析框架摘录",
    ]
    lines.extend(framework_excerpt)
    lines.extend(["", "## 外部新闻搜索"])
    lines.extend(search_lines)
    lines.extend(["", "## 市场快讯摘录"])
    lines.extend(telegraph_lines)
    lines.extend(["", "## 风险资产"])
    lines.extend(asset_lines)
    return "\n".join(lines).strip() + "\n"


def _compact_framework_excerpt(framework: str, limit: int = 8) -> list[str]:
    lines = [normalize_text(line) for line in framework.splitlines()]
    lines = [line for line in lines if line and line != "---"]
    excerpt = lines[:limit]
    if not excerpt:
        return ["- 未加载到框架内容。"]
    return [f"- {line}" for line in excerpt]


def _build_search_lines(context: ReportContext) -> list[str]:
    lines: list[str] = []
    for topic, bundle in context.news.items():
        if bundle.results:
            lines.append(f"- {topic}: {bundle.provider} 返回 {len(bundle.results)} 条结果。")
            for result in bundle.results[:2]:
                status = "已校验窗口内" if result.timestamp_verified and result.within_lookback else "缺失时间戳"
                summary = compact_text(result.content or result.title, limit=100)
                lines.append(f"  - [{status}] {result.title} | {summary}")
            continue
        if bundle.error:
            lines.append(f"- {topic}: {bundle.provider} 不可用，错误={bundle.error}")
        elif bundle.answer:
            lines.append(f"- {topic}: {normalize_text(bundle.answer)}")
        else:
            lines.append(f"- {topic}: 未获取到有效搜索结果。")
    return lines


def _build_telegraph_lines(context: ReportContext, limit: int) -> list[str]:
    lines: list[str] = []
    for item in context.telegraph[:limit]:
        source = normalize_text(item.get("source_name", "")) or normalize_text(item.get("source", ""))
        title = normalize_text(item.get(CLS_COLUMNS["title"], ""))
        content = normalize_text(item.get(CLS_COLUMNS["content"], ""))
        summary = title or compact_text(content, limit=120)
        if title and content and content != title:
            summary = f"{title} | {compact_text(content, limit=100)}"
        lines.append(f"- {normalize_text(item.get(CLS_COLUMNS['time'], ''))} | {source} | {summary}")
    return lines or ["- 未获取到有效快讯。"]


def _build_asset_lines(context: ReportContext) -> list[str]:
    lines: list[str] = []
    for asset in context.assets.values():
        lines.append(f"- {asset.name}: price={asset.price or 'N/A'} change={asset.change_pct or 'N/A'} source={asset.source}")
    return lines or ["- 未获取到风险资产数据。"]


def compact_text(value: str, limit: int = 120) -> str:
    text = normalize_text(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."
