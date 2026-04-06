# 修改文档内容

本文档提供修改WPS文档内容的所有功能和脚本模板。

## 功能列表

| 功能 | 说明 | 参数 |
|------|------|------|
| 修改段落内容 | 修改第N个段落的文本 | n: 段落索引, str: 新内容 |
| 修改区间内容 | 修改指定区间的文本 | begin: 开始位置, end: 结束位置, str: 新内容 |

---

## 1. 修改指定段落内容

### 功能描述
修改文档中第N个段落的文本内容。段落索引从1开始。

### JavaScript脚本模板

```javascript
var doc = Application.ActiveDocument;
var total = doc.Paragraphs.Count;
var maxN = ${n} < total ? ${n} : total;
var r = doc.Paragraphs.Item(maxN).Range;
var range = doc.Range(r.Start, r.End - 1);
range.Text = ${str};
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| n | uint32 | 是 | 要修改的段落索引（从1开始） |
| str | string | 是 | 修改后的内容（需要加引号） |

### 使用示例

**修改第2个段落的内容为"新的段落内容"**:

替换模板中的`${n}`为`2`，`${str}`为`"新的段落内容"`：

```javascript
var doc = Application.ActiveDocument;
var total = doc.Paragraphs.Count;
var maxN = 2 < total ? 2 : total;
var r = doc.Paragraphs.Item(maxN).Range;
var range = doc.Range(r.Start, r.End - 1);
range.Text = "新的段落内容";
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var doc = Application.ActiveDocument; var total = doc.Paragraphs.Count; var maxN = 2 < total ? 2 : total; var r = doc.Paragraphs.Item(maxN).Range; var range = doc.Range(r.Start, r.End - 1); range.Text = '新的段落内容';"
}
```

---

## 2. 修改指定区间内容

### 功能描述
修改文档中指定起始和结束字符位置之间的内容。

### JavaScript脚本模板

```javascript
var doc = Application.ActiveDocument;
if (!doc) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var range = doc.Range(${begin}, ${end});
  var maxEnd = doc.Range().End;
  if (begin >= maxEnd) {
    range = doc.Range(maxEnd, maxEnd);
    range.InsertParagraph();
  }
  range.Text = ${str};
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| begin | uint32 | 是 | 开始位置（字符索引，从0开始） |
| end | uint32 | 是 | 结束位置（字符索引） |
| str | string | 是 | 修改后的内容（需要加引号） |

### 使用示例

**修改位置10到50的内容为"替换后的文本"**:

替换模板中的参数：

```javascript
var doc = Application.ActiveDocument;
if (!doc) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var range = doc.Range(10, 50);
  var maxEnd = doc.Range().End;
  if (10 >= maxEnd) {
    range = doc.Range(maxEnd, maxEnd);
    range.InsertParagraph();
  }
  range.Text = "替换后的文本";
}
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var doc = Application.ActiveDocument; if (!doc) { JSON.stringify({ok: false, message: 'no active document', data: null}); } else { var range = doc.Range(10, 50); var maxEnd = doc.Range().End; if (10 >= maxEnd) { range = doc.Range(maxEnd, maxEnd); range.InsertParagraph(); } range.Text = '替换后的文本'; }"
}
```

---

## 高级用法

### 组合修改操作

**场景**: 修改多个段落的内容

```javascript
var doc = Application.ActiveDocument;

// 修改第1段
var r1 = doc.Paragraphs.Item(1).Range;
var range1 = doc.Range(r1.Start, r1.End - 1);
range1.Text = "第一段新内容";

// 修改第2段
var r2 = doc.Paragraphs.Item(2).Range;
var range2 = doc.Range(r2.Start, r2.End - 1);
range2.Text = "第二段新内容";

// 修改第3段
var r3 = doc.Paragraphs.Item(3).Range;
var range3 = doc.Range(r3.Start, r3.End - 1);
range3.Text = "第三段新内容";
```

---

## 注意事项

1. **字符串参数**: 在JavaScript中，字符串参数必须用引号包裹
2. **特殊字符**: 如果要替换的内容包含特殊字符（如引号、换行），需要进行转义
3. **段落索引**: 从1开始计数
4. **保留格式**: 修改文本时，会丢失原有的格式，如需保留格式，需要单独处理

## 常见问题

**Q: 如何在替换时保留原有格式？**

A: 使用`Range.FormattedText`而不是`Range.Text`：

```javascript
var r1 = doc.Paragraphs.Item(1).Range;
var source = doc.Range(r1.Start, r1.End - 1);
var r2 = doc.Paragraphs.Item(2).Range;
var target = doc.Range(r2.Start, r2.End - 1);
target.FormattedText = source.FormattedText; // 复制带格式的内容
```

**Q: 如何插入内容而不是替换？**

A: 使用`Range.InsertAfter()`或`Range.InsertBefore()`：

```javascript
var range = doc.Paragraphs.Item(1).Range;
range.InsertAfter("在段落末尾插入的内容");
range.InsertBefore("在段落开头插入的内容");
```

**Q: 如何删除段落内容？**

A: 将内容设置为空字符串：

```javascript
var r = doc.Paragraphs.Item(2).Range;
var range = doc.Range(r.Start, r.End - 1);
range.Text = "";
```
