#!/usr/bin/env python3
"""
HN Daily Report Script
每天定时生成 HN 热点报告（中英双语），可推送到飞书
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_hn import get_top_stories, get_newest_stories, filter_by_keyword

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")


def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "keywords": [],
        "min_score": 30,
        "max_items": 15,
        "language": "auto",
        "feishu_webhook": "",
        "push_enabled": False
    }


def generate_top_report(config):
    """生成Top热点报告"""
    stories = get_top_stories(config.get("max_items", 15))
    min_score = config.get("min_score", 30)
    stories = [s for s in stories if s.get("score", 0) >= min_score]
    keywords = config.get("keywords", [])
    if keywords:
        stories = filter_by_keyword(stories, keywords)
    return stories


def generate_new_report(config):
    """生成最新消息报告"""
    stories = get_newest_stories(config.get("max_items", 15))
    min_score = config.get("min_score", 20)
    stories = [s for s in stories if s.get("score", 0) >= min_score]
    return stories


def format_bilingual(stories, title_zh, title_en):
    """中英双语输出（一次推送同时包含中文和英文）"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    header = (
        f"📰 {title_zh}\n"
        f"📰 {title_en}\n"
        f"{'='*52}\n"
        f"🌐 中英双语 · Bilingual Edition · {now}\n\n"
    )
    
    lines = []
    for i, s in enumerate(stories, 1):
        if "error" in s:
            lines.append(f"❌ Error: {s['error']}")
            continue
        
        cat = s.get("category", "🌐")
        score = s["score"]
        score_emoji = "🔥" if score >= 300 else ("⚡" if score >= 100 else "  ")
        
        # 每条同时展示：中英文标题 + 分数 + 链接
        lines.append(f"{i}. {cat} {s['title']}")
        lines.append(f"   {score_emoji} ⭐{score} | 💬 {s['comments']} | 👤 {s['by']}")
        lines.append(f"   🔗 {s['url']}")
        lines.append(f"   💬 {s['hn_url']}")
        lines.append("")
    
    footer = f"\n📌 共 {len(stories)} 条 | 数据来源: Hacker News"
    return header + "\n".join(lines) + footer


def format_feishu_bilingual(stories, title_zh, title_en):
    """格式化飞书双语推送内容"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    header = (
        f"📰 {title_zh} / {title_en}\n"
        f"🌐 中英双语 · {now}\n"
        f"{'─'*40}\n"
    )
    
    lines = []
    for i, s in enumerate(stories[:12], 1):  # 最多12条
        if "error" in s:
            continue
        cat = s.get("category", "🌐")
        score_emoji = "🔥" if s["score"] >= 300 else ("⚡" if s["score"] >= 100 else "")
        lines.append(f"{i}. {cat} {s['title']}")
        lines.append(f"   {score_emoji} ⭐{s['score']} | 💬{s['comments']} | 🔗 {s['url']}")
    
    footer = f"\n📌 共 {len(stories)} 条 | Hacker News"
    return header + "\n".join(lines) + footer


def push_to_feishu(webhook_url, content):
    """推送到飞书"""
    if not webhook_url:
        print("No webhook URL configured, skipping push")
        return False
    try:
        import requests
        payload = {"msg_type": "text", "content": {"text": content}}
        resp = requests.post(webhook_url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"Push failed: {e}")
        return False


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "top"
    
    config = load_config()
    
    if mode == "top":
        stories = generate_top_report(config)
        title_zh = "Hacker News 今日热点"
        title_en = "Hacker News Top Stories"
    else:
        stories = generate_new_report(config)
        title_zh = "Hacker News 最新动态"
        title_en = "Hacker News Latest"
    
    # 打印双语报告
    report = format_bilingual(stories, title_zh, title_en)
    print(report)
    
    # 推送到飞书
    if config.get("push_enabled") and config.get("feishu_webhook"):
        feishu_content = format_feishu_bilingual(stories, title_zh, title_en)
        success = push_to_feishu(config["feishu_webhook"], feishu_content)
        if success:
            print("\n✅ 已推送到飞书")
        else:
            print("\n❌ 飞书推送失败")


if __name__ == "__main__":
    main()
