---
name: news-to-markdown-skill
description: 一键将新闻文章转换为 Markdown，支持双引擎内容提取、智能封面图选择、图片下载到本地、三层 HTML 抓取策略和多平台专项优化。支持13个平台：头条、微信公众号、36kr、知乎、掘金、简书、CSDN、人人都是产品经理、开源中国、B站专栏、SegmentFault、博客园、小红书
version: 3.1.3
author: Ping Si <sipingme@gmail.com>
user-invocable: true
requires:
  runtime:
    - name: node
      version: ">=18.0.0"
    - name: npm
      version: ">=8.0.0"
install:
  type: npx
  package: news-to-markdown
  version: "^3.1.3"
  execution: "npx --yes news-to-markdown@^3.1.3"
  riskLevel: moderate
  riskReason: "通过 npx 动态拉取并执行第三方 npm 包，存在供应链风险。使用前请审计源码。"
  source:
    registry: https://registry.npmjs.org
    repository: https://github.com/sipingme/news-to-markdown
    license: MIT
    audit: https://github.com/sipingme/news-to-markdown/blob/main/src/index.ts
tags:
  - news
  - markdown
  - converter
  - extractor
  - web-scraping
  - toutiao
  - wechat
  - 36kr
  - bilibili
  - csdn
  - cnblogs
  - segmentfault
repository: https://github.com/sipingme/news-to-markdown-skill
core-library: https://github.com/sipingme/news-to-markdown
files:
  - scripts/convert.js    # CLI 入口（npx 包装）
  - config.json           # Skill 配置
  - SKILL.md              # 技能文档
  - README.md             # 项目说明
---

# news-to-markdown Skill

## 📋 概述

这是一个专门用于将新闻文章转换为 Markdown 格式的 ClawHub Skill。它结合了智能内容提取和高质量格式转换，能够自动识别新闻正文、过滤噪音内容，并输出格式化的 Markdown 文档。

### 核心特点（先看这个）

**一眼看懂：这个 Skill 能帮你什么？**

- **提取更准**：双引擎内容提取，正文和元数据兼顾
- **图片更稳**：支持下载到本地，避免远程图片失效
- **抓取更稳**：三层抓取策略，动态页面也能处理
- **平台更全**：内置 10 个主流内容平台专项优化
- **输出可发布**：Markdown 质量高，支持后续自动化发布

#### 1) 提取更准：双引擎内容提取

- `Readability`：提取完整正文，保留图片和多媒体
- `news-extractor-node`：提取标题、作者、发布时间等元数据
- 自动选择最佳结果，减少漏提取和误提取

#### 2) 图片更稳：下载到本地 + 智能封面

- 支持将远程图片下载到本地目录并使用相对路径
- 避免 URL 签名过期和防盗链导致的图片失效
- 智能封面图选择：优先 `og:image` / `twitter:image`，失败再降级
- 完美配合 `wechat-md-publisher` 使用

#### 3) 抓取更稳：三层抓取策略

- `curl` → `wget` → `Playwright` 自动降级
- 静态页优先快速抓取，动态页自动启用浏览器渲染
- 兼顾速度与成功率

#### 4) 平台更全：10 平台专项优化

- ✅ 头条、微信公众号、人人都是产品经理
- ✅ 掘金、简书、CSDN、开源中国
- ✅ B站专栏、SegmentFault、博客园

#### 5) 输出可发布：质量与扩展性并重

- 基于 `html-to-markdown-node` 的高质量转换引擎
- 图片保护机制，避免纯图片段落被误过滤
- 支持自定义平台适配器，便于持续扩展

这是 [news-to-markdown](https://github.com/sipingme/news-to-markdown) 核心库的轻量级 CLI 包装。

## 🎯 使用场景

### ⚠️ 安全风险提示

**供应链风险**：本 Skill 通过 `npx` 动态拉取并执行第三方 npm 包 `news-to-markdown`。使用前请审计源码：
- **源码仓库**: https://github.com/sipingme/news-to-markdown
- **审计入口**: https://github.com/sipingme/news-to-markdown/blob/main/src/index.ts

### 场景 1：基础转换（推荐：下载图片到本地）⭐

**用户意图**：
- "把这个头条文章转成 Markdown"
- "提取这篇文章，图片也要保存"

**AI 调用**：
```bash
npx --yes news-to-markdown@^3.1.3 \
  --url "https://www.toutiao.com/article/123" \
  --download-images \
  --output-dir ./article
```

**为什么推荐下载图片？**
- 头条图片 URL 包含签名和过期时间，几小时后会失效
- 本地图片更可靠，不受网络波动影响
- 完美配合 wechat-md-publisher 发布到微信公众号

### 场景 2：快速转换（不下载图片）

**用户意图**：
- "快速看一下这篇文章内容"
- "只要文字，不需要图片"

**AI 调用**：
```bash
npx --yes news-to-markdown@^3.1.3 \
  --url "https://www.toutiao.com/article/123" \
  --no-download-images \
  --output "article.md"
```

**输出**：
- 包含元数据的完整 Markdown 文件
- 自动过滤广告和评论
- 收集所有图片链接

### 场景 3：批量采集新闻

**用户意图**：
- "把这些新闻都保存下来"
- "批量下载这个列表的文章"

**AI 调用**：
```bash
# 循环处理多个 URL
for url in "${urls[@]}"; do
  npx --yes news-to-markdown@^3.1.3 --url "$url" --output "articles/$(basename $url).md"
done
```

### 场景 4：处理动态网站

**用户意图**：
- "这个网站需要 JavaScript 才能显示内容"
- "页面是动态加载的"

**AI 行为**：
- 自动检测并使用 Playwright
- 等待页面完全加载
- 提取渲染后的内容

### 场景 5：自定义提取

**用户意图**：
- "只要正文，不要其他的"
- "去掉侧边栏和评论"

**AI 调用**：
```bash
npx --yes news-to-markdown@^3.1.3 \
  --url "https://example.com/news" \
  --noise ".sidebar,.comments,.ads" \
  --no-metadata
```

## 🔧 命令详解

### npx news-to-markdown

从 URL 提取新闻并转换为 Markdown。

```bash
npx --yes news-to-markdown@^3.1.3 --url <URL> [选项]
```

#### 参数

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `--url` | string | ✅ | 新闻文章的 URL | `https://example.com/news` |
| `--output` | string | ❌ | 输出文件路径 | `article.md` |
| `--download-images` | flag | ❌ | 下载图片到本地 ⭐ NEW | - |
| `--output-dir` | string | ❌ | 输出目录（用于图片下载） | `./output` |
| `--selector` | string | ❌ | CSS 选择器，指定提取区域 | `article.content` |
| `--noise` | string | ❌ | 要移除的元素（逗号分隔） | `.ad,.sidebar,.comments` |
| `--no-metadata` | flag | ❌ | 不包含元数据（标题、作者、时间） | - |

#### 返回值

**成功时**：
```json
{
  "success": true,
  "metadata": {
    "title": "文章标题",
    "author": "作者名",
    "publishTime": "2026-03-22 10:30:00",
    "imageCount": 3,
    "contentLength": 1234
  }
}
```

**失败时**：
```json
{
  "success": false,
  "error": "错误信息"
}
```

#### 输出格式

**标准格式**（包含元数据）：
```markdown
# 文章标题

**作者**: 张三  
**发布时间**: 2026-03-22 10:30:00  
**来源**: https://example.com/news/article

---

正文内容...

## 图片列表

- ![](image1.jpg)
- ![](image2.jpg)
```

**简洁格式**（`--no-metadata`）：
```markdown
正文内容...
```

## 🚀 工作流程

### 1. HTML 抓取（三层策略）

```
尝试 curl (最快，1-3秒)
  ↓ 失败
尝试 wget (备选)
  ↓ 失败
使用 Playwright (支持 JS，5-10秒)
  ↓
成功获取 HTML
```

**特点**：
- ✅ 自动选择最快的方式
- ✅ 失败时自动降级
- ✅ 显示当前使用的方法
- ✅ 整体成功率 95%+

### 2. 内容提取

使用 `news-extractor-node` 的文本密度算法：

```javascript
const extractor = new NewsExtractor();
const news = extractor.extract(html, {
  url: url,
  noiseSelectors: ['.ad', '.comment', 'aside']
});
```

**提取内容**：
- 标题（多种策略）
- 作者（正则匹配 + 选择器）
- 发布时间（多种日期格式）
- 正文（文本密度算法）
- 图片（自动收集）

### 3. Markdown 转换

使用 `@siping/html-to-markdown-node`：

```javascript
const markdown = convertString(news.contentHtml, {
  domain: url
});
```

**转换特点**：
- 保留标题层级
- 正确处理列表
- 转换代码块
- 解析相对 URL
- 智能转义

## 📊 性能指标

| 指标 | curl | wget | Playwright |
|------|------|------|------------|
| 速度 | 1-3秒 | 2-4秒 | 5-10秒 |
| 成功率 | 70% | 75% | 95% |
| JS 支持 | ❌ | ❌ | ✅ |
| 资源占用 | 极低 | 低 | 中 |

**整体性能**：
- 平均响应时间：2-5 秒
- 整体成功率：95%+
- 支持网站类型：静态 + SPA

## ⚠️ 注意事项

### 1. 网络要求

- 需要能够访问目标 URL
- 某些网站可能有反爬虫机制
- 建议使用稳定的网络连接

### 2. Playwright 安装

首次使用 Playwright 需要安装浏览器：

```bash
npx playwright install chromium
```

### 3. 网站兼容性

**高兼容性**：
- 主流新闻网站（新浪、网易、腾讯等）
- 技术博客（CSDN、掘金等）
- 官方新闻站

**可能需要调整**：
- 特殊布局的网站（使用 `--selector`）
- 需要登录的网站
- 有严格反爬虫的网站

### 4. 内容准确性

- 文本密度算法对大多数新闻网站准确率高
- 对于特殊布局，可能需要自定义选择器
- 建议检查输出结果

### 5. 版权与合规

- 对于有明确版权限制、付费墙、转载限制或平台禁止抓取的文章，需要特别处理
- 默认仅用于个人学习、内容归档和授权范围内的二次整理，不建议直接公开分发原文
- 在发布到公众号、博客或第三方平台前，建议先确认来源站点的版权声明与转载政策
- 如需对外发布，建议保留来源链接、作者信息，并仅摘录必要内容

## 🎨 AI 使用指南

### 识别新闻采集需求

**关键词**：
- "保存新闻"、"下载文章"
- "转换为 Markdown"
- "采集内容"、"提取正文"

**URL 特征**：
- 包含 `/news/`、`/article/`
- 新闻网站域名
- 博客文章链接

### 参数选择建议

**默认使用**：
```bash
npx --yes news-to-markdown@^3.1.3 --url "$URL" --output "article.md"
```

**用户要求"只要正文"**：
```bash
npx --yes news-to-markdown@^3.1.3 --url "$URL" --no-metadata
```

**用户提到"去掉广告/评论"**：
```bash
npx --yes news-to-markdown@^3.1.3 --url "$URL" --noise ".ad,.comment,.sidebar"
```

**用户指定"只要某个部分"**：
```bash
npx --yes news-to-markdown@^3.1.3 --url "$URL" --selector "article.main-content"
```

### 错误处理

**抓取失败**：
```
建议：
1. 检查 URL 是否正确
2. 尝试在浏览器中打开
3. 检查网络连接
4. 确认 Playwright 已安装
```

**提取失败**：
```
建议：
1. 使用 --selector 指定内容区域
2. 调整 --noise 过滤规则
3. 检查网站是否需要登录
```

## 🔍 常见问题

### Q1: 为什么有些网站抓取失败？

**A**: 可能的原因：
1. 网站需要 JavaScript 渲染（会自动使用 Playwright）
2. 网站有反爬虫机制
3. 需要登录才能访问
4. 网络连接问题

**解决方案**：
- 检查 Playwright 是否已安装
- 尝试在浏览器中打开 URL
- 使用 `--selector` 指定内容区域

### Q2: 提取的内容不准确怎么办？

**A**: 使用自定义选择器：
```bash
npx --yes news-to-markdown@^3.1.3 --url "$URL" --selector "article.main-content"
```

### Q3: 如何去除特定元素？

**A**: 使用 `--noise` 参数：
```bash
npx --yes news-to-markdown@^3.1.3 --url "$URL" --noise ".ad,.sidebar,.comments"
```

### Q4: 支持哪些网站？

**A**: 
- ✅ 大多数新闻网站（静态 HTML）
- ✅ 技术博客
- ✅ SPA 网站（通过 Playwright）
- ⚠️ 需要登录的网站（不支持）

## 📚 示例对话

### 示例 1: 简单保存

**用户**: "帮我保存这篇新闻 https://example.com/news/ai-breakthrough"

**AI**: 
```
我来帮你保存这篇新闻。

[调用 npx --yes news-to-markdown@^3.1.3 --url "https://example.com/news/ai-breakthrough" --output "ai-breakthrough.md"]

✅ 已成功保存到 ai-breakthrough.md

文章信息：
- 标题：AI 技术取得重大突破
- 作者：张三
- 发布时间：2026-03-22
- 图片数量：3 张
```

### 示例 2: 批量处理

**用户**: "把这些新闻都保存下来：[URL1, URL2, URL3]"

**AI**:
```
我来批量保存这些新闻。

正在处理 URL1...
✅ 已保存到 article-1.md

正在处理 URL2...
✅ 已保存到 article-2.md

正在处理 URL3...
✅ 已保存到 article-3.md

全部完成！共保存 3 篇文章。
```

### 示例 3: 自定义提取

**用户**: "只要正文，不要标题和作者信息"

**AI**:
```
好的，我只提取正文内容。

[调用 npx --yes news-to-markdown@^3.1.3 --url "$URL" --no-metadata]

✅ 已保存纯正文内容。
```

## 🛠️ 维护说明

### 依赖更新

本 Skill 使用 `npx` 动态执行，会自动拉取指定版本的包。如需清除缓存：

```bash
# 清除 npx 缓存
npm cache clean --force

# 验证版本
npx --yes news-to-markdown@^3.1.3 --version
```

### 测试

建议定期测试常用网站：

```bash
# 测试主流新闻网站
npx --yes news-to-markdown@^3.1.3 --url "https://news.sina.com.cn/..." --verbose
npx --yes news-to-markdown@^3.1.3 --url "https://36kr.com/p/..." --verbose
npx --yes news-to-markdown@^3.1.3 --url "https://mp.weixin.qq.com/s/..." --verbose
```

### 日志

脚本会输出详细的执行日志：
- 使用的抓取方式
- 提取的元数据
- 转换结果

## 📞 支持

- GitHub Issues: https://github.com/sipingme/news-to-markdown-skill/issues
- Email: sipingme@gmail.com

---

**版本**: 3.1.3  
**最后更新**: 2026-04-08

## 📝 更新日志

### v2.3.30 (2026-04-06)

#### 重构

- ✅ **改用 npx 动态执行**：移除全局依赖安装，通过 `npx --yes news-to-markdown@^3.1.3` 执行
- ✅ **添加 config.json**：符合 ClawHub Skill 规范，包含 install 规范和供应链风险声明
- ✅ **添加 scripts/convert.js**：npx 包装脚本
- ✅ **更新 SKILL.md**：所有命令示例改为 npx 方式，添加安全风险提示
- ✅ **新增 36kr 平台支持**：自动转换为移动端 URL 绕过反爬机制

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.4.29
  - 新增 36kr 平台支持
  - 优化 BasePlatform 公共方法

### v2.3.18 (2026-03-30)

#### 修复

- ✅ 修复版本号不一致问题（package.json, _meta.json, SKILL.md 统一）
- ✅ 添加运行时依赖声明（curl/wget/Playwright）
- ✅ 添加 homepage 元数据
- ✅ 完善 files 列表声明

### v2.3.17 (2026-03-30)

#### 新增

- ✅ 添加 `--download-images` 参数支持
- ✅ 添加 `--output-dir` 参数支持

### v2.3.16 (2026-03-29)

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.4.18
  - 同步核心库最新发布

### v2.3.15 (2026-03-29)

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.4.16
  - 补齐 `1.` / `1)` / `（1）` 编号标题独占段落规则
  - 正文中重复出现的封面图改为本地路径替换

### v2.3.14 (2026-03-28)

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.4.15
  - 微信 section 边界预处理，减少样式块合并
  - 编号标题与分节标题换行规则优化
  - 代码块与粗体粘连文本修复

### v2.3.13 (2026-03-28)

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.4.12
  - 默认下载测试图片（`test-url`）
  - 微信文末二维码图片过滤优化
  - 避免下载已被后处理移除的图片

### v2.3.12 (2026-03-28)

#### 微信公众号图片优化

- ✅ **修复懒加载图片处理**：先用 `data-src` 替换 `src`，再进行过滤，解决纯图片文章无法提取的问题
- ✅ **添加装饰图过滤**：
  - 过滤 `__bg_gif` 类装饰性 GIF 背景图
  - 过滤小尺寸装饰图（≤ 60px）
- ✅ **修复纯图片文章提取**：当 Readability 和 NewsExtractor 都失败时，从原始 HTML 提取图片构建内容
- ✅ **优化封面图选择**：跳过装饰性图片，使用正文第一张有效图片

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.4.7

### v2.3.11 (2026-03-26)

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.3.11
  - 修复微信公众号空段落问题
  - 压缩连续空行（3+ 个空行压缩为 2 个）
  - 防止 wenyan-md 生成过多空 `<p>` 标签

### v2.3.10 (2026-03-26)

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.3.10
  - 更新所有平台的预处理器
  - 新增调试工具和测试脚本

### v2.3.9 (2026-03-25)

#### 修复

- ✅ **封面图重复问题修复**：
  - 修复封面图在正文开头重复出现的问题
  - 自动检测并移除与 frontmatter cover 相同的正文开头图片
  - 比较图片 URL 时忽略查询参数差异
  - 确保推送到微信公众号时不会出现重复图片

#### 依赖更新

- ✅ 升级 `news-to-markdown` 到 v1.3.9

### v2.3.8 (2026-03-24)

#### 新增平台支持（共10个）

- ✅ **头条**（移动端 + PC 端）- v1.2.6
- ✅ **微信公众号** - v1.2.6
- ✅ **掘金** - v1.2.7
- ✅ **简书** - v1.2.8
- ✅ **CSDN** - v1.2.9
- ✅ **人人都是产品经理** - v1.3.0
- ✅ **开源中国** - v1.3.1
- ✅ **B站专栏** - v1.3.2
- ✅ **SegmentFault** - v1.3.3
- ✅ **博客园** - v1.3.4

#### 架构优化

- ✅ **核心库分离**：所有业务逻辑迁移到 `news-to-markdown` 核心库
- ✅ **Skill 精简化**：仅保留 CLI 包装层，专注于 ClawHub 集成
- ✅ **TypeScript 支持**：核心库完全用 TypeScript 重写
- ✅ **平台注册系统**：支持自定义平台适配器注册

#### 依赖优化

- ✅ 依赖数量从 4 个减少到 1 个（仅 `news-to-markdown`）
- ✅ 所有底层依赖由核心库管理