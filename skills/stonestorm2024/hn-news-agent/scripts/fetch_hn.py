#!/usr/bin/env python3
"""
Hacker News 新闻采集脚本
用法:
  python3 fetch_hn.py [top|newest|ask|show] [limit]
"""

import json
import sys
import re
import argparse
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

HN_BASE = "https://hacker-news.firebaseio.com/v0"
HN_WEB = "https://news.ycombinator.com"


def get_top_stories(limit=15):
    """获取Top故事"""
    if not HAS_REQUESTS:
        return fallback_fetch(f"{HN_WEB}/news", limit)
    
    try:
        resp = requests.get(f"{HN_BASE}/topstories.json", timeout=10)
        ids = resp.json()[:limit]
        
        stories = []
        for story_id in ids:
            item_resp = requests.get(f"{HN_BASE}/item/{story_id}.json", timeout=10)
            story = item_resp.json()
            if story and story.get("url"):
                stories.append(format_story(story))
        return stories
    except Exception as e:
        return [{"error": str(e), "type": "top", "count": limit}]


def get_newest_stories(limit=15):
    """获取最新故事"""
    if not HAS_REQUESTS:
        return fallback_fetch(f"{HN_WEB}/newest", limit)
    
    try:
        resp = requests.get(f"{HN_BASE}/newstories.json", timeout=10)
        ids = resp.json()[:limit]
        
        stories = []
        for story_id in ids:
            item_resp = requests.get(f"{HN_BASE}/item/{story_id}.json", timeout=10)
            story = item_resp.json()
            if story:
                stories.append(format_story(story))
        return stories
    except Exception as e:
        return [{"error": str(e), "type": "newest", "count": limit}]


def get_ask_hn(limit=10):
    """获取 Ask HN 帖子"""
    if not HAS_REQUESTS:
        return fallback_fetch(f"{HN_WEB}/ask", limit)
    
    try:
        resp = requests.get(f"{HN_BASE}/askstories.json", timeout=10)
        ids = resp.json()[:limit]
        
        stories = []
        for story_id in ids:
            item_resp = requests.get(f"{HN_BASE}/item/{story_id}.json", timeout=10)
            story = item_resp.json()
            if story:
                stories.append(format_story(story))
        return stories
    except Exception as e:
        return [{"error": str(e), "type": "ask", "count": limit}]


def get_show_hn(limit=10):
    """获取 Show HN 帖子"""
    if not HAS_REQUESTS:
        return fallback_fetch(f"{HN_WEB}/show", limit)
    
    try:
        resp = requests.get(f"{HN_BASE}/showstories.json", timeout=10)
        ids = resp.json()[:limit]
        
        stories = []
        for story_id in ids:
            item_resp = requests.get(f"{HN_BASE}/item/{story_id}.json", timeout=10)
            story = item_resp.json()
            if story:
                stories.append(format_story(story))
        return stories
    except Exception as e:
        return [{"error": str(e), "type": "show", "count": limit}]


def fallback_fetch(url, limit):
    """无requests库时的后备方案（简化版）"""
    return [{"note": "Install requests: pip3 install requests", "url": url, "count": limit}]


def format_story(story):
    """格式化单条故事"""
    score = story.get("score", 0)
    comments = story.get("descendants", 0)
    title = story.get("title", "No Title")
    url = story.get("url", f"{HN_WEB}/item?id={story.get('id')}")
    story_id = story.get("id")
    by = story.get("by", "unknown")
    time_ts = story.get("time", 0)
    
    # 提取域名
    domain = ""
    if url:
        match = re.match(r'https?://([^/]+)', url)
        if match:
            domain = match.group(1)
    
    # 分类
    category = classify(title, url)
    
    return {
        "id": story_id,
        "title": title,
        "url": url,
        "domain": domain,
        "score": score,
        "comments": comments,
        "by": by,
        "time": datetime.fromtimestamp(time_ts).strftime("%H:%M") if time_ts else "",
        "category": category,
        "hn_url": f"{HN_WEB}/item?id={story_id}"
    }


def classify(title, url):
    """简单关键词分类"""
    text = (title + " " + url).lower()
    
    ai_keywords = ["ai", "llm", "gpt", "claude", "openai", "anthropic", "gemini", "model", "machine learning", "neural", "chatgpt", "artificial intelligence"]
    oss_keywords = ["open source", "github", "open-source", "repository", "library", "framework", "released", "launch", "launched"]
    tech_keywords = ["python", "javascript", "rust", "golang", "web", "api", "database", "server", "cloud", "aws", "docker", "kubernetes"]
    startup_keywords = ["startup", "y combinator", "yc", "funding", "raised", "series", "launch", "product hunt"]
    security_keywords = ["security", "vulnerability", "hack", "breach", "cve", "exploit", "attack"]
    
    if any(k in text for k in ai_keywords):
        return "🤖 AI"
    if any(k in text for k in security_keywords):
        return "🔒 安全"
    if any(k in text for k in oss_keywords):
        return "📦 开源"
    if any(k in text for k in startup_keywords):
        return "🚀 创业"
    if any(k in text for k in tech_keywords):
        return "💻 技术"
    return "🌐 综合"


def format_output(stories, title="Hacker News 热点", lang="zh"):
    """格式化输出"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    header = f"📰 {title} — {now}\n"
    header += "=" * 50 + "\n\n"
    
    lines = []
    for i, s in enumerate(stories, 1):
        if "error" in s:
            lines.append(f"❌ Error: {s['error']}")
            continue
        
        cat = s.get("category", "🌐")
        score_emoji = "🔥" if s["score"] >= 300 else ("⚡" if s["score"] >= 100 else "  ")
        
        lines.append(f"{i}. {cat} {s['title']}")
        lines.append(f"   {score_emoji} {s['score']}⭐ | 💬 {s['comments']} | 👤 {s['by']}")
        lines.append(f"   🔗 {s['url']}")
        lines.append(f"   💬 {s['hn_url']}")
        lines.append("")
    
    return header + "\n".join(lines)


def filter_by_keyword(stories, keywords):
    """按关键词过滤"""
    filtered = []
    for s in stories:
        text = (s.get("title", "") + " " + s.get("url", "")).lower()
        if any(kw.lower() in text for kw in keywords):
            filtered.append(s)
    return filtered


def filter_by_score(stories, threshold):
    """按分数过滤"""
    return [s for s in stories if s.get("score", 0) >= threshold]


def main():
    parser = argparse.ArgumentParser(description="Hacker News Fetcher")
    parser.add_argument("cmd", nargs="?", default="top", choices=["top", "newest", "ask", "show"],
                        help="Command: top (default), newest, ask, show")
    parser.add_argument("-n", "--limit", type=int, default=15, help="Number of items")
    parser.add_argument("-k", "--keywords", nargs="*", help="Filter keywords")
    parser.add_argument("-s", "--min-score", type=int, default=0, help="Minimum score")
    parser.add_argument("-o", "--output", choices=["text", "json"], default="text")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    
    args = parser.parse_args()
    
    if args.cmd == "top":
        stories = get_top_stories(args.limit)
    elif args.cmd == "newest":
        stories = get_newest_stories(args.limit)
    elif args.cmd == "ask":
        stories = get_ask_hn(args.limit)
    elif args.cmd == "show":
        stories = get_show_hn(args.limit)
    else:
        stories = get_top_stories(args.limit)
    
    # 过滤
    if args.keywords:
        stories = filter_by_keyword(stories, args.keywords)
    if args.min_score > 0:
        stories = filter_by_score(stories, args.min_score)
    
    # 输出
    if args.output == "json":
        print(json.dumps(stories, ensure_ascii=False, indent=2))
    else:
        title_map = {
            "top": "Hacker News Top 热点",
            "newest": "Hacker News 最新发布",
            "ask": "Ask HN 精华",
            "show": "Show HN 精选"
        }
        print(format_output(stories, title_map[args.cmd], args.lang))


if __name__ == "__main__":
    main()
