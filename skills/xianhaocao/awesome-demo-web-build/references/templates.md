# Project Blueprint System

> These blueprints are **conversation guides** for understanding user needs.
> NOT pre-generated templates to output directly.
>
> Use the Pages/Components lists to **ask questions** and confirm preferences.
> Then use **scaffolding commands** to bootstrap the project, inject DESIGN.md, and add components.

---

## Scaffolding Commands

### Framework
| Framework | Command |
|-----------|---------|
| Next.js | `npx create-next-app@latest` |
| Astro | `npm create astro@latest` |
| Vite | `npm create vite@latest` |

### UI Component Library
| UI Library | Command |
|-------------|---------|
| shadcn/ui (推荐) | `npx shadcn@latest init` |
| Chakra UI | `npm i @chakra-ui/react @emotion/react` |
| Mantine | `npm i @mantine/core @mantine/hooks` |
| Ant Design | `npm i antd` |

### Icon Library
| Icon Library | Command / Usage |
|-------------|-----------------|
| **Lucide React** (推荐) | `npm install lucide-react` (已内置于 shadcn) |
| **Iconfont** | `npm install @iconfont/react` + 在 iconfont.cn 创建项目获取 symbol URL |
| **Heroicons** | `npm install @heroicons/react` |
| **Phosphor Icons** | `npm install @phosphor-icons/react` |
| **Font Awesome** | `npm install @fortawesome/react-fontawesome` |

### Iconfont 使用方法

1. 在 [iconfont.cn](https://iconfont.cn) 创建项目，获取 Symbol URL
2. 在 `app/layout.tsx` 或 `index.html` 中引入:

```html
<script src="https:////at.alicdn.com/t/font_xxx.js"></script>
```

3. 使用组件:

```tsx
// React
<svg className="icon" aria-hidden="true">
  <use href="#icon-xxx" />
</svg>

// 或使用 @iconfont/react
import { Icon } from '@iconfont/react'
<Icon type="xxx" />
```

4. 在 tailwind.config.ts 中添加:

```js
theme: {
  extend: {
    width: {
      'icon': '1em',
      'icon-sm': '0.75em',
      'icon-lg': '1.25em',
    },
    height: {
      'icon': '1em',
      'icon-sm': '0.75em',
      'icon-lg': '1.25em',
    },
  },
}
```

### Default Stack Strategy
- **Next.js** → shadcn/ui + Tailwind CSS + Lucide React
- **Astro** → 少量 shadcn islands 或纯 Tailwind + Lucide React
- **需要国产图标** → Iconfont (阿里巴巴)

---

## Project Generation Workflow

```
1. Clarify requirements (type, pages, components, design)
2. Run scaffolding command (framework + UI library)
3. Inject DESIGN.md into project root
4. Install project-specific dependencies
5. Add shadcn/ui components: button, input, card, etc.
6. Generate blueprint components
7. Apply design tokens to tailwind.config.ts
```

---

## 1. ai-tool

**典型产品:** ChatGPT, Claude, Midjourney, AI写作助手

### Scaffolding
```bash
# 1. 创建项目
npx create-next-app@latest my-ai-tool --typescript --tailwind --app --src-dir

# 2. 初始化 shadcn/ui
cd my-ai-tool
npx shadcn@latest init

# 3. 添加基础组件
npx shadcn@latest add button input card scroll-area

# 4. 安装 AI 相关依赖
npm install ai @ai-sdk/react zustand
```

### Pages
```
/chat          # 主对话页
/history       # 历史对话
/settings      # 设置页
/new           # 新建对话
```

### Core Components
| 组件 | 说明 |
|------|------|
| `ChatInput` | AI输入框, 支持多行 |
| `ChatMessage` | 消息气泡, user/assistant区分 |
| `ChatStream` | 流式输出渲染 |
| `ConversationList` | 侧边栏历史列表 |
| `ModelSelector` | 模型下拉选择 |

### Design Priority
- **输入框优先** — 对话区域占主体
- **流式反馈** — 打字效果
- **暗色主题** — 大多数AI工具偏好

---

## 2. dashboard

**典型产品:** GA分析, Admin后台, 数据看板

### Scaffolding
```bash
# 1. 创建项目
npx create-next-app@latest my-dashboard --typescript --tailwind --app --src-dir

# 2. 初始化 shadcn/ui
cd my-dashboard
npx shadcn@latest init

# 3. 添加数据相关组件
npx shadcn@latest add button input card table dropdown-menu chart

# 4. 安装数据可视化
npm install recharts @tanstack/react-table zustand
```

### Pages
```
/dashboard      # 概览页 (KPI卡片)
/analytics      # 数据分析 (图表)
/reports        # 报表 (表格)
/[table]        # 数据表 (CRUD)
```

### Core Components
| 组件 | 说明 |
|------|------|
| `StatsCard` | KPI数值卡片 |
| `DataTable` | 表格 (筛选/分页/排序) |
| `Chart` | 图表 (折线/柱状/饼图) |
| `FilterBar` | 筛选栏 (日期范围) |
| `Sidebar` | 侧边导航 |

### Design Priority
- **数据密度** — 信息紧凑
- **表格优先** — 核心交互是表格
- **图表驱动** — 可解释

---

## 3. landing-page

**典型产品:** 产品官网, 活动页, 作品集

### Scaffolding
```bash
# 1. 创建项目
npm create astro@latest my-landing --template minimal
cd my-landing
npx astro add tailwind

# 2. 纯 Tailwind 或少量 islands
npm install framer-motion clsx tailwind-merge
```

### Pages
```
/               # 单页 (多个Section)
```

### Sections
```
Hero → Features → SocialProof → Pricing → FAQ → CTA → Footer
```

### Core Components
| 组件 | 说明 |
|------|------|
| `Hero` | 大标题 + 副标题 + CTA |
| `FeatureCard` | 特性卡片 |
| `PricingTable` | 价格表 |
| `Testimonial` | 用户评价 |
| `FAQ` | 折叠问答 |

### Design Priority
- **视觉冲击** — 首屏决定转化
- **CTA清晰** — 每个Section有行动召唤
- **滚动叙事** — 单页滚动引导

---

## 4. saas-app

**典型产品:** Notion, Linear, Stripe, Slack

### Scaffolding
```bash
# 1. 创建项目
npx create-next-app@latest my-saas --typescript --tailwind --app --src-dir

# 2. 初始化 shadcn/ui
cd my-saas
npx shadcn@latest init

# 3. 添加 SaaS 常用组件
npx shadcn@latest add button input card dialog dropdown-menu tabs avatar badge separator command

# 4. 安装认证和状态
npm install @clerk/nextjs zustand @supabase/supabase-js
```

### Pages
```
/dashboard       # 工作区首页
/[module]        # 模块页 (动态路由)
/settings        # 设置
/settings/billing
/settings/team
/profile         # 个人资料
```

### Core Components
| 组件 | 说明 |
|------|------|
| `AppShell` | 整体布局 (Sidebar + Header) |
| `Sidebar` | 导航侧栏 |
| `Header` | 顶部栏 (面包屑, 搜索) |
| `ModuleView` | 模块主视图 |
| `CommandPalette` | Cmd+K 命令面板 |

### Design Priority
- **一致性** — 跨模块UI统一
- **效率优先** — 快捷键, 命令面板
- **信息架构** — 清晰模块划分

---

## 5. content-site

**典型产品:** 博客, 文档站, 知识库

### Scaffolding
```bash
# 1. 创建项目
npx create-next-app@latest my-blog --typescript --tailwind --app --src-dir

# 2. 初始化 shadcn/ui
cd my-blog
npx shadcn@latest init

# 3. 添加内容相关组件
npx shadcn@latest add button card badge separator scroll-area

# 4. 安装内容处理
npm install next-mdx-remote gray-matter fuse.js date-fns
```

### Pages
```
/                # 首页 (文章列表)
/blog            # 博客列表
/blog/[slug]     # 文章详情
/docs            # 文档列表
/docs/[slug]      # 文档页
/search          # 搜索
/category/[cat]   # 分类页
```

### Core Components
| 组件 | 说明 |
|------|------|
| `PostCard` | 文章卡片 |
| `MdxContent` | Markdown渲染 |
| `TableOfContents` | 文章目录 |
| `SearchBar` | 搜索框 |
| `TagList` | 标签列表 |
| `Pagination` | 分页器 |

### Design Priority
- **可读性** — 舒适行距, 清晰排版
- **导航** — 面包屑, 侧边目录
- **SEO** — meta, sitemap

---

## 6. tool

**典型产品:** JSON格式化, 图片压缩, 代码高亮

### Scaffolding
```bash
# 1. 创建项目
npx create-next-app@latest my-tool --typescript --tailwind --app --src-dir

# 2. 初始化 shadcn/ui
cd my-tool
npx shadcn@latest init

# 3. 添加工具相关组件
npx shadcn@latest add button input card dropdown-menu

# 4. 安装工具类依赖
npm install @uiw/react-codemirror clsx tailwind-merge
```

### Pages
```
/               # 工具首页或唯一页
/[tool]         # 工具页 (输入 → 输出)
```

### Core Components
| 组件 | 说明 |
|------|------|
| `ToolInput` | 输入区 (Textarea/Dropzone) |
| `ToolOutput` | 输出区 (结果展示) |
| `ToolOptions` | 选项配置 |
| `CopyButton` | 一键复制 |
| `FormatSelect` | 格式选择 |

### Design Priority
- **输入输出** — 左输入右输出
- **即时反馈** — 处理完成即显示
- **简洁** — 无需导航

---

## Extended Types

### 7. e-commerce
```bash
npx create-next-app@latest my-shop --typescript --tailwind --app --src-dir
cd my-shop
npx shadcn@latest init
npx shadcn@latest add button input card badge carousel separator
npm install @stripe/stripe-js @supabase/supabase-js zustand
```

### 8. community
```bash
npx create-next-app@latest my-community --typescript --tailwind --app --src-dir
cd my-community
npx shadcn@latest init
npx shadcn@latest add button input card avatar badge comment
npm install @supabase/supabase-js date-fns
```

### 9. marketplace
```bash
npx create-next-app@latest my-market --typescript --tailwind --app --src-dir
cd my-market
npx shadcn@latest init
npx shadcn@latest add button input card avatar badge search command
npm install @supabase/supabase-js zustand fuse.js
```

---

## shadcn/ui Components Reference

| Category | Components |
|----------|------------|
| 基础 | `button`, `input`, `label`, `badge` |
| 布局 | `card`, `sheet`, `separator`, `scroll-area` |
| 导航 | `sidebar`, `tabs`, `menu`, `command` |
| 数据 | `table`, `chart`, `progress` |
| 反馈 | `dialog`, `alert`, `toast`, `skeleton` |
| 表单 | `form`, `select`, `checkbox`, `radio-group` |
| 数据输入 | `textarea`, `switch`, `slider`, `date-picker` |

---

## Type → Design Priority

| Type | Design Priority |
|------|----------------|
| ai-tool | 输入框/对话 |
| dashboard | 数据密度 |
| landing-page | 视觉冲击 |
| saas-app | 一致性 |
| content-site | 可读性 |
| tool | 简洁高效 |

---

## Auto-Inference Examples

```
用户: "帮我做个 ChatGPT"
→ Framework: Next.js
→ UI: shadcn/ui
→ Pages: /chat
→ Components: ChatInput, ChatMessage
→ Design: claude

用户: "类似 Notion 的工具"
→ Framework: Next.js
→ UI: shadcn/ui
→ Pages: /dashboard, /[module], /settings
→ Components: AppShell, Sidebar
→ Design: minimal

用户: "数据分析后台"
→ Framework: Next.js
→ UI: shadcn/ui + Recharts
→ Pages: /dashboard, /analytics
→ Components: StatsCard, DataTable, Chart
→ Design: linear
```
