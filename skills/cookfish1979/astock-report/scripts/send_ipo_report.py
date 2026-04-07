#!/usr/bin/env python3
"""A股IPO周报 - 微信友好版（紧凑垂直列表）"""
import json, subprocess, re
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.insert(0, "/workspace/keys")
from keys_loader import get_webhook_url

NOW = datetime(2026, 4, 4)
TODAY_STR = "04月04日"
REPORT_START = "03月28日"
TS = NOW.strftime("%Y-%m-%d")
NEXT_WEEK_END = (NOW + timedelta(days=7)).strftime("%m/%d")
THIS_WEEK_END = (NOW + timedelta(days=3)).strftime("%m/%d")
_URL = get_webhook_url()


def wx(text):
    d = {"msgtype": "text", "text": {"content": text}}
    p = json.dumps(d, ensure_ascii=False)
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", _URL,
         "-H", "Content-Type: application/json", "-d", "@-"],
        input=p.encode("utf-8"), capture_output=True)
    try:
        return json.loads(r.stdout.decode()).get("errcode", -1)
    except:
        return -1


def shname(name, n=12):
    return name[:n] + ".." if len(name) > n else name


def sdate(dt):
    return str(dt)[5:7] + "/" + str(dt)[8:10]


def board_alias(b):
    return {"上交所科创板": "科创板", "深交所创业板": "创业板",
            "深交所主板": "深主板", "上交所主板": "沪主板",
            "北交所": "北交所"}.get(b, b)


LISTINGS_GAIN = {
    "301683": {"name": "慧谷新材", "date": "04/01", "price": 78.38, "gain": "61.66%"},
    "001257": {"name": "盛龙股份", "date": "03/31", "price": 7.82,  "gain": "254.0%"},
    "688813": {"name": "泰金新能", "date": "03/31", "price": 26.28, "gain": "88.24%"},
    "920055": {"name": "隆源股份", "date": "03/31", "price": 24.70, "gain": "53.04%"},
    "920188": {"name": "悦龙科技", "date": "03/30", "price": 14.04, "gain": "184.0%"},
}


def fmt_price(v):
    if pd.isna(v): return "N/A"
    return f"{v:.2f}元"


def fmt_amt(v, price_val):
    if pd.isna(v) or pd.isna(price_val) or v <= 0:
        return "N/A"
    val = v * price_val / 10000
    if val < 0.1:
        return f"{val*10000:.0f}万"
    return f"{val:.1f}亿"


def fmt_rate(v):
    if pd.isna(v): return "N/A"
    return f"{v*100:.3f}%"


def fmt_pe(v):
    if pd.isna(v): return "亏损/未盈利"
    return f"{v:.1f}x"


# ===== 拉取数据 =====
import akshare as ak

review = ak.stock_ipo_review_em()
review["上会日期"] = pd.to_datetime(review["上会日期"], errors="coerce").dt.tz_localize(None)
recent_r = review[
    review["上会日期"].between(pd.Timestamp("2026-03-28"), pd.Timestamp("2026-04-04"))
].dropna(subset=["上会日期"]).sort_values("上会日期")
next_r = review[
    review["上会日期"].between(pd.Timestamp("2026-04-05"), pd.Timestamp("2026-04-11"))
].dropna(subset=["上会日期"]).sort_values("上会日期")

df = ak.stock_new_ipo_cninfo()
df["申购_dt"] = pd.to_datetime(df["申购日期"], errors="coerce").dt.tz_localize(None)
df["上市_dt"] = pd.to_datetime(df["上市日期"], errors="coerce").dt.tz_localize(None)
recent_a = df[df["申购_dt"].between(pd.Timestamp("2026-03-28"), pd.Timestamp("2026-04-04"))
].dropna(subset=["申购_dt"]).sort_values("申购_dt")
next_a = df[df["申购_dt"].between(pd.Timestamp("2026-04-05"), pd.Timestamp("2026-04-11"))
].dropna(subset=["申购_dt"]).sort_values("申购_dt")
recent_l = df[df["上市_dt"].between(pd.Timestamp("2026-03-28"), pd.Timestamp("2026-04-04"))
].dropna(subset=["上市_dt"]).sort_values("上市_dt")

queue = ak.stock_ipo_declare_em()
queue["更新日期"] = pd.to_datetime(queue["更新日期"], errors="coerce").dt.tz_localize(None)
recent_up = queue[queue["更新日期"].between(pd.Timestamp("2026-03-28"), pd.Timestamp("2026-04-04"))]
reg_up = recent_up[recent_up["最新状态"].isin(["注册", "核准"])].dropna(subset=["企业名称"])

# ===== 排队数据（截至2026年3月29日 · 新浪财经）=====
QUEUE_DATE = "2026年03月29日"
# {板块: [(标签, 数量), ...]}
QUEUE = {
    "科创板": [("已受理", 2), ("问询", 35), ("提交注册", 3)],
    "创业板": [("问询", 33), ("过会", 1)],
    "沪主板": [("已受理", 2), ("问询", 15), ("提交注册", 1)],
    "深主板": [("已受理", 3), ("问询", 9), ("过会", 1), ("提交注册", 3)],
    "北交所": [("问询", 122), ("过会", 18)],
}
QUEUE_TOTALS = {"全市场": 248, "问询中": 214, "已过会": 20, "提交注册": 7}

# ===== 组装报告 =====
lines = [
    f"📋 A股IPO周报 {REPORT_START}-{TODAY_STR}",
    "",
]

# 一、排队情况
lines += [
    "━━━━━━━━━━",
    "📊 一、排队情况（截止" + QUEUE_DATE + "）",
    "",
    f"全市场共{QUEUE_TOTALS['全市场']}家：问询{QUEUE_TOTALS['问询中']}家 | "
    f"已过会待发行{QUEUE_TOTALS['已过会']}家 | 提交注册{QUEUE_TOTALS['提交注册']}家",
    "",
]
for board, items in QUEUE.items():
    total = sum(v for _, v in items)
    parts = " | ".join(f"{k}{v}" for k, v in items)
    lines.append(f"【{board}】{total}家  {parts}")

# 二、上周上会
passed_r = recent_r[recent_r["审核状态"] == "上会通过"]
failed_r = recent_r[recent_r["审核状态"].isin(["上会未通过", "取消审核"])]
lines += [
    "",
    "━━━━━━━━━━",
    f"📋 二、上周上会（{REPORT_START}-{TODAY_STR}）",
    "",
    f"✅ 通过：{len(passed_r)}家",
]
for _, r in passed_r.iterrows():
    bd = board_alias(r.get("上市板块", ""))
    nm = shname(r.get("企业名称", r.get("股票简称", "?")), 12)
    dt = sdate(r["上会日期"])
    lines.append(f"  · {nm} | {bd} | {dt}")

if len(failed_r) > 0:
    lines.append(f"❌ 否决：{len(failed_r)}家")
    for _, r in failed_r.iterrows():
        bd = board_alias(r.get("上市板块", ""))
        nm = shname(r.get("企业名称", r.get("股票简称", "?")), 12)
        lines.append(f"  · {nm} | {bd}")

# 三、上周拿文
reg_up2 = recent_up[recent_up["最新状态"].isin(["注册", "核准"])].dropna(subset=["企业名称"])
lines += ["", "━━━━━━━━━━", f"📋 三、上周拿文（{REPORT_START}-{TODAY_STR}）", ""]
if len(reg_up2) > 0:
    lines.append(f"📄 获发行批文：{len(reg_up2)}家")
    for _, r in reg_up2.iterrows():
        bd = board_alias(r.get("拟上市地点", ""))
        nm = shname(r.get("企业名称", ""), 12)
        dt = str(r["更新日期"])[:10]
        lines.append(f"  · {nm} | {bd} | {dt}")
else:
    lines.append("  （暂无数据）")

# 四、上周终止
term_up = recent_up[recent_up["最新状态"].isin(["终止"])].dropna(subset=["企业名称"])
lines += ["", "━━━━━━━━━━", f"📋 四、上周终止/撤回（{REPORT_START}-{TODAY_STR}）", ""]
if len(term_up) > 0:
    for _, r in term_up.iterrows():
        bd = board_alias(r.get("拟上市地点", ""))
        nm = shname(r.get("企业名称", ""), 12)
        lines.append(f"  · {nm} | {bd}")
else:
    lines.append("  本周无终止撤回记录")

# 五、本周上会
lines += ["", "━━━━━━━━━━", f"📋 五、本周上会计划（{THIS_WEEK_END}-{NEXT_WEEK_END}）", ""]
if len(next_r) > 0:
    for _, r in next_r.iterrows():
        bd = board_alias(r.get("上市板块", ""))
        nm = shname(r.get("企业名称", r.get("股票简称", "?")), 12)
        dt = sdate(r["上会日期"])
        lines.append(f"  · {nm} | {bd} | 计划{dt}")
else:
    lines.append("  本周暂无上会安排")

# 六、本周上市
lines += ["", "━━━━━━━━━━", f"📋 六、本周新股上市（{REPORT_START}-{TODAY_STR}）", ""]
if len(recent_l) > 0:
    for _, r in recent_l.iterrows():
        cd = str(r.get("证劵代码", ""))
        info = LISTINGS_GAIN.get(cd, {})
        if info:
            nm, dt, gain = info["name"], info["date"], info["gain"]
            pr = f"{info['price']:.2f}元"
        else:
            nm = r.get("证券简称", "?")
            dt = sdate(r["上市_dt"]) if pd.notna(r.get("上市_dt")) else "?"
            gain = "-"
            pr = fmt_price(r.get("发行价"))
        lines.append(f"  · {nm}（{cd}）| 上市:{dt} | 发行:{pr} | 涨幅:{gain}")
else:
    lines.append("  （无）")

# 底部
lines += [
    "",
    "━━━━━━━━━━",
    "📌 数据来源：新浪财经+IPO123（统计截至" + QUEUE_DATE + "）",
    "⚠️ 仅供参考，不构成投资建议。",
]

report = "\n".join(lines)
err = wx(report)
print(report)
print("\n" + ("✅ 已推送" if err == 0 else f"❌ err={err}"))
