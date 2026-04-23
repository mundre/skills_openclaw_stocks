#!/usr/bin/env python3
"""
MiMo V2 Token Cost Calculator v1.4
Usage: python3 cost.py <input_tokens> <output_tokens> <total_tokens> <used_credit> <total_credit> <avg_daily_credit> [model]
"""

import sys

MODEL_RATES = {
    "mimo-v2-pro": {"unit": "CNY", "input": 0.002, "output": 0.004, "credit": 1},
}

DEFAULT_RATE = {"unit": "CNY", "input": 0.002, "output": 0.004, "credit": 1}

def detect_rate(model):
    """动态匹配计费规则，找不到用默认"""
    for key, rate in MODEL_RATES.items():
        if key in model.lower():
            return rate
    return DEFAULT_RATE

def get_cost_report(input_tokens, output_tokens, total_tokens, used_credit, total_credit, avg_daily_credit, model="unknown"):
    rate = detect_rate(model)
    currency = rate["unit"]
    symbol = "¥" if currency == "CNY" else "$"

    session_cost = round((input_tokens * rate["input"] + output_tokens * rate["output"]) / 1000, 4)

    input_ratio = 0.7
    total_cost = round((total_tokens * input_ratio * rate["input"] + total_tokens * (1 - input_ratio) * rate["output"]) / 1000, 2)

    remaining = total_credit - used_credit
    remaining_days = round(remaining / avg_daily_credit, 1) if avg_daily_credit else "N/A"
    usage_pct = round(used_credit / total_credit * 100, 1) if total_credit else 0

    return {
        "model": model,
        "session_cost_display": f"{symbol}{session_cost}",
        "session_credits": input_tokens + output_tokens,
        "today_cost_display": f"{symbol}{total_cost}",
        "today_credits": total_tokens,
        "used_credit": used_credit,
        "total_credit": total_credit,
        "remaining_credit": remaining,
        "usage_pct": usage_pct,
        "avg_daily_credit": avg_daily_credit,
        "remaining_days": remaining_days,
    }

def format_report(d):
    return (
        f"📊 成本与额度报告\n"
        f"🧠 模型: {d['model']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 本次会话: {d['session_cost_display']} (≈ {d['session_credits']} Credit)\n"
        f"📅 今日累计: {d['today_cost_display']} (≈ {d['today_credits']} Credit)\n"
        f"💳 剩余额度: {d['remaining_credit']:,} Credit\n"
        f"📊 使用率: {d['usage_pct']}%\n"
        f"📅 日均消耗: {d['avg_daily_credit']:,} Credit\n"
        f"⏳ 预计可用: {d['remaining_days']} 天\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Usage: cost.py <input> <output> <total> <used_credit> <total_credit> <avg_daily> [model]")
        sys.exit(1)

    args = [int, int, int, int, int, float]
    vals = [fn(v) for fn, v in zip(args, sys.argv[1:7])]
    model = sys.argv[7] if len(sys.argv) > 7 else "unknown"

    result = get_cost_report(*vals, model=model)
    print(format_report(result))
