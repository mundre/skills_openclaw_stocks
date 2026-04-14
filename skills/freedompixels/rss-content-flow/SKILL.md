---
name: rss-content-flow
description: |
  RSS 订阅 + AI 内容流引擎。监控多个 RSS 源，自动抓取最新文章，
  AI 分析提取核心观点，一键生成适配知乎/小红书/公众号的原创内容。
  触发场景：用户说"帮我找今天的选题"、"RSS订阅"、"监控XX的更新"、
  "把XX的文章改写成小红书"、"我需要一些内容灵感"、"自动生成今日内容"。
  Keywords: RSS, 订阅, 内容选题, 今日内容, 内容灵感, 文章改写, feed, 监控.
---

# RSS 内容流

将 RSS 订阅转化为结构化内容素材，一站式生成多平台发布文案。

## 核心能力

1. **RSS 订阅管理** — 添加/删除/列出订阅源
2. **智能抓取** — 自动获取最新 N 篇文章
3. **AI 分析** — 提取核心观点、关键数据、金句
4. **内容生成** — 按平台风格改写（知乎/小红书/公众号）
5. **草稿保存** — 写入飞书文档或直接发布

## 快速开始

用户说"帮我找今天的选题"时：

```
1. 读取 ~/.qclaw/skills/rss-content-flow/scripts/config.json（订阅列表）
2. 用 fetch_feed() 获取各源最新条目
3. AI 分析后呈现 3-5 个可用选题
4. 用户确认后 → 生成完整内容
```

## 订阅管理

### 添加订阅源
```bash
python3 scripts/manage_feeds.py --add <name> <url>
# 示例：python3 scripts/manage_feeds.py --add 36氪 https://36kr.com/feed
```

### 列出订阅
```bash
python3 scripts/manage_feeds.py --list
```

### 删除订阅
```bash
python3 scripts/manage_feeds.py --remove <name>
```

### 默认订阅源（预配置）
| 名称 | URL | 内容方向 |
|------|-----|---------|
| 36氪 | https://36kr.com/feed | 科技/商业 |
| 虎嗅 | https://www.huxiu.com/rss/0.xml | 商业/创业 |
| 少数派 | https://sspai.com/feed | 效率/工具 |
| AI研习社 | https://ai.googleblog.com/feed/ | AI/技术 |
| OpenAI Blog | https://OpenAI.com/blog/rss.xml | AI产品 |

## 内容抓取

### 单源抓取
```bash
python3 scripts/fetch_feed.py --source 36氪 --limit 5
```

### 全源抓取
```bash
python3 scripts/fetch_feed.py --all --limit 3
```

输出示例：
```
📰 36氪 | 4篇新文章
  ① [AI创业] 标题：xxx | 浏览量预估：xxx
  ② [商业] 标题：xxx
  ...

📰 虎嗅 | 2篇新文章
  ① [汽车] 标题：xxx
  ...
```

### 抓取逻辑
1. 解析 RSS XML，获取 title/link/description/pubDate
2. 过滤：去除广告/软文/太旧的文章（>7天）
3. 按时间倒序排列
4. 返回结构化 JSON 供 AI 分析

## AI 内容分析

收到文章列表后，AI 自动执行：

```
对每篇文章：
1. 读取 description / 摘要
2. 判断：这篇文章的核心价值是什么？
3. 提取：
   - 核心观点（1-2句）
   - 关键数据（数字/排名/增长）
   - 金句（适合引用的原话）
   - 相关话题标签（3-5个）
4. 评估：适合哪些平台？
   - 知乎：深度分析/观点争议类
   - 小红书：实操教程/工具推荐/个人经验类
   - 公众号：行业趋势/商业观察类
```

## 平台内容生成

### 知乎风格
- 字数：800-1500字
- 结构：背景→问题→分析→结论
- 开头：痛点/争议性观点
- 结尾：行动号召/评论区互动
- 关键词：#AI #副业 #效率工具

### 小红书风格
- 字数：300-600字
- 结构：钩子→干货→互动
- emoji 序号 + 话题标签（#AI副业 #效率神器）
- 每段不超过3行
- 结尾：评论区互动问题

### 公众号风格
- 字数：1000-2000字
- 结构：开篇引子→案例拆解→方法论→资源推荐
- 标题公式：数字+情绪+悬念
- 文末：往期回顾/互动话题

## 输出方式

### 保存为草稿（默认）
```
feishu_doc action=create title="内容草稿 | {日期}" → 获取 doc_token
feishu_doc action=write doc_token={token} content={内容}
```

### 预览后发布
生成内容 → 用户确认 → 调用 social-media-poster 发布

### 自动发布（需用户授权）
```
用户说"自动发布"时：
1. 创建飞书文档（内容+元数据）
2. 调用 social-media-poster 发布
3. 返回发布结果
```

## 配置项

首次使用时向用户确认：

| 配置 | 说明 | 默认值 |
|------|------|--------|
| 订阅源 | 监控哪些 RSS | 36氪+虎嗅+少数派 |
| 抓取数量 | 每次取几条 | 每源3条 |
| 生成平台 | 生成哪个平台内容 | 用户指定 |
| 输出方式 | 草稿/直接发布 | 草稿 |
| 风格偏好 | 正式/轻松/专业 | 轻松 |

## 文件结构

```
rss-content-flow/
├── SKILL.md              # 本文件
├── README.md             # 用户文档
├── scripts/
│   ├── manage_feeds.py   # 订阅管理（增删查）
│   ├── fetch_feed.py     # RSS 抓取脚本
│   └── config.json       # 订阅配置（运行时生成）
├── references/
│   └── platform_style.md # 各平台风格指南
└── assets/               # 封面图模板等
```

## 与其他 Skill 的配合

- **social-media-poster**：生成内容后直接发布到知乎/小红书
- **feishu-daily-report**：每日内容草稿自动归入日报数据源
- **content-repurposer**：同一篇文章改写到不同平台

## 注意事项

- RSS 源需确保可访问，过期/失效的源自动跳过
- 生成内容时必须注明原文来源（保留链接）
- 版权合规：RSS 文章只能分析观点+改写，不得直接复制原文
- 抓取间隔建议不低于 30 分钟，避免对源站造成压力
