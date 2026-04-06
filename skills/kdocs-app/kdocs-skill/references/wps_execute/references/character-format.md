# 字符格式设置

本文档提供设置WPS文档字符格式的所有功能和脚本模板。

## 功能列表

| 功能 | 说明 | 参数 |
|------|------|------|
| 设置字体名称 | 设置字体（宋体、黑体等） | n/区间, Name: 字体名 |
| 设置字号大小 | 设置字号 | n/区间, Size: 字号 |
| 设置字体颜色 | 设置文字颜色 | n/区间, ColorIndex: 颜色枚举 |
| 设置加粗 | 设置文字加粗 | n/区间, Bold: true/false |
| 设置倾斜 | 设置文字倾斜 | n/区间, Italic: true/false |
| 设置下划线 | 设置下划线样式 | n/区间, Underline: 下划线枚举 |
| 设置高亮色 | 设置文字背景高亮色 | n/区间, HighlightColorIndex: 高亮色枚举 |

---

## 1. 设置字符格式

### 1.1 设置第N个段落的字符格式

#### 功能描述
设置文档中第N个段落的字符格式（字体、字号、颜色、样式等）。

#### JavaScript脚本模板

```javascript
var range = ActiveDocument.Paragraphs.Item(${n}).Range;
range.Font.${key} = ${value};
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| n | uint32 | 是 | 段落索引（从1开始） |
| key | string | 是 | 字符属性名称，详见下表 |
| value | varies | 是 | 属性值，根据key不同而不同 |

#### 字符属性对照表

| Key | 含义 | Value类型 | Value值说明 | 示例 |
|-----|------|-----------|-------------|------|
| Name | 设置字体名 | string | 字体名称 | "宋体"、"Arial" |
| Size | 设置字号 | uint32 | 字号大小 | 12、14、16 |
| ColorIndex | 设置字体颜色 | enum | 颜色枚举值 | wdRed、wdBlue |
| Bold | 设置加粗 | bool | true或false | true、false |
| Italic | 设置倾斜 | bool | true或false | true、false |
| Underline | 设置下划线 | enum | 下划线样式枚举值 | wdUnderlineSingle |

#### 使用示例

**设置第1个段落字体为宋体**:

```javascript
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.Font.Name = "宋体";
```

**设置第1个段落字号为14**:

```javascript
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.Font.Size = 14;
```

**设置第1个段落颜色为红色**:

```javascript
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.Font.ColorIndex = wdRed;
```

**设置第1个段落加粗**:

```javascript
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.Font.Bold = true;
```

**设置第1个段落倾斜**:

```javascript
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.Font.Italic = true;
```

**设置第1个段落单下划线**:

```javascript
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.Font.Underline = wdUnderlineSingle;
```

---

### 1.2 设置区间内的字符格式

#### 功能描述
设置文档中指定字符位置区间内的字符格式。

#### JavaScript脚本模板

```javascript
var range = ActiveDocument.Range(${begin}, ${end});
range.Font.${key} = ${value};
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| begin | uint32 | 是 | 开始位置（字符索引） |
| end | uint32 | 是 | 结束位置（字符索引） |
| key | string | 是 | 字符属性名称 |
| value | varies | 是 | 属性值 |

#### 使用示例

**设置位置0到50的文本为蓝色**:

```javascript
var range = ActiveDocument.Range(0, 50);
range.Font.ColorIndex = wdBlue;
```

**设置位置0到50的文本为倾斜**:

```javascript
var range = ActiveDocument.Range(0, 50);
range.Font.Italic = true;
```

---

## 2. 设置字符高亮色

### 2.1 设置第N个段落的高亮色

#### 功能描述
设置文档中第N个段落的背景高亮色。

#### JavaScript脚本模板

```javascript
var range = ActiveDocument.Paragraphs.Item(${n}).Range;
range.HighlightColorIndex = ${highColor};
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| n | uint32 | 是 | 段落索引（从1开始） |
| highColor | enum | 是 | 高亮色枚举值，详见下表 |

#### 高亮色枚举值

| 常量名 | 值 | 说明 |
|--------|-----|------|
| wdNoHighlight | 0 | 清除高亮 |
| wdYellow | 7 | 黄色（常用） |
| wdBrightGreen | 4 | 鲜绿色 |
| wdTurquoise | 3 | 青绿色 |
| wdPink | 5 | 粉红色 |
| wdBlue | 2 | 蓝色 |
| wdRed | 6 | 红色 |
| wdDarkBlue | 9 | 深蓝色 |
| wdTeal | 10 | 青色 |
| wdGreen | 11 | 绿色 |
| wdViolet | 12 | 紫色 |
| wdDarkRed | 13 | 深红色 |
| wdDarkYellow | 14 | 深黄色 |
| wdGray50 | 15 | 50%灰色 |
| wdGray25 | 16 | 25%灰色 |

#### 使用示例

**设置第1个段落黄色高亮**:

```javascript
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.HighlightColorIndex = wdYellow;
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var range = ActiveDocument.Paragraphs.Item(1).Range; range.HighlightColorIndex = wdYellow;"
}
```

---

### 2.2 设置区间内的高亮色

#### 功能描述
设置文档中指定区间的背景高亮色。

#### JavaScript脚本模板

```javascript
var range = ActiveDocument.Range(${begin}, ${end});
range.HighlightColorIndex = ${highColor};
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| begin | uint32 | 是 | 开始位置 |
| end | uint32 | 是 | 结束位置 |
| highColor | enum | 是 | 高亮色枚举值 |

#### 使用示例

**设置位置0到100的文本绿色高亮**:

```javascript
var range = ActiveDocument.Range(0, 100);
range.HighlightColorIndex = wdBrightGreen;
```

---

## 3. 颜色枚举值参考

### 字体颜色枚举

| 常量名 | 说明 |
|--------|------|
| wdAuto | 自动配色（默认，通常为黑色） |
| wdBlack | 黑色 |
| wdBlue | 蓝色 |
| wdBrightGreen | 鲜绿色 |
| wdByAuthor | 由文档作者定义 |
| wdDarkBlue | 深蓝色 |
| wdDarkRed | 深红色 |
| wdDarkYellow | 深黄色 |
| wdGray25 | 25%灰色底纹 |
| wdGray50 | 50%灰色底纹 |
| wdGreen | 绿色 |
| wdPink | 粉红色 |
| wdRed | 红色 |
| wdTeal | 青色 |
| wdTurquoise | 青绿色 |
| wdViolet | 紫色 |
| wdWhite | 白色 |
| wdYellow | 黄色 |

---

## 4. 下划线样式枚举值

| 常量名 | 说明 |
|--------|------|
| wdUnderlineNone | 无下划线（默认） |
| wdUnderlineSingle | 单下划线 |
| wdUnderlineDouble | 双下划线 |
| wdUnderlineThick | 单粗线 |
| wdUnderlineDash | 划线 |
| wdUnderlineDashHeavy | 粗划线 |
| wdUnderlineDashLong | 长划线 |
| wdUnderlineDashLongHeavy | 长粗划线 |
| wdUnderlineDotted | 点线 |
| wdUnderlineDottedHeavy | 粗点线 |
| wdUnderlineDotDash | 点划相间线 |
| wdUnderlineDotDashHeavy | 粗点划相间线 |
| wdUnderlineDotDotDash | 点-点-划线相间 |
| wdUnderlineDotDotDashHeavy | 粗点-点-划线相间 |
| wdUnderlineWavy | 单波浪线 |
| wdUnderlineWavyDouble | 双波浪线 |
| wdUnderlineWavyHeavy | 粗波浪线 |
| wdUnderlineWords | 仅为单个字加下划线 |

---

## 高级用法

### 组合设置多种格式

**场景**: 同时设置字体、字号、颜色、加粗

```javascript
var range = ActiveDocument.Paragraphs.Item(1).Range;
range.Font.Name = "宋体";
range.Font.Size = 18;
range.Font.ColorIndex = wdRed;
range.Font.Bold = true;
```

### 设置标题样式

**场景**: 创建一个标准的标题样式

```javascript
var title = ActiveDocument.Paragraphs.Item(1).Range;

// 设置字符格式
title.Font.Name = "黑体";
title.Font.Size = 22;
title.Font.ColorIndex = wdBlue;
title.Font.Bold = true;

// 设置段落格式
title.ParagraphFormat.Alignment = wdAlignParagraphCenter;
```

### 查找并设置格式

**场景**: 查找关键词并添加黄色高亮

```javascript
var doc = ActiveDocument;
var findText = "重要";
var range = doc.Content;

// 循环查找所有匹配项
while (range.Find.Execute(findText)) {
  range.HighlightColorIndex = wdYellow;
  range.Font.Bold = true;
  range.Collapse(0); // wdCollapseEnd
}
```

### 清除格式

**场景**: 清除文本的所有格式

```javascript
var range = ActiveDocument.Paragraphs.Item(1).Range;

// 清除加粗
range.Font.Bold = false;

// 清除倾斜
range.Font.Italic = false;

// 清除下划线
range.Font.Underline = wdUnderlineNone;

// 清除高亮
range.HighlightColorIndex = wdNoHighlight;

// 恢复默认颜色
range.Font.ColorIndex = wdAuto;
```

---

## 注意事项

1. **格式范围**: 字符格式设置会影响指定范围内的所有字符
2. **枚举常量**: 颜色、下划线样式必须使用预定义的枚举常量
3. **布尔值**: Bold和Italic使用true/false
4. **字体名称**: 字体名称必须是系统已安装的字体
5. **高亮优先级**: 高亮色会覆盖背景色
6. **组合使用**: 可以在一个Range上连续设置多个属性

## 常见问题

**Q: 如何检查字体是否可用？**

A: WPS会自动使用系统默认字体替代不可用的字体，但建议使用常见字体如"宋体"、"黑体"等。

**Q: 如何设置RGB颜色？**

A: 使用`Font.Color`属性而不是`ColorIndex`：

```javascript
range.Font.Color = RGB(255, 0, 0); // 红色
```

**Q: 如何同时设置多个段落的格式？**

A: 使用循环或区间：

```javascript
// 方法1: 循环
for (var i = 1; i <= 5; i++) {
  var range = ActiveDocument.Paragraphs.Item(i).Range;
  range.Font.Bold = true;
}

// 方法2: 区间
var range = ActiveDocument.Range(0, 500);
range.Font.Bold = true;
```

**Q: 格式是否会被保存？**

A: 是的，通过API设置的格式会保存到文档中。

---

## 相关文档

- [enums.md](enums.md) - 完整的枚举值列表
- [paragraph-format.md](paragraph-format.md) - 段落格式设置
- [modify-content.md](modify-content.md) - 修改文档内容
