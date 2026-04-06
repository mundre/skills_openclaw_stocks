# 段落格式设置

本文档提供设置WPS文档段落格式的所有功能和脚本模板。

## 功能列表

| 功能 | 说明 | 参数 | 状态 |
|------|------|------|------|
| 设置段落对齐 | 设置第N个段落的对齐方式 | n: 段落索引, algMode: 对齐方式 | ✅ |
| 设置区间对齐 | 设置指定区间的段落对齐方式 | begin: 开始位置, end: 结束位置, algMode: 对齐方式 | ✅ |
| 设置段落缩进 | 设置段落的首行缩进或悬挂缩进 | 待补充 | 🔜 |
| 设置行间距 | 设置段落的行间距 | 待补充 | 🔜 |

---

## 1. 设置段落对齐方式

### 1.1 设置第N个段落的对齐方式

#### 功能描述
设置文档中第N个段落的对齐方式（左对齐、居中、右对齐、两端对齐等）。

#### JavaScript脚本模板

```javascript
ActiveDocument.Paragraphs.Item(${n}).Alignment = ${algMode};
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| n | uint32 | 是 | 段落索引（从1开始） |
| algMode | enum | 是 | 对齐方式枚举值，详见下表 |

#### 对齐方式枚举值

| 常量名 | 值 | 说明 |
|--------|-----|------|
| wdAlignParagraphLeft | 0 | 左对齐 |
| wdAlignParagraphCenter | 1 | 居中 |
| wdAlignParagraphRight | 2 | 右对齐 |
| wdAlignParagraphJustify | 3 | 完全两端对齐 |
| wdAlignParagraphDistribute | 4 | 分散对齐，字符分布排列填满段落宽度 |
| wdAlignParagraphJustifyMed | 5 | 两端对齐，字符中度压缩 |
| wdAlignParagraphJustifyHi | 7 | 两端对齐，字符高度压缩 |
| wdAlignParagraphJustifyLow | 8 | 两端对齐，字符轻微压缩 |
| wdAlignParagraphThaiJustify | 9 | 泰语格式两端对齐 |

#### 使用示例

**设置第1个段落居中对齐**:

```javascript
ActiveDocument.Paragraphs.Item(1).Alignment = wdAlignParagraphCenter;
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "ActiveDocument.Paragraphs.Item(1).Alignment = wdAlignParagraphCenter;"
}
```

**设置第2个段落右对齐**:

```javascript
ActiveDocument.Paragraphs.Item(2).Alignment = wdAlignParagraphRight;
```

**设置第3个段落两端对齐**:

```javascript
ActiveDocument.Paragraphs.Item(3).Alignment = wdAlignParagraphJustify;
```

---

### 1.2 设置区间内的段落对齐方式

#### 功能描述
设置文档中指定字符位置区间内所有段落的对齐方式。

#### JavaScript脚本模板

```javascript
var range = ActiveDocument.Range(${begin}, ${end});
range.ParagraphFormat.Alignment = ${algMode};
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| begin | uint32 | 是 | 开始位置（字符索引） |
| end | uint32 | 是 | 结束位置（字符索引） |
| algMode | enum | 是 | 对齐方式枚举值 |

#### 使用示例

**设置位置0到100的段落右对齐**:

```javascript
var range = ActiveDocument.Range(0, 100);
range.ParagraphFormat.Alignment = wdAlignParagraphRight;
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var range = ActiveDocument.Range(0, 100); range.ParagraphFormat.Alignment = wdAlignParagraphRight;"
}
```

---

## 2. 设置段落缩进

### 功能描述
设置段落的首行缩进、左缩进、右缩进或悬挂缩进。

### 状态
🔜 功能规划中，待后续版本补充

### 预期参数

| 参数 | 类型 | 说明 |
|------|------|------|
| n | uint32 | 段落索引 |
| indentType | enum | 缩进类型（首行/左/右/悬挂） |
| value | float | 缩进值（磅或字符数） |

### 预期脚本模板（待确认）

```javascript
// 设置首行缩进
ActiveDocument.Paragraphs.Item(${n}).FirstLineIndent = ${value};

// 设置左缩进
ActiveDocument.Paragraphs.Item(${n}).LeftIndent = ${value};

// 设置右缩进
ActiveDocument.Paragraphs.Item(${n}).RightIndent = ${value};
```

---

## 3. 设置行间距

### 功能描述
设置段落的行间距（单倍行距、1.5倍行距、双倍行距、固定值等）。

### 状态
🔜 功能规划中，待后续版本补充

### 预期参数

| 参数 | 类型 | 说明 |
|------|------|------|
| n | uint32 | 段落索引 |
| lineSpacingRule | enum | 行距规则 |
| value | float | 行距值 |

### 预期脚本模板（待确认）

```javascript
// 设置单倍行距
ActiveDocument.Paragraphs.Item(${n}).LineSpacingRule = wdLineSpaceSingle;

// 设置1.5倍行距
ActiveDocument.Paragraphs.Item(${n}).LineSpacingRule = wdLineSpace1pt5;

// 设置双倍行距
ActiveDocument.Paragraphs.Item(${n}).LineSpacingRule = wdLineSpaceDouble;

// 设置固定值行距
ActiveDocument.Paragraphs.Item(${n}).LineSpacingRule = wdLineSpaceExactly;
ActiveDocument.Paragraphs.Item(${n}).LineSpacing = ${value};
```

---

## 高级用法

### 批量设置段落格式

**场景**: 设置多个段落为统一的对齐方式

```javascript
// 方法1: 逐个设置
for (var i = 1; i <= 5; i++) {
  ActiveDocument.Paragraphs.Item(i).Alignment = wdAlignParagraphJustify;
}

// 方法2: 使用区间（如果知道位置范围）
var range = ActiveDocument.Range(0, 500);
range.ParagraphFormat.Alignment = wdAlignParagraphJustify;
```

### 组合设置段落和字符格式

**场景**: 同时设置段落对齐和字体格式

```javascript
var para = ActiveDocument.Paragraphs.Item(1);

// 设置段落对齐
para.Alignment = wdAlignParagraphCenter;

// 设置字体
para.Range.Font.Name = "宋体";
para.Range.Font.Size = 16;
para.Range.Font.Bold = true;
```

### 获取当前段落格式

**场景**: 读取段落的当前对齐方式

```javascript
var alignment = ActiveDocument.Paragraphs.Item(1).Alignment;
JSON.stringify({ok: true, message: "success", data: alignment});
```

---

## 注意事项

1. **段落索引**: 从1开始计数
2. **枚举常量**: 必须使用WPS预定义的常量名（如`wdAlignParagraphCenter`）
3. **区间设置**: 影响区间内的所有段落，即使只有部分字符在区间内
4. **格式继承**: 新创建的段落会继承前一个段落的格式
5. **批量操作**: 尽量使用区间操作，减少API调用次数

## 常见问题

**Q: 如何设置标题段落的格式？**

A: 通常标题使用居中对齐：

```javascript
ActiveDocument.Paragraphs.Item(1).Alignment = wdAlignParagraphCenter;
```

**Q: 如何设置正文段落为两端对齐？**

A: 使用两端对齐枚举值：

```javascript
ActiveDocument.Paragraphs.Item(2).Alignment = wdAlignParagraphJustify;
```

**Q: 对齐方式的数值和常量名可以混用吗？**

A: 可以，但建议使用常量名以提高可读性：

```javascript
// 两种方式等效
ActiveDocument.Paragraphs.Item(1).Alignment = wdAlignParagraphCenter;
ActiveDocument.Paragraphs.Item(1).Alignment = 1;
```

**Q: 如何恢复段落的默认对齐方式？**

A: 设置为左对齐即可：

```javascript
ActiveDocument.Paragraphs.Item(1).Alignment = wdAlignParagraphLeft;
```

---

## 相关文档

- [enums.md](enums.md) - 查看完整的枚举值列表
- [character-format.md](character-format.md) - 字符格式设置
- [modify-content.md](modify-content.md) - 修改文档内容
