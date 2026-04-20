---
name: multi-platform-trend
description: |
  多平台热点聚合与选题分析。一站式抓取知乎热榜、微博热搜、百度热搜等中国主流平台实时热点，
  AI 分析热度趋势，自动匹配内容机会评分，帮助创作者精准选题。
  触发场景：用户说"今天什么热点"、"帮我看看热搜"、"找选题"、"今天写什么"、
  "知乎热榜"、"微博热搜"、"热搜分析"、"趋势分析"、"什么话题火"。
  Keywords: 热搜, 热榜, 热点, 选题, trending, hot topic, 知乎热榜, 微博热搜, 今日热点.
---

# 多平台热点聚合

一站式抓取中国主流平台实时热点，AI 分析并推荐最佳选题方向。

## 核心能力

1. **多平台抓取** — 知乎热榜、微博热搜、百度热搜、B站排行榜
2. **智能分类** — 自动按领域分类（科技、商业、社会、娱乐等）
3. **AI 选题评分** — 评估每个热点的「内容机会值」（热度 × 契合度 × 竞争窗口）
4. **选题推荐** — 根据创作者定位，推荐最适合写作的热点

## 快速开始

用户说"今天什么热点"时：

```
1. 运行 python3 scripts/fetch_trends.py --all
2. AI 分析热点，按领域分类
3. 评估每个热点的内容机会
4. 推荐 Top 5 选题 + 写作角度建议
```

## 支持平台

| 平台 | 数据源 | 频率 | 更新速度 |
|------|--------|------|----------|
| 知乎热榜 | api.zhihu.com | 实时 | ⚡ 最快 |
| 微博热搜 | weibo.com/ajax | 实时 | ⚡ 最快 |
| 百度热搜 | top.baidu.com | 实时 | ⚡ 最快 |
| B站排行榜 | api.bilibili.com | 每日 | 🕐 次日更新 |
| 36氪热榜 | 36kr.com/feed | 实时 | ⚡ 最快 |

## 使用方式

### 查看所有平台热点
```bash
python3 scripts/fetch_trends.py --all --limit 20
```

### 查看单平台
```bash
python3 scripts/fetch_trends.py --platform zhihu --limit 10
python3 scripts/fetch_trends.py --platform weibo --limit 10
python3 scripts/fetch_trends.py --platform baidu --limit 10
python3 scripts/fetch_trends.py --platform bilibili --limit 10
```

### 按关键词过滤
```bash
python3 scripts/fetch_trends.py --all --keyword "AI"
python3 scripts/fetch_trends.py --all --keyword "科技"
```

### JSON 输出（供程序处理）
```bash
python3 scripts/fetch_trends.py --all --json
```

## AI 选题分析

收到热点数据后，AI 自动执行：

```
1. 领域分类
   将热点分为：科技/AI、商业/财经、社会/民生、娱乐/体育、教育/职场、其他

2. 内容机会评分（0-100）
   评分维度：
   - 🔥 热度分（30%）：热度值越高分越高
   - 🎯 契合度（30%）：与用户定位的匹配度
   - ⏰ 时效窗口（20%）：热点越新窗口越大
   - 📝 竞争度（20%）：回答/文章越少，机会越大

3. 选题推荐
   Top 5 推荐，每个包含：
   - 热点标题
   - 内容机会评分
   - 推荐写作角度
   - 建议发布平台
   - 预估阅读量区间
```

## 输出格式

### 文字报告
```
📊 今日热点速览（2026-04-11 06:30）

🔥 科技/AI
  1. [92分] 追觅科技砸2亿年薪招首席科学家
     → 角度：AI人才争夺战背后的行业真相
     → 建议：知乎长文 + 小红书短评

  2. [85分] OpenAI发布新模型
     → 角度：实测对比+实用场景
     → 建议：知乎回答 + 公众号深度

📰 商业/财经
  3. [78分] 某品牌被曝都是假洋牌
     → 角度：国货崛起的商业逻辑
     → 建议：知乎文章 + 小红书种草

---
💡 今日最佳选题：追觅科技AI人才争夺战
   - 热度高 + AI相关 + 竞争少 = 优质窗口
   - 建议在2小时内发布（时效窗口）
```

### JSON 输出
```json
[
  {
    "title": "...",
    "platform": "zhihu",
    "heat": 1520000,
    "category": "科技/AI",
    "opportunity_score": 92,
    "suggested_angle": "AI人才争夺战",
    "suggested_platform": ["知乎", "小红书"]
  }
]
```

## 配置项

首次使用时向用户确认：

| 配置 | 说明 | 默认值 |
|------|------|--------|
| 监控平台 | 抓取哪些平台 | 知乎+微博+百度 |
| 过滤关键词 | 只看哪些领域 | 无（全部） |
| 创作者定位 | 内容方向定位 | AI/科技 |

配置确认后记录到 memory/YYYY-MM-DD.md。

## 与其他 Skill 的配合

- **rss-content-flow**：热点 + RSS = 完整内容来源
- **content-creator**：选题 → 生成内容 → 发布的完整链路

## 文件结构

```
multi-platform-trend/
├── SKILL.md              # 本文件
├── README.md             # 用户文档
├── scripts/
│   ├── fetch_trends.py   # 热点抓取脚本
│   └── config.json       # 用户配置（运行时生成）
└── references/
    └── scoring_guide.md  # 选题评分指南
```

## 注意事项

- API 请求设置合理的超时（10秒），失败时自动跳过
- 微博热搜需要 User-Agent 伪装，已在脚本中处理
- 热度数据为估算值，仅供参考
- AI 分析基于标题和热度，无法获取文章完整内容
- 建议结合 rss-content-flow 获取完整文章内容后再写作
