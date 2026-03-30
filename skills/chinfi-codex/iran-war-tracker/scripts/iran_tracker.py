#!/usr/bin/env python3
"""Thin CLI entrypoint for iran-war-tracker."""

from __future__ import annotations

import argparse
import io
import os
import sys
from datetime import datetime

import requests

from ai_client import call_ai, has_model_config
from cls_feed import collect_filtered_telegraph
from config import AI_TIMEOUT, DEFAULT_LOOKBACK_HOURS, DEFAULT_MAX_RESULTS
from framework_loader import load_framework
from market_data import collect_assets
from news_search import collect_news
from prompt_builder import build_fallback_markdown, build_report_prompt
from report_writer import build_json_payload, write_json, write_markdown
from schemas import ReportContext


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Iran conflict tracking report.")
    parser.add_argument("--output", help="Optional path to write the Markdown report.")
    parser.add_argument("--json-output", help="Optional path to write the raw JSON payload.")
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS, help="Max results per topic.")
    parser.add_argument("--hours", type=int, default=DEFAULT_LOOKBACK_HOURS, help="Lookback window in hours. Default: 18.")
    parser.add_argument("--prefer-model-search", action="store_true", help="Prefer model-based search when available.")
    parser.add_argument("--force-tavily", action="store_true", help="Disable model-based search and use Tavily first.")
    return parser.parse_args()


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "iran-war-tracker/2.0"})
    return session


def collect_context(max_results: int, lookback_hours: int = DEFAULT_LOOKBACK_HOURS, prefer_model_search: bool = True) -> ReportContext:
    session = get_session()
    framework = load_framework(session)
    tavily_api_key = os.getenv("TAVILY_API_KEY", "").strip()
    use_model_search = prefer_model_search and has_model_config()
    news, news_stats, providers = collect_news(
        session=session,
        max_results=max_results,
        lookback_hours=lookback_hours,
        prefer_model_search=use_model_search,
        tavily_api_key=tavily_api_key,
    )
    telegraph_items, telegraph_counts = collect_filtered_telegraph(session, lookback_hours=lookback_hours)
    assets = collect_assets(session)
    provider_values = list(dict.fromkeys(providers.values()))
    search_method = provider_values[0] if len(provider_values) == 1 else "mixed"
    meta = {
        "lookback_hours": lookback_hours,
        "search_method": search_method,
        "providers": providers,
        "framework_source": framework.get("source", ""),
        "framework_error": framework.get("error", ""),
        "counts": {
            "news_topics": len(news),
            "news_results": sum(len(bundle.results) for bundle in news.values()),
            **telegraph_counts,
            "assets": len(assets),
        },
        "news_results_in_window": news_stats["news_results_in_window"],
        "news_filtered_in_window": news_stats["news_results_in_window"],
        "news_missing_timestamp": news_stats["news_missing_timestamp"],
        "telegraph_items_in_window": telegraph_counts["telegraph_items_in_window"],
        "telegraph_filtered_in_window": telegraph_counts["telegraph_items_in_window"],
        "telegraph_total_before_window": telegraph_counts["telegraph_total_before_window"],
        "fallbacks": {
            "framework_local_fallback": framework.get("source") == "local",
            "report_without_model": not has_model_config(),
        },
    }
    return ReportContext(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        framework=framework,
        news=news,
        telegraph=telegraph_items,
        assets=assets,
        meta=meta,
    )


def generate_report(context: ReportContext) -> str:
    prompt = build_report_prompt(context)
    if has_model_config():
        markdown = call_ai(prompt, timeout=AI_TIMEOUT).strip()
        if markdown:
            return markdown + ("\n" if not markdown.endswith("\n") else "")
    return build_fallback_markdown(context)


def main() -> int:
    args = parse_args()
    prefer_model_search = args.prefer_model_search or not args.force_tavily
    context = collect_context(
        max_results=args.max_results,
        lookback_hours=args.hours,
        prefer_model_search=prefer_model_search,
    )
    markdown = generate_report(context)
    if args.output:
        write_markdown(args.output, markdown)
    else:
        print(markdown)
    if args.json_output:
        write_json(args.json_output, build_json_payload(context, report_markdown=markdown))
    return 0


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
