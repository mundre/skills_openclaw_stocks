#!/usr/bin/env python3
"""生成今日晚安书摘"""

import os
import random
from datetime import datetime

LIBRARY_PATH = "~/book-companion-library"

def get_today_topic():
    """从今日对话记录中提取主题"""
    discussions_path = os.path.expanduser(f"{LIBRARY_PATH}/memories/reading_log.md")
    if not os.path.exists(discussions_path):
        return None

    today_str = datetime.today().strftime("%Y-%m-%d")
    with open(discussions_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找今日记录
    lines = content.splitlines()
    today_lines = []
    in_today = False
    for line in lines:
        if today_str in line and "- 日期：" in line:
            in_today = True
            today_lines.append(line)
        elif in_today:
            if line.startswith("- 日期：") and today_str not in line:
                break
            today_lines.append(line)

    if not today_lines:
        return None

    # 提取书名
    for line in today_lines:
        if "书籍：" in line:
            return line.split("书籍：")[-1].strip()

    return "今日"

def get_book_quotes(book_name):
    """从知识库中获取相关书摘（简化版）"""
    # 实际实现中可以从书籍内容中随机提取精彩段落
    # 这里提供一个基于书名的映射作为fallback
    quotes_db = {
        "全职猎人": [
            ("所谓活着，就是不断把重要的人装进心里。即使知道有一天会失去。", "蚁王"),
            ("人类之所以强大，是因为能够思考。", "尼特罗"),
            ("真正的强大，不是不流泪，而是含泪继续前行。", "奇犽"),
        ],
        "炎拳": [
            ("活下去。", "露娜"),
            ("为了活下去，即使是谎言也要相信。", "阿格尼"),
        ],
        "电锯人": [
            ("我想当玛奇玛小姐的狗。", "电次"),
            ("拥抱是世上最美好的事情。", "帕瓦"),
        ],
        "局外人": [
            ("今天，妈妈死了。也许是昨天，我不知道。", "默尔索"),
            ("面对着充满信息和星斗的夜，我第一次向这个世界的动人的冷漠敞开了心扉。", "加缪"),
        ],
        "百年孤独": [
            ("多年以后，面对行刑队，奥雷里亚诺上校将会回想起父亲带他去见识冰块的那个遥远的下午。", "马尔克斯"),
        ],
    }

    return quotes_db.get(book_name, [
        ("阅读是一座随身携带的避难所。", "毛姆"),
        ("世界上任何书籍都不能带给你好运，但是它们能让你悄悄成为自己。", "黑塞"),
        ("一个人只拥有此生此世是不够的，他还应该拥有诗意的世界。", "王小波"),
    ])

def generate_snippet():
    topic = get_today_topic() or "经典"
    quotes = get_book_quotes(topic)
    quote, source = random.choice(quotes)

    today_str = datetime.today().strftime("%Y年%m月%d日")

    # 保存到历史
    snippet_dir = os.path.expanduser(f"{LIBRARY_PATH}/memories/daily_snippets")
    os.makedirs(snippet_dir, exist_ok=True)
    snippet_path = os.path.join(snippet_dir, f"{datetime.today().strftime('%Y-%m-%d')}.md")

    snippet = f"""# {today_str} 晚安书摘

> {quote}
——《{source}》

今日话题：{topic}
生成时间：{datetime.now().strftime("%H:%M")}
"""

    with open(snippet_path, 'w', encoding='utf-8') as f:
        f.write(snippet)

    # 输出给书搭子使用
    endings = [
        "晚安，愿你好梦。",
        "晚安，明天见。",
        "夜深了，记得盖好被子。",
        "我在。晚安。",
        "今天的对话我会好好记住。晚安。",
    ]

    print(f"QUOTE:{quote}")
    print(f"SOURCE:{source}")
    print(f"ENDING:{random.choice(endings)}")

if __name__ == "__main__":
    generate_snippet()
