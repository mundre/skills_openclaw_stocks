---
name: skill-market-analyzer
slug: skylv-skill-market-analyzer
version: 1.0.2
description: ClawHub skill market analyzer. Tracks trending skills, competitor analysis, and pricing strategy insights. Triggers: skill market, clawhub analytics, skill trends.
author: SKY-lv
license: MIT
tags: [clawhub, market-analysis, data, trends, competitor]
keywords: openclaw, skill, automation, ai-agent
triggers: skill market analyzer
---

# Skill Market Analyzer — ClawHub 市场数据分析

## 功能说明

深度分析 ClawHub 技能市场，提供热门技能追踪、趋势预测、竞品分析和定价策略建议。用数据驱动技能开发和运营决策。

## 核心能力

### 1. 热门技能追踪 (Trending Skills)

```yaml
metrics:
  - installs_24h: 24 小时安装量
  - installs_7d: 7 日安装量
  - growth_rate: 增长率
  - rating: 用户评分
  - reviews: 评论数

categories:
  - productivity: 生产力工具
  - development: 开发工具
  - marketing: 营销工具
  - data: 数据分析
  - ai: AI 增强
  - automation: 自动化
```

**使用示例：**
```
用户：ClawHub 现在什么技能最火？
Agent: 
  1. 获取 Top 50 热门技能
  2. 分析增长趋势
  3. 识别新兴类别
  4. 提供开发建议
```

### 2. 趋势预测 (Trend Prediction)

```yaml
signals:
  - search_volume: 搜索量变化
  - github_stars: GitHub 相关项目热度
  - social_mentions: 社交媒体提及
  - new_releases: 新技能发布频率

prediction_model:
  - 时间序列分析（ARIMA）
  - 关键词热度追踪
  - 竞品动向监测
```

**使用示例：**
```
用户：预测下个月什么类型的技能会火？
Agent:
  1. 分析搜索趋势
  2. 监测 GitHub 热门项目
  3. 追踪社交媒体讨论
  4. 输出预测报告
```

### 3. 竞品分析 (Competitor Analysis)

```yaml
analysis:
  - feature_comparison: 功能对比
  - pricing_analysis: 定价分析
  - user_reviews: 用户评价
  - update_frequency: 更新频率
  - author_reputation: 作者声誉

output:
  - 竞品功能矩阵
  - 定价策略建议
  - 差异化机会点
  - 用户痛点分析
```

**使用示例：**
```
用户：分析 skill-creator 的竞品情况
Agent:
  1. 识别直接竞品（5-10 个）
  2. 功能对比分析
  3. 定价策略对比
  4. 用户评价情感分析
  5. 差异化建议
```

### 4. 定价策略 (Pricing Strategy)

```yaml
factors:
  - development_cost: 开发成本
  - market_rate: 市场均价
  - value_proposition: 价值主张
  - competitor_pricing: 竞品定价
  - target_audience: 目标用户支付意愿

pricing_models:
  - free: 免费（引流）
  - freemium: 免费 + 付费功能
  - one_time: 一次性购买
  - subscription: 订阅制
  - usage_based: 按使用量计费
```

**使用示例：**
```
用户：我的 skill-creator 应该定价多少？
Agent:
  1. 分析竞品定价
  2. 评估独特价值
  3. 计算开发成本
  4. 推荐定价策略
```

## 数据看板

### 市场概览

```yaml
total_skills: 2,500+
active_authors: 800+
total_installs: 100,000+
avg_rating: 4.2/5
top_category: productivity (28%)
fastest_growing: ai-tools (+156% MoM)
```

### 热门类别 Top 5

| 类别 | 技能数 | 占比 | 增长率 |
|------|--------|------|--------|
| Productivity | 700 | 28% | +12% |
| Development | 550 | 22% | +18% |
| Marketing | 380 | 15% | +25% |
| Data Analysis | 320 | 13% | +31% |
| AI Tools | 280 | 11% | +156% |

### 新兴趋势

1. **AI 增强工具** — +156% MoM
   - Prompt 优化器
   - AI 代码审查
   - 自动文档生成

2. **跨平台集成** — +89% MoM
   - Telegram Bot 构建器
   - 微信生态工具
   - Discord 机器人

3. **数据可视化** — +67% MoM
   - 仪表盘生成器
   - 报告自动化
   - 实时数据监控

## 工具函数

### get_trending_skills

```python
def get_trending_skills(category: str = None, limit: int = 50) -> list:
    """
    获取热门技能
    
    Args:
        category: 类别（可选）
        limit: 返回数量
    
    Returns:
        [
            {
                "name": "skill-creator",
                "author": "SKY-lv",
                "installs_24h": 150,
                "installs_7d": 890,
                "growth_rate": 0.23,
                "rating": 4.8,
                "reviews": 45
            }
        ]
    """
```

### analyze_competitor

```python
def analyze_competitor(skill_slug: str) -> dict:
    """
    竞品分析
    
    Args:
        skill_slug: 技能 slug
    
    Returns:
        {
            "direct_competitors": ["competitor-1", "competitor-2"],
            "feature_matrix": {...},
            "pricing_comparison": {...},
            "user_sentiment": {...},
            "opportunities": ["差异化点 1", "差异化点 2"]
        }
    """
```

### predict_trends

```python
def predict_trends(timeframe: str = "30d") -> dict:
    """
    趋势预测
    
    Args:
        timeframe: 预测时间范围
    
    Returns:
        {
            "hot_categories": ["ai-tools", "cross-platform"],
            "emerging_keywords": ["prompt-optimizer", "bot-builder"],
            "market_gaps": ["未满足的需求 1", "未满足的需求 2"],
            "recommendation": "建议开发方向"
        }
    """
```

### pricing_recommendation

```python
def pricing_recommendation(skill_type: str, features: list, target_audience: str) -> dict:
    """
    定价建议
    
    Args:
        skill_type: 技能类型
        features: 功能列表
        target_audience: 目标用户
    
    Returns:
        {
            "model": "freemium",
            "price": {
                "free": "基础功能",
                "pro": "$9.99/月",
                "enterprise": "$49.99/月"
            },
            "reasoning": "定价理由",
            "competitor_range": "$5-15/月"
        }
    """
```

## 市场洞察

### 成功技能特征

1. **解决真实痛点** — 不是"锦上添花"
2. **开箱即用** — 配置简单，5 分钟内上手
3. **持续更新** — 每月至少 1 次更新
4. **良好文档** — README 清晰，有使用示例
5. **用户反馈响应** — 24 小时内回复 issue

### 失败技能特征

1. **功能泛泛** — "XX 助手"但没有独特价值
2. **文档缺失** — 不知道如何使用
3. **一次性发布** — 发布后不再维护
4. **过度承诺** — 功能描述与实际不符
5. **定价不合理** — 过高或过低

### 定价策略建议

| 技能类型 | 推荐模式 | 价格区间 |
|---------|---------|---------|
| 工具类 | Freemium | $0 + $9.99/月 |
| 模板类 | 一次性 | $4.99-$19.99 |
| 数据类 | 订阅制 | $19.99-$49.99/月 |
| 企业类 | 定制报价 | $99+/月 |
| 开源类 | 免费 + 捐赠 | $0 + 捐赠 |

## 相关文件

- [ClawHub](https://clawhub.ai)
- [ClawHub 文档](https://docs.openclaw.ai/tools/clawhub)
- [awesome-openclaw-skills](https://github.com/SKY-lv/awesome-openclaw-skills)

## 触发词

- 自动：检测 market、analysis、trends、competitor、pricing 相关关键词
- 手动：/skill-market, /market-analysis, /competitor-analysis
- 短语：市场分析、竞品分析、趋势预测、定价策略

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
