#!/usr/bin/env python3
"""Native web search helper for autoresearch.

Called as a subprocess: python web_search_helper.py "<query>"
Returns JSON list of {title, url, snippet} to stdout.

Uses the openclaw Brave Search API (same key the agent uses for web_search tool).
Falls back to a simple httpx Brave call if OPENCLAW_BRAVE_KEY is set,
otherwise tries to read from openclaw config.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def get_brave_key() -> str | None:
    """Try to find Brave API key from openclaw config."""
    # Check env first
    key = os.environ.get("BRAVE_API_KEY") or os.environ.get("OPENCLAW_BRAVE_KEY")
    if key:
        return key

    # Try openclaw config paths
    config_paths = [
        Path.home() / ".openclaw" / "config.json",
        Path.home() / ".openclaw" / "agents" / "main" / "config.json",
    ]
    for path in config_paths:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                # Look for brave key in various config structures
                brave = (
                    data.get("braveApiKey")
                    or data.get("brave_api_key")
                    or data.get("search", {}).get("braveApiKey")
                    or data.get("tools", {}).get("web_search", {}).get("apiKey")
                )
                if brave:
                    return brave
            except Exception:
                pass
    return None


def search_brave(query: str, api_key: str, count: int = 5) -> list[dict]:
    """Search Brave API and return list of results."""
    import urllib.request
    import urllib.parse

    params = urllib.parse.urlencode({"q": query, "count": count, "freshness": "pw"})
    url = f"https://api.search.brave.com/res/v1/web/search?{params}"
    req = urllib.request.Request(url, headers={
        "X-Subscription-Token": api_key,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    results = []
    for item in data.get("web", {}).get("results", [])[:count]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("description", ""),
        })
    return results


def main() -> None:
    if len(sys.argv) < 2:
        print("[]")
        return

    query = sys.argv[1]
    api_key = get_brave_key()

    if not api_key:
        print("[]", file=sys.stdout)
        print(f"[web_search_helper] no API key found", file=sys.stderr)
        return

    try:
        results = search_brave(query, api_key)
        print(json.dumps(results))
    except Exception as exc:
        print("[]", file=sys.stdout)
        print(f"[web_search_helper] search failed: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
