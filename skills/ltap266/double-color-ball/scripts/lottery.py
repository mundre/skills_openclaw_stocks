#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球开奖查询脚本
获取近一个月开奖号码、走势分析、预测推荐
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import random
import re
from datetime import datetime, timedelta

# 模拟数据 - 实际使用时通过web_fetch获取
# 这里预存最近几期数据作为示例
LOTTERY_DATA = """
26029期 2026-03-17 06 19 22 23 28 31 05
26028期 2026-03-15 02 06 09 17 25 28 15
26027期 2026-03-12 02 13 17 18 25 26 13
26026期 2026-03-10 02 09 16 22 25 29 03
26025期 2026-03-08 02 03 15 20 23 24 10
26024期 2026-03-05 01 02 13 21 23 29 14
26023期 2026-03-03 01 02 19 29 30 32 05
26022期 2026-03-01 15 18 23 25 28 32 11
26021期 2026-02-26 03 13 25 26 30 31 04
"""

def parse_lottery_data():
    """解析开奖数据"""
    results = []
    for line in LOTTERY_DATA.strip().split('\n'):
        if line.strip():
            parts = line.split()
            if len(parts) >= 8:
                results.append({
                    'period': parts[0],
                    'date': parts[1],
                    'red': [int(x) for x in parts[2:8]],
                    'blue': int(parts[8])
                })
    return results

def analyze_trends(results):
    """分析走势"""
    analysis = {
        'hot_red': {},      # 红球出现频率
        'hot_blue': {},     # 蓝球出现频率
        'consecutive': [], # 连号统计
        'repeat': [],       # 重号统计
        'zones': {'z1': 0, 'z2': 0, 'z3': 0}  # 三区分布
    }
    
    # 统计红球出现频率
    for r in results:
        for red in r['red']:
            analysis['hot_red'][red] = analysis['hot_red'].get(red, 0) + 1
        
        # 蓝球频率
        analysis['hot_blue'][r['blue']] = analysis['hot_blue'].get(r['blue'], 0) + 1
        
        # 连号检测
        red_sorted = sorted(r['red'])
        for i in range(len(red_sorted) - 1):
            if red_sorted[i+1] - red_sorted[i] == 1:
                analysis['consecutive'].append(f"{red_sorted[i]}-{red_sorted[i+1]}")
        
        # 三区统计
        for red in r['red']:
            if red <= 11:
                analysis['zones']['z1'] += 1
            elif red <= 22:
                analysis['zones']['z2'] += 1
            else:
                analysis['zones']['z3'] += 1
    
    # 统计重号
    for i in range(len(results) - 1):
        current_reds = set(results[i]['red'])
        next_reds = set(results[i+1]['red'])
        repeats = current_reds & next_reds
        if repeats:
            analysis['repeat'].append(f"第{results[i+1]['period']}: {repeats}")
    
    return analysis

def generate_prediction(results, analysis):
    """生成预测号码（娱乐性质）"""
    # 基于热号和趋势的娱乐预测
    
    # 最热红球
    hot_reds = sorted(analysis['hot_red'].items(), key=lambda x: x[1], reverse=True)
    hot_red_nums = [x[0] for x in hot_reds[:10]]
    
    # 最热蓝球
    hot_blues = sorted(analysis['hot_blue'].items(), key=lambda x: x[1], reverse=True)
    hot_blue_nums = [x[0] for x in hot_blues[:5]]
    
    # 生成两注预测
    predictions = []
    
    # 预测1：热号为主
    pred1_red = random.sample(hot_red_nums[:8], 4) + random.sample([x for x in range(1, 34) if x not in hot_red_nums[:8]], 2)
    pred1_red = sorted(pred1_red)
    pred1_blue = random.choice(hot_blue_nums)
    predictions.append({
        'red': pred1_red,
        'blue': pred1_blue
    })
    
    # 预测2：冷热搭配
    pred2_red = random.sample(hot_red_nums[:6], 3) + random.sample([x for x in range(1, 34) if x not in hot_red_nums[:10]], 3)
    pred2_red = sorted(pred2_red)
    pred2_blue = random.choice([x for x in range(1, 16) if x not in hot_blue_nums[:3]] or [1,2,3])
    predictions.append({
        'red': pred2_red,
        'blue': pred2_blue
    })
    
    return predictions

def format_output():
    """格式化输出"""
    results = parse_lottery_data()
    analysis = analyze_trends(results)
    predictions = generate_prediction(results, analysis)
    
    output = "## 双色球近一个月开奖号码\n\n"
    output += "| 期号 | 开奖日期 | 红球 | 蓝球 |\n"
    output += "|------|----------|------|------|\n"
    
    for r in results:
        output += f"| {r['period']} | {r['date']} | {' '.join(f'{x:02d}' for x in r['red'])} | {r['blue']:02d} |\n"
    
    output += "\n## 走势特点\n\n"
    output += f"- 三区分布: 一区{analysis['zones']['z1']}个 / 二区{analysis['zones']['z2']}个 / 三区{analysis['zones']['z3']}个\n"
    output += f"- 连号: {', '.join(analysis['consecutive'][-5:]) if analysis['consecutive'] else '无'}\n"
    output += f"- 重号: {', '.join(analysis['repeat'][-3:]) if analysis['repeat'] else '无'}\n"
    
    # 热号TOP5
    hot = sorted(analysis['hot_red'].items(), key=lambda x: x[1], reverse=True)[:5]
    output += f"- 热号TOP5: {', '.join(f'{x[0]}({x[1]}次)' for x in hot)}\n"
    
    output += "\n## 预测推荐（娱乐仅供参考）\n\n"
    
    output += "**第1注：**\n"
    output += f"红球：{' '.join(f'{x:02d}' for x in predictions[0]['red'])} + 蓝球 {predictions[0]['blue']:02d}\n\n"
    
    output += "**第2注：**\n"
    output += f"红球：{' '.join(f'{x:02d}' for x in predictions[1]['red'])} + 蓝球 {predictions[1]['blue']:02d}\n\n"
    
    output += "---\n**声明**：预测纯属娱乐，无科学依据！购彩需理性。\n"
    
    return output

if __name__ == "__main__":
    print(format_output())
