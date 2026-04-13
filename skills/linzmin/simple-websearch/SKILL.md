---
name: simple-websearch
description: 极简网络搜索技能 - 支持通用搜索 + 社交媒体搜索（小红书/知乎/微博）
version: 2.0.0
author: 鸭鸭 (Yaya)
license: MIT
tags:
  - search
  - web
  - internet
  - exa
  - social-media
  - xiaohongshu
  - zhihu
  - weibo
emoji: 🔍
---

# Simple Web Search Skill V2

极简网络搜索技能增强版，无需任何 API Key，开箱即用。

## 🆕 V2.0 新特性

- 🔍 **通用搜索** - Exa AI + 必应 + 百度，三引擎智能降级
- 📱 **社交媒体搜索** - 小红书/知乎/微博，一键搜索全网热点
- ⚡ **稳定可靠** - 国内网络优化，保证可用性
- 📦 **零依赖** - 仅需 `requests`，可选 Playwright 增强

---

## 特点

- 🚀 **Exa AI 优先** - OpenCode 同款搜索接口，免费无需 API Key
- 🔍 **多引擎备用** - Exa → 必应 → 百度，自动降级保证有结果
- 📱 **社交搜索** - 支持小红书/知乎/微博内容搜索
- 🎯 **结果精准** - 优化过的正则提取，过滤广告
- 📦 **开箱即用** - 无需配置，安装即可搜索
- ⚡ **轻量快速** - 仅需 `requests` 一个 Python 依赖

---

## 搜索引擎策略

### 通用搜索
1. **Exa AI 优先** - OpenCode 同款，免费、快速、质量好
2. **必应备用** - Exa 无结果时自动切换
3. **百度补充** - 中文内容补充

### 社交媒体搜索
1. **小红书** - 种草笔记、产品评测、生活分享
2. **知乎** - 专业问答、深度讨论、知识分享
3. **微博** - 实时热点、新闻动态、话题讨论

---

## 使用方法

### 基本搜索（通用）

```python
result = main({
    "action": "search",
    "query": "Python 教程",
    "num_results": 5,
    "type": "general"  # 默认值，可省略
})
```

### 社交媒体搜索

```python
# 搜索所有平台
result = main({
    "action": "search",
    "query": "AI Agent",
    "num_results": 10,
    "type": "social_media"
})

# 只搜索小红书
result = main({
    "action": "search",
    "query": "护肤品推荐",
    "platform": "xiaohongshu",
    "type": "social_media"
})

# 只搜索知乎
result = main({
    "action": "search",
    "query": "如何学习编程",
    "platform": "zhihu",
    "type": "social_media"
})

# 只搜索微博
result = main({
    "action": "search",
    "query": "今日热搜",
    "platform": "weibo",
    "type": "social_media"
})
```

### 命令行

```bash
# 通用搜索
python3 scripts/search_v2.py "搜索关键词" 5 general

# 社交媒体搜索
python3 scripts/search_v2.py "AI Agent" 10 social_media

# 指定平台
python3 scripts/search_v2.py "护肤" 5 social_media
```

---

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | 是 | 操作类型：`search` / `test` |
| query | string | 是 | 搜索关键词 |
| num_results | int | 否 | 结果数量，默认 5，最大 20 |
| type | string | 否 | 搜索类型：`general` / `social_media` |
| platform | string | 否 | 社交媒体平台：`xiaohongshu` / `zhihu` / `weibo` / `all` |

---

## 输出格式

### 通用搜索结果

```json
{
    "success": true,
    "query": "搜索关键词",
    "type": "general",
    "engine": "exa+bing",
    "num_results": 5,
    "results": [
        {
            "title": "结果标题",
            "href": "https://...",
            "body": "摘要内容"
        }
    ],
    "message": "搜索完成",
    "timestamp": "2026-04-09T08:00:00Z"
}
```

### 社交媒体搜索结果

```json
{
    "success": true,
    "query": "搜索关键词",
    "type": "social_media",
    "platforms": ["xiaohongshu", "zhihu", "weibo"],
    "num_results": 3,
    "results": [
        {
            "title": "[小红书] 结果标题",
            "href": "https://www.xiaohongshu.com/...",
            "body": "小红书笔记",
            "source": "xiaohongshu"
        },
        {
            "title": "[知乎] 问题标题",
            "href": "https://www.zhihu.com/...",
            "body": "知乎问答",
            "source": "zhihu"
        }
    ],
    "message": "搜索完成 (平台：xiaohongshu, zhihu)"
}
```

---

## 示例

### 示例 1：搜索新闻

```python
result = main({
    "action": "search",
    "query": "AI 最新进展 2026",
    "num_results": 8
})

if result["success"]:
    for r in result["results"]:
        print(f"- {r['title']}: {r['href']}")
```

### 示例 2：搜索股票信息

```python
result = main({
    "action": "search",
    "query": "三六零 601360 股价",
    "num_results": 5
})
```

### 示例 3：小红书种草

```python
result = main({
    "action": "search",
    "query": "敏感肌护肤品",
    "platform": "xiaohongshu",
    "type": "social_media"
})
```

### 示例 4：知乎专业问答

```python
result = main({
    "action": "search",
    "query": "如何评价 GPT-5",
    "platform": "zhihu",
    "type": "social_media"
})
```

### 示例 5：微博热点

```python
result = main({
    "action": "search",
    "query": "今日热搜",
    "platform": "weibo",
    "type": "social_media"
})
```

### 示例 6：测试搜索引擎可用性

```python
result = main({
    "action": "test"
})

# 输出：
# {
#     "success": true,
#     "results": {
#         "exa": true,
#         "bing": true,
#         "baidu": true
#     }
# }
```

---

## 依赖

仅需一个 Python 包：

```bash
pip install requests
```

### 可选依赖（社交媒体搜索增强）

```bash
pip install playwright
playwright install chromium
```

安装后可启用动态网页抓取，获取更丰富的社交媒体内容。

---

## 与 web-search-ex-skill 的区别

| 特性 | simple-websearch | web-search-ex-skill |
|------|------------------|---------------------|
| 依赖 | requests | requests + baidusearch + crawl4ai + playwright |
| 安装大小 | ~100KB | ~200MB+ |
| 启动速度 | 毫秒级 | 秒级（Playwright 冷启动） |
| 搜索深度 | 基础搜索 + 社交媒体 | 支持深度搜索/爬虫 |
| 社交媒体 | ✅ 小红书/知乎/微博 | ❌ 无 |
| 适用场景 | 日常快速搜索 + 社交热点 | 需要抓取网页详情 |

---

## 搜索引擎对比

| 引擎 | 优点 | 缺点 | 使用场景 |
|------|------|------|----------|
| **Exa AI** | 免费、快速、质量好 | 中文内容较少 | 技术搜索、英文内容 |
| **必应** | 中英文兼顾、结果丰富 | 需要网络请求 | 通用搜索 |
| **百度** | 中文内容最全 | 广告较多 | 中文内容搜索 |
| **小红书** | 种草笔记、真实体验 | 需要动态抓取 | 产品评测、生活分享 |
| **知乎** | 专业问答、深度讨论 | 需要动态抓取 | 知识学习、问题分析 |
| **微博** | 实时热点、新闻动态 | 内容较碎片 | 热点追踪、舆情监控 |

---

## 注意事项

1. 首次运行会自动安装 `requests`
2. 搜索结果可能因网络环境而异
3. 建议单次查询不超过 10 条结果
4. 社交媒体搜索需要动态网页抓取支持（可选）
5. 国内用户建议优先使用 Exa + 必应组合

---

## 常见问题

### Q: 为什么搜索结果有时为空？

**A:** 可能是网络问题或搜索引擎限流。建议：
1. 检查网络连接
2. 减少结果数量
3. 更换搜索关键词
4. 使用 `action: test` 测试引擎可用性

### Q: 社交媒体搜索为什么只有链接没有内容？

**A:** 这是正常行为。社交媒体有反爬机制，为了稳定性：
- 基础模式：返回搜索链接，用户点击查看详情
- 增强模式：安装 Playwright 后可抓取部分内容

### Q: 如何提高搜索质量？

**A:** 
1. 使用更具体的关键词
2. 指定搜索平台（如只搜知乎）
3. 结合多个平台结果对比

---

## 💬 反馈与支持

如果你觉得这个技能有用：
- ⭐ **给个 Star** - 在 ClawHub 上收藏支持一下
- 💬 **留个评论** - 你的反馈帮助我改进
- 🐛 **报告问题** - 遇到问题欢迎提 issue

你的支持是我更新维护的动力！🦆

---

_简洁，但不简单。_ 🦆
