import json, sys, requests
sys.path.insert(0, r'C:\Users\Administrator\.qclaw\workspace-ag01\scripts')
sys.path.insert(0, r'C:\Users\Administrator\.qclaw\workspace-ag01\skills\trend-launch-scanner')
from unified_score import calc_unified_score
from sell_signal import calc_sell_score, add_indicators as sell_add_indicators
from trend_scanner import fetch_kline_tencent, add_indicators
from datetime import date

HOLDINGS = [
    {"code": "002363", "buy_price": 8.41, "buy_date": "2026-04-13"},
    {"code": "000532", "buy_price": 13.67, "buy_date": "2026-04-15"},
    {"code": "000682", "buy_price": 13.20, "buy_date": "2026-04-15"},
    {"code": "300529", "buy_price": 18.60, "buy_date": "2026-04-22"},
    {"code": "002202", "buy_price": 26.10, "buy_date": "2026-04-22"},
]

def get_name(code):
    prefix = 'sz' if code.startswith(('0', '3')) else 'sh'
    try:
        r = requests.get(f'https://qt.gtimg.cn/q={prefix}{code}', timeout=5)
        return r.content.split(b'~')[1].decode('gbk', errors='replace')
    except:
        return code

def get_price(code):
    prefix = 'sz' if code.startswith(('0', '3')) else 'sh'
    try:
        r = requests.get(f'https://qt.gtimg.cn/q={prefix}{code}', timeout=5)
        return float(r.content.split(b'~')[3].decode('gbk'))
    except:
        return 0

results = []
for h in HOLDINGS:
    code = h['code']
    name = get_name(code)
    cur_price = get_price(code)
    buy_price = h['buy_price']
    buy_date = h['buy_date']
    profit_pct = (cur_price / buy_price - 1) * 100
    days = (date.today() - date.fromisoformat(buy_date)).days

    df = fetch_kline_tencent(code, days=80)
    buy_score = None
    sell_score_info = None

    if df is not None and len(df) >= 25:
        df1 = add_indicators(df.copy())
        buy_score = calc_unified_score(df1)
        df2 = sell_add_indicators(df.copy())
        sell_score_info = calc_sell_score(df2, buy_price, buy_date)

    buy_score_val = buy_score['final_score'] if buy_score else 0
    macd_s = buy_score.get('macd_score', 0) if buy_score else 0
    ma_s = buy_score.get('ma_score', 0) if buy_score else 0
    rsi_s = buy_score.get('rsi_score', 0) if buy_score else 0
    vol_s = buy_score.get('vol_score', 0) if buy_score else 0
    rsi_val = round(buy_score.get('rsi', 0), 1) if buy_score else 0

    sell_score_val = sell_score_info['sell_score'] if sell_score_info else 0
    sell_action = sell_score_info['action'] if sell_score_info else ''
    sell_signals = sell_score_info.get('sell_signals', []) if sell_score_info else []

    if sell_score_val >= 40:
        overall = "SELL"
    elif sell_score_val >= 25:
        overall = "WARNING"
    else:
        overall = "HOLD"

    status = "PASS" if buy_score_val >= 55 else "FAIL"
    if overall == "SELL":
        status = "SELL"
    elif overall == "WARNING":
        status = "WARN"

    results.append({
        "code": code,
        "name": name,
        "cur_price": cur_price,
        "buy_price": buy_price,
        "profit_pct": round(profit_pct, 2),
        "days": days,
        "buy_score": buy_score_val,
        "macd_score": macd_s,
        "ma_score": ma_s,
        "rsi_score": rsi_s,
        "vol_score": vol_s,
        "sell_score": sell_score_val,
        "sell_action": sell_action,
        "sell_signals": [s[0] for s in sell_signals],
        "rsi": rsi_val,
        "overall": overall,
        "status": status
    })

out = {
    "date": str(date.today()),
    "positions": results,
    "summary": {
        "avg_profit": round(sum(r['profit_pct'] for r in results) / len(results), 2),
        "avg_buy_score": round(sum(r['buy_score'] for r in results) / len(results), 1),
        "avg_sell_score": round(sum(r['sell_score'] for r in results) / len(results), 1),
        "sell_count": sum(1 for r in results if r['sell_score'] >= 40),
        "warning_count": sum(1 for r in results if 25 <= r['sell_score'] < 40),
    }
}

# Save JSON
with open(r'C:\Users\Administrator\.qclaw\workspace-ag01\data\_holdings_v4.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# Print standard format
today_str = date.today().strftime('%m-%d')
print('=== HOLDINGS ANALYSIS {} ==='.format(today_str))
for r in results:
    print('  [{}]  {} {} score={} M={} A={} R={} V={} profit={:+.1f}% close={:.2f} buy={:.2f}'.format(
        r['status'].upper(), r['code'], r['name'][:6], r['buy_score'],
        r['macd_score'], r['ma_score'], r['rsi_score'], r['vol_score'],
        r['profit_pct'], r['cur_price'], r['buy_price']))
    print('        sell_score={} {} signals={}'.format(
        r['sell_score'], r['overall'], r['sell_signals']))

print()
print('Total positions: {}'.format(len(results)))
print('Overall P&L: {:+.1f}%'.format(out['summary']['avg_profit']))
print('Avg buy_score: {}  Avg sell_score: {}'.format(
    out['summary']['avg_buy_score'], out['summary']['avg_sell_score']))
print('Sell signals: {}  Warnings: {}'.format(
    out['summary']['sell_count'], out['summary']['warning_count']))
