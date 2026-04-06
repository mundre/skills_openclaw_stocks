# WPS文字基础能力

提供对文档操作的原子能力，通过执行JSAPI来操作文档。


## 功能清单

下表列出了当前支持的所有功能。点击详情文档链接查看完整的脚本模板和参数说明。

### 文档内容操作

| 功能分类 | 功能描述 | 详情文档 | 状态 |
|---------|---------|---------|------|
| 读取全文 | 读取整个文档的文本内容。<br/>**使用场景**：查询文档中是否包含特定内容、对文档进行总结分析、提取关键信息、内容检索等需要获取完整文档内容的场景 | [read-content.md](references/read-content.md) | ✅ |
| 读取段落 | 读取指定第N个段落的内容 | [read-content.md](references/read-content.md) | ✅ |
| 读取区间 | 读取指定起始和结束位置的内容 | [read-content.md](references/read-content.md) | ✅ |
| 读取段落个数 | 获取文档中段落的总数 | [read-content.md](references/read-content.md) | ✅ |
| 修改段落 | 修改指定段落的文本内容 | [modify-content.md](references/modify-content.md) | ✅ |
| 修改区间 | 修改指定区间的文本内容 | [modify-content.md](references/modify-content.md) | ✅ |

### 段落格式设置

| 功能分类 | 功能描述 | 详情文档 | 状态 |
|---------|---------|---------|------|
| 段落对齐 | 设置段落对齐方式（左/中/右/两端） | [paragraph-format.md](references/paragraph-format.md) | ✅ |
| 区间对齐 | 设置指定区间的段落对齐方式 | [paragraph-format.md](references/paragraph-format.md) | ✅ |
| 段落缩进 | 设置段落缩进（首行/悬挂） | [paragraph-format.md](references/paragraph-format.md) | 🔜 |
| 行间距 | 设置段落行间距 | [paragraph-format.md](references/paragraph-format.md) | 🔜 |

### 字符格式设置

| 功能分类 | 功能描述 | 详情文档 | 状态 |
|---------|---------|---------|------|
| 字体名称 | 设置字体名称（宋体/黑体等） | [character-format.md](references/character-format.md) | ✅ |
| 字体大小 | 设置字号大小 | [character-format.md](references/character-format.md) | ✅ |
| 字体颜色 | 设置字体颜色 | [character-format.md](references/character-format.md) | ✅ |
| 字体样式 | 设置加粗、倾斜、下划线 | [character-format.md](references/character-format.md) | ✅ |
| 文字高亮 | 设置文字背景高亮色 | [character-format.md](references/character-format.md) | ✅ |

### 查找/替换内容功能

| 功能分类 | 功能描述 | 详情文档 | 状态 |
|---------|---------|---------|------|
| 查找内容 | 查找指定文本内容并返回位置 | [find-replace.md](references/find-replace.md) | ✅ |
| 替换内容 | 查找并替换文档中的文本 | [find-replace.md](references/find-replace.md) | ✅ |

---

## 使用工作流

当用户请求操作WPS文档时，按以下步骤处理：

### 步骤1: 分析用户需求

**识别操作数量**：判断用户是单一操作还是组合操作

- **单一操作**：如"读取第1段"、"设置居中"
- **组合操作**：如"修改第1段为xxx并设置右对齐"、"将第2段加粗并设置为红色"

**识别涉及的功能**：
- 读取操作：读取、获取、查看
- 修改操作：修改、改为、设置内容
- 查找/替换操作：查找、替换
- 格式操作：对齐、字体、颜色、加粗、倾斜、高亮

### 步骤2: 检查功能支持

**重要**：在功能清单中验证所需功能是否已定义。

**检查方法**：
1. 将用户需求拆解为具体的操作（如：修改内容、设置对齐、设置字体）
2. 在[功能清单](#功能清单)表格中逐一查找每个操作
3. 如果所有操作都在清单中 → 继续步骤3
4. 如果任何操作不在清单中 → **立即返回不支持**

**不支持时的返回示例**：
```
抱歉，当前不支持"设置段落缩进"功能。
```

### 步骤3: 查找原子操作模板

在功能清单表格中找到所需的功能：
- 单一操作：找到对应的一个功能
- 组合操作：找到多个相关功能的模板

### 步骤4: 读取详情文档

根据功能清单中的"详情文档"链接，读取对应的md文件获取：
- 完整的JavaScript脚本模板
- 参数说明和类型
- 使用示例

### 步骤5: 组合脚本（如需要）

**组合原则**：参考 [combined-operations.md](references/combined-operations.md)

**单一操作**：
- 直接使用单个脚本模板
- 填充参数（替换`${变量名}`占位符）

**组合操作**：
- 只使用已读取的原子操作模板进行组合
- 共享变量（如Range对象），避免重复获取
- 按逻辑顺序组合（先修改内容，再设置格式）
- 示例：

```javascript
// ✅ 正确：基于原子操作模板组合
// 原子操作1：修改段落（来自modify-content.md）
// 原子操作2：设置对齐（来自paragraph-format.md）
var paragraph = ActiveDocument.Paragraphs.Item(1);
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = "标题";  // 原子操作1的核心代码（Range操作）
paragraph.Alignment = wdAlignParagraphCenter;  // 原子操作2的核心代码（Paragraph操作）

// ❌ 错误：使用未定义的操作
// 不要自创任何不在功能清单中的操作
```

### 步骤6: 返回结果

提供完整的调用示例给用户，包括：
- `file_id`：在线文字文件 ID
- `jsStr`：构建好的 JavaScript 脚本

**调用格式示例**：
```json
{
  "file_id": "file_xxx",
  "jsStr": "ActiveDocument.Paragraphs.Item(1).Alignment = wdAlignParagraphCenter;"
}
```

---

## 快速参考

### 重要说明
- **功能检查**: 使用前必须先在功能清单中确认功能是否支持，不支持的功能应明确告知用户
- **段落索引**: 从1开始计数
- **字符位置**: 从0开始计数
- **枚举常量**: 使用WPS预定义常量（如`wdRed`、`wdAlignParagraphCenter`）
- **返回格式**: `{ok: boolean, message: string, data: any}`
- **组合操作**: 可以在一个脚本中组合多个操作，共享对象提高效率，但只能使用已定义的原子操作

### 组合操作示例

**修改内容+设置对齐**：
```javascript
var paragraph = ActiveDocument.Paragraphs.Item(1);
var r = paragraph.Range;
var range = ActiveDocument.Range(r.Start, r.End - 1);
range.Text = "标题";
paragraph.Alignment = wdAlignParagraphCenter;
```

**设置完整样式**：
```javascript
var paragraph = ActiveDocument.Paragraphs.Item(1);
var range = paragraph.Range;
range.Font.Name = "黑体";
range.Font.Size = 18;
range.Font.ColorIndex = wdRed;
range.Font.Bold = true;
paragraph.Alignment = wdAlignParagraphCenter;
```

更多组合场景请参考 [combined-operations.md](references/combined-operations.md)

### 常用枚举值

完整的枚举值列表请参考 [enums.md](references/enums.md)

**对齐方式快速参考**:
- `wdAlignParagraphLeft` (0) - 左对齐
- `wdAlignParagraphCenter` (1) - 居中
- `wdAlignParagraphRight` (2) - 右对齐
- `wdAlignParagraphJustify` (3) - 两端对齐

**颜色快速参考**:
- `wdBlack` - 黑色
- `wdRed` - 红色
- `wdBlue` - 蓝色
- `wdGreen` - 绿色
