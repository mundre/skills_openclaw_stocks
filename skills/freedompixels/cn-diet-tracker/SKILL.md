---
name: cn-diet-tracker
description: |
  中文饮食记录助手。记录每日饮食、计算热量、营养分析。
  本地存储，无需账号。
  当用户说"饮食记录"、"今天吃了什么"、"热量计算"、"营养分析"时触发。
  Keywords: 饮食, 热量, 卡路里, 营养, diet, food, meal.
metadata: {"openclaw": {"emoji": "🥗"}}
---

# 🥗 CN Diet Tracker — 中文饮食记录

记录饮食，关注健康。

## 核心功能

| 功能 | 说明 |
|------|------|
| 记录饮食 | 一句话记录：食物名+估算热量 |
| 热量统计 | 今日/本周摄入 |
| 营养分析 | 碳水/蛋白/脂肪占比 |
| 目标管理 | 设定每日热量目标 |

## 使用方式

```bash
# 记录一餐
python3 scripts/diet.py --add "白米饭一碗" 230 --category 主食
python3 scripts/diet.py --add "番茄炒蛋" 180 --category 菜品
python3 scripts/diet.py --add "苹果" 80 --category 水果

# 今日统计
python3 scripts/diet.py --today

# 设定目标
python3 scripts/diet.py --target 2000

# 周报
python3 scripts/diet.py --week
```

## 数据存储

本地 JSON：~/.qclaw/workspace/diet.json