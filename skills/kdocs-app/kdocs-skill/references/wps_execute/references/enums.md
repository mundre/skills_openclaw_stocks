# 枚举值参考

本文档提供WPS文字API中所有枚举常量的完整参考。

## 目录

- [段落对齐方式](#段落对齐方式)
- [字体颜色](#字体颜色)
- [高亮色](#高亮色)
- [下划线样式](#下划线样式)
- [其他常用枚举](#其他常用枚举)

---

## 段落对齐方式

用于设置段落的对齐方式。

| 常量名 | 值 | 说明 | 使用场景 |
|--------|-----|------|----------|
| wdAlignParagraphLeft | 0 | 左对齐 | 正文段落（默认） |
| wdAlignParagraphCenter | 1 | 居中 | 标题、居中文本 |
| wdAlignParagraphRight | 2 | 右对齐 | 日期、签名 |
| wdAlignParagraphJustify | 3 | 完全两端对齐 | 正式文档正文 |
| wdAlignParagraphDistribute | 4 | 分散对齐 | 字符均匀分布 |
| wdAlignParagraphJustifyMed | 5 | 两端对齐（中度压缩） | 需要压缩字符的文本 |
| wdAlignParagraphJustifyHi | 7 | 两端对齐（高度压缩） | 需要高度压缩的文本 |
| wdAlignParagraphJustifyLow | 8 | 两端对齐（轻微压缩） | 需要轻微压缩的文本 |
| wdAlignParagraphThaiJustify | 9 | 泰语格式两端对齐 | 泰语文档 |

### 使用示例

```javascript
// 设置居中对齐
ActiveDocument.Paragraphs.Item(1).Alignment = wdAlignParagraphCenter;

// 设置两端对齐
ActiveDocument.Paragraphs.Item(2).Alignment = wdAlignParagraphJustify;
```

---

## 字体颜色

用于设置文字的颜色。

### 基础颜色

| 常量名 | 说明 | 适用场景 |
|--------|------|----------|
| wdAuto | 自动配色（通常为黑色） | 默认文本 |
| wdBlack | 黑色 | 正文 |
| wdWhite | 白色 | 深色背景上的文字 |
| wdRed | 红色 | 强调、警告 |
| wdBlue | 蓝色 | 标题、链接 |
| wdGreen | 绿色 | 成功、通过 |
| wdYellow | 黄色 | 注意事项 |

### 扩展颜色

| 常量名 | 说明 | 适用场景 |
|--------|------|----------|
| wdBrightGreen | 鲜绿色 | 醒目提示 |
| wdDarkBlue | 深蓝色 | 专业标题 |
| wdDarkRed | 深红色 | 重要警告 |
| wdDarkYellow | 深黄色 | 次要警告 |
| wdPink | 粉红色 | 柔和强调 |
| wdViolet | 紫色 | 特殊标记 |
| wdTeal | 青色 | 信息提示 |
| wdTurquoise | 青绿色 | 补充信息 |

### 灰度颜色

| 常量名 | 说明 | 适用场景 |
|--------|------|----------|
| wdGray25 | 25%灰色底纹 | 次要文本 |
| wdGray50 | 50%灰色底纹 | 禁用文本 |

### 特殊值

| 常量名 | 值 | 说明 |
|--------|-----|------|
| wdByAuthor | -1 | 由文档作者定义的颜色 |
| wdNoHighlight | 0 | 清除已应用的突出显示 |

### 使用示例

```javascript
// 设置红色文字
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.Font.ColorIndex = wdRed;

// 设置蓝色文字
var range = ActiveDocument.Paragraphs.Item(2).Range;
range.Font.ColorIndex = wdBlue;
```

---

## 高亮色

用于设置文字的背景高亮色。

| 常量名 | 值 | 说明 | 视觉效果 |
|--------|-----|------|----------|
| wdNoHighlight | 0 | 清除高亮 | 无背景色 |
| wdBlack | 1 | 黑色 | 黑色背景（慎用） |
| wdBlue | 2 | 蓝色 | 蓝色背景 |
| wdTurquoise | 3 | 青绿色 | 青绿色背景 |
| wdBrightGreen | 4 | 鲜绿色 | 鲜绿色背景 |
| wdPink | 5 | 粉红色 | 粉红色背景 |
| wdRed | 6 | 红色 | 红色背景 |
| wdYellow | 7 | 黄色 | 黄色背景（最常用） |
| wdWhite | 8 | 白色 | 白色背景 |
| wdDarkBlue | 9 | 深蓝色 | 深蓝色背景 |
| wdTeal | 10 | 青色 | 青色背景 |
| wdGreen | 11 | 绿色 | 绿色背景 |
| wdViolet | 12 | 紫色 | 紫色背景 |
| wdDarkRed | 13 | 深红色 | 深红色背景 |
| wdDarkYellow | 14 | 深黄色 | 深黄色背景 |
| wdGray50 | 15 | 50%灰色底纹 | 灰色背景 |
| wdGray25 | 16 | 25%灰色底纹 | 浅灰色背景 |
| wdByAuthor | -1 | 由文档作者定义 | 自定义颜色 |

### 常用高亮色组合

| 使用场景 | 推荐颜色 | 常量 |
|----------|----------|------|
| 重要内容标记 | 黄色 | wdYellow |
| 错误标记 | 红色 | wdRed |
| 成功标记 | 绿色 | wdBrightGreen |
| 信息标记 | 蓝色 | wdTurquoise |
| 清除高亮 | 无 | wdNoHighlight |

### 使用示例

```javascript
// 设置黄色高亮
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.HighlightColorIndex = wdYellow;

// 清除高亮
var range = ActiveDocument.Paragraphs.Item(2).Range;
range.HighlightColorIndex = wdNoHighlight;
```

---

## 下划线样式

用于设置文字的下划线样式。

### 基础样式

| 常量名 | 说明 | 视觉效果 |
|--------|------|----------|
| wdUnderlineNone | 无下划线（默认） | 无 |
| wdUnderlineSingle | 单下划线 | _____ |
| wdUnderlineDouble | 双下划线 | ===== |
| wdUnderlineThick | 单粗线 | ▬▬▬▬▬ |
| wdUnderlineWords | 仅为单个字加下划线 | _  _  _ |

### 虚线样式

| 常量名 | 说明 | 视觉效果 |
|--------|------|----------|
| wdUnderlineDash | 划线 | - - - - - |
| wdUnderlineDashHeavy | 粗划线 | ━ ━ ━ ━ |
| wdUnderlineDashLong | 长划线 | ── ── ── |
| wdUnderlineDashLongHeavy | 长粗划线 | ━━ ━━ ━━ |

### 点线样式

| 常量名 | 说明 | 视觉效果 |
|--------|------|----------|
| wdUnderlineDotted | 点线 | · · · · · |
| wdUnderlineDottedHeavy | 粗点线 | • • • • • |
| wdUnderlineDotDash | 点划相间线 | · - · - · - |
| wdUnderlineDotDashHeavy | 粗点划相间线 | • ━ • ━ • |
| wdUnderlineDotDotDash | 点-点-划线相间 | · · - · · - |
| wdUnderlineDotDotDashHeavy | 粗点-点-划线相间 | • • ━ • • |

### 波浪线样式

| 常量名 | 说明 | 视觉效果 |
|--------|------|----------|
| wdUnderlineWavy | 单波浪线 | ～～～～ |
| wdUnderlineWavyDouble | 双波浪线 | ≈≈≈≈≈ |
| wdUnderlineWavyHeavy | 粗波浪线 | ≋≋≋≋≋ |

### 使用场景建议

| 场景 | 推荐样式 | 常量 |
|------|----------|------|
| 普通强调 | 单下划线 | wdUnderlineSingle |
| 重要强调 | 双下划线 | wdUnderlineDouble |
| 链接 | 单下划线 | wdUnderlineSingle |
| 拼写错误标记 | 波浪线 | wdUnderlineWavy |
| 语法错误标记 | 粗波浪线 | wdUnderlineWavyHeavy |

### 使用示例

```javascript
// 设置单下划线
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.Font.Underline = wdUnderlineSingle;

// 设置波浪线
var range = ActiveDocument.Paragraphs.Item(2).Range;
range.Font.Underline = wdUnderlineWavy;

// 清除下划线
var range = ActiveDocument.Paragraphs.Item(3).Range;
range.Font.Underline = wdUnderlineNone;
```

---

## 其他常用枚举

### 替换模式

用于`Find.Execute`的替换参数。

| 常量名 | 值 | 说明 |
|--------|-----|------|
| wdReplaceNone | 0 | 不替换（仅查找） |
| wdReplaceOne | 1 | 替换第一个匹配项 |
| wdReplaceAll | 2 | 替换所有匹配项 |

### 使用示例

```javascript
// 替换所有匹配项
var range = ActiveDocument.Content;
range.Find.Execute("旧文本", null, null, null, null, null, null, null, null, "新文本", wdReplaceAll);
```

### 范围折叠方向

用于`Range.Collapse`方法。

| 常量名 | 值 | 说明 |
|--------|-----|------|
| wdCollapseStart | 1 | 折叠到起始位置 |
| wdCollapseEnd | 0 | 折叠到结束位置 |

### 使用示例

```javascript
// 在查找后折叠到结束位置
var range = ActiveDocument.Content;
if (range.Find.Execute("关键词")) {
  range.HighlightColorIndex = wdYellow;
  range.Collapse(0); // wdCollapseEnd
}
```

---

## 枚举值使用技巧

### 1. 常量名 vs 数值

虽然可以直接使用数值，但强烈建议使用常量名以提高可读性：

```javascript
// 推荐：使用常量名
range.Font.ColorIndex = wdRed;

// 不推荐：使用数值
range.Font.ColorIndex = 6;
```

### 2. 检查枚举值

可以读取当前的枚举值：

```javascript
var alignment = ActiveDocument.Paragraphs.Item(1).Alignment;
if (alignment === wdAlignParagraphCenter) {
  // 当前是居中对齐
}
```

### 3. 枚举值的兼容性

这些枚举值在WPS和Microsoft Word中通用，但某些特定枚举值可能在不同版本中有差异。

### 4. 组合使用枚举

不同类型的枚举可以组合使用：

```javascript
var paragraph = ActiveDocument.Paragraphs.Item(1);
var range = paragraph.Range;

// 设置多种格式
range.Font.ColorIndex = wdRed;           // 颜色
range.Font.Underline = wdUnderlineSingle; // 下划线
range.HighlightColorIndex = wdYellow;     // 高亮
paragraph.Alignment = wdAlignParagraphCenter; // 对齐
```

---

## 快速查询

### 按颜色查询

| 颜色 | 字体颜色常量 | 高亮色常量 |
|------|-------------|-----------|
| 黑色 | wdBlack | wdBlack |
| 白色 | wdWhite | wdWhite |
| 红色 | wdRed | wdRed |
| 蓝色 | wdBlue | wdBlue |
| 绿色 | wdGreen | wdGreen |
| 黄色 | wdYellow | wdYellow |

### 按用途查询

| 用途 | 推荐枚举 |
|------|----------|
| 标题居中 | wdAlignParagraphCenter |
| 正文两端对齐 | wdAlignParagraphJustify |
| 强调文字 | wdRed + wdYellow (高亮) |
| 链接样式 | wdBlue + wdUnderlineSingle |
| 错误标记 | wdRed + wdUnderlineWavy |

---

## 相关文档

- [paragraph-format.md](paragraph-format.md) - 段落格式设置示例
- [character-format.md](character-format.md) - 字符格式设置示例
- [execute.md](../execute.md) - 返回主文档
