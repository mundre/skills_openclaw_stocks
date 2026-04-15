#!/usr/bin/env python3
"""分析情绪日志，预测低谷期"""

import os
import re
from datetime import datetime, timedelta

MOOD_LOG_PATH = "~/book-companion-library/memories/mood_log.md"

def parse_mood_entries(text):
    """解析情绪记录"""
    entries = []
    # 匹配格式：- 2026-04-05: 低落，提到工作压力大
    pattern = r'- (\d{4}-\d{2}-\d{2}):\s*(.+?)(?:\n|$)'
    for match in re.finditer(pattern, text):
        date_str, content = match.groups()
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            entries.append({
                'date': date,
                'content': content.strip(),
                'day_of_month': date.day
            })
        except:
            pass
    return entries

def analyze_low_patterns(entries):
    """分析低谷期规律"""
    if len(entries) < 3:
        return None

    # 找出标记为低落/疲惫/烦躁的条目
    negative_keywords = ['低落', '疲惫', '烦躁', '焦虑', '难过', '压力大', '累']
    low_entries = [e for e in entries if any(k in e['content'] for k in negative_keywords)]

    if len(low_entries) < 2:
        return None

    # 分析日期规律
    days = [e['day_of_month'] for e in low_entries]
    avg_day = sum(days) / len(days)

    # 如果集中在月中（15-25），判断为月度规律
    in_mid_month = sum(1 for d in days if 15 <= d <= 25)
    if in_mid_month / len(days) > 0.6:
        return f"每月{int(avg_day)}号左右"

    return None

def predict_next_low(entries):
    """预测下次低谷期"""
    pattern = analyze_low_patterns(entries)
    if not pattern:
        return None

    today = datetime.today()
    # 简单预测：如果本月已过半且没有记录，可能是下个月的周期
    if today.day > 20:
        next_month = today.replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        return next_month.replace(day=18)  # 假设月中
    return None

def main():
    path = os.path.expanduser(MOOD_LOG_PATH)
    if not os.path.exists(path):
        print("NO_DATA")
        return

    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    entries = parse_mood_entries(text)
    if not entries:
        print("NO_ENTRIES")
        return

    print(f"TOTAL_ENTRIES:{len(entries)}")

    pattern = analyze_low_patterns(entries)
    if pattern:
        print(f"PATTERN:{pattern}")

    prediction = predict_next_low(entries)
    if prediction:
        print(f"PREDICT:{prediction.strftime('%Y-%m-%d')}")

    # 最近情绪
    if entries:
        latest = max(entries, key=lambda x: x['date'])
        days_since = (datetime.today() - latest['date']).days
        print(f"LATEST:{days_since}天前 - {latest['content']}")

if __name__ == "__main__":
    main()
