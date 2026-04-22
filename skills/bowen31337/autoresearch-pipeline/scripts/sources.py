"""Data fetchers for all sources.

Each fetcher returns a list of SourceItem dataclasses.
All HTTP uses httpx with 15s timeouts.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class SourceItem:
    """Unified item from any source."""
    title: str
    url: str
    source: str              # "arxiv" | "github" | "hackernews" | "web"
    summary: str             # 1-3 sentence description
    score: float             # normalised relevance 0.0-1.0
    date: str | None = None  # ISO date if available
    metadata: dict | None = None  # source-specific extras
    # arxiv: {"authors": [...], "categories": [...]}
    # github: {"stars": int, "language": str, "stars_today": int}
    # hackernews: {"points": int, "comments": int, "hn_id": int}
    # web: {"snippet": str}


@dataclass
class TrackConfig:
    """Per-track query configuration (loaded from config.json)."""
    name: str
    display_name: str
    arxiv_categories: list[str]
    arxiv_keywords: list[str]
    github_languages: list[str]
    github_topics: list[str]
    hn_keywords: list[str]
    web_queries: list[str]
    max_items_per_source: int = 10


def load_track_config(track_name: str, config_path: Path) -> TrackConfig:
    """Load a TrackConfig from config.json for the given track name."""
    with open(config_path) as f:
        config = json.load(f)

    tracks = config.get("tracks", {})
    if track_name not in tracks:
        raise ValueError(f"Track '{track_name}' not found in config.json. Available: {list(tracks.keys())}")

    t = tracks[track_name]
    defaults = config.get("defaults", {})
    max_items = t.get("max_items_per_source", defaults.get("max_items_per_source", 10))

    return TrackConfig(
        name=track_name,
        display_name=t.get("display_name", track_name),
        arxiv_categories=t.get("arxiv_categories", []),
        arxiv_keywords=t.get("arxiv_keywords", []),
        github_languages=t.get("github_languages", []),
        github_topics=t.get("github_topics", []),
        hn_keywords=t.get("hn_keywords", []),
        web_queries=t.get("web_queries", []),
        max_items_per_source=max_items,
    )


# ─── arXiv fetcher ────────────────────────────────────────────────────────────

ARXIV_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def _arxiv_score(title: str, summary: str, keywords: list[str]) -> float:
    """Score a paper by keyword presence."""
    title_lower = title.lower()
    summary_lower = summary.lower()
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in title_lower:
            return 1.0
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in summary_lower:
            return 0.7
    return 0.5


async def fetch_arxiv(config: TrackConfig, client) -> list[SourceItem]:
    """Fetch recent papers from arXiv Atom API."""
    import httpx

    items: list[SourceItem] = []
    seen_urls: set[str] = set()

    # Build category query: cat:cs.AI OR cat:cs.MA ...
    categories = config.arxiv_categories
    if not categories:
        return []

    cat_query = " OR ".join(f"cat:{c}" for c in categories)
    params = {
        "search_query": cat_query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": 25,
    }

    try:
        print(f"[autoresearch] INFO  arXiv: fetching categories {categories}", file=sys.stderr)
        resp = await client.get("https://export.arxiv.org/api/query", params=params, timeout=15.0)
        resp.raise_for_status()
        xml_text = resp.text
    except Exception as exc:
        print(f"[autoresearch] WARN  arXiv fetch failed: {exc}", file=sys.stderr)
        return []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        print(f"[autoresearch] WARN  arXiv XML parse error: {exc}", file=sys.stderr)
        return []

    entries = root.findall("atom:entry", ARXIV_NS)
    print(f"[autoresearch] INFO  arXiv: got {len(entries)} entries", file=sys.stderr)

    for entry in entries:
        if len(items) >= config.max_items_per_source:
            break

        # ID
        id_el = entry.find("atom:id", ARXIV_NS)
        if id_el is None or not id_el.text:
            continue
        url = id_el.text.strip()
        if url in seen_urls:
            continue
        seen_urls.add(url)

        # Title
        title_el = entry.find("atom:title", ARXIV_NS)
        title = (title_el.text or "").strip().replace("\n", " ") if title_el is not None else "Untitled"

        # Summary
        summary_el = entry.find("atom:summary", ARXIV_NS)
        summary_raw = (summary_el.text or "").strip().replace("\n", " ") if summary_el is not None else ""
        # Trim to ~200 chars for display
        summary = (summary_raw[:200] + "…") if len(summary_raw) > 200 else summary_raw

        # Authors
        author_els = entry.findall("atom:author", ARXIV_NS)
        authors = []
        for a in author_els[:3]:
            name_el = a.find("atom:name", ARXIV_NS)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        # Published date
        pub_el = entry.find("atom:published", ARXIV_NS)
        date_str = None
        if pub_el is not None and pub_el.text:
            date_str = pub_el.text.strip()[:10]  # YYYY-MM-DD

        # Categories
        cat_els = entry.findall("atom:category", ARXIV_NS)
        paper_cats = [c.get("term", "") for c in cat_els if c.get("term")]

        score = _arxiv_score(title, summary_raw, config.arxiv_keywords)

        items.append(SourceItem(
            title=title,
            url=url,
            source="arxiv",
            summary=summary,
            score=score,
            date=date_str,
            metadata={
                "authors": authors,
                "categories": paper_cats,
            },
        ))

    # Sort by score and return top N
    items.sort(key=lambda x: x.score, reverse=True)
    result = items[:5]
    print(f"[autoresearch] INFO  arXiv: returning {len(result)} items", file=sys.stderr)
    return result


# ─── GitHub Trending fetcher ───────────────────────────────────────────────────

def _parse_github_trending(html: str) -> list[dict]:
    """Parse GitHub trending page HTML. Returns list of repo dicts."""
    results = []

    # Find all <article class="Box-row"> blocks
    article_blocks = re.findall(
        r'<article\s+class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>',
        html,
        re.DOTALL | re.IGNORECASE,
    )

    if not article_blocks:
        print("[autoresearch] WARN  GitHub trending: STRUCTURE_CHANGED — no Box-row articles found", file=sys.stderr)
        return []

    for block in article_blocks:
        # Repo path — look for /owner/repo in h2 > a href
        repo_match = re.search(
            r'<h2[^>]*>\s*<a\s+href="/([^/"]+/[^/"]+)"',
            block,
            re.IGNORECASE | re.DOTALL,
        )
        if not repo_match:
            # Try alternative: any href="/{owner}/{repo}" at top of article
            repo_match = re.search(
                r'href="/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"',
                block,
                re.IGNORECASE,
            )
        if not repo_match:
            continue
        repo_path = repo_match.group(1).strip()
        repo_url = f"https://github.com/{repo_path}"

        # Description — target col-9 paragraph (avoids Star/button boilerplate)
        desc_match = re.search(r'<p[^>]*col-9[^>]*>(.*?)</p>', block, re.DOTALL | re.IGNORECASE)
        if not desc_match:
            # fallback: any <p> that doesn't start with whitespace-only or "Star"
            for m in re.finditer(r'<p[^>]*>(.*?)</p>', block, re.DOTALL | re.IGNORECASE):
                candidate = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                if candidate and not candidate.lower().startswith('star'):
                    desc_match = m
                    break
        description = ""
        if desc_match:
            raw = desc_match.group(1)
            description = re.sub(r'<[^>]+>', '', raw).strip()

        # Stars — look for star count pattern
        stars = 0
        stars_match = re.search(
            r'aria-label="[^"]*star[^"]*"\s*>\s*([\d,]+)',
            block,
            re.IGNORECASE,
        )
        if not stars_match:
            stars_match = re.search(r'([\d,]+)\s*stars?', block, re.IGNORECASE)
        if stars_match:
            try:
                stars = int(stars_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # Stars today
        stars_today = 0
        today_match = re.search(r'([\d,]+)\s*stars?\s*today', block, re.IGNORECASE)
        if today_match:
            try:
                stars_today = int(today_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # Language
        lang_match = re.search(
            r'itemprop="programmingLanguage"[^>]*>(.*?)<',
            block,
            re.IGNORECASE | re.DOTALL,
        )
        language = ""
        if lang_match:
            language = lang_match.group(1).strip()

        results.append({
            "repo_path": repo_path,
            "url": repo_url,
            "description": description,
            "stars": stars,
            "stars_today": stars_today,
            "language": language,
        })

    return results


def _repo_matches_topics(repo_path: str, description: str, topics: list[str]) -> bool:
    """Check if a repo matches any of the track topics (loose keyword match)."""
    text = (repo_path + " " + description).lower()
    for topic in topics:
        # Strip hyphens for matching
        kw = topic.lower().replace("-", " ").replace("_", " ")
        kw_nospace = topic.lower().replace("-", "").replace("_", "")
        if kw in text or kw_nospace in text:
            return True
    return False


async def fetch_github_trending(config: TrackConfig, client) -> list[SourceItem]:
    """Scrape GitHub trending page for relevant repos."""
    all_repos: list[dict] = []
    seen_urls: set[str] = set()

    languages = config.github_languages or [""]

    for lang in languages:
        url = f"https://github.com/trending/{lang}" if lang else "https://github.com/trending"
        params = {"since": "daily"}
        try:
            print(f"[autoresearch] INFO  GitHub trending: fetching {url}", file=sys.stderr)
            resp = await client.get(url, params=params, timeout=15.0,
                                    headers={"Accept": "text/html", "User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            repos = _parse_github_trending(resp.text)
            for r in repos:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    all_repos.append(r)
        except Exception as exc:
            print(f"[autoresearch] WARN  GitHub trending fetch ({lang}) failed: {exc}", file=sys.stderr)
            continue

    if not all_repos:
        return []

    print(f"[autoresearch] INFO  GitHub trending: {len(all_repos)} total repos found", file=sys.stderr)

    # Filter by topics
    matching = [r for r in all_repos if _repo_matches_topics(r["repo_path"], r["description"], config.github_topics)]

    # If no matches, use all repos (don't return empty when trending is valid)
    if not matching:
        matching = all_repos
        print("[autoresearch] INFO  GitHub trending: no topic matches, using all repos", file=sys.stderr)

    # Score by stars_today (normalised) + stars (secondary)
    max_stars_today = max((r["stars_today"] for r in matching), default=1) or 1
    max_stars = max((r["stars"] for r in matching), default=1) or 1

    items = []
    for r in matching:
        score = 0.7 * (r["stars_today"] / max_stars_today) + 0.3 * (r["stars"] / max_stars)
        owner_repo = r["repo_path"]
        desc = r["description"] or "No description available."
        items.append(SourceItem(
            title=owner_repo,
            url=r["url"],
            source="github",
            summary=desc,
            score=round(score, 4),
            date=None,
            metadata={
                "stars": r["stars"],
                "language": r["language"],
                "stars_today": r["stars_today"],
            },
        ))

    items.sort(key=lambda x: x.score, reverse=True)
    result = items[:5]
    print(f"[autoresearch] INFO  GitHub trending: returning {len(result)} items", file=sys.stderr)
    return result


# ─── Hacker News fetcher ───────────────────────────────────────────────────────

HN_BASE = "https://hacker-news.firebaseio.com/v0"


async def _fetch_hn_item(item_id: int, client) -> dict | None:
    """Fetch a single HN item."""
    try:
        resp = await client.get(f"{HN_BASE}/item/{item_id}.json", timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


async def fetch_hackernews(config: TrackConfig, client) -> list[SourceItem]:
    """Fetch top HN stories filtered by track keywords."""
    # Step 1: get top story IDs
    try:
        print("[autoresearch] INFO  HN: fetching top stories", file=sys.stderr)
        resp = await client.get(f"{HN_BASE}/topstories.json", timeout=15.0)
        resp.raise_for_status()
        all_ids: list[int] = resp.json()
    except Exception as exc:
        print(f"[autoresearch] WARN  HN topstories fetch failed: {exc}", file=sys.stderr)
        return []

    # Take top N IDs (scan depth from plan: 60)
    scan_ids = all_ids[:60]
    print(f"[autoresearch] INFO  HN: scanning top {len(scan_ids)} stories", file=sys.stderr)

    # Step 2: fetch items in batches of 10
    items_data: list[dict] = []

    async def fetch_batch(batch: list[int]) -> list[dict]:
        tasks = [_fetch_hn_item(id_, client) for id_ in batch]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    try:
        all_items = await asyncio.wait_for(
            _fetch_hn_items_all(scan_ids, client),
            timeout=30.0,
        )
    except asyncio.TimeoutError:
        print("[autoresearch] WARN  HN: 30s budget exceeded, using partial results", file=sys.stderr)
        all_items = []

    if not all_items:
        # Fallback: try just first 10
        try:
            all_items = await fetch_batch(scan_ids[:10])
        except Exception as exc:
            print(f"[autoresearch] WARN  HN batch fallback failed: {exc}", file=sys.stderr)
            return []

    print(f"[autoresearch] INFO  HN: fetched {len(all_items)} story details", file=sys.stderr)

    # Step 3: filter by keywords
    keywords_lower = [kw.lower() for kw in config.hn_keywords]

    def matches(item: dict) -> bool:
        title = (item.get("title") or "").lower()
        url = (item.get("url") or "").lower()
        return any(kw in title or kw in url for kw in keywords_lower)

    matched = [item for item in all_items if matches(item) and item.get("type") == "story"]

    print(f"[autoresearch] INFO  HN: {len(matched)} stories match keywords", file=sys.stderr)

    if not matched:
        # Return top 5 regardless, sorted by score
        matched = [item for item in all_items if item.get("type") == "story"][:10]

    # Sort by score (HN points)
    matched.sort(key=lambda x: x.get("score", 0), reverse=True)

    max_points = max((item.get("score", 0) for item in matched), default=1) or 1

    result = []
    for item in matched[:config.max_items_per_source]:
        points = item.get("score", 0)
        comments = item.get("descendants", 0)
        title = item.get("title", "Untitled")
        url = item.get("url") or f"https://news.ycombinator.com/item?id={item.get('id', '')}"
        hn_id = item.get("id", 0)
        domain = ""
        if item.get("url"):
            domain_match = re.search(r"https?://(?:www\.)?([^/]+)", item["url"])
            if domain_match:
                domain = domain_match.group(1)

        result.append(SourceItem(
            title=title,
            url=url,
            source="hackernews",
            summary=f"_{domain}_" if domain else f"HN discussion ({comments} comments)",
            score=round(points / max_points, 4),
            date=None,
            metadata={
                "points": points,
                "comments": comments,
                "hn_id": hn_id,
            },
        ))

    result = result[:5]
    print(f"[autoresearch] INFO  HN: returning {len(result)} items", file=sys.stderr)
    return result


async def _fetch_hn_items_all(ids: list[int], client) -> list[dict]:
    """Fetch HN items in batches of 10."""
    results = []
    batch_size = 10
    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        tasks = [_fetch_hn_item(id_, client) for id_ in batch]
        batch_results = await asyncio.gather(*tasks)
        results.extend(r for r in batch_results if r is not None)
    return results


# ─── Web narratives fetcher (Brave Search API) ────────────────────────────────

async def fetch_web_narratives(config: TrackConfig, client) -> list[SourceItem]:
    """Search for fresh narratives via Brave Search API (primary) or openclaw web_search (fallback).

    Primary: BRAVE_API_KEY env var → direct Brave REST API
    Fallback: openclaw web_search subprocess (uses agent's native Brave integration)
    """
    api_key = os.environ.get("BRAVE_API_KEY", "")

    if api_key:
        # Primary: direct Brave API
        return await _fetch_web_brave_direct(config, client, api_key)

    # Fallback: openclaw native web_search via subprocess helper
    print("[autoresearch] INFO  web: no BRAVE_API_KEY — trying openclaw native web_search", file=sys.stderr)
    return await _fetch_web_native(config)


async def _fetch_web_brave_direct(config: TrackConfig, client, api_key: str) -> list[SourceItem]:
    """Fetch via direct Brave Search API (requires BRAVE_API_KEY)."""
    all_items: list[SourceItem] = []
    seen_urls: set[str] = set()
    headers = {
        "X-Subscription-Token": api_key,
        "Accept": "application/json",
    }
    for query in config.web_queries:
        params = {"q": query, "count": 5, "freshness": "pd"}
        try:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            print(f"[autoresearch] WARN  web: Brave direct failed for '{query}': {exc}", file=sys.stderr)
            continue
        for rank, result in enumerate(data.get("web", {}).get("results", [])):
            url = result.get("url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            title = result.get("title", "Untitled")
            snippet = result.get("description", "")
            all_items.append(SourceItem(
                title=title,
                url=url,
                source="web",
                summary=snippet[:200] + "…" if len(snippet) > 200 else snippet,
                score=round(max(0.1, 1.0 - rank * 0.15), 4),
                date=result.get("page_age", None),
                metadata={"snippet": snippet},
            ))
        if len(all_items) >= config.max_items_per_source:
            break
    result = all_items[:5]
    print(f"[autoresearch] INFO  web: returning {len(result)} items (direct)", file=sys.stderr)
    return result


async def _fetch_web_native(config: TrackConfig) -> list[SourceItem]:
    """Fallback: call openclaw's native web_search via a helper script."""
    import subprocess
    helper = Path(__file__).parent / "web_search_helper.py"
    if not helper.exists():
        print("[autoresearch] WARN  web: web_search_helper.py not found — skipping", file=sys.stderr)
        return []

    all_items: list[SourceItem] = []
    seen_urls: set[str] = set()
    queries = config.web_queries[:2]  # limit to 2 queries for the native path

    for query in queries:
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(helper), query,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
            if proc.returncode != 0:
                print(f"[autoresearch] WARN  web: helper failed for '{query}': {stderr.decode()[:200]}", file=sys.stderr)
                continue
            items = json.loads(stdout.decode())
            for rank, item in enumerate(items):
                url = item.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                all_items.append(SourceItem(
                    title=item.get("title", "Untitled"),
                    url=url,
                    source="web",
                    summary=item.get("snippet", "")[:200],
                    score=round(max(0.1, 1.0 - rank * 0.15), 4),
                    metadata={"snippet": item.get("snippet", "")},
                ))
            if len(all_items) >= config.max_items_per_source:
                break
        except asyncio.TimeoutError:
            print(f"[autoresearch] WARN  web: helper timed out for '{query}'", file=sys.stderr)
        except Exception as exc:
            print(f"[autoresearch] WARN  web: helper error for '{query}': {exc}", file=sys.stderr)

    result = all_items[:5]
    print(f"[autoresearch] INFO  web: returning {len(result)} items (native fallback)", file=sys.stderr)
    return result


# ─── Combined fetcher ──────────────────────────────────────────────────────────

async def fetch_all(config: TrackConfig, config_path: Path) -> dict[str, list[SourceItem]]:
    """Run all fetchers concurrently via asyncio.gather.

    Returns: {"arxiv": [...], "github": [...], "hackernews": [...], "web": [...]}
    Each source that fails returns [] (logged, not raised).
    """
    import httpx

    timeout = httpx.Timeout(15.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        results = await asyncio.gather(
            fetch_arxiv(config, client),
            fetch_github_trending(config, client),
            fetch_hackernews(config, client),
            fetch_web_narratives(config, client),
            return_exceptions=True,
        )

    def safe(result, source_name: str) -> list[SourceItem]:
        if isinstance(result, Exception):
            print(f"[autoresearch] ERROR {source_name} raised exception: {result}", file=sys.stderr)
            return []
        return result or []

    return {
        "arxiv": safe(results[0], "arXiv"),
        "github": safe(results[1], "GitHub"),
        "hackernews": safe(results[2], "HN"),
        "web": safe(results[3], "web"),
    }
