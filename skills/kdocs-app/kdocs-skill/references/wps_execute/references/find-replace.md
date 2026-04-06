# 查找/替换文档内容

本文档提供查找和替换WPS文档内容的所有功能和脚本模板。

## 功能列表

| 功能 | 说明 | 参数 |
|------|------|------|
| 查找内容 | 查找指定文本并返回位置 | findText: 查找内容 |
| 替换内容 | 查找并替换文本 | findText: 查找内容, replaceText: 替换内容 |

---

## 1. 查找指定内容

### 功能描述
在文档中查找指定的文本内容，并返回找到的位置信息。

### JavaScript脚本模板

```javascript
var range = ActiveDocument.Content;
var found = range.Find.Execute(${findText}, null, null, null, null, null, null);
if (range.Find.Found) {
  JSON.stringify({ok: true, message: "success", data: {begin: range.Start, end: range.End}});
} else {
  JSON.stringify({ok: false, message: "not found", data: null});
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| findText | string | 是 | 要查找的内容（需要加引号） |

### 使用示例

**查找文本"关键词"**:

替换模板中的`${findText}`为`"关键词"`：

```javascript
var range = ActiveDocument.Content;
var found = range.Find.Execute("关键词", null, null, null, null, null, null);
if (range.Find.Found) {
  JSON.stringify({ok: true, message: "success", data: {begin: range.Start, end: range.End}});
} else {
  JSON.stringify({ok: false, message: "not found", data: null});
}
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var range = ActiveDocument.Content; var found = range.Find.Execute('关键词', null, null, null, null, null, null); if (range.Find.Found) { JSON.stringify({ok: true, message: 'success', data: {begin: range.Start, end: range.End}}); } else { JSON.stringify({ok: false, message: 'not found', data: null}); }"
}
```

### 返回值示例

**查找成功**:
```json
{
  "ok": true,
  "message": "success",
  "data": {
    "begin": 45,
    "end": 48
  }
}
```

**查找失败**:
```json
{
  "ok": false,
  "message": "not found",
  "data": null
}
```

---

## 2. 替换内容

### 功能描述
在整个文档中查找指定的文本，并替换为新内容。支持全部替换。

### JavaScript脚本模板

```javascript
var findText = ${findText};
var replaceText = ${replaceText};
var range = ActiveDocument.Content;
range.Find.Execute(findText, null, null, null, null, null, null, null, null, replaceText, wdReplaceAll);
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| findText | string | 是 | 需要查找的内容（需要加引号） |
| replaceText | string | 是 | 替换后的内容（需要加引号） |

### 使用示例

**将所有"旧文本"替换为"新文本"**:

替换模板中的参数：

```javascript
var findText = "旧文本";
var replaceText = "新文本";
var range = ActiveDocument.Content;
range.Find.Execute(findText, null, null, null, null, null, null, null, null, replaceText, wdReplaceAll);
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var findText = '旧文本'; var replaceText = '新文本'; var range = ActiveDocument.Content; range.Find.Execute(findText, null, null, null, null, null, null, null, null, replaceText, wdReplaceAll);"
}
```

---

## 高级用法

### 条件替换

**场景**: 只替换第一个匹配项

将脚本中的`wdReplaceAll`改为`wdReplaceOne`：

```javascript
var findText = "旧文本";
var replaceText = "新文本";
var range = ActiveDocument.Content;
range.Find.Execute(findText, null, null, null, null, null, null, null, null, replaceText, wdReplaceOne);
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var findText = '旧文本'; var replaceText = '新文本'; var range = ActiveDocument.Content; range.Find.Execute(findText, null, null, null, null, null, null, null, null, replaceText, wdReplaceOne);"
}
```

### 查找并高亮（不替换）

**场景**: 查找关键词但不替换，而是添加高亮

```javascript
var doc = ActiveDocument;
var findText = "关键词";
var range = doc.Content;

// 循环查找所有匹配项
while (range.Find.Execute(findText)) {
  range.HighlightColorIndex = wdYellow;
  range.Collapse(0); // wdCollapseEnd，移动到匹配内容的末尾
}
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var doc = ActiveDocument; var findText = '关键词'; var range = doc.Content; while (range.Find.Execute(findText)) { range.HighlightColorIndex = wdYellow; range.Collapse(0); }"
}
```

### 查找并应用格式

**场景**: 查找关键词并设置为红色加粗

```javascript
var doc = ActiveDocument;
var findText = "重要";
var range = doc.Content;

// 循环查找所有匹配项
while (range.Find.Execute(findText)) {
  range.Font.ColorIndex = wdRed;
  range.Font.Bold = true;
  range.Collapse(0); // wdCollapseEnd
}
```

**调用**:
```json
{
  "file_id": "file_xxx",
  "jsStr": "var doc = ActiveDocument; var findText = '重要'; var range = doc.Content; while (range.Find.Execute(findText)) { range.Font.ColorIndex = wdRed; range.Font.Bold = true; range.Collapse(0); }"
}
```

---

## 注意事项

1. **字符串参数**: 在JavaScript中，字符串参数必须用引号包裹
2. **特殊字符**: 如果要查找或替换的内容包含特殊字符（如引号、换行），需要进行转义
3. **替换常量**: 
   - `wdReplaceAll` - 替换所有匹配项
   - `wdReplaceOne` - 只替换第一个匹配项
   - `wdReplaceNone` - 不替换（仅查找）
4. **大小写**: 默认查找不区分大小写，可通过参数调整
5. **查找结果**: 查找成功后，range对象会定位到找到的位置

## 常见问题

**Q: 如何查找下一个匹配项？**

A: 在找到第一个后，调用`range.Collapse(0)`移动到末尾，再次执行查找：

```javascript
var range = ActiveDocument.Content;
if (range.Find.Execute("关键词")) {
  // 处理第一个匹配项
  var first = {begin: range.Start, end: range.End};
  
  // 移动到末尾继续查找
  range.Collapse(0);
  if (range.Find.Execute("关键词")) {
    // 处理第二个匹配项
    var second = {begin: range.Start, end: range.End};
  }
}
```

**Q: 查找替换是否支持正则表达式？**

A: WPS的Find.Execute支持通配符模式，但不是完整的正则表达式。需要设置相关参数启用通配符模式。

**Q: 如何统计查找到的匹配项数量？**

A: 使用循环计数：

```javascript
var doc = ActiveDocument;
var findText = "关键词";
var range = doc.Content;
var count = 0;

while (range.Find.Execute(findText)) {
  count++;
  range.Collapse(0);
}

JSON.stringify({ok: true, message: "success", data: count});
```

---

## 相关文档

- [modify-content.md](modify-content.md) - 修改文档内容
- [character-format.md](character-format.md) - 字符格式设置
- [enums.md](enums.md) - 枚举值列表
