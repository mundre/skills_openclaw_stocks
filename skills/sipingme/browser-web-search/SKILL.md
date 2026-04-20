---
name: browser-web-search
description: 把任何网站变成命令行 API。13 平台 41 命令 — 知乎、小红书、B站、GitHub、豆瓣等。专为 OpenClaw 设计，复用浏览器登录态。
version: 0.1.0
author: Ping Si <sipingme@gmail.com>
type: cli
requires:
  - npm: browser-web-search
  - node: ">=18.0.0"
tags:
  - browser
  - web-search
  - scraping
  - automation
  - ai-agent
repository: https://github.com/sipingme/browser-web-search-skill
package: https://github.com/sipingme/browser-web-search
npm: https://www.npmjs.com/package/browser-web-search
---

# Browser Web Search (BWS) Skill

把任何网站变成命令行 API，专为 OpenClaw 设计，复用浏览器登录态。

## 🏗️ 架构说明

```
OpenClaw/AI Agent
    ↓ (读取 Skill 配置)
browser-web-search-skill
    ↓ (调用 CLI)
bws 命令
    ↓ (OpenClaw Browser)
目标网站
```

## 🎯 项目特点

### 专为 OpenClaw 设计
- **零配置**：无需 Chrome Extension、无需 Daemon，开箱即用
- **深度集成**：直接使用 OpenClaw 浏览器，与其他 Skill 共享登录态
- **轻量精简**：核心代码仅 22KB，无运行时依赖

### 复用登录态
- **无需 API Key**：使用你在浏览器中的登录状态
- **绕过反爬**：请求来自真实浏览器，不会被封禁
- **隐私安全**：数据在本地处理，不经过第三方服务器

### AI Agent 友好
- **结构化输出**：所有命令返回 JSON，便于 AI 解析
- **jq 过滤**：内置 jq 支持，精确提取所需数据
- **错误提示**：清晰的错误信息和修复建议

## 📋 前置要求

### 安装 browser-web-search

```bash
npm install -g browser-web-search
```

### 验证安装

```bash
bws --version
bws site list
```

## 🚀 快速开始

```bash
# 查看所有可用命令
bws site list

# 运行 adapter
bws zhihu/hot                      # 知乎热榜
bws xiaohongshu/search "旅行"       # 小红书搜索
bws bilibili/popular               # B站热门
bws github/repo facebook/react     # GitHub 仓库
```

## 📊 内置平台（13 平台 41 命令）

| 分类 | 平台 | 命令数 | 示例命令 |
|-----|-----|-------|---------|
| **搜索** | Google, Baidu, Bing | 3 | `bws google/search "query"` |
| **社交** | 小红书, 知乎 | 10 | `bws zhihu/hot` |
| **新闻** | 36kr, 今日头条 | 3 | `bws 36kr/newsflash` |
| **开发** | GitHub, CSDN, 博客园 | 8 | `bws github/repo owner/repo` |
| **视频** | Bilibili | 9 | `bws bilibili/popular` |
| **娱乐** | 豆瓣 | 6 | `bws douban/top250` |
| **招聘** | BOSS直聘 | 2 | `bws boss/search "职位"` |

## 🔧 标准操作流程 (SOP)

### 操作 1：查看可用命令

**场景**：用户想知道有哪些可用的 adapter

**命令**：
```bash
bws site list
```

**输出示例**：
```
zhihu/
  hot                  - Get Zhihu hot list
  search               - Search Zhihu
  question             - Get question details
  me                   - Get logged-in user info

xiaohongshu/
  search               - 搜索小红书笔记
  note                 - 获取笔记详情
  ...
```

---

### 操作 2：搜索 adapter

**场景**：用户想找特定平台的命令

**命令**：
```bash
bws site search bilibili
```

**输出示例**：
```
bilibili/popular       Get Bilibili popular videos
bilibili/search        Search Bilibili videos
bilibili/video         Get video details
...
```

---

### 操作 3：查看 adapter 详情

**场景**：用户想了解某个命令的参数

**命令**：
```bash
bws site info bilibili/video
```

**输出示例**：
```
bilibili/video - Get Bilibili video details by bvid

参数:
  bvid (required)      视频 BV 号

示例:
  bws site bilibili/video BV1xx411c7mD
```

---

### 操作 4：获取知乎热榜

**场景**：用户想获取知乎热门话题

**命令**：
```bash
bws zhihu/hot
```

**输出示例**：
```json
{
  "items": [
    {
      "title": "如何评价...",
      "url": "https://www.zhihu.com/question/...",
      "heat": "1234万热度"
    }
  ]
}
```

---

### 操作 5：搜索小红书

**场景**：用户想搜索小红书内容

**命令**：
```bash
bws xiaohongshu/search "旅行攻略"
```

**输出示例**：
```json
{
  "notes": [
    {
      "id": "abc123",
      "title": "云南旅行攻略",
      "author": "旅行博主",
      "likes": 1234
    }
  ]
}
```

---

### 操作 6：获取 B站热门视频

**场景**：用户想看 B站热门

**命令**：
```bash
bws bilibili/popular
```

**输出示例**：
```json
{
  "videos": [
    {
      "bvid": "BV1xx411c7mD",
      "title": "视频标题",
      "author": "UP主",
      "play": "100万",
      "like": "5万"
    }
  ]
}
```

---

### 操作 7：使用 jq 过滤

**场景**：用户只需要部分数据

**命令**：
```bash
# 只获取标题
bws zhihu/hot --jq '.items[].title'

# 提取特定字段
bws bilibili/popular --jq '.videos[] | {title, play}'
```

---

### 操作 8：获取 GitHub 仓库信息

**场景**：用户想查看某个 GitHub 仓库

**命令**：
```bash
bws github/repo facebook/react
```

**输出示例**：
```json
{
  "name": "react",
  "description": "A declarative, efficient, and flexible JavaScript library...",
  "stars": 220000,
  "forks": 45000,
  "language": "JavaScript"
}
```

---

### 操作 9：搜索引擎搜索

**场景**：用户想使用搜索引擎

**命令**：
```bash
bws google/search "OpenClaw AI"
bws baidu/search "人工智能"
bws bing/search "machine learning"
```

---

## ⚠️ 登录态管理

如果网站需要登录，命令会返回 401/403 错误。

**解决步骤**：

1. 在 OpenClaw 浏览器中打开网站：
   ```bash
   openclaw browser open https://xiaohongshu.com
   ```

2. 手动完成登录

3. 重试命令：
   ```bash
   bws xiaohongshu/me
   ```

---

## 📝 输出格式

所有命令默认返回 JSON 格式：

**成功响应**：
```json
{
  "items": [...],
  "count": 10
}
```

**错误响应**：
```json
{
  "success": false,
  "error": "错误信息"
}
```

---

## 🎓 示例对话

**用户**：帮我看看知乎今天有什么热门话题

**AI**：好的，我来获取知乎热榜。

```bash
bws zhihu/hot
```

**AI**：以下是知乎热榜前 10：
1. 如何评价...（1234万热度）
2. 为什么...（890万热度）
...

---

**用户**：搜索一下小红书上关于"露营"的笔记

**AI**：好的，我来搜索小红书。

```bash
bws xiaohongshu/search "露营"
```

**AI**：找到以下相关笔记：
1. 《新手露营装备清单》- 点赞 5.2k
2. 《周末露营好去处》- 点赞 3.8k
...

---

## 🔒 安全性说明

- ✅ 所有操作在本地执行
- ✅ 使用 OpenClaw 浏览器的登录态
- ❌ 不会收集用户信息
- ❌ 不会上传到第三方服务器

---

## 📚 参考资料

- [项目 GitHub](https://github.com/sipingme/browser-web-search-skill)
- [browser-web-search 核心库](https://github.com/sipingme/browser-web-search)
- [npm 包](https://www.npmjs.com/package/browser-web-search)

---

## 📝 维护说明

- **版本**: 0.1.0
- **最后更新**: 2026-03-31
- **维护者**: Ping Si <sipingme@gmail.com>
- **许可证**: MIT

---

## ✅ 首次成功检查清单

新用户应该能在 2 分钟内完成：

- [ ] 安装工具：`npm install -g browser-web-search`
- [ ] 检查安装：`bws --version`
- [ ] 查看命令：`bws site list`
- [ ] 测试运行：`bws zhihu/hot`
- [ ] 看到 JSON 输出

如果以上步骤都能顺利完成，说明 Skill 已正确配置！
