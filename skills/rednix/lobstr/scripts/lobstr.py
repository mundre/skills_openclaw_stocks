#!/usr/bin/env python3
"""
LOBSTR — Startup Idea Scorer
Usage: python3 lobstr.py "your startup idea"
Requires: ANTHROPIC_API_KEY, EXA_API_KEY
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")

missing = []
if not ANTHROPIC_API_KEY:
    missing.append("ANTHROPIC_API_KEY")
if not EXA_API_KEY:
    missing.append("EXA_API_KEY")
if missing:
    print(f"Error: missing required environment variable(s): {', '.join(missing)}", file=sys.stderr)
    print("Export them in your shell before running lobstr.py:", file=sys.stderr)
    for key in missing:
        print(f"  export {key}=<your-key>", file=sys.stderr)
    sys.exit(1)

# ── helpers ──────────────────────────────────────────────────────────────────

def anthropic_call(model: str, system: str, user: str, max_tokens: int = 1024) -> str:
    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read())
    return body["content"][0]["text"].strip()


def exa_search(query: str, num_results: int = 5) -> list[dict]:
    payload = json.dumps({
        "query": query,
        "numResults": num_results,
        "type": "neural",
        "useAutoprompt": True,
        "contents": {"text": {"maxCharacters": 200}},
    }).encode()
    req = urllib.request.Request(
        "https://api.exa.ai/search",
        data=payload,
        headers={
            "x-api-key": EXA_API_KEY,
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
        return body.get("results", [])
    except Exception:
        return []


def grid_match(category: str, geography: str, keywords: str) -> dict:
    params = urllib.parse.urlencode({
        "category": category,
        "geography": geography,
        "keywords": keywords,
    })
    url = f"https://grid.nma.vc/api/public/vcs/match-count?{params}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except Exception:
        return {"investor_count": 0, "match_quality": "unknown"}


def score_bar(score: int) -> str:
    filled = round(score / 10)
    return "█" * filled + "░" * (10 - filled)


def color_dot(score: int) -> str:
    if score >= 70:
        return "🟢"
    if score >= 50:
        return "🟡"
    return "🔴"


# ── step 1: parse idea ────────────────────────────────────────────────────────

def parse_idea(idea: str) -> dict:
    system = (
        "You are a startup analyst. Given a startup idea, extract structured data. "
        "Reply with ONLY valid JSON, no markdown fences, no extra text."
    )
    prompt = f"""Startup idea: {idea}

Return JSON with these keys:
- problem: one sentence
- solution: one sentence
- market: short market name (e.g. "Legal Tech", "FinTech", "HealthTech")
- geography: short region (e.g. "Global", "EU", "US", "MENA", "APAC", "LATAM")
- category: one of [B2B SaaS, B2C, Marketplace, Infrastructure, DeepTech, Consumer, Other]
- queries: array of exactly 3 short search queries to find competitors
"""
    raw = anthropic_call("claude-haiku-4-5", system, prompt, max_tokens=512)
    # strip markdown fences if model adds them despite instructions
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── step 2: search competitors ────────────────────────────────────────────────

def search_competitors(queries: list[str]) -> list[str]:
    results = []
    for q in queries:
        hits = exa_search(q, num_results=4)
        for h in hits:
            title = h.get("title") or h.get("url", "")
            url = h.get("url", "")
            snippet = (h.get("text") or "")[:120]
            if title or url:
                results.append(f"• {title} ({url}) — {snippet}")
    return results[:12]  # cap context


# ── step 3: score idea ────────────────────────────────────────────────────────

def score_idea(idea: str, parsed: dict, competitors: list[str]) -> dict:
    system = (
        "You are a senior VC partner with a sharp, honest voice. "
        "Score startup ideas with precision. Reply ONLY with valid JSON, no markdown."
    )
    competitor_text = "\n".join(competitors) if competitors else "No competitors found."
    prompt = f"""Startup idea: {idea}

Problem: {parsed['problem']}
Solution: {parsed['solution']}
Market: {parsed['market']}
Geography: {parsed['geography']}
Category: {parsed['category']}

Competitor search results:
{competitor_text}

Score this idea on 6 LOBSTR dimensions, each 0-100:
- L (Landscape): How crowded/favorable is the competitive landscape?
- O (Opportunity): How large and real is the market opportunity?
- B (Business model): How clear, defensible, and scalable is the biz model?
- S (Sharpness): How crisp and differentiated is the idea vs. alternatives?
- T (Timing): Is the market timing right (tailwinds, tech readiness, cultural moment)?
- R (Reach): How easily can this scale to reach a large audience/user base?

Return JSON:
{{
  "L": {{"score": 0-100, "verdict": "one line, sharp"}},
  "O": {{"score": 0-100, "verdict": "one line, sharp"}},
  "B": {{"score": 0-100, "verdict": "one line, sharp"}},
  "S": {{"score": 0-100, "verdict": "one line, sharp"}},
  "T": {{"score": 0-100, "verdict": "one line, sharp"}},
  "R": {{"score": 0-100, "verdict": "one line, sharp"}},
  "overall": 0-100,
  "verdict": "Two sentence VC voice verdict. Honest, no fluff.",
  "build_it": true or false
}}

The overall score is a weighted judgment — not an average. Weight S and B higher.
"""
    raw = anthropic_call("claude-sonnet-4-5", system, prompt, max_tokens=1024)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── step 4: format score card ─────────────────────────────────────────────────

def format_card(idea: str, scores: dict, grid: dict) -> str:
    overall = scores["overall"]
    bar = score_bar(overall)
    build_str = "✅ BUILD IT." if scores["build_it"] else "🚫 NOT YET."

    investor_count = grid.get("investor_count", 0)
    match_quality = grid.get("match_quality", "")

    dim_labels = {
        "L": "Landscape  ",
        "O": "Opportunity",
        "B": "Biz model  ",
        "S": "Sharpness  ",
        "T": "Timing     ",
        "R": "Reach      ",
    }

    lines = [
        "🦞 LOBSTR SCAN",
        f'"{idea}"',
        "",
        f"LOBSTR SCORE  {overall}/100  {bar}",
        "",
    ]
    for key, label in dim_labels.items():
        d = scores[key]
        s = d["score"]
        v = d["verdict"]
        lines.append(f"{key}  {label}  {color_dot(s)}  {s}/100  {v}")

    lines += [
        "",
        "VERDICT",
        scores["verdict"],
        "",
        build_str,
    ]

    if investor_count:
        grid_line = f"GRID: {investor_count} investor"
        if investor_count != 1:
            grid_line += "s"
        if match_quality and match_quality != "unknown":
            grid_line += f" ({match_quality} match)"
        grid_line += " match this space → https://grid.nma.vc"
        lines.append("")
        lines.append(grid_line)

    return "\n".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 lobstr.py \"your startup idea\"", file=sys.stderr)
        sys.exit(1)

    idea = " ".join(sys.argv[1:]).strip('"').strip("'")

    # Step 1: parse
    parsed = parse_idea(idea)

    # Step 2: search
    competitors = search_competitors(parsed.get("queries", []))

    # Step 3: score
    scores = score_idea(idea, parsed, competitors)

    # Step 4: investor match
    grid = grid_match(
        category=parsed.get("category", ""),
        geography=parsed.get("geography", ""),
        keywords=parsed.get("market", idea[:60]),
    )

    # Step 5: format and print
    card = format_card(idea, scores, grid)
    print(card)


if __name__ == "__main__":
    main()
