#!/usr/bin/env python3
"""Crisis Detector - 危机检测模块 for stress-toolkit"""

HIGH_RISK = ["自杀", "自残", "不想活了", "死", "活着没意思", "割腕", "跳楼", "活够了", "抑郁", "绝望"]
MEDIUM_RISK = ["焦虑", "恐惧", "害怕", "担心", "失眠", "崩溃", "无力", "很烦", "喘不过气", "压力大"]

def is_crisis(text):
    """
    检测危机风险等级
    返回: (是否危机, 风险等级)
    """
    text = text.lower()
    
    for k in HIGH_RISK:
        if k in text:
            return True, "high"
    
    for k in MEDIUM_RISK:
        if k in text:
            return True, "medium"
    
    return False, "safe"
