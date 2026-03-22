#!/usr/bin/env python3
"""
Iran conflict tracker.

Collects:
- Tavily news search results for fixed intelligence topics
- CLS Telegraph fast news via the bundled crawler method
- Risk asset snapshots from Stooq with CoinGecko BTC fallback

Produces a Chinese report that explicitly uses a remote-first framework file to
analyze war intensity, Hormuz risk, oil and gas supply implications, macro
transmission, and risk asset reactions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests


DEFAULT_TIMEOUT = 20
DEFAULT_MAX_RESULTS = 5
TAVILY_URL = "https://api.tavily.com/search"
FRAMEWORK_MAX_CHARS = 4000
FRAMEWORK_REMOTE_TIMEOUT = 10
FRAMEWORK_GIST_URL = "https://gist.githubusercontent.com/chinfi-codex/b311c4c284c8aa6dae9c833a146a1840/raw/%E4%BC%8A%E6%9C%97%E5%B1%80%E5%8A%BF%E5%85%B3%E9%94%AE%E5%8F%98%E9%87%8F%E4%B8%8E%E7%BB%8F%E6%B5%8E%E5%BD%B1%E5%93%8D%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A.md"

# OpenClaw 环境模型搜索配置
OPENCLAW_SEARCH_URL = os.getenv("OPENCLAW_SEARCH_URL", "")
OPENCLAW_API_KEY = os.getenv("OPENCLAW_API_KEY", "")

# DuckDuckGo Lite 搜索配置（作为 Tavily 的降级）
DDG_LITE_URL = "https://lite.duckduckgo.com/lite/"
DDG_MAX_RETRIES = 2

FRAMEWORK_CANDIDATES = ["伊朗局势关键变量与经济影响分析报告.md"]

TAVILY_QUERIES = {
    "war_updates": "Iran Israel United States war situation latest developments",
    "hormuz": "Iran Strait of Hormuz closure transit ship passage tanker attack latest",
    "oil_supply": "Iran oil production exports supply disruption sanctions latest",
    "gas_supply": "Iran natural gas production exports supply disruption LNG latest",
    "leaders": "Iran United States Israel leaders diplomats military officials statements latest",
}

TAVILY_TOPIC_FILTERS = {
    "war_updates": {"war", "diplomacy"},
    "hormuz": {"war", "economy"},
    "oil_supply": {"economy"},
    "gas_supply": {"economy"},
    "leaders": {"diplomacy"},
}

RISK_ASSETS = {
    "BTC": "btcusd",
    "黄金": "xauusd",
    "原油(WTI)": "cl.f",
    "天然气": "ng.f",
    "纳指期货": "nq.f",
}

IRAN_CORE_KEYWORDS = ["iran", "iranian", "tehran", "islamic republic", "伊朗", "德黑兰"]
FOCUS_GEO_KEYWORDS = ["iran", "iranian", "tehran", "strait of hormuz", "hormuz", "persian gulf", "伊朗", "德黑兰", "霍尔木兹", "波斯湾"]
WAR_TOPIC_KEYWORDS = ["war", "strike", "airstrike", "missile", "drone", "military", "troop", "attack", "conflict", "retaliation", "ground operation", "战争", "空袭", "导弹", "无人机", "军事", "部队", "袭击", "冲突", "报复", "地面行动"]
ECON_TOPIC_KEYWORDS = ["oil", "gas", "lng", "energy", "export", "supply", "production", "sanction", "shipping", "economy", "inflation", "tanker", "石油", "原油", "天然气", "能源", "出口", "供给", "产量", "制裁", "航运", "经济", "通胀", "油轮"]
DIPLO_TOPIC_KEYWORDS = ["president", "prime minister", "foreign minister", "defense minister", "diplomat", "talks", "negotiation", "ceasefire", "statement", "remarks", "united nations", "un ", "总统", "总理", "外长", "防长", "外交", "谈判", "停火", "声明", "表态", "联合国"]
WAR_EXPANSION_KEYWORDS = ["airstrike", "strike", "missile", "drone", "troop movement", "ground operation", "closure", "attack", "空袭", "袭击", "导弹", "无人机", "地面行动", "部队调动", "封锁"]
WAR_EASING_KEYWORDS = ["ceasefire", "negotiation", "talks", "de-escalation", "停火", "谈判", "会谈", "降温"]
US_KEYWORDS = ["united states", "u.s.", "america", "american", "trump", "white house", "美国", "白宫"]
ISRAEL_KEYWORDS = ["israel", "israeli", "idf", "netanyahu", "israeli military", "以色列", "以军"]
IRAN_KEYWORDS = ["iran", "iranian", "tehran", "khamenei", "araghchi", "伊朗", "德黑兰", "哈梅内伊"]
LEADER_KEYWORDS = ["president", "prime minister", "foreign minister", "defense minister", "commander", "trump", "netanyahu", "khamenei", "araghchi", "总统", "总理", "外长", "防长", "指挥官"]
CLS_NOISE_KEYWORDS = ["market wrap", "premarket", "stocks to watch", "stock market", "app store", "盘前要闻", "股市"]

CLS_COL_TITLE = "标题"
CLS_COL_CONTENT = "内容"
CLS_COL_LEVEL = "等级"
CLS_COL_TAGS = "标签"
CLS_COL_TIME = "发布时间"
CLS_COL_DATE = "发布日期"


@dataclass
class SearchBundle:
    query: str
    answer: str
    results: list[dict[str, Any]]
    error: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Iran conflict tracking report.")
    parser.add_argument("--output", help="Optional path to write the Markdown report.")
    parser.add_argument("--json-output", help="Optional path to write raw JSON payload.")
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS, help="Max results per topic.")
    parser.add_argument("--prefer-model-search", action="store_true", help="优先使用OpenClaw环境中的模型搜索能力（如果在OpenClaw环境中）")
    parser.add_argument("--force-tavily", action="store_true", help="强制使用Tavily搜索，不使用模型搜索")
    return parser.parse_args()


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "iran-war-tracker/1.1"})
    return session


def normalize_text(value: Any) -> str:
    return str(value or "").strip()


def lowered_text(parts: list[Any]) -> str:
    return " ".join(normalize_text(part) for part in parts if normalize_text(part)).lower()


def has_any_keyword(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def topic_matches(text: str) -> set[str]:
    matches: set[str] = set()
    if has_any_keyword(text, WAR_TOPIC_KEYWORDS):
        matches.add("war")
    if has_any_keyword(text, ECON_TOPIC_KEYWORDS):
        matches.add("economy")
    if has_any_keyword(text, DIPLO_TOPIC_KEYWORDS):
        matches.add("diplomacy")
    return matches


def relevance_score(text: str) -> int:
    score = 0
    if has_any_keyword(text, IRAN_CORE_KEYWORDS):
        score += 3
    score += len(topic_matches(text)) * 2
    if has_any_keyword(text, ["hormuz", "strait of hormuz", "霍尔木兹"]):
        score += 2
    return score


def is_iran_war_related(text: str, allowed_topics: set[str] | None = None) -> bool:
    if not has_any_keyword(text, IRAN_CORE_KEYWORDS):
        return False
    matches = topic_matches(text)
    if not matches:
        return False
    if allowed_topics is None:
        return True
    return bool(matches & allowed_topics)


def compact_snippet(value: Any, limit: int = 180) -> str:
    text = " ".join(normalize_text(value).split())
    for marker in ["...", ". ", "! ", "? ", "\n"]:
        if marker in text:
            text = text.split(marker, 1)[0].strip()
            break
    return text[: limit - 1].rstrip() + "…" if len(text) > limit else text


def unique_lines(items: list[str], limit: int | None = None) -> list[str]:
    seen: list[str] = []
    for item in items:
        value = normalize_text(item)
        if value and value not in seen:
            seen.append(value)
        if limit is not None and len(seen) >= limit:
            break
    return seen


def filter_tavily_results(results: list[dict[str, Any]], limit: int, allowed_topics: set[str]) -> list[dict[str, Any]]:
    ranked: list[tuple[int, dict[str, Any]]] = []
    for result in results:
        title = normalize_text(result.get("title", ""))
        content = normalize_text(result.get("content", ""))
        title_text = lowered_text([title])
        full_text = lowered_text([title, content])
        if not is_iran_war_related(full_text, allowed_topics=allowed_topics):
            continue
        if not has_any_keyword(title_text, FOCUS_GEO_KEYWORDS):
            continue
        if allowed_topics == {"diplomacy"} and not has_any_keyword(full_text, LEADER_KEYWORDS):
            continue
        trimmed = dict(result)
        trimmed["title"] = compact_snippet(title, limit=140)
        trimmed["content"] = compact_snippet(content, limit=180)
        trimmed.pop("raw_content", None)
        ranked.append((relevance_score(full_text), trimmed))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:limit]]


def is_openclaw_environment() -> bool:
    """检测是否在 OpenClaw 环境中"""
    return bool(os.getenv("OPENCLAW_ENV") or os.getenv("KIMI_API_KEY") or os.getenv("AGENT_ENV"))


def model_search(session: requests.Session, query: str, max_results: int) -> SearchBundle:
    """
    使用 OpenClaw 环境中当前模型的搜索能力
    通过调用本地 MCP 搜索服务或模型 API
    """
    try:
        # 尝试使用 AutoGLM WebSearch MCP
        search_prompt = f"""搜索以下主题的最新新闻，返回 {max_results} 条最相关的结果：

搜索主题: {query}

请以 JSON 格式返回结果：
{{
  "answer": "简要总结",
  "results": [
    {{"title": "标题", "content": "内容摘要", "url": "链接", "published_date": "日期"}}
  ]
}}
"""
        
        # 如果在 OpenClaw 环境中，尝试调用模型搜索
        # 方式1: 通过本地 MCP 服务
        mcp_urls = [
            "http://127.0.0.1:53699/search",  # AutoGLM search endpoint
            "http://localhost:8080/search",    # 本地 MCP
        ]
        
        for mcp_url in mcp_urls:
            try:
                payload = {
                    "query": query,
                    "max_results": max_results * 2,
                    "time_range": "day"
                }
                resp = session.post(mcp_url, json=payload, timeout=DEFAULT_TIMEOUT)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    # 转换结果格式以兼容现有逻辑
                    formatted_results = []
                    for r in results:
                        formatted_results.append({
                            "title": r.get("title", ""),
                            "content": r.get("content", r.get("snippet", "")),
                            "url": r.get("url", ""),
                            "published_date": r.get("published_date", "")
                        })
                    return SearchBundle(
                        query=query,
                        answer=compact_snippet(data.get("answer", ""), limit=240),
                        results=formatted_results
                    )
            except Exception:
                continue
        
        # 方式2: 通过环境变量配置的搜索端点
        if OPENCLAW_SEARCH_URL:
            headers = {}
            if OPENCLAW_API_KEY:
                headers["Authorization"] = f"Bearer {OPENCLAW_API_KEY}"
            payload = {
                "query": query,
                "max_results": max_results * 2,
                "search_type": "news"
            }
            resp = session.post(OPENCLAW_SEARCH_URL, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                return SearchBundle(
                    query=query,
                    answer=compact_snippet(data.get("answer", ""), limit=240),
                    results=results
                )
        
        return SearchBundle(query=query, answer="", results=[], error="OpenClaw model search not available")
    except Exception as exc:
        return SearchBundle(query=query, answer="", results=[], error=f"Model search failed: {exc}")


def duckduckgo_search(session: requests.Session, query: str, max_results: int) -> SearchBundle:
    """
    使用 DuckDuckGo Lite 进行搜索（无需 API key）
    作为 Tavily 的降级方案
    """
    try:
        import urllib.parse
        
        # URL encode query
        encoded_query = urllib.parse.quote_plus(query)
        url = f"{DDG_LITE_URL}?q={encoded_query}&kl=us-en"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        
        for attempt in range(DDG_MAX_RETRIES):
            try:
                response = session.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
                response.raise_for_status()
                
                # Parse HTML results
                html_content = response.text
                results = _parse_ddg_results(html_content, max_results)
                
                if results:
                    # 生成简要总结
                    answer = f"DuckDuckGo found {len(results)} results for '{query}'"
                    return SearchBundle(
                        query=query,
                        answer=answer,
                        results=results
                    )
                
                # 如果没有结果，可能是 DDG 返回了验证码页面，等待后重试
                if attempt < DDG_MAX_RETRIES - 1:
                    time.sleep(1)
                    
            except Exception as e:
                if attempt < DDG_MAX_RETRIES - 1:
                    time.sleep(1)
                    continue
                raise
        
        return SearchBundle(query=query, answer="", results=[], error="DuckDuckGo returned no results")
        
    except Exception as exc:
        return SearchBundle(query=query, answer="", results=[], error=f"DuckDuckGo search failed: {exc}")


def _parse_ddg_results(html_content: str, max_results: int) -> list[dict[str, Any]]:
    """
    解析 DuckDuckGo Lite 的 HTML 结果
    """
    results = []
    
    try:
        from html.parser import HTMLParser
        
        class DDGResultParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_result = False
                self.in_title = False
                self.in_snippet = False
                self.current_result = {}
                self.results = []
                self.skip_sponsored = False
                
            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                
                # 检测是否为广告结果
                if tag == "span" and attrs_dict.get("class") == "result--ad":
                    self.skip_sponsored = True
                    return
                
                # 检测结果行
                if tag == "tr" and attrs_dict.get("class") and "result-link" in attrs_dict.get("class", ""):
                    if not self.skip_sponsored:
                        self.in_result = True
                        self.current_result = {}
                
                # 检测标题链接
                if self.in_result and tag == "a" and attrs_dict.get("class") == "result-link":
                    self.in_title = True
                    self.current_result["url"] = attrs_dict.get("href", "")
                
                # 检测摘要
                if tag == "td" and attrs_dict.get("class") == "result-snippet":
                    self.in_snippet = True
                    
            def handle_data(self, data):
                if self.in_title:
                    self.current_result["title"] = self.current_result.get("title", "") + data
                if self.in_snippet:
                    self.current_result["content"] = self.current_result.get("content", "") + data
                    
            def handle_endtag(self, tag):
                if tag == "span" and self.skip_sponsored:
                    self.skip_sponsored = False
                    
                if self.in_title and tag == "a":
                    self.in_title = False
                    
                if self.in_snippet and tag == "td":
                    self.in_snippet = False
                    
                # 一个结果结束
                if self.in_result and tag == "tr":
                    if self.current_result.get("title") and self.current_result.get("url"):
                        # 清理数据
                        title = self.current_result.get("title", "").strip()
                        content = self.current_result.get("content", "").strip()
                        url = self.current_result.get("url", "").strip()
                        
                        # 跳过广告
                        if "Sponsored" not in title and url.startswith("http"):
                            self.results.append({
                                "title": title,
                                "content": content[:300] if content else title,  # 限制摘要长度
                                "url": url,
                            })
                    
                    self.in_result = False
                    self.current_result = {}
        
        parser = DDGResultParser()
        parser.feed(html_content)
        
        # 返回前 N 个结果
        return parser.results[:max_results]
        
    except Exception as e:
        # 如果解析失败，尝试简单的正则提取
        import re
        results = []
        
        # 尝试匹配链接和标题模式
        link_pattern = r'<a[^>]*class="result-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        matches = re.findall(link_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for url, title_html in matches[:max_results]:
            # 清理标题中的 HTML 标签
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            if title and url.startswith("http") and "duckduckgo.com" not in url:
                results.append({
                    "title": title,
                    "content": title,
                    "url": url,
                })
        
        return results


def tavily_search(session: requests.Session, api_key: str, topic_name: str, query: str, max_results: int) -> SearchBundle:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "query": query,
        "topic": "news",
        "search_depth": "advanced",
        "max_results": max_results * 2,
        "time_range": "day",
        "include_answer": "advanced",
        "include_raw_content": False,
    }
    response: requests.Response | None = None
    try:
        response = session.post(TAVILY_URL, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        filtered = filter_tavily_results(data.get("results", []) or [], max_results, TAVILY_TOPIC_FILTERS.get(topic_name, {"war", "economy", "diplomacy"}))
        return SearchBundle(query=query, answer=compact_snippet(data.get("answer", ""), limit=240), results=filtered)
    except Exception as exc:
        detail = normalize_text(response.text[:500]) if response is not None else ""
        suffix = f" | body={detail}" if detail else ""
        return SearchBundle(query=query, answer="", results=[], error=f"{exc}{suffix}")


def smart_search(session: requests.Session, api_key: str, topic_name: str, query: str, max_results: int, prefer_model: bool = True) -> SearchBundle:
    """
    智能搜索：
    1. 优先使用模型搜索（如果在OpenClaw环境且 prefer_model=True）
    2. 回退到 Tavily API（如果有 API key）
    3. 降级到 DuckDuckGo（无需 API key）
    """
    errors = []
    
    # 第1层：如果在 OpenClaw 环境且 prefer_model 为 True，先尝试模型搜索
    if prefer_model and is_openclaw_environment():
        bundle = model_search(session, query, max_results)
        if not bundle.error and bundle.results:
            filtered = filter_tavily_results(bundle.results, max_results, TAVILY_TOPIC_FILTERS.get(topic_name, {"war", "economy", "diplomacy"}))
            return SearchBundle(query=query, answer=bundle.answer, results=filtered, error="model")
        errors.append(f"Model search: {bundle.error}")
    
    # 第2层：尝试 Tavily
    if api_key:
        bundle = tavily_search(session, api_key, topic_name, query, max_results)
        if not bundle.error:
            return bundle
        errors.append(f"Tavily: {bundle.error}")
    
    # 第3层：Tavily 失败，尝试模型搜索作为备选（如果之前没试过）
    if is_openclaw_environment() and not prefer_model:
        bundle = model_search(session, query, max_results)
        if not bundle.error and bundle.results:
            filtered = filter_tavily_results(bundle.results, max_results, TAVILY_TOPIC_FILTERS.get(topic_name, {"war", "economy", "diplomacy"}))
            return SearchBundle(query=query, answer=bundle.answer, results=filtered, error="model")
        errors.append(f"Model search fallback: {bundle.error}")
    
    # 第4层：降级到 DuckDuckGo（无需 API key）
    ddg_bundle = duckduckgo_search(session, query, max_results)
    if not ddg_bundle.error and ddg_bundle.results:
        filtered = filter_tavily_results(ddg_bundle.results, max_results, TAVILY_TOPIC_FILTERS.get(topic_name, {"war", "economy", "diplomacy"}))
        if filtered:
            return SearchBundle(query=query, answer=ddg_bundle.answer, results=filtered, error="duckduckgo")
    errors.append(f"DuckDuckGo: {ddg_bundle.error}")
    
    # 所有方法都失败
    return SearchBundle(query=query, answer="", results=[], error=" | ".join(errors))


def cls_telegraphs(session: requests.Session) -> pd.DataFrame:
    current_time = int(time.time())
    url = "https://www.cls.cn/nodeapi/telegraphList"
    params = {"app": "CailianpressWeb", "category": "", "lastTime": current_time, "last_time": current_time, "os": "web", "refresh_type": "1", "rn": "2000", "sv": "7.7.5"}
    text = session.get(url, params=params, timeout=DEFAULT_TIMEOUT).url.split("?")[1]
    text_bytes = text if isinstance(text, bytes) else bytes(text, "utf-8")
    sha1 = hashlib.sha1(text_bytes).hexdigest()
    params["sign"] = hashlib.md5(sha1.encode()).hexdigest()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Host": "www.cls.cn",
        "Pragma": "no-cache",
        "Referer": "https://www.cls.cn/telegraph",
        "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }
    data = session.get(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT).json()
    df = pd.DataFrame(data["data"]["roll_data"])
    df = df[["title", "content", "level", "subjects", "ctime"]]
    df["ctime"] = pd.to_datetime(df["ctime"], unit="s", utc=True).dt.tz_convert("Asia/Shanghai")
    df.columns = [CLS_COL_TITLE, CLS_COL_CONTENT, CLS_COL_LEVEL, CLS_COL_TAGS, CLS_COL_TIME]
    df.sort_values([CLS_COL_TIME], ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)
    df[CLS_COL_TAGS] = [",".join([t["subject_name"] for t in tags]) if tags else "" for tags in df[CLS_COL_TAGS].to_numpy()]
    df[CLS_COL_DATE] = df[CLS_COL_TIME].dt.date.astype(str)
    df[CLS_COL_TIME] = df[CLS_COL_TIME].dt.strftime("%H:%M:%S")
    return df


def filter_cls_items(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    ranked: list[tuple[int, dict[str, Any]]] = []
    for item in df.to_dict("records"):
        title = normalize_text(item.get(CLS_COL_TITLE, ""))
        content = normalize_text(item.get(CLS_COL_CONTENT, ""))
        tags = normalize_text(item.get(CLS_COL_TAGS, ""))
        title_text = lowered_text([title])
        primary_text = lowered_text([title, tags])
        full_text = lowered_text([title, content, tags])
        if has_any_keyword(title_text, CLS_NOISE_KEYWORDS):
            continue
        if not is_iran_war_related(full_text, allowed_topics={"war", "economy", "diplomacy"}):
            continue
        if not has_any_keyword(primary_text, FOCUS_GEO_KEYWORDS):
            continue
        trimmed = dict(item)
        trimmed[CLS_COL_TITLE] = compact_snippet(title, limit=90)
        trimmed[CLS_COL_CONTENT] = compact_snippet(content, limit=120)
        ranked.append((relevance_score(full_text), trimmed))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:20]]


def fetch_stooq_asset(session: requests.Session, symbol: str) -> dict[str, Any] | None:
    try:
        response = session.get(f"https://stooq.com/q/l/?s={symbol}&f=sd2t2ohlcv&h&e=csv", timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        rows = list(csv.DictReader(io.StringIO(response.text)))
        if not rows:
            return None
        row = rows[-1]
        open_price = float(row["Open"])
        close_price = float(row["Close"])
        change_pct = round(((close_price - open_price) / open_price) * 100, 2) if open_price else 0.0
        return {"symbol": symbol, "date": row["Date"], "time": row["Time"], "open": open_price, "close": close_price, "high": float(row["High"]), "low": float(row["Low"]), "change_pct": change_pct, "source": "stooq"}
    except Exception:
        return None


def fetch_btc_fallback(session: requests.Session) -> dict[str, Any] | None:
    try:
        response = session.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        price = float(response.json()["bitcoin"]["usd"])
        now = datetime.now()
        return {"symbol": "btcusd", "date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M:%S"), "open": price, "close": price, "high": price, "low": price, "change_pct": 0.0, "source": "coingecko"}
    except Exception:
        return None


def collect_risk_assets(session: requests.Session) -> dict[str, Any]:
    assets: dict[str, Any] = {}
    for name, symbol in RISK_ASSETS.items():
        asset = fetch_stooq_asset(session, symbol)
        if name == "BTC" and not asset:
            asset = fetch_btc_fallback(session)
        assets[name] = asset
    return assets


def read_text_with_fallbacks(path: Path) -> str:
    for encoding in ["utf-8", "utf-8-sig", "gb18030", "gbk"]:
        try:
            return path.read_text(encoding=encoding)
        except Exception:
            pass
    return ""


def load_framework_remote() -> tuple[str, str, str]:
    try:
        response = requests.get(FRAMEWORK_GIST_URL, timeout=FRAMEWORK_REMOTE_TIMEOUT)
        response.raise_for_status()
        text = normalize_text(response.text)
        if text:
            return text[:FRAMEWORK_MAX_CHARS], FRAMEWORK_GIST_URL, "gist"
    except Exception:
        pass
    return "", "", ""


def load_framework_local() -> tuple[str, str, str]:
    base = Path(__file__).resolve().parents[1]
    for candidate in FRAMEWORK_CANDIDATES:
        path = base / candidate
        if path.exists():
            return read_text_with_fallbacks(path)[:FRAMEWORK_MAX_CHARS], path.name, "local"
    for path in sorted(base.glob("*.md")):
        if path.name != "SKILL.md" and ("伊朗局势" in path.name or "经济影响分析报告" in path.name):
            return read_text_with_fallbacks(path)[:FRAMEWORK_MAX_CHARS], path.name, "local"
    return "", "", ""


def load_framework_excerpt() -> tuple[str, str, str]:
    remote_excerpt, remote_name, remote_source = load_framework_remote()
    if remote_excerpt:
        return remote_excerpt, remote_name, remote_source
    return load_framework_local()


def bundle_text(bundle: SearchBundle) -> str:
    parts = [bundle.answer]
    for item in bundle.results:
        parts.extend([item.get("title", ""), item.get("content", "")])
    return lowered_text(parts)


def cls_text(items: list[dict[str, Any]]) -> str:
    return lowered_text([" ".join([normalize_text(item.get(CLS_COL_TITLE, "")), normalize_text(item.get(CLS_COL_CONTENT, "")), normalize_text(item.get(CLS_COL_TAGS, ""))]) for item in items])


def source_lines(bundle: SearchBundle, limit: int) -> list[str]:
    lines = []
    for result in bundle.results:
        title = normalize_text(result.get("title", ""))
        content = normalize_text(result.get("content", ""))
        url = normalize_text(result.get("url", ""))
        text = " | ".join(part for part in [title, content] if part)
        if url:
            text = f"{text} ({url})" if text else url
        if text:
            lines.append(text)
    return unique_lines(lines, limit)


def cls_lines(items: list[dict[str, Any]], limit: int) -> list[str]:
    lines = []
    for item in items:
        line = " | ".join(part for part in [normalize_text(item.get(CLS_COL_TIME, "")), normalize_text(item.get(CLS_COL_TITLE, "")), normalize_text(item.get(CLS_COL_CONTENT, ""))] if part)
        if line:
            lines.append(line)
    return unique_lines(lines, limit)


def country_summary(name: str, bundle: SearchBundle, cls_items: list[dict[str, Any]], keywords: list[str]) -> list[str]:
    lines = []
    for item in source_lines(bundle, 8) + cls_lines(cls_items, 8):
        lowered = item.lower()
        if has_any_keyword(lowered, keywords) and is_iran_war_related(lowered):
            lines.append(item)
    if not lines:
        return [f"{name}方向暂无足够增量信息。", f"{name}部分需要继续观察后续公开表态与行动变化。"]
    lines = unique_lines(lines, 3)
    leader_hits = [item for item in lines if has_any_keyword(item.lower(), LEADER_KEYWORDS)]
    if leader_hits:
        lines.append("重要人物表态: " + "；".join(unique_lines(leader_hits, 2)))
    return lines[:4]


def classify_heat(all_text: str) -> tuple[str, list[str]]:
    expansion_hits = sum(all_text.count(word.lower()) for word in [w.lower() for w in WAR_EXPANSION_KEYWORDS])
    easing_hits = sum(all_text.count(word.lower()) for word in [w.lower() for w in WAR_EASING_KEYWORDS])
    bullets = [f"扩大信号命中数: {expansion_hits}", f"缓和信号命中数: {easing_hits}"]
    if expansion_hits >= 8 and expansion_hits > easing_hits:
        return "高", bullets + ["判断: 扩大战事与封锁风险占上风，需重点盯住空袭频率、导弹袭击和航运受阻。"]
    if easing_hits >= expansion_hits and easing_hits >= 3:
        return "中", bullets + ["判断: 紧张仍在，但谈判、停火或降温措辞有所增加。"]
    return "中高", bullets + ["判断: 局势维持紧张，缓和证据不足，仍偏向高风险平衡。"]


def marginal_change_assessment(all_text: str, hormuz_bundle: SearchBundle) -> list[str]:
    expansion_hits = sum(all_text.count(word.lower()) for word in [w.lower() for w in WAR_EXPANSION_KEYWORDS])
    easing_hits = sum(all_text.count(word.lower()) for word in [w.lower() for w in WAR_EASING_KEYWORDS])
    hormuz_text = bundle_text(hormuz_bundle)
    lines = []
    lines.append("边际变化: 空袭、导弹、封锁、部队调动等升级词频高于谈判与停火词频。" if expansion_hits > easing_hits else "边际变化: 谈判、停火或降温措辞增加，显示局势边际上没有继续恶化。")
    if any(word in hormuz_text for word in ["closure", "closed", "attack", "tanker", "封锁", "油轮", "袭船"]):
        lines.append("霍尔木兹状态: 海峡存在封锁、遇袭或油轮受扰风险，航运与保险成本敏感度上升。")
    elif any(word in hormuz_text for word in ["transit", "passage", "reopen", "通过", "恢复"]):
        lines.append("霍尔木兹状态: 更像高风险通行而不是完全停摆，关键在于通过效率与安全事件频率。")
    else:
        lines.append("霍尔木兹状态: 当前公开增量证据有限，需继续追踪商船通行、保险费率和袭船事件。")
    lines.append("关注点: 若出现持续性海峡受阻、油轮受袭或更强制裁，油气风险溢价将继续抬升。")
    return lines


def describe_asset(asset: dict[str, Any] | None, label: str) -> str:
    if not asset:
        return f"{label}: 数据缺失。"
    return f"{label}: 收盘/最新 {asset.get('close')} USD，日内涨跌 {asset.get('change_pct')}%，区间 {asset.get('low')}-{asset.get('high')}，来源 {asset.get('source')}。"


def extract_framework_dimensions(framework_excerpt: str) -> list[str]:
    if not framework_excerpt:
        return ["未加载分析框架，以下映射基于通用油气冲击逻辑。"]
    lowered = framework_excerpt.lower()
    hints = []
    if "霍尔木兹" in framework_excerpt or "hormuz" in lowered:
        hints.append("框架维度1: 霍尔木兹海峡通行量和通航效率。")
    if "出口" in framework_excerpt or "export" in lowered:
        hints.append("框架维度2: 原油或天然气出口损失与替代能力。")
    if "产量" in framework_excerpt or "production" in lowered:
        hints.append("框架维度3: 上游产量、中游设施、炼厂或液化设施受损。")
    if "需求" in framework_excerpt or "inflation" in lowered or "通胀" in framework_excerpt:
        hints.append("框架维度4: 需求破坏、通胀压力和全球经济反馈。")
    return hints or ["框架已加载，但未能自动提取关键词，仍按海峡通行、供给损失、价格传导和宏观冲击展开。"]


def energy_analysis(oil_bundle: SearchBundle, gas_bundle: SearchBundle, assets: dict[str, Any], framework_excerpt: str) -> tuple[list[str], list[str], list[str], list[str]]:
    oil_text = bundle_text(oil_bundle)
    gas_text = bundle_text(gas_bundle)
    oil_lines = [
        "事实/供给: 原油相关新闻已出现供给扰动、出口受限或制裁相关信号，说明市场正在重新定价中东供应安全。" if any(word in oil_text for word in ["disruption", "export", "sanction", "supply", "石油", "原油", "出口", "供给", "制裁"]) else "事实/供给: 暂未看到大规模新增停供证据，但航运与制裁风险本身足以抬高短期风险溢价。",
        "框架映射: 原油核心不是库存故事，而是霍尔木兹海峡通行效率、油轮安全和出口连续性。",
        "市场信号: " + describe_asset(assets.get("原油(WTI)"), "WTI"),
        "推演: 若海峡通行持续受阻，油轮与保险价格上升会先于实体断供反映到油价曲线。",
        "推演: 若只是短促袭扰而非持续封锁，油价更可能表现为事件驱动跳涨后回落，而不是单边失控。",
    ]
    gas_lines = [
        "事实/供给: 天然气相关新闻存在供给、出口、设施或 LNG 相关扰动线索，需区分地区性冲击与全球性冲击。" if any(word in gas_text for word in ["gas", "lng", "supply", "export", "天然气", "供给", "出口", "设施"]) else "事实/供给: 当前天然气更多体现为预期层面的紧张，尚未充分证实为持续的实体供给收缩。",
        "框架映射: 天然气要看设施完好性、区域管道/LNG 装置、以及是否形成可持续出口中断。",
        "市场信号: " + describe_asset(assets.get("天然气"), "天然气"),
        "推演: 若冲击集中在区域设施或运输链，天然气价格可能先反映区域供需错配，再决定是否外溢到全球 LNG。",
        "推演: 如果原油与天然气同步走强，说明交易逻辑从单一地缘事件扩散到更广义能源紧张。",
    ]
    macro_lines = [
        "宏观传导: 油气上行会推高通胀预期，压缩全球央行的宽松空间，并对高耗能经济体和风险资产形成压力。",
        "宏观传导: 原油冲击更容易迅速进入交通与工业成本，天然气冲击更容易体现为公用事业、工业燃料和区域能源替代成本。",
        "宏观传导: 如果只是风险溢价抬升而非实体供给断裂，金融市场反应通常会先于宏观数据恶化。",
    ]
    return oil_lines, gas_lines, extract_framework_dimensions(framework_excerpt), macro_lines


def trade_clues(heat_level: str, assets: dict[str, Any], marginal_lines: list[str]) -> list[str]:
    gold = assets.get("黄金") or {}
    oil = assets.get("原油(WTI)") or {}
    gas = assets.get("天然气") or {}
    btc = assets.get("BTC") or {}
    nasdaq = assets.get("纳指期货") or {}
    clues = ["主线: 若战事继续升级，优先关注黄金、原油、天然气的风险溢价扩张。" if heat_level == "高" else "主线: 在局势未进一步恶化前，先观察风险溢价是否只停留在事件冲击而不是趋势行情。"]
    clues.append("确认条件: 黄金走强说明避险需求正在接力，地缘风险叙事得到资金验证。" if gold and float(gold.get("change_pct", 0) or 0) > 0.5 else "反证条件: 黄金未明显走强，说明市场对地缘冲击的持续性仍存怀疑。")
    clues.append("确认条件: WTI 明显上行，说明市场已经把霍尔木兹或出口扰动纳入定价。" if oil and float(oil.get("change_pct", 0) or 0) > 1 else "反证条件: 原油未延续上涨，意味着供给扰动暂时停留在 headlines 而非基本面。")
    if gas and float(gas.get("change_pct", 0) or 0) > 1:
        clues.append("扩散信号: 天然气同步走强时，表明能源紧张从原油向更广泛能源链扩散。")
    if btc and float(btc.get("change_pct", 0) or 0) < 0:
        clues.append("风险偏好: BTC 走弱可视为风险偏好回落的辅助信号。")
    if nasdaq and float(nasdaq.get("change_pct", 0) or 0) < 0:
        clues.append("权益反应: 纳指期货转弱，说明宏观与风险偏好传导已经开始影响成长资产。")
    clues.extend(marginal_lines[:2])
    return unique_lines(clues, 6)


def scenario_analysis(heat_level: str, marginal_lines: list[str], assets: dict[str, Any]) -> list[str]:
    oil_change = float((assets.get("原油(WTI)") or {}).get("change_pct", 0) or 0)
    gold_change = float((assets.get("黄金") or {}).get("change_pct", 0) or 0)
    return [
        f"当前观测: 热度={heat_level}，WTI 日内涨跌={oil_change}%，黄金日内涨跌={gold_change}%。",
        f"边际判断: {marginal_lines[0] if marginal_lines else '暂无边际变化结论。'}",
        f"验证重点: {marginal_lines[1] if len(marginal_lines) > 1 else '继续盯住霍尔木兹通行与袭船事件。'}",
        "基准情景: 局势维持高压但未失控，霍尔木兹仍可通行但风险溢价维持，对应表现是原油偏强、黄金偏强、风险资产承压但未出现连锁抛售。",
        "升级情景: 海峡通行显著受阻、油轮遇袭增多或制裁/打击升级，油气价格会进一步跳升，纳指期货与 BTC 更容易走弱，黄金受益最明确。",
        "缓和情景: 若出现停火、降温会谈、通行恢复或袭扰频率下降，油气风险溢价会先回落，黄金降温，风险资产修复。",
    ]


def build_report(max_results: int, prefer_model_search: bool = True) -> dict[str, Any]:
    session = get_session()
    tavily_api_key = normalize_text(os.getenv("TAVILY_API_KEY", ""))
    
    # 检测搜索策略
    use_model_first = prefer_model_search and is_openclaw_environment()
    
    # 使用智能搜索（自动处理降级逻辑）
    searches = {name: smart_search(session, tavily_api_key, name, query, max_results, prefer_model=use_model_first) for name, query in TAVILY_QUERIES.items()}
    
    # 检测实际使用的搜索方法
    search_methods_used = set()
    for bundle in searches.values():
        if bundle.error == "model":
            search_methods_used.add("model")
        elif bundle.error == "duckduckgo":
            search_methods_used.add("duckduckgo")
        elif bundle.error == "":
            search_methods_used.add("tavily")
    
    # 确定主要搜索方法
    if "model" in search_methods_used:
        search_method = "model"
    elif "tavily" in search_methods_used:
        search_method = "tavily"
    elif "duckduckgo" in search_methods_used:
        search_method = "duckduckgo"
    else:
        search_method = "failed"
    cls_items = filter_cls_items(cls_telegraphs(session))
    assets = collect_risk_assets(session)
    framework_excerpt, framework_name, framework_source = load_framework_excerpt()
    all_text = " ".join(bundle_text(bundle) for bundle in searches.values()) + " " + cls_text(cls_items)
    heat_level, heat_lines = classify_heat(all_text)
    marginal_lines = marginal_change_assessment(all_text, searches["hormuz"])
    oil_lines, gas_lines, framework_lines, macro_lines = energy_analysis(searches["oil_supply"], searches["gas_supply"], assets, framework_excerpt)
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "heat_level": heat_level,
        "executive_summary": unique_lines([f"当前战事热度评估为 {heat_level}。", marginal_lines[1], oil_lines[0], gas_lines[0]], 4),
        "heat_lines": heat_lines,
        "us_lines": country_summary("美国", searches["leaders"], cls_items, US_KEYWORDS),
        "israel_lines": country_summary("以色列", searches["leaders"], cls_items, ISRAEL_KEYWORDS),
        "iran_lines": country_summary("伊朗", searches["leaders"], cls_items, IRAN_KEYWORDS),
        "marginal_lines": marginal_lines,
        "oil_lines": oil_lines,
        "gas_lines": gas_lines,
        "framework_lines": framework_lines,
        "macro_lines": macro_lines,
        "risk_lines": [describe_asset(asset, name) for name, asset in assets.items()],
        "trade_lines": trade_clues(heat_level, assets, marginal_lines),
        "scenario_lines": scenario_analysis(heat_level, marginal_lines, assets),
        "evidence": {key: source_lines(bundle, 4) for key, bundle in searches.items()} | {"cls": cls_lines(cls_items, 6)},
        "searches": {key: {"query": bundle.query, "answer": bundle.answer, "error": bundle.error, "result_count": len(bundle.results)} for key, bundle in searches.items()},
        "cls_count": len(cls_items),
        "framework_loaded": bool(framework_excerpt),
        "framework_name": framework_name,
        "framework_source": framework_source,
        "search_method": search_method,
        "openclaw_env": is_openclaw_environment(),
    }


def add_bullets(lines: list[str], items: list[str], prefix: str = "- ") -> None:
    lines.extend(f"{prefix}{item}" for item in items)


def change_symbol(heat_level: str) -> str:
    if heat_level == "高":
        return "🔺上升"
    if heat_level == "中":
        return "🔻下降"
    return "➡️持平"


def first_or(items: list[str], default: str) -> str:
    return items[0] if items else default


def classify_country_blocks(items: list[str], military_label: str) -> tuple[str, str, str]:
    military = []
    leaders = []
    other = []
    for item in items:
        lowered = item.lower()
        if has_any_keyword(lowered, LEADER_KEYWORDS):
            leaders.append(item)
        elif has_any_keyword(lowered, WAR_TOPIC_KEYWORDS):
            military.append(item)
        else:
            other.append(item)
    return (
        "；".join(unique_lines(military, 2)) or "暂无明确增量信息。",
        "；".join(unique_lines(leaders, 2)) or "暂无高置信度领导人新增表态。",
        "；".join(unique_lines(other, 2)) or "暂无其他值得单列的新增动态。",
    )


def to_markdown(report: dict[str, Any]) -> str:
    us_military, us_leaders, us_other = classify_country_blocks(report["us_lines"], "军事行动")
    il_military, il_leaders, il_other = classify_country_blocks(report["israel_lines"], "军事行动")
    ir_counter, ir_leaders, ir_other = classify_country_blocks(report["iran_lines"], "反击行动")

    expansion = first_or([line for line in report["marginal_lines"] if "边际变化" in line], "暂无明确战争扩大信号。")
    hormuz = [line for line in report["marginal_lines"] if "霍尔木兹" in line or "关注点" in line]
    easing = [line for line in report["heat_lines"] if "缓和" in line or "谈判" in line]

    lines = [
        "### 📊 【战争烈度评估】",
        f"**{report['heat_level']}级（{change_symbol(report['heat_level'])}）**",
        f"- 当前态势简述：{first_or(report['executive_summary'], '当前局势仍处于高敏感观察期。')}",
        f"- 关键变化点：{first_or(report['heat_lines'], '暂无足够证据支持方向性变化。')}",
        "",
        "───────────────────────────────────────────────────────────────",
        "",
        "### ⚔️ 【局势进展】",
        "",
        "**▸ 🇺🇸 美国汇总**",
        f"- 🎯 军事行动：{us_military}",
        f"- 🎤 领导人表态：{us_leaders}",
        f"- 📌 其他动态：{us_other}",
        "",
        "**▸ 🇮🇱 以色列汇总**",
        f"- 🎯 军事行动：{il_military}",
        f"- 🎤 领导人表态：{il_leaders}",
        f"- 📌 其他动态：{il_other}",
        "",
        "**▸ 🇮🇷 伊朗汇总**",
        f"- ⚡ 反击行动：{ir_counter}",
        f"- 🎤 领导人表态：{ir_leaders}",
        f"- 📌 其他动态：{ir_other}",
        "",
        "**▸ 📈 边际变化评估**",
        "├─ 🔴 战争扩大信号：",
        f"│   • 空袭烈度/频次是否加大：{expansion}",
        f"│   • 地面进攻迹象：{first_or(report['marginal_lines'][1:2], '暂无明确地面进攻升级证据。')}",
        f"│   • 新参战方动态：{first_or(report['marginal_lines'][2:3], '暂无高置信度新参战方加入。')}",
        "│",
        "├─ 🟢 战争缓和信号：",
        f"│   • 谈判信号：{first_or(easing, '公开谈判信号有限。')}",
        f"│   • 停火提议：{report['heat_lines'][-1] if report['heat_lines'] else '暂无明确停火提议。'}",
        "│   • 外交斡旋：继续跟踪美欧、中东周边国家与国际组织的斡旋动作。",
        "│",
        "└─ 🚢 霍尔木兹海峡封锁：",
        f"    • 通航状态：{first_or(hormuz, '暂无确定性封锁结论，但风险溢价仍需跟踪。')}",
        f"    • 袭船事件：{hormuz[1] if len(hormuz) > 1 else '暂无新增高置信度袭船细节。'}",
        "    • 船只动态：继续观察商船通行效率、油轮保险费率和改道情况。",
        "",
        "### 🛢️ 【油气分析】",
        "",
        "**原油**",
    ]
    add_bullets(lines, report["oil_lines"])
    lines.extend(["", "**天然气**"])
    add_bullets(lines, report["gas_lines"])
    lines.extend(["", "**分析框架映射**"])
    add_bullets(lines, report["framework_lines"])
    lines.extend(["", "**宏观传导**"])
    add_bullets(lines, report["macro_lines"])

    lines.extend(["", "## 风险资产波动"])
    add_bullets(lines, report["risk_lines"])

    lines.extend(
        [
            "",
            "### 💡 【交易线索】",
            "",
            "**🎯 核心判断：**",
            first_or(report["trade_lines"], "当前更适合跟踪边际变化，而不是提前押注单边趋势。"),
            "",
            "**📋 操作建议：**",
            f"• 🛢️ 原油：{'看多' if report['heat_level'] == '高' else '观望'}，{first_or(report['oil_lines'], '核心观察霍尔木兹与出口扰动。')}",
            f"• ⚡ 能源替代：{'观望' if report['heat_level'] != '高' else '看多'}，{first_or(report['gas_lines'], '关注天然气与替代能源链条是否同步走强。')}",
            f"• 📊 AI科技：{'观望' if report['heat_level'] == '中高' else '看多'}，{first_or(report['risk_lines'], '重点看纳指期货与风险偏好是否受压。')}",
            "",
            "**⚠️ 风险提示：**",
        ]
    )
    add_bullets(lines, report["trade_lines"][1:], prefix="• ")

    lines.extend(["", "## 情景推演"])
    add_bullets(lines, report["scenario_lines"])

    # 根据搜索方法调整标题
    search_method = report.get("search_method", "tavily")
    news_source_title = "模型搜索 / 新闻" if search_method == "model" else "Tavily / 新闻搜索"
    
    lines.extend(["", "## 证据摘录", f"### {news_source_title}"])
    for key in ["war_updates", "hormuz", "oil_supply", "gas_supply", "leaders"]:
        lines.append(f"- {key}")
        add_bullets(lines, report["evidence"].get(key, []), "  - ")
    lines.extend(["", "### CLS 财联社快讯"])
    add_bullets(lines, report["evidence"].get("cls", []))
    
    # 数据源状态
    search_method_display = "模型搜索" if search_method == "model" else ("智能混合" if search_method == "smart" else "Tavily")
    openclaw_status = f" | OpenClaw环境: {'是' if report.get('openclaw_env') else '否'}"
    framework_source_display = "远程Gist" if report.get("framework_source") == "gist" else ("本地回退" if report.get("framework_source") == "local" else "未加载")
    lines.extend(["", "## 数据源状态", f"- 新闻搜索方法: {search_method_display}{openclaw_status}", f"- 主题搜索数: {len(report['searches'])}", f"- CLS 快讯命中数: {report['cls_count']}", f"- 框架已加载: {'是' if report['framework_loaded'] else '否'}", f"- 框架来源: {framework_source_display}", f"- 框架文件: {report['framework_name'] or '未找到'}"])
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    # 确定搜索策略
    prefer_model = args.prefer_model_search
    if args.force_tavily:
        prefer_model = False
    elif is_openclaw_environment() and not args.prefer_model_search:
        # 在OpenClaw环境中默认优先使用模型搜索
        prefer_model = True
    
    report = build_report(max_results=args.max_results, prefer_model_search=prefer_model)
    markdown = to_markdown(report)
    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
    else:
        try:
            print(markdown)
        except UnicodeEncodeError:
            # 处理Windows控制台编码问题
            print(markdown.encode('utf-8', errors='replace').decode('utf-8'))
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
