# 读取文档内容

本文档提供读取WPS文档内容的所有功能和脚本模板。

## 功能列表

| 功能 | 说明 | 参数 |
|------|------|------|
| 读取全文 | 读取整个文档的文本内容 | 无 |
| 读取第N个段落 | 读取指定段落的内容 | n: 段落索引 |
| 读取指定区间 | 读取指定起始和结束位置的内容 | begin: 开始位置, end: 结束位置 |
| 读取段落个数 | 获取文档中段落的总数 | 无 |

---

## 1. 读取全文

### 功能描述
读取整个文档的完整文本内容。

### 使用场景
- **内容查询**：检查文档中是否包含特定的关键词、短语或内容
- **文档总结**：获取完整文本以便进行内容总结、摘要生成
- **信息提取**：从完整文档中提取关键信息、数据或特定模式
- **内容分析**：对文档进行全文分析，如字数统计、主题识别、情感分析
- **内容检索**：在文档全文中搜索、匹配特定内容模式
- **文档对比**：获取完整内容用于与其他文档进行对比
- **内容验证**：验证文档内容是否符合特定要求或标准

### JavaScript脚本模板

```javascript
var d = Application.ActiveDocument;
if (!d) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var text = d.Content.Text;
  JSON.stringify({ok: true, message: "success", data: text});
}
```

### 参数说明
无需参数。

### 返回值
包含文档完整文本内容的JSON对象。

### 使用示例

```javascript
var d = Application.ActiveDocument;
if (!d) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var text = d.Content.Text;
  JSON.stringify({ok: true, message: "success", data: text});
}
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var d = Application.ActiveDocument; if (!d) { JSON.stringify({ok: false, message: 'no active document', data: null}); } else { var text = d.Content.Text; JSON.stringify({ok: true, message: 'success', data: text}); }"
}
```

### 返回值示例

```json
{
  "ok": true,
  "message": "success",
  "data": "这是文档的完整内容...\n第二段内容...\n第三段内容..."
}
```

---

## 2. 读取第N个段落

### 功能描述
读取文档中指定的第N个段落的内容。段落索引从1开始。

### JavaScript脚本模板

```javascript
var d = Application.ActiveDocument;
if (!d) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var total = d.Paragraphs.Count;
  var maxN = ${n} < total ? ${n} : total;
  var text = d.Paragraphs.Item(maxN).Range.Text;

  JSON.stringify({ok: true, message: "success", data: text});
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| n | uint32 | 是 | 段落的索引值，从1开始计数 |

### 使用示例

**读取第3个段落**:

替换模板中的`${n}`为`3`：

```javascript
var d = Application.ActiveDocument;
if (!d) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var total = d.Paragraphs.Count;
  var maxN = 3 < total ? 3 : total;
  var text = d.Paragraphs.Item(maxN).Range.Text;

  JSON.stringify({ok: true, message: "success", data: text});
}
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var d = Application.ActiveDocument; if (!d) { JSON.stringify({ok: false, message: 'no active document', data: null}); } else { var total = d.Paragraphs.Count; var maxN = 3 < total ? 3 : total; var text = d.Paragraphs.Item(maxN).Range.Text; JSON.stringify({ok: true, message: 'success', data: text}); }"
}
```

### 返回值示例

```json
{
  "ok": true,
  "message": "success",
  "data": "这是第三个段落的内容"
}
```

---

## 3. 读取指定区间

### 功能描述
读取文档中指定起始和结束字符位置之间的内容。字符位置从0开始。

### JavaScript脚本模板

```javascript
var doc = Application.ActiveDocument;
if (!doc) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var t = doc.Range(${begin}, ${end}).Text;

  JSON.stringify({ok: true, message: "success", data: t});
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| begin | uint32 | 是 | 读取开始位置（字符索引，从0开始） |
| end | uint32 | 是 | 读取结束位置（字符索引） |

### 使用示例

**读取位置0到100的内容**:

替换模板中的`${begin}`为`0`，`${end}`为`100`：

```javascript
var doc = Application.ActiveDocument;
if (!doc) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var t = doc.Range(0, 100).Text;

  JSON.stringify({ok: true, message: "success", data: t});
}
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var doc = Application.ActiveDocument; if (!doc) { JSON.stringify({ok: false, message: 'no active document', data: null}); } else { var t = doc.Range(0, 100).Text; JSON.stringify({ok: true, message: 'success', data: t}); }"
}
```

### 返回值示例

```json
{
  "ok": true,
  "message": "success",
  "data": "文档前100个字符的内容..."
}
```

---

## 4. 读取段落个数

### 功能描述
获取文档中段落的总数。

### JavaScript脚本模板

```javascript
var d = Application.ActiveDocument;
if (!d) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var count = d.Paragraphs.Count;
  JSON.stringify({ok: true, message: "success", data: count});
}
```

### 参数说明
无需参数。

### 返回值
包含段落总数（整数）的JSON对象。

### 使用示例

```javascript
var d = Application.ActiveDocument;
if (!d) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var count = d.Paragraphs.Count;
  JSON.stringify({ok: true, message: "success", data: count});
}
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var d = Application.ActiveDocument; if (!d) { JSON.stringify({ok: false, message: 'no active document', data: null}); } else { var count = d.Paragraphs.Count; JSON.stringify({ok: true, message: 'success', data: count}); }"
}
```

### 返回值示例

```json
{
  "ok": true,
  "message": "success",
  "data": 15
}
```

**说明**: 表示文档共有15个段落。

---

## 注意事项

1. **段落索引**: 从1开始计数，不是0
2. **字符位置**: 从0开始计数
3. **越界保护**: 读取段落时，脚本会自动限制在有效范围内
4. **错误处理**: 所有脚本都包含文档存在性检查
5. **返回格式**: 返回统一的JSON格式，包含ok、message、data字段

## 常见问题

**Q: 如何获取文档的段落总数？**

A: 使用功能4"读取段落个数"，或直接使用以下脚本：

```javascript
var d = Application.ActiveDocument;
if (!d) {
  JSON.stringify({ok: false, message: "no active document", data: null});
} else {
  var count = d.Paragraphs.Count;
  JSON.stringify({ok: true, message: "success", data: count});
}
```

**Q: 读取区间时，如何确定字符位置？**

A: 可以先读取全文，计算文本长度，或者逐段读取并累加长度。

**Q: 读取的文本是否包含格式信息？**

A: 不包含。这些方法只返回纯文本内容，不包含格式信息。
