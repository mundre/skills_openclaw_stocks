#!/usr/bin/env python3
"""News search providers and fallback orchestration."""

from __future__ import annotations

import urllib.parse
from html.parser import HTMLParser

import requests

from config import DDG_LITE_URL, NEWS_QUERIES, OPENCLAW_API_KEY, OPENCLAW_SEARCH_URL, TAVILY_URL
from normalize import compact_snippet, contains_any, lowercase_text, normalize_text
from schemas import NewsBundle, SearchResult
from time_utils import isoformat_or_empty, parse_timestamp, within_lookback


def collect_news(
    session: requests.Session,
    max_results: int,
    lookback_hours: int,
    prefer_model_search: bool,
    tavily_api_key: str,
) -> tuple[dict[str, NewsBundle], dict[str, int], dict[str, str]]:
    bundles: dict[str, NewsBundle] = {}
    stats = {
        "news_results_in_window": 0,
        "news_missing_timestamp": 0,
    }
    providers: dict[str, str] = {}
    for topic, query in NEWS_QUERIES.items():
        bundle = search_topic(
            session=session,
            topic=topic,
            query=query,
            max_results=max_results,
            lookback_hours=lookback_hours,
            prefer_model_search=prefer_model_search,
            tavily_api_key=tavily_api_key,
        )
        bundles[topic] = bundle
        providers[topic] = bundle.provider
        for result in bundle.results:
            if result.timestamp_verified and result.within_lookback:
                stats["news_results_in_window"] += 1
            if not result.timestamp_verified:
                stats["news_missing_timestamp"] += 1
    return bundles, stats, providers


def search_topic(
    session: requests.Session,
    topic: str,
    query: str,
    max_results: int,
    lookback_hours: int,
    prefer_model_search: bool,
    tavily_api_key: str,
) -> NewsBundle:
    attempts = []
    if prefer_model_search:
        attempts.append(lambda: model_search(session, topic, query, max_results, lookback_hours))
    if tavily_api_key:
        attempts.append(lambda: tavily_search(session, topic, query, max_results, tavily_api_key, lookback_hours))
    attempts.append(lambda: duckduckgo_search(session, topic, query, max_results, lookback_hours))

    last_bundle = NewsBundle(topic=topic, query=query, provider="none", error="no provider available")
    for fetch in attempts:
        bundle = fetch()
        if bundle.results or not bundle.error:
            return bundle
        last_bundle = bundle
    return last_bundle


def model_search(session: requests.Session, topic: str, query: str, max_results: int, lookback_hours: int) -> NewsBundle:
    urls = [OPENCLAW_SEARCH_URL] if OPENCLAW_SEARCH_URL else [
        "http://127.0.0.1:53699/search",
        "http://localhost:8080/search",
    ]
    headers = {}
    if OPENCLAW_API_KEY:
        headers["Authorization"] = f"Bearer {OPENCLAW_API_KEY}"
    last_error = ""
    for url in urls:
        try:
            response = session.post(
                url,
                json={"query": query, "max_results": max_results, "time_range": "day"},
                headers=headers,
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            return NewsBundle(
                topic=topic,
                query=query,
                provider="model",
                answer=compact_snippet(data.get("answer", ""), limit=240),
                results=normalize_results(data.get("results", []), source="model", limit=max_results, lookback_hours=lookback_hours),
            )
        except Exception as exc:
            last_error = normalize_text(exc)
    return NewsBundle(topic=topic, query=query, provider="model", error=last_error or "model search failed")


def tavily_search(
    session: requests.Session,
    topic: str,
    query: str,
    max_results: int,
    api_key: str,
    lookback_hours: int,
) -> NewsBundle:
    try:
        response = session.post(
            TAVILY_URL,
            json={
                "query": query,
                "topic": "news",
                "search_depth": "advanced",
                "max_results": max_results,
                "time_range": "day",
                "include_answer": "advanced",
            },
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return NewsBundle(
            topic=topic,
            query=query,
            provider="tavily",
            answer=compact_snippet(data.get("answer", ""), limit=240),
            results=normalize_results(data.get("results", []), source="tavily", limit=max_results, lookback_hours=lookback_hours),
        )
    except Exception as exc:
        return NewsBundle(topic=topic, query=query, provider="tavily", error=normalize_text(exc))


def duckduckgo_search(session: requests.Session, topic: str, query: str, max_results: int, lookback_hours: int) -> NewsBundle:
    try:
        encoded_query = urllib.parse.quote_plus(query)
        response = session.get(f"{DDG_LITE_URL}?q={encoded_query}&kl=us-en", timeout=20)
        response.raise_for_status()
        challenge_markers = [
            "Unfortunately, bots use DuckDuckGo too.",
            "anomaly-modal",
            "Please complete the following challenge",
        ]
        if any(marker in response.text for marker in challenge_markers):
            return NewsBundle(
                topic=topic,
                query=query,
                provider="duckduckgo",
                error="DuckDuckGo returned a bot challenge page",
            )
        results = parse_ddg_results(response.text, max_results, lookback_hours)
        if not results:
            return NewsBundle(
                topic=topic,
                query=query,
                provider="duckduckgo",
                error="DuckDuckGo returned no parseable results",
            )
        return NewsBundle(
            topic=topic,
            query=query,
            provider="duckduckgo",
            answer=f"DuckDuckGo returned {len(results)} results for {query}",
            results=results,
        )
    except Exception as exc:
        return NewsBundle(topic=topic, query=query, provider="duckduckgo", error=normalize_text(exc))


def normalize_results(raw_results: list[dict[str, object]], source: str, limit: int, lookback_hours: int) -> list[SearchResult]:
    results: list[SearchResult] = []
    for item in raw_results[:limit]:
        title = compact_snippet(item.get("title", ""), limit=140)
        content = compact_snippet(item.get("content", item.get("snippet", "")), limit=220)
        url = normalize_text(item.get("url", ""))
        if not title and not content:
            continue
        haystack = lowercase_text(title, content, url)
        if not contains_any(haystack, ["iran", "hormuz", "israel", "tehran", "oil", "gas", "伊朗", "霍尔木兹"]):
            continue
        published_date = normalize_text(item.get("published_date", item.get("date", "")))
        parsed = parse_timestamp(published_date)
        timestamp_verified = parsed is not None
        in_window = within_lookback(parsed, lookback_hours) if timestamp_verified else False
        if timestamp_verified and not in_window:
            continue
        results.append(
            SearchResult(
                title=title,
                content=content or title,
                url=url,
                published_date=published_date,
                published_at=isoformat_or_empty(parsed),
                source=source,
                timestamp_verified=timestamp_verified,
                within_lookback=in_window,
            )
        )
    return results


class DuckResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current_href = ""
        self.capture_title = False
        self.current_title = ""
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "a" and attrs_dict.get("class") == "result-link":
            self.capture_title = True
            self.current_href = attrs_dict.get("href") or ""
            self.current_title = ""

    def handle_data(self, data: str) -> None:
        if self.capture_title:
            self.current_title += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.capture_title:
            self.capture_title = False
            if self.current_href and self.current_title:
                self.links.append((self.current_href, normalize_text(self.current_title)))


def parse_ddg_results(html: str, max_results: int, lookback_hours: int) -> list[SearchResult]:
    parser = DuckResultParser()
    parser.feed(html)
    results: list[SearchResult] = []
    for url, title in parser.links:
        if not url.startswith("http"):
            continue
        results.append(
            SearchResult(
                title=title,
                content=title,
                url=url,
                source="duckduckgo",
                timestamp_verified=False,
                within_lookback=False,
            )
        )
        if len(results) >= max_results:
            break
    return results
