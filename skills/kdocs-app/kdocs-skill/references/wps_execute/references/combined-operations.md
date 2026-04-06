# 组合操作指南

本文档提供如何基于原子操作模板组合多个操作的方法论。**不穷举所有场景，而是教你如何根据已定义的原子操作灵活组合。**

## ⚠️ 核心原则

### 只使用已定义的原子操作

**严格限制**：
- ✅ 所有操作必须来自功能清单中已定义的原子操作模板
- ✅ 从对应的md文档中获取完整的脚本模板
- ❌ 不要自创或使用未在文档中定义的操作
- ❌ 不要使用功能清单中标记为🔜的未实现功能
- ❌ 如果用户需求涉及未支持的功能，应明确告知不支持

**支持的原子操作清单**：
详见[功能清单](../execute.md#功能清单)

**不支持时应该**：
```
抱歉，当前不支持"[具体功能名称]"功能。
```

---

## 组合方法

### 1. 正确的对象共享

理解WPS对象层级关系：
- `Paragraph对象`: 代表一个段落，有Alignment等属性
- `Range对象`: 代表一个文本区域，通过`Paragraph.Range`获取，有Text、Font等属性

**正确的共享方式**：

```javascript
// ✅ 推荐：同时共享Paragraph和Range对象，保留换行符
var paragraph = ActiveDocument.Paragraphs.Item(1);
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);  // 保留段落换行符
range.Text = "标题";                    // Range对象上的操作
paragraph.Alignment = wdAlignParagraphCenter;  // Paragraph对象上的操作
range.Font.Bold = true;                 // Range对象上的操作

// ❌ 不推荐：重复获取对象，且未保留换行符
ActiveDocument.Paragraphs.Item(1).Range.Text = "标题";
ActiveDocument.Paragraphs.Item(1).Alignment = wdAlignParagraphCenter;
ActiveDocument.Paragraphs.Item(1).Range.Font.Bold = true;
```

**对象层级关系**：
```
ActiveDocument
└── Paragraphs.Item(n) ← Paragraph对象
    ├── .Alignment         (段落属性，在Paragraph上)
    ├── .Range            (获取Range对象)
    │   ├── .Text          (文本内容，在Range上)
    │   ├── .Font          (字体，在Range上)
    │   │   ├── .Name
    │   │   ├── .Size
    │   │   ├── .ColorIndex
    │   │   ├── .Bold
    │   │   └── ...
    │   ├── .HighlightColorIndex (高亮，在Range上)
    │   └── .ParagraphFormat     (也可以通过这个访问段落格式)
    │       └── .Alignment       (等效于Paragraph.Alignment)
    └── ...
```

### 2. 逻辑顺序原则

按照正确的顺序组合操作：

**推荐顺序**：
1. 修改文本内容
2. 设置段落格式（对齐）
3. 设置字体属性（名称、大小）
4. 设置字体样式（加粗、倾斜）
5. 设置颜色和高亮

```javascript
// 正确的组合方式
var paragraph = ActiveDocument.Paragraphs.Item(1);
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = "新标题";                      // 1. 内容（Range）
paragraph.Alignment = wdAlignParagraphCenter;  // 2. 段落格式（Paragraph）
range.Font.Name = "黑体";                   // 3. 字体属性（Range.Font）
range.Font.Size = 22;
range.Font.Bold = true;                     // 4. 字体样式（Range.Font）
range.Font.ColorIndex = wdBlue;             // 5. 颜色（Range.Font）
```

### 3. 从原子模板提取核心代码

**步骤**：

1. **从功能清单找到需要的原子操作**
2. **读取对应md文档获取完整模板**
3. **提取核心赋值语句**
4. **组合时共享对象(如：Range)**

**示例**：用户说"把第1段改为'标题'并设置居中红色加粗"

**Step 1**: 识别需要的原子操作
- 修改段落内容（modify-content.md）
- 设置段落对齐（paragraph-format.md）
- 设置字体颜色（character-format.md）
- 设置字体加粗（character-format.md）

**Step 2**: 从各md文档读取模板

从modify-content.md获取：
```javascript
var doc = Application.ActiveDocument;
var total = doc.Paragraphs.Count;
var maxN = ${n} < total ? ${n} : total;
var r = doc.Paragraphs.Item(maxN).Range;
var range = doc.Range(r.Start, r.End - 1);
range.Text = ${str};
```

从paragraph-format.md获取：
```javascript
ActiveDocument.Paragraphs.Item(${n}).Alignment = ${algMode};
```

从character-format.md获取：
```javascript
var range = ActiveDocument.Paragraphs.Item(${n}).Range;
range.Font.ColorIndex = ${value};

var range = ActiveDocument.Paragraphs.Item(${n}).Range;
range.Font.Bold = ${value};
```

**Step 3**: 提取核心代码并组合

```javascript
// 组合后的脚本（共享Paragraph和Range对象）
var paragraph = ActiveDocument.Paragraphs.Item(1);
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = "标题";                         // 来自modify-content.md (Range操作)
paragraph.Alignment = wdAlignParagraphCenter;  // 来自paragraph-format.md (Paragraph操作)
range.Font.ColorIndex = wdRed;               // 来自character-format.md (Range.Font操作)
range.Font.Bold = true;                      // 来自character-format.md (Range.Font操作)
```

---

## 组合模式参考

以下是一些常见的组合模式，都是基于原子操作的组合：

### 模式1: 内容修改 + 段落格式

**原子操作来源**：
- modify-content.md：修改段落
- paragraph-format.md：设置对齐

**组合结构**：
```javascript
var paragraph = ActiveDocument.Paragraphs.Item(${n});
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = ${text};        // 原子操作1: Range上操作
paragraph.Alignment = ${align};  // 原子操作2: Paragraph上操作
```

### 模式2: 内容修改 + 字符格式

**原子操作来源**：
- modify-content.md：修改段落
- character-format.md：设置字体属性（可多个）

**组合结构**：
```javascript
var paragraph = ActiveDocument.Paragraphs.Item(${n});
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = ${text};                // 原子操作1: 修改内容
range.Font.Name = ${fontName};       // 原子操作2-5: 都在Range.Font上
range.Font.Size = ${fontSize};
range.Font.ColorIndex = ${color};
range.Font.Bold = ${bold};
```

### 模式3: 段落格式 + 字符格式（不修改内容）

**原子操作来源**：
- paragraph-format.md：设置对齐
- character-format.md：设置字体属性

**组合结构**：
```javascript
var paragraph = ActiveDocument.Paragraphs.Item(${n});
var range = paragraph.Range;
paragraph.Alignment = ${align};      // 原子操作1: Paragraph上操作
range.Font.Name = ${fontName};       // 原子操作2-4: Range.Font上操作
range.Font.Size = ${fontSize};
range.Font.ColorIndex = ${color};
```

### 模式4: 完整组合（内容+段落+字符）

**原子操作来源**：
- modify-content.md：修改内容
- paragraph-format.md：段落格式
- character-format.md：字符格式

**组合结构**：
```javascript
var paragraph = ActiveDocument.Paragraphs.Item(${n});
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = ${text};                // modify-content.md: Range操作
paragraph.Alignment = ${align};      // paragraph-format.md: Paragraph操作
range.Font.Name = ${fontName};       // character-format.md: Range.Font操作
range.Font.Size = ${fontSize};
range.Font.ColorIndex = ${color};
range.Font.Bold = ${bold};
```

### 模式5: 批量应用（循环）

**原子操作来源**：任何原子操作
**组合方式**：使用循环批量应用

**组合结构**：
```javascript
var doc = ActiveDocument;
for (var i = ${startN}; i <= ${endN}; i++) {
  var paragraph = doc.Paragraphs.Item(i);
  var range = paragraph.Range;
  // 在这里应用原子操作
  paragraph.Alignment = ${align};    // 如果涉及段落格式
  range.Font.Name = ${fontName};     // 如果涉及字体
  range.Font.Size = ${fontSize};
}
```

---

## 实际示例

### 示例1: 基础组合（2个原子操作）

**用户需求**："把第1段改为'文档标题'并设置居中"

**组合脚本**：
```javascript
var paragraph = ActiveDocument.Paragraphs.Item(1);
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = "文档标题";                 // 来自modify-content.md: Range操作
paragraph.Alignment = wdAlignParagraphCenter;  // 来自paragraph-format.md: Paragraph操作
```

### 示例2: 中等组合（4个原子操作）

**用户需求**："把第1段改为'重要通知'并设置为红色加粗黄色高亮"

**组合脚本**：
```javascript
var paragraph = ActiveDocument.Paragraphs.Item(1);
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = "重要通知";               // 来自modify-content.md
range.Font.ColorIndex = wdRed;         // 来自character-format.md
range.Font.Bold = true;                // 来自character-format.md
range.HighlightColorIndex = wdYellow;  // 来自character-format.md
```

**说明**：此场景不涉及Paragraph属性，但仍需保留换行符。

### 示例3: 完整组合（6个原子操作）

**用户需求**："把第1段改为'项目报告'，设置为黑体18号居中红色加粗"

**组合脚本**：
```javascript
var paragraph = ActiveDocument.Paragraphs.Item(1);
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = "项目报告";                 // 来自modify-content.md: Range操作
range.Font.Name = "黑体";                // 来自character-format.md: Range.Font操作
range.Font.Size = 18;                    // 来自character-format.md: Range.Font操作
paragraph.Alignment = wdAlignParagraphCenter;  // 来自paragraph-format.md: Paragraph操作
range.Font.ColorIndex = wdRed;           // 来自character-format.md: Range.Font操作
range.Font.Bold = true;                  // 来自character-format.md: Range.Font操作
```

### 示例4: 批量组合

**用户需求**："把第2到5段设置为宋体12号两端对齐"

**组合脚本**：
```javascript
var doc = ActiveDocument;
for (var i = 2; i <= 5; i++) {
  var paragraph = doc.Paragraphs.Item(i);
  var range = paragraph.Range;
  range.Font.Name = "宋体";              // 来自character-format.md: Range.Font操作
  range.Font.Size = 12;                  // 来自character-format.md: Range.Font操作
  paragraph.Alignment = wdAlignParagraphJustify;  // 来自paragraph-format.md: Paragraph操作
}
```

---

## 组合检查清单

在组合操作时，检查以下几点：

- [ ] 所有操作都来自已定义的原子模板
- [ ] 是否能使用共享对象，能则使用共享对象
- [ ] 操作按逻辑顺序排列
- [ ] 所有参数已正确替换
- [ ] 使用了正确的枚举常量
- [ ] 适当添加了错误处理
