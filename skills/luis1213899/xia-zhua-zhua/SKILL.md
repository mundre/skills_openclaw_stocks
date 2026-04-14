---
name: xia-zhua-zhua
description: 将任意网页抓取并保存为 Markdown 文件（中文名：虾抓抓）。使用 Playwright + Turndown 引擎，支持所有网页。触发条件：用户要求抓取网页、网页转 markdown、clip 网页、虾抓抓。
---

# 虾抓抓 - 网页转 Markdown

## 使用方式

```bash
# 单个网页
node markdown-clip.js <url> [outputDir]

# 批量并发抓取（多URL）
node batch-clip.js <url文件> [并发数] [输出目录]
# url文件格式：每行一个URL，支持 # 注释
```

## 功能

- **网页抓取** — 使用 Playwright 模拟浏览器访问页面，自动过滤 script/style/nav/header/footer
- **HTML → Markdown** — 使用 Turndown 引擎转换，保留图片/链接/代码块
- **元数据** — 自动提取 title/author/description/cover
- **文件命名** — `日期-域名-标题.md`
- **Frontmatter** — YAML 元数据（title/author/description/cover/source/clipped）
- **批量并发** — 支持 `batch-clip.js` 并发抓取多 URL（默认 3 并发，最大 10）

## 反爬措施

- 随机 User-Agent（4种浏览器）
- 隐藏 `navigator.webdriver` 标志
- 伪造 `navigator.plugins` / `languages`
- 注入 `window.chrome = { runtime: {} }`
- 随机等待 1~3s 模拟人类访问节奏
- 加载失败自动降级重试

## 依赖

技能目录已包含 `package.json`，运行 `npm install` 会自动安装：
- playwright
- turndown

## 安装其他用户

**方式一（推荐）：**
```bash
openclaw skill install xia-zhua-zhua.skill
```

**方式二：**
直接把 `xia-zhua-zhua` 文件夹放入 `~/.openclaw/workspace/skills/` 目录。

## 首次使用前准备

```bash
cd ~/.openclaw/workspace/skills/xia-zhua-zhua
npm install
npx playwright install chromium
```

只需执行一次，后续直接使用即可。
