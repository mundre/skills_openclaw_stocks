---
name: seo-agent
slug: skylv-seo-agent
version: 2.0.2
description: SEO optimization expert. Keyword research, content optimization, ranking monitoring, and technical SEO auditing. Triggers: seo, search optimization, google ranking, keyword research.
author: SKY-lv
license: MIT
tags: [seo, keyword, optimization, search, marketing]
keywords: seo, search, optimization, content, ranking
triggers: seo agent
---

# SEO Agent — 搜索引擎优化专家

## 功能说明

专业 SEO 优化助手，提供关键词研究、内容优化、排名监控、技术 SEO 审计和竞品分析。集成真实 SEO API 数据，不是泛泛而谈的建议。

## 核心能力

### 1. 关键词研究 (Keyword Research)

```yaml
输入：种子关键词、目标市场、行业
输出：关键词列表 + 指标数据

metrics:
  - search_volume: 月搜索量
  - keyword_difficulty: 难度 (0-100)
  - cpc: 点击成本
  - trend: 搜索趋势 (12 个月)
  - intent: 搜索意图 (信息/导航/交易/商业)

data_sources:
  - Google Keyword Planner API
  - Ahrefs API (备选)
  - SEMrush API (备选)
  - Google Trends API
```

**使用示例：**
```
用户：帮我研究"AI 工具"的关键词机会
Agent: 
  1. 调用 keyword_research API
  2. 输出 50 个相关关键词 + 指标
  3. 推荐 10 个低难度高价值关键词
  4. 提供内容建议
```

### 2. 内容优化 (Content Optimization)

```yaml
输入：文章草稿、目标关键词
输出：优化建议 + 修改版本

on_page_factors:
  - title_tag: 标题标签 (50-60 字符)
  - meta_description: 描述标签 (150-160 字符)
  - h1_h2_h3: 标题结构
  - keyword_density: 关键词密度 (1-2%)
  - internal_links: 内链建议
  - image_alt: 图片 ALT 文本
  - url_structure: URL 优化
  - readability: 可读性评分

tools:
  - content_audit: 内容审计
  - keyword_placement: 关键词布局建议
  - meta_generator: 元标签生成
  - readability_checker: 可读性检查
```

**使用示例：**
```
用户：优化这篇关于"OpenClaw Skills"的文章 SEO
Agent:
  1. 分析当前内容（标题、结构、关键词密度）
  2. 输出优化建议清单
  3. 生成优化后的标题/描述
  4. 提供内链建议
```

### 3. 排名监控 (Rank Tracking)

```yaml
输入：关键词列表、目标 URL、地理位置
输出：排名数据 + 趋势分析

tracking:
  - current_rank: 当前排名
  - rank_change: 排名变化 (日/周/月)
  - top_10_competitors: 前 10 竞品
  - featured_snippet: 是否获得精选摘要
  - local_pack: 是否进入本地包

alerts:
  - rank_drop: 排名下降>5 位
  - new_competitor: 新竞品进入前 10
  - featured_snippet_won: 获得精选摘要
```

### 4. 技术 SEO 审计 (Technical SEO Audit)

```yaml
输入：网站 URL
输出：技术 SEO 报告 + 修复建议

audit_items:
  - crawlability: 可抓取性 (robots.txt, sitemap)
  - indexability: 可索引性 (noindex, canonical)
  - site_speed: 页面速度 (Core Web Vitals)
  - mobile_friendly: 移动端适配
  - https: HTTPS 配置
  - structured_data: 结构化数据 (Schema.org)
  - internal_linking: 内链结构
  - duplicate_content: 重复内容
  - broken_links: 死链检测
  - xml_sitemap: Sitemap 完整性

tools:
  - site_crawl: 网站爬取
  - speed_test: 速度测试 (PageSpeed Insights API)
  - mobile_test: 移动端测试
  - schema_validator: 结构化数据验证
```

**使用示例：**
```
用户：审计 mywebsite.com 的技术 SEO
Agent:
  1. 爬取网站（最多 100 页）
  2. 检测 Core Web Vitals
  3. 检查结构化数据
  4. 输出优先级修复清单（高/中/低）
```

### 5. 竞品分析 (Competitor Analysis)

```yaml
输入：竞品域名、目标关键词
输出：竞品 SEO 策略分析

analysis:
  - top_keywords: 竞品排名靠前的关键词
  - backlink_profile: 外链数量/质量
  - content_gaps: 内容缺口（竞品有我们没有的）
  - traffic_estimate: 预估自然流量
  - top_pages: 流量最高的页面

tools:
  - competitor_keywords: 竞品关键词分析
  - backlink_analyzer: 外链分析
  - content_gap: 内容缺口分析
  - traffic_estimator: 流量预估
```

## SEO 检查清单

### 发布前检查

- [ ] 目标关键词已研究（搜索量>100，难度<50）
- [ ] 标题标签包含关键词（50-60 字符）
- [ ] Meta 描述包含关键词（150-160 字符）
- [ ] H1 标签包含关键词（每页仅 1 个 H1）
- [ ] H2/H3 结构清晰，包含相关关键词
- [ ] URL 简短，包含关键词（<60 字符）
- [ ] 图片有 ALT 文本
- [ ] 内链到相关页面（3-5 个）
- [ ] 外链到权威来源（2-3 个）
- [ ] 移动端适配测试通过
- [ ] 页面加载速度<3 秒

### 技术 SEO 检查

- [ ] robots.txt 配置正确
- [ ] XML Sitemap 已提交 Google Search Console
- [ ] HTTPS 配置正确
- [ ] Canonical 标签设置
- [ ] 结构化数据（Schema.org）添加
- [ ] Core Web Vitals 达标（LCP<2.5s, FID<100ms, CLS<0.1）
- [ ] 无 404 错误
- [ ] 无重复内容问题

## 工具函数

### keyword_research

```python
def keyword_research(seed_keyword: str, location: str = "CN", language: str = "zh") -> dict:
    """
    关键词研究
    
    Args:
        seed_keyword: 种子关键词
        location: 目标地理位置 (CN/US/UK 等)
        language: 目标语言 (zh/en 等)
    
    Returns:
        {
            "keywords": [
                {
                    "keyword": "AI 工具",
                    "search_volume": 12000,
                    "difficulty": 45,
                    "cpc": 2.5,
                    "trend": [8000, 9000, 10000, ...],
                    "intent": "commercial"
                }
            ],
            "recommendations": ["低难度高价值关键词列表"]
        }
    """
```

### content_optimize

```python
def content_optimize(content: str, target_keyword: str) -> dict:
    """
    内容优化
    
    Args:
        content: 文章内容
        target_keyword: 目标关键词
    
    Returns:
        {
            "score": 75,  # SEO 评分 (0-100)
            "suggestions": [
                {"type": "title", "issue": "标题未包含关键词", "fix": "在标题中加入'AI 工具'"},
                {"type": "density", "issue": "关键词密度过低", "fix": "增加 2-3 处关键词"}
            ],
            "optimized_version": "优化后的内容"
        }
    """
```

### technical_audit

```python
def technical_audit(url: str) -> dict:
    """
    技术 SEO 审计
    
    Args:
        url: 网站 URL
    
    Returns:
        {
            "score": 68,  # 技术 SEO 评分
            "issues": {
                "high": ["Core Web Vitals 不达标", "移动端适配问题"],
                "medium": ["缺少结构化数据", "内链不足"],
                "low": ["图片 ALT 文本缺失"]
            },
            "fix_priority": ["修复 LCP", "添加 Schema", "优化图片"]
        }
    """
```

## SEO 最佳实践

### 关键词策略

1. **长尾关键词优先** — 难度低，转化率高
   - ❌ "AI 工具"（难度 65，搜索量 50000）
   - ✅ "OpenClaw Skills 安装教程"（难度 25，搜索量 500）

2. **搜索意图匹配** — 信息型 vs 交易型
   - 信息型：教程、指南、对比 → 博客文章
   - 交易型：购买、价格、评测 → 产品页面

3. **关键词布局** — 自然分布，避免堆砌
   - 标题、H1、首段、结尾
   - 密度 1-2%，不要超过 3%

### 内容策略

1. **E-E-A-T 原则** — Google 排名核心
   - Experience（经验）
   - Expertise（专业性）
   - Authoritativeness（权威性）
   - Trustworthiness（可信度）

2. **内容深度** — 2000+ 字长文排名更好
   - 全面覆盖主题
   - 包含案例、数据、图表
   - 定期更新（Google 喜欢新鲜内容）

3. **内部链接** — 传递权重
   - 每篇文章链接 3-5 篇相关内容
   - 使用描述性锚文本
   - 建立内容集群（Topic Cluster）

## 相关文件

- [Google Search Console](https://search.google.com/search-console)
- [Google Keyword Planner](https://ads.google.com/keywordplanner)
- [Ahrefs](https://ahrefs.com)
- [SEMrush](https://semrush.com)
- [Moz](https://moz.com)

## 触发词

- 自动：检测 SEO、关键词、排名、优化相关关键词
- 手动：/seo-agent, /keyword-research, /seo-audit
- 短语：SEO 优化、关键词研究、排名监控、技术审计

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
