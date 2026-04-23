#!/usr/bin/env python3
# Multi-currency Pricing Strategist - handler.py
import json, re

SKILL_INFO = {"name": "Multi-currency Pricing Strategist", "slug": "cb-multi-currency-pricing", "version": "1.0.0"}

RATES = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 149.5, "AUD": 1.53, "CAD": 1.36, "BRL": 4.97, "INR": 83.2, "KRW": 1320, "CHF": 0.88, "CNY": 7.24}

MARKET_DATA = {
    "Germany": {"currency": "EUR", "ppp_index": 0.95, "price_sensitivity": "medium", "volatility": 0.05, "review_freq": "Quarterly", "competition_level": "high"},
    "Japan": {"currency": "JPY", "ppp_index": 0.88, "price_sensitivity": "medium", "volatility": 0.08, "review_freq": "Quarterly", "competition_level": "medium"},
    "UK": {"currency": "GBP", "ppp_index": 0.92, "price_sensitivity": "medium-high", "volatility": 0.07, "review_freq": "Quarterly", "competition_level": "high"},
    "Australia": {"currency": "AUD", "ppp_index": 1.05, "price_sensitivity": "high", "volatility": 0.06, "review_freq": "Quarterly", "competition_level": "medium"},
    "Canada": {"currency": "CAD", "ppp_index": 1.02, "price_sensitivity": "medium", "volatility": 0.05, "review_freq": "Quarterly", "competition_level": "medium"},
    "France": {"currency": "EUR", "ppp_index": 0.94, "price_sensitivity": "medium", "volatility": 0.05, "review_freq": "Quarterly", "competition_level": "high"},
    "Brazil": {"currency": "BRL", "ppp_index": 1.65, "price_sensitivity": "very_high", "volatility": 0.15, "review_freq": "Monthly", "competition_level": "medium"},
    "India": {"currency": "INR", "ppp_index": 2.1, "price_sensitivity": "very_high", "volatility": 0.06, "review_freq": "Monthly", "competition_level": "high"},
    "South Korea": {"currency": "KRW", "ppp_index": 0.85, "price_sensitivity": "medium", "volatility": 0.07, "review_freq": "Quarterly", "competition_level": "high"},
    "US": {"currency": "USD", "ppp_index": 1.0, "price_sensitivity": "medium", "volatility": 0.03, "review_freq": "Quarterly", "competition_level": "very_high"},
}

SENSITIVITY_ADJ = {"very_high": 0.7, "high": 0.85, "medium-high": 0.92, "medium": 1.0}

def _parse_input(user_input):
    inp = user_input.lower()
    p = {"original_input": user_input[:100], "word_count": len(user_input.split())}
    m = re.search(r"\$?(\d+(?:\.\d+)?)", user_input.replace(",", ""))
    p["base_usd_price"] = float(m.group(1)) if m else 100.0
    found = [m for m in MARKET_DATA if m.lower() in inp]
    p["target_markets"] = found[:5] if found else list(MARKET_DATA.keys())[:5]
    cats = []
    for cat, terms in [("electronics", ["electronics", "electronic", "tech", "gadget"]),
                        ("apparel", ["apparel", "clothing", "fashion", "wear"]),
                        ("beauty", ["beauty", "cosmetics", "skincare"]),
                        ("home", ["home", "furniture", "decor"])]:
        if any(t in inp for t in terms):
            cats.append(cat)
    p["product_category"] = cats[0] if cats else "general"
    if "premium" in inp:
        p["strategy_focus"] = "premium"
    elif "competit" in inp:
        p["strategy_focus"] = "competitive"
    else:
        p["strategy_focus"] = "balanced"
    return p

def _calc_price(base_usd, market):
    data = MARKET_DATA.get(market)
    if not data:
        return None
    rate = RATES.get(data["currency"], 1.0)
    adj = SENSITIVITY_ADJ.get(data["price_sensitivity"], 1.0)
    ppp_adj = base_usd * data["ppp_index"]
    currency_price = round(ppp_adj * rate, 2)
    competitor_price = round(base_usd * rate * 1.1, 2)
    return {"market": market, "currency": data["currency"], "exchange_rate": rate,
            "ppp_adjusted_usd": round(ppp_adj, 2), "recommended_local_price": currency_price,
            "price_sensitivity": data["price_sensitivity"], "adjustment_factor": adj,
            "estimated_competitor_price": competitor_price}

def _pricing_framework(focus):
    frameworks = {
        "premium": {"strategy": "Premium pricing", "adjustment_factor": 1.15, "rationale": "Position as high-quality international brand; target less price-sensitive segments"},
        "competitive": {"strategy": "Competitive pricing", "adjustment_factor": 0.9, "rationale": "Match or slightly undercut local competitors; prioritize volume and market share"},
        "balanced": {"strategy": "Balanced pricing", "adjustment_factor": 1.0, "rationale": "Balance between premium positioning and market competitiveness; moderate volume target"},
    }
    return frameworks.get(focus, frameworks["balanced"])

def _currency_risks(markets):
    risks = []
    for m in markets:
        data = MARKET_DATA.get(m)
        if not data:
            continue
        risk_level = "low" if data["volatility"] < 0.05 else "medium" if data["volatility"] < 0.1 else "high"
        annual_range = f"+/- {round(data['volatility'] * 100)}%"
        risks.append({"market": m, "currency": data["currency"], "volatility_level": risk_level,
                      "annual_range": annual_range, "recommended_review_frequency": data["review_freq"],
                      "risk_mitigation": "Use dynamic pricing; set floor/ceiling limits; review frequently" if risk_level != "low" else "Standard quarterly review"})
    return {"currency_risk_assessment": risks}

def _competitive_positioning(base_usd, markets):
    positions = {}
    for m in markets:
        data = MARKET_DATA.get(m)
        if not data:
            continue
        adj = SENSITIVITY_ADJ.get(data["price_sensitivity"], 1.0)
        local_equiv = round(base_usd * data["ppp_index"], 2)
        positions[m] = {"base_usd_price": base_usd, "ppp_adjusted_local_value": local_equiv,
                        "competition_level": data["competition_level"],
                        "positioning_advice": "Premium positioning viable" if data["competition_level"] in ("high", "very_high") else "Competitive pricing recommended"}
    return {"competitive_positioning": positions}

def handle(user_input):
    parsed = _parse_input(user_input)
    prices = [_calc_price(parsed["base_usd_price"], m) for m in parsed["target_markets"]]
    prices = [p for p in prices if p]
    return json.dumps({
        "skill": SKILL_INFO["slug"], "name": SKILL_INFO["name"],
        "input_analysis": parsed,
        "multi_currency_pricing": {"prices": prices},
        "pricing_strategy_framework": _pricing_framework(parsed["strategy_focus"]),
        "currency_risk_management": _currency_risks(parsed["target_markets"]),
        "competitive_positioning": _competitive_positioning(parsed["base_usd_price"], parsed["target_markets"]),
        "disclaimer": "Descriptive guidance only. Not professional legal, tax, financial, or business advice. Currency exchange rates fluctuate. Verify current rates before setting prices.",
    }, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    for t in ["multi-currency pricing for my electronics product at 100 for Germany Japan and Australia",
              "help me price my apparel at 50 for UK Canada and Brazil competitive pricing",
              "how should I price products in multiple currencies premium strategy 200"]:
        p = json.loads(handle(t))
        assert "multi_currency_pricing" in p and "pricing_strategy_framework" in p
        assert "currency_risk_management" in p and "disclaimer" in p
        print("  PASS: " + t[:50])
    print("All self-tests passed!")
