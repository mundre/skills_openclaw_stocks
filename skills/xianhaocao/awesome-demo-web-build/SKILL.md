---
name: awesome-demo-web-build
description: AI-native web demo project generator using Project Blueprint system. Use when user wants to "build a demo", "create a web project", "generate a landing page", "make an AI tool UI", or similar requests.
---

# AI Web Demo Builder

## Interaction Style

**Must use selection + free-input for all questions.**

- Show **selectable options** first
- Always allow **custom input** as alternative
- Ask **one question at a time**
- Use **numbered choices** for easy selection

---

## Phase 1: Project Type

**请选择项目类型：**

| # | 类型 | 说明 |
|---|------|------|
| 1 | AI Tool | ChatGPT、Claude、AI助手类 |
| 2 | Dashboard | 数据看板、管理后台 |
| 3 | Landing Page | 产品官网、落地页 |
| 4 | SaaS App | Notion、Linear 多模块应用 |
| 5 | Content Site | 博客、文档站 |
| 6 | Tool | JSON格式化、图片处理等工具 |
| 7 | E-commerce | 电商、购物车 |
| 8 | Community | 论坛、社交社区 |
| 9 | Marketplace | 双边市场平台 |

输入数字或直接描述你的需求：

---

## Phase 2: Pages

**请选择需要的页面（可多选，用逗号分隔）：**

根据 `type` 显示对应 pages 列表：

**AI Tool:** `/chat`, `/history`, `/settings`, `/new`
**Dashboard:** `/dashboard`, `/analytics`, `/reports`, `/[table]`
**SaaS App:** `/dashboard`, `/[module]`, `/settings`, `/profile`
**Landing Page:** `/` (单页)
**Content Site:** `/`, `/blog`, `/blog/[slug]`, `/docs`, `/search`

输入数字、多选或直接描述：

---

## Phase 3: Components

**请选择核心组件（可多选）：**

根据 `type` 显示对应 components 列表：

示例 - AI Tool:
| # | 组件 | 说明 |
|---|------|------|
| 1 | ChatInput | AI输入框 |
| 2 | ChatMessage | 消息气泡 |
| 3 | ChatStream | 流式输出 |
| 4 | ConversationList | 历史列表 |
| 5 | ModelSelector | 模型选择 |

输入数字或描述需要的组件：

---

## Phase 4: UI Library

**请选择 UI 组件库：**

| # | UI Library | 说明 |
|---|------------|------|
| 0 | 使用推荐方案 | shadcn/ui + Tailwind (默认) |
| 1 | shadcn/ui | 高度可定制，基于 Radix |
| 2 | Chakra UI | 快速原型，主题系统 |
| 3 | Mantine | 全功能，现代感 |
| 4 | Ant Design | 企业后台，规范严格 |

输入数字或指定其他：

---

## Phase 5: Design Style

**请选择设计风格：**

**方式 1: 从 57 种预设选择**

| # | Design | 说明 |
|---|--------|------|
| 1 | claude | Claude AI 风格 |
| 2 | linear | Linear 暗色简洁 |
| 3 | stripe | Stripe 浅色商务 |
| 4 | openai | OpenAI 风格 |
| 5 | vercel | Vercel 极简 |
| ... | [其他 52 种](references/design-catalog.md) | 见完整列表 |

**方式 2: 提供参考网站/截图**

直接粘贴 URL 或上传截图，我会分析并匹配最接近的设计风格。

**方式 3: 自定义描述**

描述你想要的视觉风格，我会基于描述生成 DESIGN.md。

输入数字、URL 或直接描述：

---

## Phase 6: Icon Library

**请选择图标库（可选）：**

| # | Icon Library | 说明 |
|---|--------------|------|
| 0 | 使用推荐方案 | Lucide React (默认) |
| 1 | Lucide React | 现代简洁，默认选项 |
| 2 | Iconfont | 阿里巴巴图标，可自选图标 |
| 3 | Heroicons | Tailwind 官方图标 |
| 4 | Phosphor Icons | 丰富多样 |
| 5 | 不需要图标 | - |

输入数字或指定其他：

---

## Project Summary (确认)

```
项目类型: [type]
页面: [pages]
组件: [components]
UI 库: [ui-library]
设计风格: [design]
图标库: [icon-library]

Scaffolding 命令:
[command]

是否正确？输入 "确认" 开始生成，或告诉我需要修改的部分。
```

---

## Phase 7: Generate Project

确认后执行：

**Step 1: Scaffolding**
```bash
npx create-next-app@latest my-project --typescript --tailwind --app --src-dir
cd my-project
npx shadcn@latest init
npx shadcn@latest add [components]
npm install [dependencies]
```

**Step 2: Inject DESIGN.md**
- WebFetch 获取 design-catalog.md 中的 URL
- 写入项目根目录 `DESIGN.md`

**Step 3: Generate Code**
- 基于 blueprint 生成 components
- 遵循 best-practices.md

---

## Output Structure

```
/project-name
├── app/                    # Next.js pages
├── components/
│   └── ui/                 # shadcn components
├── lib/                    # utils
├── DESIGN.md               # ← 注入的设计规范
├── tailwind.config.ts      # ← 应用 design tokens
└── package.json
```

---

## Reference Files

| File | Purpose |
|------|---------|
| `references/templates.md` | Blueprint 定义 (pages, components, scaffolding) |
| `references/design-catalog.md` | 57 种设计风格 URL 映射 |
| `references/best-practices.md` | 技术栈最佳实践 |
| `references/tech-catalog.md` | 技术文档 URL 映射 |

---

## Key Principles

- **Selection + Free-input** — 选项优先，但允许自定义
- **One question at a time** — 一次只问一个维度
- **Confirmation before generate** — 确认后再生成
- **DESIGN.md lives in project** — AI 编程时读取设计规范
- **Use scaffolding CLI** — 不从零开始生成
