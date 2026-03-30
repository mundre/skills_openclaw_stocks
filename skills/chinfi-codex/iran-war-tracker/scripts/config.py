#!/usr/bin/env python3
"""Runtime configuration for iran-war-tracker."""

from __future__ import annotations

import os
from pathlib import Path


DEFAULT_TIMEOUT = 20
DEFAULT_MAX_RESULTS = 5
DEFAULT_LOOKBACK_HOURS = 18
FRAMEWORK_REMOTE_TIMEOUT = 20
FRAMEWORK_MAX_CHARS = 4000
AI_TIMEOUT = 120

TAVILY_URL = "https://api.tavily.com/search"
DDG_LITE_URL = "https://lite.duckduckgo.com/lite/"
FRAMEWORK_GIST_URL = (
    "https://gist.githubusercontent.com/chinfi-codex/"
    "b311c4c284c8aa6dae9c833a146a1840/raw/"
    "%E4%BC%8A%E6%9C%97%E5%B1%80%E5%8A%BF%E5%85%B3%E9%94%AE"
    "%E5%8F%98%E9%87%8F%E4%B8%8E%E7%BB%8F%E6%B5%8E%E5%BD%B1%E5%93%8D"
    "%E5%88%86%E6%9E%90%E6%A1%86%E6%9E%B6.md"
)

FRAMEWORK_CANDIDATES = [
    "伊朗局势关键变量与经济影响分析框架.md",
]

NEWS_QUERIES = {
    "war_updates": "Iran Israel United States war situation latest developments",
    "hormuz": "Iran Strait of Hormuz closure transit tanker ship attack latest",
    "oil_supply": "Iran oil production exports sanctions supply latest",
    "gas_supply": "Iran natural gas LNG exports infrastructure latest",
    "leaders": "Iran Israel United States leader diplomat military statement latest",
}

RISK_ASSETS = {
    "BTC": "btcusd",
    "黄金": "xauusd",
    "原油(WTI)": "cl.f",
    "天然气": "ng.f",
    "纳指期货": "nq.f",
}

COINGECKO_BTC_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
)

CLS_COLUMNS = {
    "title": "标题",
    "content": "内容",
    "level": "等级",
    "tags": "标签",
    "time": "发布时间",
    "date": "发布日期",
}

CLS_NOISE_KEYWORDS = [
    "market wrap",
    "premarket",
    "stocks to watch",
    "stock market",
    "app store",
    "隔夜全球要闻",
    "你需要知道的隔夜全球要闻",
    "全球要闻",
    "盘前要闻",
    "新闻精选",
    "午间新闻精选",
    "股市",
]

TOPIC_HINTS = [
    "iran",
    "iranian",
    "tehran",
    "hormuz",
    "strait of hormuz",
    "伊朗",
    "德黑兰",
    "霍尔木兹",
    "波斯湾",
    "布什尔",
    "克尔曼沙阿",
]

CLS_CONTEXT_HINTS = [
    "中东",
    "中东局势",
    "中东冲突",
    "美以",
    "美国",
    "以色列",
    "以军",
    "胡塞",
    "黎巴嫩",
    "也门",
    "伊拉克",
    "沙特",
    "空袭",
    "导弹",
    "航母",
    "核设施",
    "停火",
]

CLS_TOPIC_TAG_HINTS = [
    "中东冲突",
]

OPENCLAW_SEARCH_URL = os.getenv("OPENCLAW_SEARCH_URL", "").strip()
OPENCLAW_API_KEY = os.getenv("OPENCLAW_API_KEY", "").strip()


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent
