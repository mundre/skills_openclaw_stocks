---
name: xhs-html-cover
description: 用Playwright将HTML模板渲染生成小红书封面图。完全免费，无需API Key，支持多种风格模板，适用于玄学/黄历/星座/知识科普等内容的封面生成。
version: 1.0.0
author: 旺财 x 大作家
category: image
tags: [xiaohongshu, cover-image, html, playwright, free]
license: MIT
---

# 小红书封面图生成器

## 核心原理

**HTML + CSS → Playwright渲染 → PNG图片**

不依赖任何付费API，纯本地生成，免费无限使用。

## 功能

- 支持多种风格：黄历风、星座风、知识科普、教程指南
- 支持自定义主题、颜色、内容
- 输出PNG格式，适合小红书发布
- 可调整尺寸（默认1080px宽，高度自适应）

## 使用方式

### 基础用法

```
生成一张小红书封面图
主题：[你的主题]
风格：[可选的风格，默认warm]
颜色：[可选的主色调，默认自动匹配风格]
```

### 可选风格

| 风格 | 说明 | 配色 |
|------|------|------|
| warm | 暖色调，适合情感/玄学类 | 橙红黄渐变 |
| fresh | 小清新，适合生活/旅游 | 绿蓝白 |
| bold | 高对比，适合干货/知识类 | 深色+亮色 |
| minimal | 简约白底，适合极简风格 | 黑白灰 |
| vintage | 复古色调，适合怀旧话题 | 棕褐色调 |
| cute | 可爱粉嫩，适合星座/情感 | 粉色系 |
| notion | Notion风，适合知识管理 | 冷灰+彩色 |
| dark | 深色背景，适合潮流/娱乐 | 深色+霓虹 |

## 示例场景

### 1. 属相运势封面

```
主题：属虎人2026年转运指南
风格：warm
```

### 2. 星座周历封面

```
主题：本周星座运势排行榜
风格：cute
```

### 3. 黄历封面

```
主题：今日黄历 - 吉
风格：warm
```

### 4. 知识科普封面

```
主题：5个改变命运的小习惯
风格：bold
```

### 5. 教程指南封面

```
主题：3步学会看手相
风格：notion
```

## 技术实现

### 核心脚本

```powershell
# HTML模板路径
$htmlPath = "C:\Users\Administrator\.openclaw\scripts\ templates\v zodiac-cover.html"

# Playwright截图命令
& "C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\skills\playwright-scraper-skill\node_modules\.bin\playwright.cmd" screenshot --browser=chromium --full-page "file:///$htmlPath" "C:\output.png"
```

### Playwright路径

Windows:
```
C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\skills\playwright-scraper-skill\node_modules\.bin\playwright.cmd
```

### 模板变量

| 变量 | 说明 |
|------|------|
| {{title}} | 封面标题 |
| {{subtitle}} | 副标题 |
| {{emoji}} | emoji图标 |
| {{color}} | 主色调 |
| {{content}} | 内容要点 |
| {{footer}} | 底部标语 |

## 模板文件

| 文件 | 用途 |
|------|------|
| templates/zodiac-cover.html | 生肖运势封面 |
| templates/horoscope-cover.html | 星座周历封面 |
| templates/fortune-cover.html | 黄历封面 |
| templates/knowledge-cover.html | 知识科普封面 |
| templates/tutorial-cover.html | 教程指南封面 |

## 输出规格

- 默认尺寸：1080px宽，高度自适应
- 建议发布尺寸：1240x1754px（小红书最佳比例）
- 格式：PNG
- 质量：高

## 优势

1. **完全免费** - 不需要任何API Key
2. **本地生成** - 不依赖网络
3. **质量稳定** - PNG矢量级清晰度
4. **可定制** - HTML/CSS完全可控
5. **快速** - 5-10秒生成一张

## 依赖

- Playwright（已内置于OpenClaw skills）
- Chrome/Chromium浏览器

## 作者

由大作家原创，旺财整理发布
