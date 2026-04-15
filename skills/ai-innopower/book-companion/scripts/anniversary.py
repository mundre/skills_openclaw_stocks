#!/usr/bin/env python3
"""计算相识天数和纪念日状态"""

import sys
from datetime import datetime

PROFILE_PATH = "~/book-companion-library/user_profile.md"

def parse_created_date(text):
    for line in text.splitlines():
        if "相识纪念日：" in line:
            return line.split("相识纪念日：")[-1].strip()
    return None

def main():
    import os
    path = os.path.expanduser(PROFILE_PATH)
    if not os.path.exists(path):
        print("NOT_FOUND")
        return

    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    date_str = parse_created_date(text)
    if not date_str:
        print("UNKNOWN")
        return

    created = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.today()
    days_together = (today - created).days

    # 检查纪念日
    milestones = []
    if days_together == 100:
        milestones.append("100天")
    elif days_together == 365:
        milestones.append("1周年")
    elif days_together == 730:
        milestones.append("2周年")
    elif days_together % 30 == 0 and days_together > 0:
        milestones.append(f"{days_together//30}个月")

    print(f"DAYS:{days_together}")
    if milestones:
        print(f"MILESTONE:{','.join(milestones)}")

    # 成长阶段
    if days_together < 30:
        print("STAGE:新生儿")
    elif days_together < 90:
        print("STAGE:学步期")
    elif days_together < 180:
        print("STAGE:成熟期")
    else:
        print("STAGE:老友期")

if __name__ == "__main__":
    main()
