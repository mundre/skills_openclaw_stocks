#!/usr/bin/env python3
import argparse
import hashlib
import json
import random
import re
import urllib.parse
import urllib.request

from typing import Dict, List, Optional

UNSPLASH_RANDOM = "https://source.unsplash.com/featured/1200x1800/?{query}"
LOREM_PICSUM = "https://picsum.photos/1200/1800"
PINTEREST_SEARCH = "https://www.pinterest.com/search/pins/?q={query}"
PINTEREST_RESOURCE = "https://www.pinterest.com/resource/BaseSearchResource/get/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"


class PinterestClient:
    def __init__(self):
        self._cache: Dict[str, object] = {}

    @staticmethod
    def _extract_cookie_value(cookies: List[str], name: str) -> Optional[str]:
        for cookie in cookies:
            if cookie.startswith(f"{name}="):
                return cookie.split("=", 1)[1].split(";", 1)[0]
        return None

    def _get_pinterest_context(self, query: str):
        if self._cache:
            return self._cache

        search_url = PINTEREST_SEARCH.format(query=urllib.parse.quote(query))
        req = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=25) as response:
            html = response.read().decode("utf-8", errors="ignore")
            cookies = response.headers.get_all("Set-Cookie") or []

        m = re.search(r'"appVersion":"([^"]+)"', html)
        app_version = m.group(1) if m else ""
        cookie = " ; ".join([c.split(";", 1)[0] for c in cookies])
        csrf = self._extract_cookie_value(cookies, "csrftoken") or ""

        if not app_version or not cookie:
            raise RuntimeError("Could not initialize Pinterest session")

        self._cache = {
            "app_version": app_version,
            "cookie": cookie,
            "csrf": csrf,
            "search_query": query,
        }
        return self._cache

    def fetch_query_images(self, query: str, limit: int = 6, seed: str | None = None) -> List[str]:
        context = self._get_pinterest_context(query)
        data = {
            "options": {
                "query": query,
                "scope": "pins",
                "page_size": max(10, limit * 2),
                "bookmarks": [],
            },
            "context": {},
        }
        payload = urllib.parse.urlencode(
            {
                "source_url": f"/search/pins/?q={urllib.parse.quote(query)}",
                "data": json.dumps(data),
                "_": "0",
            }
        )
        url = f"{PINTEREST_RESOURCE}?{payload}"

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": PINTEREST_SEARCH.format(query=urllib.parse.quote(query)),
            "Cookie": context["cookie"],
            "X-Requested-With": "XMLHttpRequest",
            "X-Pinterest-App-Version": context["app_version"],
            "X-Pinterest-PWS-Handler": "www/search",
            "X-CSRFToken": context["csrf"],
            "X-APP-VERSION": context["app_version"],
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8", errors="ignore"))

        data_obj = payload.get("resource_response", {})
        results = data_obj.get("data", {}).get("results", [])

        urls: List[str] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            images = item.get("images", {})
            if not isinstance(images, dict):
                continue

            for size_key in ("736x", "474x", "orig", "236x", "170x"):
                image_data = images.get(size_key)
                if isinstance(image_data, dict) and isinstance(image_data.get("url"), str):
                    urls.append(image_data["url"])
                    break

        if not urls:
            return []

        random.seed(seed or query)
        random.shuffle(urls)
        # de-dup while preserving random order
        uniq = []
        seen = set()
        for u in urls:
            if u not in seen:
                seen.add(u)
                uniq.append(u)

        return uniq[:limit]


def looks_like_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def build_image_url(query: str, seed: str | None = None) -> str:
    q = urllib.parse.quote(query.strip())
    if not q:
        return f"{LOREM_PICSUM}?random={urllib.parse.quote(seed or 'default')}"
    if seed:
        return f"{UNSPLASH_RANDOM.format(query=q)}&sig={urllib.parse.quote(seed)}"
    return UNSPLASH_RANDOM.format(query=q)


def build_resolved_url(slide: dict, default_query: Optional[str], pinterest_client: PinterestClient) -> Optional[str]:
    # Prefer explicit imagePath/imageUrl set by caller.
    image_query = slide.get("imageQuery")
    if slide.get("imagePath"):
        return slide["imagePath"]

    if image_query:
        return resolve_query_image(image_query, pinterest_client)

    if default_query:
        return resolve_query_image(default_query, pinterest_client)

    raise ValueError("Slide is missing imagePath, imageUrl, and imageQuery")


def resolve_query_image(query: str, pinterest_client: PinterestClient) -> str:
    # Default: pull candidate images from Pinterest.
    urls = pinterest_client.fetch_query_images(query, limit=6, seed=query)
    if urls:
        return urls[0]
    # Fallback if Pinterest returns no images
    return build_image_url(query)


def resolve_project(project: dict) -> dict:
    slides = project.get('slides', [])
    if not isinstance(slides, list):
        raise ValueError("project.slides must be a list")

    slug = project.get('slug', 'post')
    default_query = project.get('defaultImageQuery')
    pinterest_client = PinterestClient()

    for idx, slide in enumerate(slides, start=1):
        if slide.get('imagePath') or slide.get('imageUrl'):
            continue

        query = slide.get('imageQuery') or default_query
        if not query:
            raise ValueError(f"Slide {idx} is missing imagePath, imageUrl, and imageQuery")

        resolved_url = resolve_query_image(query, pinterest_client)
        slide['imageUrl'] = resolved_url
        slide['resolvedFromQuery'] = query

    return project


def parse_local_file(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description='Resolve imageQuery fields into imageUrl values.')
    parser.add_argument('project', help='Project JSON file')
    parser.add_argument('--output', help='Write resolved project JSON to this path')
    args = parser.parse_args()

    project = parse_local_file(args.project)
    resolved = resolve_project(project)
    rendered = json.dumps(resolved, ensure_ascii=False, indent=2)

    if args.output:
        out = args.output
        with open(out, 'w', encoding='utf-8') as f:
            f.write(rendered)
        print(out)
    else:
        print(rendered)


if __name__ == '__main__':
    main()
