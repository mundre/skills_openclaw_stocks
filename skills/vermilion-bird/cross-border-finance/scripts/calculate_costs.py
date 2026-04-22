#!/usr/bin/env python3
"""
Cross-border finance cost calculator.
Fetches real-time FX rates and computes costs for all paths given amount + currencies.

Usage:
  python3 calculate_costs.py --amount 10000 --from CNY --to USD
  python3 calculate_costs.py --amount 5000 --from USD --to CNY
  python3 calculate_costs.py --amount 1000 --from USDT --to CNY
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

# ─── Static Platform Fee Structures (update quarterly) ────────────────────────
# fee_pct: percentage of send amount (0.005 = 0.5%)
# fee_fixed: fixed fee in source currency
# fx_spread_pct: markup over mid-market rate (0 = mid-market)
# receive_fee: fee charged to recipient side (in dest currency)
# speed: typical arrival time
# annual_limit_usd: per-person annual limit (None = no limit)
# notes: key caveats

BANKING_PLATFORMS = {
    "wise": {
        "name": "Wise (TransferWise)",
        "fee_pct": 0.005,       # ~0.5% avg; actual varies 0.35–2% by corridor
        "fee_fixed": 0.0,
        "fx_spread_pct": 0.0,   # uses live mid-market rate
        "receive_fee": 0.0,
        "speed": "0–1 business day",
        "kyc": "required (passport/ID)",
        "annual_limit_usd": None,
        "cny_outbound": False,  # cannot send from mainland CNY account
        "cny_inbound": True,    # can receive CNY via CNH sort code (HK)
        "notes": "Best for overseas → RMB via HK account. Not usable for direct mainland outbound CNY."
    },
    "n26": {
        "name": "N26 (EU Neobank)",
        "fee_pct": 0.0,
        "fee_fixed": 0.0,
        "fx_spread_pct": 0.0,   # uses Wise for international; passes Wise fee
        "receive_fee": 0.0,
        "speed": "SEPA same day; international 1–3 days",
        "kyc": "required (EU residents only)",
        "annual_limit_usd": None,
        "cny_outbound": False,
        "cny_inbound": False,
        "notes": "EUR-centric. Useful for EUR↔USD corridor. No CNY support."
    },
    "ifast": {
        "name": "iFAST Financial (Singapore)",
        "fee_pct": 0.001,       # custody fee; transfer fee varies
        "fee_fixed": 10.0,      # SGD 10 per outbound SWIFT
        "fx_spread_pct": 0.005, # ~0.5% FX spread
        "receive_fee": 0.0,
        "speed": "1–3 business days",
        "kyc": "required (SG/HK residents)",
        "annual_limit_usd": None,
        "cny_outbound": False,
        "cny_inbound": True,    # can handle CNH
        "notes": "Good for SG/HK corridor. Handles CNH (offshore RMB). Not for mainland CNY."
    },
    "citic_intl": {
        "name": "中信国际银行 (CITIC Bank International, HK)",
        "fee_pct": 0.001,       # 0.1% min HKD 100
        "fee_fixed": 0.0,
        "fx_spread_pct": 0.015, # ~1.5% FX spread vs mid-market
        "receive_fee": 0.0,
        "speed": "same day (HK↔mainland); 1–2 days international",
        "kyc": "required (HK ID or mainland passport + 港澳通行证)",
        "annual_limit_usd": None,
        "cny_outbound": True,   # key: CNY↔HKD bridge
        "cny_inbound": True,
        "notes": "Best bridge between mainland CNY and HKD/overseas. Requires HK account."
    },
    "domestic_bank_swift": {
        "name": "国内银行 SWIFT 汇款 (BOC/ICBC/CCB)",
        "fee_pct": 0.001,       # ~0.1%
        "fee_fixed": 150.0,     # CNY 150 telegraphic transfer fee
        "fx_spread_pct": 0.02,  # ~2% vs mid-market (bank exchange rate)
        "receive_fee": 25.0,    # USD 15–35 intermediary bank fee
        "speed": "2–5 business days",
        "kyc": "required (Chinese ID)",
        "annual_limit_usd": 50000,  # China annual individual outbound limit
        "cny_outbound": True,
        "cny_inbound": True,
        "notes": "Regulatory limit: $50,000 USD equivalent per person per year. Purpose declaration required."
    },
    "unionpay_overseas": {
        "name": "银联卡境外消费/取现",
        "fee_pct": 0.0,
        "fee_fixed": 0.0,
        "fx_spread_pct": 0.015, # ~1.5% FX conversion fee
        "receive_fee": 0.0,
        "speed": "instant (spending) / 1–3 days (settlement)",
        "kyc": "Chinese ID + bank account",
        "annual_limit_usd": 10000,  # cash withdrawal limit; spending is higher
        "cny_outbound": True,
        "cny_inbound": False,
        "notes": "Convenient for overseas spending. High FX spread. ATM withdrawal limit USD 10,000/year."
    },
}

CRYPTO_PLATFORMS = {
    "okx_p2p": {
        "name": "OKX P2P (CNY↔USDT)",
        "fee_pct": 0.0,         # P2P trading fee = 0 (maker/taker pay each other)
        "fee_fixed": 0.0,
        "p2p_spread_pct": 0.01, # ~1% P2P premium over mid-market
        "withdrawal_fee_usdt": 1.0,  # USDT-TRC20 withdrawal: ~1 USDT
        "speed": "15–30 min (P2P) + 5 min (blockchain)",
        "kyc": "required for fiat (Chinese ID + bank card)",
        "annual_limit_usd": None,
        "notes": "Most liquid CNY P2P market. Use TRC20 for lowest withdrawal fees."
    },
    "bybit_p2p": {
        "name": "Bybit P2P (CNY↔USDT)",
        "fee_pct": 0.0,
        "fee_fixed": 0.0,
        "p2p_spread_pct": 0.012,  # ~1.2% spread
        "withdrawal_fee_usdt": 1.0,
        "speed": "20–40 min (P2P) + 5 min (blockchain)",
        "kyc": "required (passport/ID)",
        "annual_limit_usd": None,
        "notes": "Good liquidity. Slightly higher P2P spread than OKX."
    },
    "kraken": {
        "name": "Kraken (USD/EUR↔Crypto)",
        "fee_pct": 0.0016,      # 0.16% taker fee (maker 0.0%)
        "fee_fixed": 0.0,
        "fx_spread_pct": 0.0,
        "withdrawal_fee_usdt": 2.5,  # USDT withdrawal fee
        "fiat_deposit_fee": 0.0,     # SEPA free; SWIFT $5
        "fiat_withdrawal_fee": 35.0, # SWIFT withdrawal USD 35
        "speed": "trade: instant; SWIFT withdrawal: 1–3 days",
        "kyc": "required (Tier 2 for fiat; passport + proof of address)",
        "annual_limit_usd": None,
        "cny_support": False,
        "notes": "Best for EUR/USD↔crypto. No CNY. Regulated (US/EU). High SWIFT fees."
    },
    "usdt_trc20_transfer": {
        "name": "USDT TRC20 链上转账",
        "fee_pct": 0.0,
        "fee_fixed": 0.0,
        "network_fee_usd": 1.0,  # ~$1 USD for TRC20
        "speed": "3–5 min",
        "kyc": "none (wallet to wallet)",
        "annual_limit_usd": None,
        "notes": "Cheapest cross-border value transfer. Use TRC20 (not ERC20 which costs $5–50)."
    },
}

# ─── Common Path Definitions ──────────────────────────────────────────────────

PATHS = {
    # ── RMB → 海外法币 ──
    "rmb_swift_direct": {
        "label": "国内银行 SWIFT 直汇",
        "flow": ["国内银行", "→ SWIFT →", "境外银行"],
        "applicable": ["CNY→USD", "CNY→EUR", "CNY→HKD"],
        "platforms": ["domestic_bank_swift"],
        "cost_components": ["fee_fixed(CNY150)", "fx_spread(2%)", "receive_fee(USD25)"],
        "speed": "2–5个工作日",
        "security": "高",
        "limit": "每人每年 $50,000 USD 等值",
        "legal_status": "合规",
    },
    "rmb_citic_wise": {
        "label": "国内银行 → 中信国际 → Wise",
        "flow": ["国内银行", "→ 中信国际(HK)", "→ Wise"],
        "applicable": ["CNY→USD", "CNY→EUR", "CNY→GBP"],
        "platforms": ["citic_intl", "wise"],
        "cost_components": ["citic_fx_spread(1.5%)", "wise_fee(0.5%)"],
        "speed": "1–2个工作日",
        "security": "高",
        "limit": "需有中信HK账户",
        "legal_status": "合规",
    },
    "rmb_p2p_crypto_out": {
        "label": "OKX P2P 买 USDT → 境外交易所出金",
        "flow": ["国内银行", "→ OKX P2P买USDT", "→ Kraken/Bybit", "→ 境外银行"],
        "applicable": ["CNY→USD", "CNY→EUR"],
        "platforms": ["okx_p2p", "kraken"],
        "cost_components": ["p2p_spread(1%)", "kraken_fee(0.16%)", "kraken_withdrawal(USD35)"],
        "speed": "1–2小时",
        "security": "中（监管灰色区域）",
        "limit": "无官方限额",
        "legal_status": "监管灰色（P2P不违法但存在合规风险）",
    },
    # ── 海外法币 → RMB ──
    "overseas_swift_domestic": {
        "label": "境外银行 SWIFT 直汇 国内",
        "flow": ["境外银行", "→ SWIFT →", "国内银行"],
        "applicable": ["USD→CNY", "EUR→CNY"],
        "platforms": ["domestic_bank_swift"],
        "cost_components": ["sender_fee(varies)", "intermediary_fee(USD15-35)", "domestic_fx_spread(2%)"],
        "speed": "2–5个工作日",
        "security": "高",
        "limit": "每笔需申报来源；大额需证明",
        "legal_status": "合规",
    },
    "wise_to_citic_domestic": {
        "label": "Wise → 中信国际 → 国内",
        "flow": ["境外收款", "→ Wise", "→ 中信国际(HK)", "→ 国内银行"],
        "applicable": ["USD→CNY", "EUR→CNY"],
        "platforms": ["wise", "citic_intl"],
        "cost_components": ["wise_fee(0.5%)", "citic_fx_spread(1.5%)"],
        "speed": "1–2个工作日",
        "security": "高",
        "limit": "需有中信HK账户",
        "legal_status": "合规",
    },
    "overseas_p2p_in": {
        "label": "境外交易所 → USDT → OKX P2P 卖出 → 国内",
        "flow": ["境外法币", "→ Kraken买USDT", "→ OKX P2P卖USDT", "→ 国内银行"],
        "applicable": ["USD→CNY", "EUR→CNY"],
        "platforms": ["kraken", "okx_p2p"],
        "cost_components": ["kraken_deposit_free", "kraken_fee(0.16%)", "p2p_spread(1%)"],
        "speed": "1–3小时",
        "security": "中",
        "limit": "无官方限额",
        "legal_status": "监管灰色",
    },
    # ── 法币 ↔ 加密货币 ──
    "cny_to_usdt_p2p": {
        "label": "国内银行 → OKX P2P → USDT",
        "flow": ["国内银行", "→ OKX P2P", "→ USDT(TRC20)"],
        "applicable": ["CNY→USDT"],
        "platforms": ["okx_p2p"],
        "cost_components": ["p2p_spread(1%)", "withdrawal_fee(USDT1)"],
        "speed": "30–60分钟",
        "security": "中",
        "limit": "无官方限额",
        "legal_status": "监管灰色",
    },
    "usdt_to_cny_okx": {
        "label": "USDT → OKX P2P → 国内银行",
        "flow": ["USDT", "→ OKX P2P卖出", "→ 国内银行"],
        "applicable": ["USDT→CNY"],
        "platforms": ["okx_p2p"],
        "cost_components": ["p2p_spread(1%)", "deposit_fee(USDT1)"],
        "speed": "20–40分钟",
        "security": "中",
        "limit": "无官方限额",
        "legal_status": "监管灰色",
    },
    "usdt_to_cny_bybit": {
        "label": "USDT → Bybit P2P → 国内银行",
        "flow": ["USDT", "→ Bybit P2P卖出", "→ 国内银行"],
        "applicable": ["USDT→CNY"],
        "platforms": ["bybit_p2p"],
        "cost_components": ["p2p_spread(1.2%)", "deposit_fee(USDT1)"],
        "speed": "20–50分钟",
        "security": "中",
        "limit": "无官方限额",
        "legal_status": "监管灰色",
    },
    "overseas_fiat_to_usdt_kraken": {
        "label": "Kraken 法币 → USDT",
        "flow": ["境外银行", "→ Kraken(SEPA/SWIFT)", "→ 买USDT"],
        "applicable": ["USD→USDT", "EUR→USDT"],
        "platforms": ["kraken"],
        "cost_components": ["deposit_free(SEPA)/USD5(SWIFT)", "trading_fee(0.16%)"],
        "speed": "SEPA即日; SWIFT 1–3天",
        "security": "高",
        "limit": "无",
        "legal_status": "合规",
    },
}

# ─── Exchange Rate Fetcher ────────────────────────────────────────────────────

# Fallback rates vs USD (approximate, updated 2025-Q2)
FALLBACK_RATES_VS_USD = {
    "CNY": 7.25, "EUR": 0.92, "GBP": 0.79, "HKD": 7.83,
    "SGD": 1.35, "AUD": 1.53, "JPY": 155.0, "USDT": 1.0,
}

def fetch_exchange_rates(base="USD"):
    """Fetch live rates from frankfurter.app (free, no API key). Falls back to static rates."""
    url = f"https://api.frankfurter.app/latest?from={base}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            rates = data.get("rates", {})
            if rates:
                return rates
    except Exception:
        pass
    # Build fallback: convert FALLBACK_RATES_VS_USD to base-relative rates
    base_vs_usd = FALLBACK_RATES_VS_USD.get(base, 1.0)
    return {ccy: rate / base_vs_usd for ccy, rate in FALLBACK_RATES_VS_USD.items() if ccy != base}

def get_rate(from_ccy, to_ccy, rates_cache):
    """Return rate: 1 from_ccy = X to_ccy. USDT treated as USD."""
    from_ccy = "USD" if from_ccy == "USDT" else from_ccy
    to_ccy   = "USD" if to_ccy   == "USDT" else to_ccy
    if from_ccy == to_ccy:
        return 1.0
    if from_ccy not in rates_cache:
        rates = fetch_exchange_rates(from_ccy)
        rates_cache[from_ccy] = rates
    r = rates_cache.get(from_ccy, {}).get(to_ccy)
    if r:
        return r
    # try inverse
    if to_ccy not in rates_cache:
        rates = fetch_exchange_rates(to_ccy)
        rates_cache[to_ccy] = rates
    r = rates_cache.get(to_ccy, {}).get(from_ccy)
    return 1.0 / r if r else None

# ─── Cost Calculator ──────────────────────────────────────────────────────────

def estimate_path_cost(path_key, amount, from_ccy, to_ccy, rates_cache):
    """Return dict with cost breakdown and received amount."""
    path = PATHS[path_key]
    mid_rate = get_rate(from_ccy, to_ccy, rates_cache)
    if mid_rate is None:
        return None

    total_fee_src = 0.0  # fees denominated in source currency
    total_fee_dst = 0.0  # fees denominated in destination currency
    effective_rate = mid_rate

    for plat_key in path["platforms"]:
        plat = BANKING_PLATFORMS.get(plat_key) or CRYPTO_PLATFORMS.get(plat_key, {})
        # Fixed fee in source
        total_fee_src += plat.get("fee_fixed", 0.0)
        # Percent fee
        total_fee_src += amount * plat.get("fee_pct", 0.0)
        # FX spread reduces effective rate
        effective_rate *= (1 - plat.get("fx_spread_pct", 0.0))
        # Receive fee in dest
        total_fee_dst += plat.get("receive_fee", 0.0)
        # P2P spread
        if from_ccy == "CNY":
            effective_rate *= (1 - plat.get("p2p_spread_pct", 0.0))
        else:
            effective_rate *= (1 - plat.get("p2p_spread_pct", 0.0))
        # Crypto withdrawal fee (treat as dest currency USD)
        wf = plat.get("withdrawal_fee_usdt", 0.0)
        if wf:
            wf_in_dst = wf * get_rate("USD", to_ccy, rates_cache) if to_ccy != "USD" else wf
            total_fee_dst += wf_in_dst if wf_in_dst else wf
        # Kraken SWIFT withdrawal
        if plat_key == "kraken":
            wf_fiat = plat.get("fiat_withdrawal_fee", 0.0)
            total_fee_dst += wf_fiat

    after_src_fees = amount - total_fee_src
    gross_dst = after_src_fees * effective_rate
    net_dst = gross_dst - total_fee_dst

    total_cost_pct = (1 - net_dst / (amount * mid_rate)) * 100 if (amount * mid_rate) > 0 else 0

    return {
        "path_key": path_key,
        "label": path["label"],
        "flow": " ".join(path["flow"]),
        "received": round(net_dst, 2),
        "mid_market_received": round(amount * mid_rate, 2),
        "total_loss_pct": round(total_cost_pct, 2),
        "speed": path["speed"],
        "security": path["security"],
        "legal_status": path["legal_status"],
        "limit": path["limit"],
        "notes": " | ".join(BANKING_PLATFORMS.get(p, CRYPTO_PLATFORMS.get(p, {})).get("notes", "")
                             for p in path["platforms"]),
    }

# ─── Output Formatter ─────────────────────────────────────────────────────────

def print_comparison_table(results, from_ccy, to_ccy, amount):
    print(f"\n{'='*80}")
    print(f"  跨境汇款费用对比  |  {amount:,.0f} {from_ccy} → {to_ccy}  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")
    print(f"  {'路径':<30} {'到账':<14} {'总损耗%':>7} {'速度':<18} {'安全性':<8} {'合规状态'}")
    print(f"  {'-'*76}")
    for r in results:
        if r:
            print(f"  {r['label']:<30} {r['to_ccy']} {r['received']:>10,.2f}  {r['total_loss_pct']:>6.2f}%  {r['speed']:<18} {r['security']:<8} {r['legal_status']}")
    print(f"{'='*80}")
    if results:
        print(f"  中间价参考到账: {results[0]['mid_market_received']:,.2f} {to_ccy}  (无任何费用理论值，汇率为备用静态值)")
    print(f"{'='*80}\n")

def print_recommendation(results, priority="cost"):
    valid = [r for r in results if r and r["received"] > 0]
    if not valid:
        print("无可用路径。")
        return

    legal = [r for r in valid if r["legal_status"] == "合规"]
    gray  = [r for r in valid if r["legal_status"] != "合规"]

    # Sort by priority
    key = "received" if priority == "cost" else "speed" if priority == "speed" else "security"
    legal_sorted = sorted(legal, key=lambda x: x["received"], reverse=True)
    gray_sorted  = sorted(gray,  key=lambda x: x["received"], reverse=True)

    print("━━ 推荐路径 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if legal_sorted:
        best = legal_sorted[0]
        print(f"✅ 合规最优: {best['label']}")
        print(f"   路径: {best['flow']}")
        print(f"   到账: {best['received']:,.2f} | 损耗: {best['total_loss_pct']:.2f}% | 速度: {best['speed']}")
        print(f"   注意: {best['notes'][:120]}")
    if gray_sorted:
        best_g = gray_sorted[0]
        print(f"\n⚠️  灰色区域最优: {best_g['label']} (请自行评估合规风险)")
        print(f"   路径: {best_g['flow']}")
        print(f"   到账: {best_g['received']:,.2f} | 损耗: {best_g['total_loss_pct']:.2f}% | 速度: {best_g['speed']}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="跨境汇款费用计算器")
    parser.add_argument("--amount", type=float, required=True, help="发送金额")
    parser.add_argument("--from", dest="from_ccy", required=True, help="源货币 (CNY/USD/EUR/USDT)")
    parser.add_argument("--to",   dest="to_ccy",   required=True, help="目标货币 (CNY/USD/EUR/USDT)")
    parser.add_argument("--priority", choices=["cost", "speed", "security"], default="cost")
    args = parser.parse_args()

    from_ccy = args.from_ccy.upper()
    to_ccy   = args.to_ccy.upper()
    amount   = args.amount

    corridor = f"{from_ccy}→{to_ccy}"
    rates_cache = {}

    # Filter applicable paths
    applicable = [k for k, v in PATHS.items() if corridor in v["applicable"]]
    if not applicable:
        print(f"暂无 {corridor} 的预定义路径。支持: CNY→USD, CNY→EUR, USD→CNY, EUR→CNY, CNY→USDT, USDT→CNY, USD→USDT, EUR→USDT")
        sys.exit(1)

    results = []
    for pk in applicable:
        r = estimate_path_cost(pk, amount, from_ccy, to_ccy, rates_cache)
        if r:
            r["to_ccy"] = to_ccy
            results.append(r)

    results.sort(key=lambda x: x["received"], reverse=True)
    print_comparison_table(results, from_ccy, to_ccy, amount)
    print_recommendation(results, args.priority)

if __name__ == "__main__":
    main()
