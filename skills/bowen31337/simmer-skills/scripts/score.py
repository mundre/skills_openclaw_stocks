#!/usr/bin/env python3
"""
Simmer Score — Score and rank Simmer opportunities for trading.
Reads brief JSON from stdin (output of brief.py), outputs ranked recommendations.

Scoring criteria:
  - Divergence: simmer price vs external (Polymarket/Kalshi) price gap
  - Domain edge: AI/tech/crypto markets where we have knowledge advantage
  - Liquidity signal: opportunity_score from Simmer API
  - Time filter: >1h to resolution, <30 days out (not too far)
  - Price filter: 0.05 < price < 0.95 (not already decided)

Usage:
    uv run python skills/simmer/scripts/brief.py | uv run python skills/simmer/scripts/score.py
    uv run python skills/simmer/scripts/score.py < brief.json
    uv run python skills/simmer/scripts/score.py --top 5 --min-confidence 0.6
    uv run python skills/simmer/scripts/score.py --sim-amount 50 --usdc-amount 5
"""

import argparse
import json
import sys
from datetime import datetime, timezone

# Domain keyword weights for edge scoring
# Higher = stronger knowledge advantage for us
DOMAIN_WEIGHTS = {
    # Strong AI/LLM edge — we know this domain
    "anthropic": 3.5, "openai": 3.5, "gemini": 3.5, "claude": 3.5,
    "gpt": 3.5, "llm": 3.0, "ai model": 3.5, "best ai": 3.5,
    "large language": 3.0, "foundation model": 3.0,
    # Tech company edge
    "google": 2.5, "apple": 2.0, "microsoft": 2.5, "meta": 2.0,
    "nvidia": 2.5,
    # Political/macro — some edge
    "fed chair": 2.5, "fed reserve": 2.0, "federal reserve": 2.0,
    "trump": 1.0, "election": 0.8,
    # Crypto macro (not coinflip)
    "will bitcoin": 1.5, "will ethereum": 1.5, "will btc": 1.5,
    # PENALISE: short-term coinflip BTC Up/Down (no edge, random)
    "bitcoin up or down": -3.0,
    "btc up or down": -3.0,
}

TAG_WEIGHTS = {
    "ai": 2.0, "tech": 1.5,
    "polymarket": 0.3, "kalshi": 0.3,
    "fast": -2.0,   # very short-term = coinflip, strongly penalise
    "sports": -2.0, # sports = no edge
    "crypto": 0.5,
}

MIN_HOURS = 1.0              # minimum hours to resolution
MAX_HOURS = 4 * 365 * 24.0  # maximum hours to resolution (4 years)
MIN_PRICE = 0.05             # minimum probability (not already decided)
MAX_PRICE = 0.95             # maximum probability
LONG_TERM_THRESHOLD = 30 * 24.0  # >30 days = long-term (apply confidence discount)


def parse_tags(tags_str: str) -> list[str]:
    try:
        return json.loads(tags_str)
    except Exception:
        return []


def domain_edge_score(question: str, tags: list[str]) -> float:
    """Score based on our knowledge domain advantage."""
    q_lower = question.lower()
    score = 0.0

    for keyword, weight in DOMAIN_WEIGHTS.items():
        if keyword in q_lower:
            score += weight

    for tag in tags:
        tag_lower = tag.lower()
        for t, w in TAG_WEIGHTS.items():
            if t in tag_lower:
                score += w

    return min(score, 5.0)  # cap at 5


def divergence_score(current_price: float | None, external_price: float | None) -> tuple[float, float, str]:
    """
    Score based on price divergence between Simmer and external market.
    Returns (score, divergence_pct, direction).
    """
    if current_price is None or external_price is None:
        return 0.0, 0.0, "unknown"

    diff = external_price - current_price  # positive = external thinks YES is more likely
    abs_diff = abs(diff)

    # Score: 0–5 based on magnitude of divergence
    if abs_diff < 0.02:
        div_score = 0.0
    elif abs_diff < 0.05:
        div_score = 1.0
    elif abs_diff < 0.10:
        div_score = 2.0
    elif abs_diff < 0.15:
        div_score = 3.0
    elif abs_diff < 0.25:
        div_score = 4.0
    else:
        div_score = 5.0

    # Direction: if external > simmer → external thinks YES is underpriced on simmer → trade YES
    direction = "yes" if diff > 0 else "no"
    return div_score, round(diff * 100, 1), direction


def score_opportunity(opp: dict) -> dict | None:
    """Score a single opportunity. Returns None if filtered out."""
    question = opp.get("question", "")
    current_price = opp.get("current_price")
    external_price = opp.get("external_price_yes")
    hours = opp.get("hours_to_resolution")
    opportunity_score_api = opp.get("opportunity_score", 0) or 0
    tags = parse_tags(opp.get("tags", "[]"))

    # ── Filters ────────────────────────────────────────────────────────────────
    if hours is None:
        return None
    if hours < MIN_HOURS or hours > MAX_HOURS:
        return None
    if current_price is None:
        return None
    if not (MIN_PRICE <= current_price <= MAX_PRICE):
        return None

    # ── Scoring ────────────────────────────────────────────────────────────────
    div_score, div_pct, direction = divergence_score(current_price, external_price)
    edge = domain_edge_score(question, tags)
    # API opportunity score carries heavy weight — Simmer's own signal
    api_bonus = min(opportunity_score_api / 10.0, 5.0)  # 0–100 → 0–5

    total = div_score + edge + api_bonus

    # Long-term discount: >30 days = reduce confidence (more uncertainty)
    long_term_discount = 1.0
    if hours > LONG_TERM_THRESHOLD:
        long_term_discount = max(0.4, 1.0 - (hours - LONG_TERM_THRESHOLD) / (MAX_HOURS * 2))

    confidence = min((total / 12.0) * long_term_discount, 0.99)  # normalise to 0–1

    # Never recommend if negative score (penalised market)
    if total <= 0:
        return None

    # Determine side
    side = direction  # follows divergence
    if external_price is None or div_pct == 0:
        # No divergence signal: use domain edge to pick the side with mispricing
        # If simmer price > 0.6 and we have edge → likely overpriced → trade NO
        side = "no" if current_price > 0.6 else "yes"

    # Build reasoning
    parts = []
    if div_pct != 0:
        parts.append(f"divergence {div_pct:+.1f}% vs external → {side.upper()}")
    if edge > 0:
        parts.append(f"domain edge {edge:.1f}/5")
    if opportunity_score_api > 0:
        parts.append(f"API score {opportunity_score_api:.0f}")
    if hours > LONG_TERM_THRESHOLD:
        parts.append(f"long-term discount applied ({hours/24:.0f}d)")
    reasoning = "; ".join(parts) if parts else "rule-based scoring"

    return {
        "market_id": opp["market_id"],
        "question": question,
        "side": side,
        "current_price": current_price,
        "external_price_yes": external_price,
        "divergence_pct": div_pct,
        "hours_to_resolution": hours,
        "resolves_at": opp.get("resolves_at"),
        "url": opp.get("url"),
        "scores": {
            "divergence": round(div_score, 2),
            "domain_edge": round(edge, 2),
            "api_bonus": round(api_bonus, 2),
            "total": round(total, 2),
        },
        "confidence": round(confidence, 3),
        "reasoning": reasoning,
        "tags": tags,
    }


def main():
    parser = argparse.ArgumentParser(description="Simmer Score — rank opportunities")
    parser.add_argument("--top", type=int, default=5, help="Number of top picks to output")
    parser.add_argument("--min-confidence", type=float, default=0.3,
                        help="Minimum confidence threshold (0–1)")
    parser.add_argument("--sim-amount", type=float, default=100.0,
                        help="$SIM amount per trade")
    parser.add_argument("--usdc-amount", type=float, default=0.0,
                        help="USDC amount per trade (real money, set carefully)")
    args = parser.parse_args()

    # Read brief from stdin
    try:
        brief = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": f"Invalid JSON from brief: {e}"}))
        sys.exit(1)

    if not brief.get("ok"):
        print(json.dumps({"ok": False, "error": "Brief reported failure", "brief": brief}))
        sys.exit(1)

    opportunities = brief.get("opportunities", [])
    portfolio = brief.get("portfolio", {})
    risk_alerts = brief.get("risk_alerts", [])

    # Score all opportunities
    scored = []
    for opp in opportunities:
        result = score_opportunity(opp)
        if result and result["confidence"] >= args.min_confidence:
            scored.append(result)

    # Sort by confidence descending
    scored.sort(key=lambda x: x["scores"]["total"], reverse=True)
    top_picks = scored[:args.top]

    # Attach trade parameters
    for pick in top_picks:
        pick["trade"] = {
            "sim_amount": args.sim_amount,
            "usdc_amount": args.usdc_amount,
            "venue": "simmer",
            "source": "sdk:lobster-pipeline",
        }

    # Build summary for approval display
    summary_lines = []
    summary_lines.append(f"Portfolio: {portfolio.get('sim_balance', '?')} $SIM | "
                         f"{portfolio.get('usdc_balance', '?')} USDC | "
                         f"{portfolio.get('positions_count', '?')} positions")
    if risk_alerts:
        summary_lines.append(f"⚠️  {len(risk_alerts)} RISK ALERT(S): "
                             + "; ".join(str(a) for a in risk_alerts[:3]))

    summary_lines.append(f"\nTop {len(top_picks)} picks (of {len(opportunities)} opportunities):")
    for i, pick in enumerate(top_picks, 1):
        summary_lines.append(
            f"  {i}. [{pick['side'].upper()}] {pick['question'][:60]}"
            f" | conf={pick['confidence']:.0%}"
            f" | {pick['hours_to_resolution']:.1f}h"
            f" | {pick['reasoning'][:60]}"
        )

    output = {
        "ok": True,
        "summary": "\n".join(summary_lines),
        "risk_alerts": risk_alerts,
        "portfolio": portfolio,
        "picks": top_picks,
        "stats": {
            "opportunities_evaluated": len(opportunities),
            "passed_filter": len(scored),
            "top_picks": len(top_picks),
        },
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
