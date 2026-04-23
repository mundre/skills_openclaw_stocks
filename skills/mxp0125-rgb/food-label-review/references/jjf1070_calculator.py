#!/usr/bin/env python3
"""JJF 1070-2023 定量包装商品净含量计量检验规则 - 允差计算工具
Usage: python3 jjf1070_calculator.py QN UNIT [samples...]

Examples:
  python3 jjf1070_calculator.py 500 mL 488 492 490 495 491
  python3 jjf1070_calculator.py 100 g 97 98 99 96 97 98 99 97 98 96
  python3 jjf1070_calculator.py 500 mL    # no samples -> show tolerance only
"""

import sys
import math


def calc_allowable_shortage(qn, unit):
    qn_g = qn * 1000.0 if unit.lower() in ['kg', 'l'] else qn
    if qn_g <= 50:
        t = 0.09 * qn_g
    elif qn_g <= 100:
        t = 4.5
    elif qn_g <= 200:
        t = 0.045 * qn_g
    elif qn_g <= 300:
        t = 9.0
    elif qn_g <= 500:
        t = 0.03 * qn_g
    elif qn_g <= 1000:
        t = 15.0
    elif qn_g <= 10000:
        t = 0.015 * qn_g
    else:
        t = 150.0
    return round(t, 3)


def get_tier_label(qn, unit):
    qn_g = qn * 1000.0 if unit.lower() in ['kg', 'l'] else qn
    if qn_g <= 50:
        return "Qn<=50g/mL  =>  T=9%*Qn"
    elif qn_g <= 100:
        return "50g/mL<Qn<=100g/mL  =>  T=4.5g/mL(fixed)"
    elif qn_g <= 200:
        return "100g/mL<Qn<=200g/mL  =>  T=4.5%*Qn"
    elif qn_g <= 300:
        return "200g/mL<Qn<=300g/mL  =>  T=9g/mL(fixed)"
    elif qn_g <= 500:
        return "300g/mL<Qn<=500g/mL  =>  T=3%*Qn"
    elif qn_g <= 1000:
        return "500g/mL<Qn<=1kg/mL  =>  T=15g/mL(fixed)"
    elif qn_g <= 10000:
        return "1kg/mL<Qn<=10kg/mL  =>  T=1.5%*Qn"
    else:
        return "Qn>10kg/mL  =>  T=1.5%*Qn (max 150g)"


def assess(qn, unit, samples):
    t = calc_allowable_shortage(qn, unit)
    lower = round(qn - t, 3)
    results = []
    for v in samples:
        ok = v >= lower
        diff = round(v - qn, 3)
        diff_pct = round(diff / qn * 100, 2) if qn > 0 else 0
        results.append({"v": v, "ok": ok, "diff": diff, "diff_pct": diff_pct})

    avg = round(sum(samples) / len(samples), 3)
    avg_check = avg >= (qn - t / math.sqrt(len(samples)))
    unqualified = sum(1 for r in results if not r["ok"])
    pass_rate = round((len(samples) - unqualified) / len(samples) * 100, 1)
    return {"tier": get_tier_label(qn, unit), "t": t, "lower": lower,
            "avg": avg, "avg_check": avg_check,
            "results": results, "unqualified": unqualified, "pass_rate": pass_rate,
            "qn": qn, "unit": unit}


def print_report(r):
    print("\n" + "=" * 55)
    print("  JJF 1070-2023 定量包装商品净含量计量检验报告")
    print("=" * 55)
    print("  标注净含量 Qn = {} {}".format(r["qn"], r["unit"]))
    print("  档位: {}".format(r["tier"]))
    print("  允许短缺量 T = {} {}".format(r["t"], r["unit"]))
    print("  单件允收下限 = Qn - T = {} {}".format(r["lower"], r["unit"]))
    print("-" * 55)
    hdr = "{:<6}  {:>10}  {:>10}  {:>7}  {:<20}"
    print(hdr.format("件号", "实测值", "偏差", "偏差%", "单项判定"))
    print("-" * 55)
    for i, res in enumerate(r["results"], 1):
        status = "OK" if res["ok"] else "FAIL"
        print(hdr.format(i, round(res["v"], 3), res["diff"], str(res["diff_pct"]) + "%", status))
    print("-" * 55)
    avg_check_str = "OK" if r["avg_check"] else "FAIL"
    print("  样本均值 = {} {}  [avg_check: {}]".format(r["avg"], r["unit"], avg_check_str))
    print("  不合格件数: {}/{}  通过率: {}%".format(r["unqualified"], len(r["results"]), r["pass_rate"]))
    print("=" * 55)
    if r["avg_check"] and r["unqualified"] == 0:
        verdict = "综合判定: PASS - 该批次净含量合格"
    elif not r["avg_check"]:
        verdict = "综合判定: FAIL - 平均值复核不合格，该批次不合格"
    else:
        verdict = "综合判定: WARN - 有{}件单项不合格，但平均值复核合格".format(r["unqualified"])
    print("  " + verdict)
    print()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    qn = float(sys.argv[1])
    unit = sys.argv[2]
    sample_vals = []
    if len(sys.argv) > 3:
        sample_vals = [float(x) for x in sys.argv[3:]]

    t = calc_allowable_shortage(qn, unit)
    lower = round(qn - t, 3)
    print("JJF 1070-2023 净含量允差计算")
    print("标注净含量 Qn = {} {}".format(qn, unit))
    print("档位: {}".format(get_tier_label(qn, unit)))
    print("允许短缺量 T = {} {}".format(t, unit))
    print("单件允收下限 = Qn - T = {} {}".format(lower, unit))

    if not sample_vals:
        print("(提供实测值以获得完整审核报告)")
    else:
        report = assess(qn, unit, sample_vals)
        print_report(report)
