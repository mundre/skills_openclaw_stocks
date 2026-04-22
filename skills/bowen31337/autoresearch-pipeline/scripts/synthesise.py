"""Synthesise raw source data into a structured markdown report."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from dataclasses import dataclass

# SourceItem is imported lazily to avoid circular; callers import it from sources.py


def deduplicate(items: list) -> list:
    """Remove items with duplicate URLs. Keep highest-scored version."""
    seen: dict[str, object] = {}
    for item in items:
        url = item.url
        if url not in seen or item.score > seen[url].score:
            seen[url] = item
    return list(seen.values())


def rank_items(items: list, max_items: int = 10) -> list:
    """Sort by score descending, take top N."""
    return sorted(items, key=lambda x: x.score, reverse=True)[:max_items]


def _format_arxiv_item(item, idx: int) -> str:
    """Format a single arXiv paper item."""
    meta = item.metadata or {}
    authors = ", ".join(meta.get("authors", []))
    categories = ", ".join(meta.get("categories", []))
    date_str = item.date or "unknown"
    lines = [
        f"{idx}. **[{item.title}]({item.url})**",
        f"   > {item.summary}",
        f"   _Authors: {authors} | Categories: {categories} | Published: {date_str}_",
    ]
    return "\n".join(lines)


def _format_github_item(item, idx: int) -> str:
    """Format a single GitHub trending item."""
    meta = item.metadata or {}
    stars = meta.get("stars", 0)
    language = meta.get("language", "")
    stars_today = meta.get("stars_today", 0)
    stars_str = f"⭐ {stars:,}" if stars else ""
    today_str = f"📈 +{stars_today} today" if stars_today else ""
    lang_str = f"{language}" if language else ""
    extras = " | ".join(filter(None, [stars_str, today_str, lang_str]))
    desc = item.summary or "No description available."
    lines = [
        f"{idx}. **[{item.title}]({item.url})**" + (f" — {extras}" if extras else ""),
        f"   > {desc}",
    ]
    return "\n".join(lines)


def _format_hn_item(item, idx: int) -> str:
    """Format a single HN story item."""
    meta = item.metadata or {}
    points = meta.get("points", 0)
    comments = meta.get("comments", 0)
    summary = item.summary or ""
    lines = [
        f"{idx}. **[{item.title}]({item.url})** — {points} pts, {comments} comments",
        f"   > {summary}",
    ]
    return "\n".join(lines)


def _format_web_item(item, idx: int) -> str:
    """Format a single web search result item."""
    snippet = item.summary or ""
    lines = [
        f"{idx}. **[{item.title}]({item.url})**",
        f"   > {snippet}",
    ]
    return "\n".join(lines)


def build_section(heading: str, items: list, formatter, max_items: int = 5) -> str:
    """Format a section of the report as markdown."""
    if not items:
        return f"## {heading}\n\n_No items found for this source._\n"

    top = items[:max_items]
    lines = [f"## {heading}", ""]
    for i, item in enumerate(top, 1):
        lines.append(formatter(item, i))
        lines.append("")

    lines.append(f"_(up to {max_items} items)_")
    return "\n".join(lines)


def build_teaser(track_display_name: str, sources: dict) -> str:
    """Generate a 3-line Telegram teaser."""
    arxiv_items = sources.get("arxiv", [])
    github_items = sources.get("github", [])
    hn_items = sources.get("hackernews", [])
    web_items = sources.get("web", [])

    all_empty = not any([arxiv_items, github_items, hn_items, web_items])
    if all_empty:
        return f"⚠️ **Nightly Research: {track_display_name}** — all sources failed. Check logs."

    # Line 1
    line1 = f"🔬 **Nightly Research: {track_display_name}**"

    # Line 2 — top paper
    if arxiv_items:
        paper = arxiv_items[0]
        title_short = paper.title[:60] + "…" if len(paper.title) > 60 else paper.title
        summary_short = paper.summary[:80] + "…" if len(paper.summary) > 80 else paper.summary
        line2 = f"• Top paper: {title_short} — {summary_short}"
    elif web_items:
        item = web_items[0]
        title_short = item.title[:60] + "…" if len(item.title) > 60 else item.title
        line2 = f"• Top article: {title_short}"
    else:
        line2 = "• Papers: none available"

    # Line 3 — trending + HN
    parts = []
    if github_items:
        gh = github_items[0]
        meta = gh.metadata or {}
        stars = meta.get("stars_today", meta.get("stars", 0))
        parts.append(f"Trending: {gh.title} ⭐{stars}")
    if hn_items:
        hn = hn_items[0]
        title_short = hn.title[:50] + "…" if len(hn.title) > 50 else hn.title
        parts.append(f"HN: {title_short}")

    if parts:
        line3 = "• " + " | ".join(parts)
    else:
        line3 = "• Check the full report for details"

    return "\n".join([line1, line2, line3])


def build_report(
    track_display_name: str,
    track_name: str,
    sources: dict,
    run_timestamp: str,
    next_track_display: str = "",
) -> tuple[str, str]:
    """Build the full markdown report + teaser.

    Returns: (full_report_markdown, teaser_text)
    """
    from state import TRACKS  # noqa: avoid circular at module level

    arxiv_items = rank_items(sources.get("arxiv", []), 5)
    github_items = rank_items(sources.get("github", []), 5)
    hn_items = rank_items(sources.get("hackernews", []), 5)
    web_items = rank_items(sources.get("web", []), 5)

    # Format timestamp for display (AEST)
    try:
        ts_dt = datetime.fromisoformat(run_timestamp)
    except Exception:
        ts_dt = datetime.now(timezone.utc)
    # Convert to AEST for display (UTC+10, or AEDT UTC+11 — just label as AEST)
    from datetime import timedelta
    aest_dt = ts_dt + timedelta(hours=10)  # approximate AEST
    ts_display = aest_dt.strftime("%Y-%m-%d %H:%M AEST")

    # Track position
    track_index = TRACKS.index(track_name) + 1 if track_name in TRACKS else "?"
    track_total = len(TRACKS)

    report_lines = [
        f"# 🔬 Nightly Research: {track_display_name}",
        "",
        f"> Generated: {ts_display} | Track: {track_name} ({track_index} of {track_total})",
        "",
        "---",
        "",
    ]

    # Papers section
    report_lines.append(build_section(
        "📄 Top Papers (arXiv)",
        arxiv_items,
        _format_arxiv_item,
        max_items=5,
    ))
    report_lines.append("\n---\n")

    # GitHub section
    report_lines.append(build_section(
        "🔥 Trending Repos (GitHub)",
        github_items,
        _format_github_item,
        max_items=5,
    ))
    report_lines.append("\n---\n")

    # HN section
    report_lines.append(build_section(
        "🗞️ Hacker News Highlights",
        hn_items,
        _format_hn_item,
        max_items=5,
    ))
    report_lines.append("\n---\n")

    # Web section (omit if empty)
    if web_items:
        report_lines.append(build_section(
            "🌐 Fresh Narratives (Web)",
            web_items,
            _format_web_item,
            max_items=5,
        ))
        report_lines.append("\n---\n")

    # Source summary table
    def _status(items: list, source_name: str, was_skipped: bool = False) -> str:
        if was_skipped:
            return "⏭️ skipped"
        if not items:
            return "❌ failed"
        if len(items) < 3:
            return "⚠️ partial"
        return "✅"

    web_skipped = not bool(os.environ.get("BRAVE_API_KEY", "")) if web_items == [] else False

    summary_rows = [
        f"| arXiv | {len(sources.get('arxiv', []))} | {len(arxiv_items)} | {_status(arxiv_items, 'arxiv')} |",
        f"| GitHub Trending | {len(sources.get('github', []))} | {len(github_items)} | {_status(github_items, 'github')} |",
        f"| Hacker News | {len(sources.get('hackernews', []))} | {len(hn_items)} | {_status(hn_items, 'hackernews')} |",
        f"| Web Search | {len(sources.get('web', []))} | {len(web_items)} | {_status(web_items, 'web', web_skipped)} |",
    ]

    report_lines.extend([
        "## 📊 Source Summary",
        "",
        "| Source | Items Found | Items Used | Status |",
        "|--------|------------|------------|--------|",
    ])
    report_lines.extend(summary_rows)
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    next_track_str = next_track_display or "—"
    report_lines.append(f"_Next track: {next_track_str} | Archive: memory/autoresearch-archive.md_")

    full_report = "\n".join(report_lines)
    teaser = build_teaser(track_display_name, sources)

    return full_report, teaser


# Make os available for the web_skipped check
