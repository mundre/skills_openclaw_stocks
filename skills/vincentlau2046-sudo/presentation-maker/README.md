# Presentation Maker

将文档大纲转换为专业演示幻灯片的自动化技能。

## 版本信息
- **版本**: 1.0.0
- **发布日期**: 2026-03-29
- **兼容性**: OpenClaw v2.0+

## 功能特性
- 📄 **Markdown输入**: 支持标准Markdown格式大纲
- 🎨 **自动布局**: 智能规划幻灯片结构（封面+目录+内容+总结）
- 📊 **数据可视化**: 自动生成SVG图表强化数据呈现
- ⌨️ **完整交互**: 键盘翻页 + 一键全屏演示模式
- 📱 **响应式设计**: 严格16:9比例，适配各种屏幕
- 🎭 **主题支持**: 多种预设主题（科技/创意/商务/教育）

## 安装方法

### OpenClaw ClawHub
```bash
/openclaw skills install presentation-maker
```

### 手动安装
```bash
git clone https://github.com/openclaw/presentation-maker.git
cd presentation-maker
npm install
sudo ln -sf $(pwd)/scripts/generate.js /usr/local/bin/presentation-maker
```

## 使用方法

### 基本用法
```bash
presentation-maker "input-document.md"
```

### 高级选项
```bash
# 自定义输出目录
presentation-maker "document.md" --output-dir "slides"

# 自定义主题颜色
presentation-maker "document.md" --primary-color "#76b900" --secondary-color "#00a2ff"

# 指定主题类型
presentation-maker "document.md" --theme "creative"
```

## 输出结构
```
output-directory/
├── index.html          # 入口页面
├── css/style.css       # 统一样式文件
├── js/main.js          # 交互逻辑
└── slides/
    ├── 01-cover.html   # 封面页
    ├── 02-toc.html     # 目录页
    └── ...             # 内容幻灯片
```

## 技术规格
- **依赖**: Node.js 18+, marked.js
- **输出**: 纯静态HTML/CSS/JS
- **兼容性**: Chrome, Firefox, Safari, Edge
- **性能**: 单页加载 < 1秒

## 变更日志

### v1.0.0 (2026-03-29)
- 初始版本发布
- 支持Markdown文档解析
- 自动生成8页标准幻灯片结构
- 内置科技主题（英伟达风格）
- 完整键盘交互和全屏支持

## 许可证
MIT License

## 作者
OpenClaw Community