#!/usr/bin/env python3
# International Shipping Optimizer - handler.py
import json, re

SKILL_INFO = {"name": "International Shipping Optimizer", "slug": "cb-shipping-optimizer", "version": "1.0.0"}

CARRIERS = {
    "DHL Express": {"speed_score": 9, "cost_per_kg": 18, "reliability": 9, "tracking": 10, "customs": 9, "best_for": "Time-sensitive documents, high-value goods, Europe"},
    "FedEx": {"speed_score": 9, "cost_per_kg": 20, "reliability": 9, "tracking": 10, "customs": 9, "best_for": "Priority shipments, Americas, international freight"},
    "UPS": {"speed_score": 8, "cost_per_kg": 17, "reliability": 9, "tracking": 10, "customs": 9, "best_for": "E-commerce, heavy packages, Americas"},
    "TNT Express": {"speed_score": 8, "cost_per_kg": 15, "reliability": 8, "tracking": 8, "customs": 8, "best_for": "European road express, economy freight"},
    "EMS/ePacket": {"speed_score": 6, "cost_per_kg": 10, "reliability": 6, "tracking": 5, "customs": 5, "best_for": "Small packages, budget, e-commerce lightweight"},
    "SF Express": {"speed_score": 7, "cost_per_kg": 14, "reliability": 8, "tracking": 8, "customs": 7, "best_for": "China outbound, Asia Pacific"},
    "Aramex": {"speed_score": 7, "cost_per_kg": 16, "reliability": 7, "tracking": 7, "customs": 7, "best_for": "Middle East, Africa, emerging markets"},
    "Sea Freight": {"speed_score": 2, "cost_per_kg": 3, "reliability": 5, "tracking": 3, "customs": 4, "best_for": "Bulk orders, non-urgent, large shipments"},
    "USPS": {"speed_score": 5, "cost_per_kg": 12, "reliability": 6, "tracking": 6, "customs": 6, "best_for": "US inbound small packages, economy"},
    "China Post": {"speed_score": 4, "cost_per_kg": 8, "reliability": 5, "tracking": 4, "customs": 4, "best_for": "Budget small parcels, no tracking needed"},
}

CUSTOMS_DATA = {
    "US": {"duty_threshold": "$800", "documentation": ["Commercial invoice", "Packing list", "Customs bond if >$2,500"], "tips": ["Use Section 321 ($800 de minimis)", "FCC compliance for electronics"]},
    "Germany": {"duty_threshold": "150 EUR", "documentation": ["Commercial invoice", "Packing list", "EUR1 certificate"], "tips": ["EU OSS scheme for VAT", "Importer of record considerations"]},
    "UK": {"duty_threshold": "135 GBP", "documentation": ["Commercial invoice", "Customs declaration", "Certificate of origin"], "tips": ["UKCA marking required post-Brexit", "Consider UK fulfillment partner"]},
    "Japan": {"duty_threshold": "10,000 JPY", "documentation": ["Commercial invoice", "Packing list", "Certificate of origin"], "tips": ["PSE mark for electronics", "Bonded warehouse for stock"]},
    "Australia": {"duty_threshold": "A$1,000", "documentation": ["Commercial invoice", "Packing list", "Certificate of origin"], "tips": ["GST at border if >A$1,000", "RCM compliance for electronics"]},
    "France": {"duty_threshold": "150 EUR", "documentation": ["Commercial invoice", "Packing list"], "tips": ["OSS scheme available", "French documentation required"]},
    "Brazil": {"duty_threshold": "$50", "documentation": ["Commercial invoice Portuguese", "Electronic DI", "INMETRO cert"], "tips": ["High duties 60%+", "Consider local fulfillment"]},
    "India": {"duty_threshold": "5,000 INR", "documentation": ["Bill of entry", "Commercial invoice", "GST invoice"], "tips": ["GST on imports", "BIS certification required"]},
}

LANES = {
    "China_to_US": {"carriers": ["DHL Express", "FedEx", "SF Express", "EMS/ePacket", "Sea Freight"], "avg_days": "3-25"},
    "China_to_Germany": {"carriers": ["DHL Express", "UPS", "TNT Express", "SF Express", "EMS/ePacket"], "avg_days": "4-28"},
    "China_to_UK": {"carriers": ["DHL Express", "UPS", "TNT Express", "EMS/ePacket"], "avg_days": "4-28"},
    "China_to_Japan": {"carriers": ["SF Express", "DHL Express", "EMS/ePacket", "Sea Freight"], "avg_days": "2-15"},
    "China_to_Australia": {"carriers": ["DHL Express", "UPS", "SF Express", "EMS/ePacket"], "avg_days": "4-20"},
}

def _parse_input(user_input):
    inp = user_input.lower()
    p = {"original_input": user_input[:100], "word_count": len(user_input.split())}
    p["origin_country"] = "China"
    dests = [m for m in CUSTOMS_DATA if m.lower() in inp]
    p["destination_markets"] = dests[:5] if dests else ["US", "Germany", "UK"]
    m = re.search(r"(\d+)\s*kg", inp)
    p["weight_kg"] = float(m.group(1)) if m else 2.0
    m2 = re.search(r"\$?(\d+)\s*(k|K|)", inp.replace(",", ""))
    if m2:
        val = int(m2.group(1))
        if m2.group(2) in ("k", "K"):
            val = val * 1000
        p["value_usd"] = val
    else:
        p["value_usd"] = 100
    if "fast" in inp or "priority" in inp:
        p["delivery_preference"] = "fast"
    elif "econom" in inp:
        p["delivery_preference"] = "economy"
    else:
        p["delivery_preference"] = "balanced"
    p["tracking_required"] = "no tracking" not in inp
    p["insurance_required"] = "insurance" in inp or p["value_usd"] > 500
    return p

def _evaluate():
    results = []
    for name, data in CARRIERS.items():
        score = data["speed_score"] * 0.25 + (10 - data["cost_per_kg"] / 3) * 0.25 + data["reliability"] * 0.2 + data["tracking"] * 0.15 + data["customs"] * 0.15
        results.append({"carrier": name, "overall_score": round(score, 1), "speed_score": data["speed_score"],
                        "cost_rating": round(10 - data["cost_per_kg"] / 3, 1), "reliability_score": data["reliability"],
                        "tracking_score": data["tracking"], "customs_score": data["customs"], "best_for": data["best_for"]})
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return {"carrier_evaluation": results}

def _lane_recs(origin, destinations):
    recs = []
    for d in destinations:
        key = f"{origin}_to_{d}"
        if key in LANES:
            carriers = LANES[key]["carriers"]
            recs.append({"lane": f"{origin} to {d}", "recommended_carriers": carriers[:3], "estimated_delivery_days": LANES[key]["avg_days"]})
        else:
            recs.append({"lane": f"{origin} to {d}", "recommended_carriers": ["DHL Express", "UPS", "EMS/ePacket"], "estimated_delivery_days": "3-30"})
    return {"lane_recommendations": recs}

def _customs_guide(destinations):
    guides = []
    for d in destinations:
        if d in CUSTOMS_DATA:
            cd = CUSTOMS_DATA[d]
            guides.append({"market": d, "duty_threshold": cd["duty_threshold"], "documentation_required": cd["documentation"], "clearance_tips": cd["tips"]})
    return {"customs_clearance_framework": guides}

def _cost_optimization():
    return {"cost_optimization_strategies": [
        {"strategy": "Consolidate shipments", "saving_potential": "15-25%", "implementation": "Combine multiple orders into one shipment to a regional warehouse"},
        {"strategy": "Use economy carriers for non-urgent", "saving_potential": "30-50%", "implementation": "Switch from express to ePacket/Sea for non-time-sensitive orders"},
        {"strategy": "Regional fulfillment centers", "saving_potential": "20-40%", "implementation": "Pre-ship bulk inventory to regional warehouses (3PL)"},
        {"strategy": "Negotiate volume discounts", "saving_potential": "10-20%", "implementation": "Consolidate volume with single carrier; request tiered pricing"},
        {"strategy": "Optimize packaging", "saving_potential": "5-15%", "implementation": "Reduce dimensional weight by right-sizing packaging"},
        {"strategy": "Use carrier multi-package discounts", "saving_potential": "10-15%", "implementation": "Split large orders into multiple packages within optimal weight tiers"},
    ]}

def handle(user_input):
    parsed = _parse_input(user_input)
    return json.dumps({
        "skill": SKILL_INFO["slug"], "name": SKILL_INFO["name"],
        "input_analysis": parsed,
        "carrier_evaluation_matrix": _evaluate(),
        "lane_recommendations": _lane_recs(parsed["origin_country"], parsed["destination_markets"]),
        "customs_clearance_framework": _customs_guide(parsed["destination_markets"]),
        "cost_optimization_strategies": _cost_optimization(),
        "disclaimer": "Descriptive guidance only. Not professional legal, regulatory, or business advice. Shipping costs and regulations change. Verify current information with carriers and customs authorities.",
    }, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    for t in ["best shipping options for electronics from China to US and Germany 2kg package value 200",
              "how to reduce international shipping costs for apparel to UK Japan Australia",
              "shipping strategy for multiple international markets fast delivery 5kg"]:
        p = json.loads(handle(t))
        assert "carrier_evaluation_matrix" in p and "lane_recommendations" in p
        assert "cost_optimization_strategies" in p and "disclaimer" in p
        print("  PASS: " + t[:50])
    print("All self-tests passed!")
