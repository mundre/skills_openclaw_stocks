#!/usr/bin/env python3
"""
共享工具函数
"""

def load_json(filepath):
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def format_currency(amount):
    """格式化金额显示"""
    if amount >= 10000:
        return f"{amount/10000:.1f}万"
    return str(amount)

def risk_level_to_stars(level):
    """风险等级转星级（1-5星）"""
    if level in ["高", "低", "中"]:
        return {"高": "⭐", "中": "⭐⭐⭐", "低": "⭐⭐⭐⭐⭐"}.get(level, "?")
    return level
