# HTML Report Slides

> 深蓝科技风单文件汇报稿生成器 · AI Agent Skill

把汇报内容（战略规划、成本分析、架构图、产品路线图等）一键生成为 **单个 HTML 文件** 的 PPT 风格页面。每个 slide 是一个 1280×720 的卡片，垂直堆叠，可直接浏览、打印或截图。

## 核心特性

- 🎨 **暗色科技风**：深蓝底 `#0a0e1a` + 渐变标题（白→蓝→紫）
- 📐 **1280×720 标准卡片**：垂直堆叠，适合屏幕分享/截图
- 🏗️ **SVG 架构图**：多层架构、故事线、连线关系的最佳实践
- 🖨️ **打印友好**：`@media print` 样式，一键导出 PDF
- 🧩 **10 个即用组件**：封面、KPI、进度条、时间线、对比卡、成本表、架构图等
- 📚 **2 个完整范例**：成本汇报 + 战略规划

## 快速开始

### 方式 1：通过 ClawHub 安装

```bash
clawhub install html-report-slides
```

### 方式 2：手动克隆

```bash
git clone https://github.com/dengjiawei1226/html-report-slides.git ~/.workbuddy/skills/html-report-slides
```

安装后直接对 AI 助手说 **"帮我做一个汇报页面"** 即可触发。

## 触发词

汇报页面、汇报 PPT、HTML 汇报、科技风汇报、PPT 页面、单文件演示、战略汇报、成本汇报、架构全景图、故事线规划、领导汇报稿、深蓝风汇报、产品规划汇报、slide html

## 目录结构

```
html-report-slides/
├── SKILL.md              # Skill 入口（Agent 读取的主文件）
├── components/           # 10 个可复用组件片段
│   ├── cover-slide.html
│   ├── kpi-cards.html
│   ├── progress-bar.html
│   ├── timeline.html
│   ├── comparison-card.html
│   ├── cost-table.html
│   ├── architecture-svg.html
│   └── ...
├── references/
│   ├── design-system.md        # 颜色/字体/间距系统
│   └── svg-architecture-rules.md  # SVG 布局规范
└── examples/
    ├── cost-report.html         # 成本汇报范例
    └── strategy-report.html     # 战略规划范例
```

## 设计系统摘要

- **基础色**：深蓝 `#0a0e1a` / 卡片 `#111827` / 强调蓝 `#7cacff` / 强调紫 `#a78bfa`
- **字体**：系统 UI 字体栈，中英混排
- **字号**：标题 48px / 一级 32px / 二级 22px / 正文 15px
- **圆角**：卡片 16px / 小元素 8px
- **虚线框**：`stroke-dasharray="4,4"` 用于分组容器

详见 [`references/design-system.md`](references/design-system.md)。

## SVG 架构图布局要点

1. 所有方块在容器内 **均匀分布**（计算容器宽 - 元素总宽 → 按间隙数均分）
2. 连线起终点 **必须对准方块中心**（从 rect 属性反推坐标）
3. 嵌套分组的内外空间要协调
4. 移动方块后同步调整所有关联连线

详见 [`references/svg-architecture-rules.md`](references/svg-architecture-rules.md)。

## License

MIT-0 · 免费使用/修改/再分发，无需署名。

## 相关链接

- 📦 ClawHub：https://clawhub.ai/skill/html-report-slides
- 🔗 Knot（腾讯内网）：https://knot.woa.com/skills/detail/26608
