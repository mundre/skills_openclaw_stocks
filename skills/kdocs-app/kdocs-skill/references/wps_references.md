# 在线文字（wps）工具完整参考文档

本文件包含金山文档 Skill 中在线文字（`wps.*`）工具的操作说明。该类工具面向在线编辑中的文字文档，适合创建空白文档、导出、执行 JSAPI 等场景。

---

## 通用说明

### 在线文字特点

- 面向在线文字文档，不是本地 `.docx` 文件直传接口
- 支持创建空白在线文档、导出为 DOCX / PDF / 图片 / AP
- **通过 `wps.execute` 执行文档操作的原子能力**（推荐使用，详见下文）
- 若只是读取正文内容，仍优先使用通用工具 `read_file_content`

### 何时使用 `wps.*`

- 需要新建一个空白在线文字文档
- 需要把在线文字导出为 DOCX、PDF、图片或 AP 文稿
- **需要对在线文字执行文档操作（内容、格式、查找替换等）→ 优先使用 `wps.execute`**

### 何时不要用 `wps.*`

- 创建普通 `.docx` 文件：用 `create_file`
- 上传或覆盖本地 docx/pdf 文件：用 `upload_file`
- 写 Markdown 富文本内容到智能文档：用 `otl.*`

## 工具总览

| 工具 | 作用 |
|------|------|
| `wps.create_empty_document` | 创建空白在线文字文档 |
| `wps.export` | 文档导出入口，支持 docx / pdf / ap |
| `wps.export_image` | 将在线文字导出为 png / jpeg 图片 |
| `wps.query_export` | 统一查询异步导出结果，支持 pdf / ap |
| `wps.execute` | 透传执行在线文字 JSAPI |

### `wps.*`工具调用说明
- 格式：服务名和工具分开: 服务名 wps.xx
  例如：kdocs wps.execute

## 1. 导出能力总览

### 功能说明

`wps.*` 中的导出能力对外拆分为三个工具：

- `wps.export`：导出 DOCX、创建 PDF 导出任务、发起 AP 导出流程
- `wps.export_image`：导出 PNG / JPEG 图片
- `wps.query_export`：统一查询异步导出结果

### 选择建议

- 需要拿到 `.docx` 下载地址：用 `wps.export`，传 `format=docx`
- 需要导出图片：用 `wps.export_image`，传 `link_id` 和 `format=png/jpeg`
- 需要导出 PDF：先 `wps.export`，传 `format=pdf`；再按需用 `wps.query_export`
- 需要导出 AP：先 `wps.export`，传 `format=ap`；再用 `wps.query_export`

---

### 1.1 wps.export

### 功能说明

统一导出在线文字文档，按 `format` 分发到不同导出分支：

- `docx`：返回 DOCX 下载结果
- `pdf`：创建 PDF 导出任务
- `ap`：发起 AP 导出流程

### `format=docx` 示例

```json
{
  "link_id": "link_xxx",
  "format": "docx",
  "with_checksums": "md5,sha256"
}
```

### `format=pdf` 示例

```json
{
  "link_id": "link_xxx",
  "format": "pdf",
  "from_page": 1,
  "to_page": 10
}
```

### `format=ap` 示例

```json
{
  "link_id": "link_xxx",
  "format": "ap",
  "name": "季度经营分析"
}
```

### 参数说明

- `link_id` (string, 必填): 在线文字文件链接 ID
- `format` (string, 必填): `docx` / `pdf` / `ap`
- `with_checksums` (string, 可选): `format=docx` 时可传，校验算法列表，如 `md5,sha256`
- `cid` (string, 可选): `format=docx` 时可传，分享链接 ID
- `from_page` (number, 可选): `format=pdf` 时可传，默认 `1`
- `to_page` (number, 可选): `format=pdf` 时可传，默认 `9999`
- `client_id` (string, 可选): 导出时可传的客户端标识
- `password` (string, 可选): `format=pdf` 时可传，源文档密码
- `store_type` (string, 可选): `format=pdf` 时可传，如 `ks3`、`cloud`
- `multipage` (number, 可选): `format=pdf` 时可传，默认 `1`
- `opt_frame` (boolean, 可选): `format=pdf` 时可传，默认 `true`
- `export_open_password` (string, 可选): `format=pdf` 时可传
- `export_modify_password` (string, 可选): `format=pdf` 时可传
- `name` (string, 可选): `format=ap` 时必填，AP 文稿名称，不含后缀

---

### 1.2 wps.export_image

### 功能说明

将在线文字导出为 `png` 或 `jpeg` 图片。该接口走图片导出链路，入参必须使用 `link_id`，不能使用 `file_id`。

### 调用示例

```json
{
  "link_id": "link_xxx",
  "format": "png",
  "dpi": 150,
  "from_page": 1,
  "to_page": 3,
  "combine_long_pic": true
}
```

### 参数说明

- `link_id` (string, 必填): 在线文字文件链接 ID
- `format` (string, 必填): `png` / `jpeg`
- `dpi` (number, 可选): 默认 `96`
- `water_mark` (boolean, 可选): 默认 `true`
- `from_page` (number, 可选): 默认 `1`
- `to_page` (number, 可选): 默认 `9999`
- `combine_long_pic` (boolean, 可选): 默认 `true`
- `use_xva` (boolean, 可选): 是否启用 XVA 渲染
- `client_id` (string, 可选): 导出时可传的客户端标识
- `password` (string, 可选): 源文档密码
- `store_type` (string, 可选): 如 `ks3`、`cloud`

---

### 1.3 wps.query_export

### 功能说明

统一查询异步导出结果：

- `format=pdf`：查询 PDF 导出任务
- `format=ap`：查询 AP 导出任务

### `format=pdf` 示例

```json
{
  "format": "pdf",
  "task_id": "task_xxx",
  "task_type": "normal_export"
}
```

### `format=ap` 示例

```json
{
  "format": "ap",
  "file_id": "ap_file_xxx",
  "task_id": "task_xxx"
}
```

### 参数说明

- `format` (string, 必填): `pdf` / `ap`
- `task_id` (string, 必填): 导出任务 ID
- `task_type` (string, 可选): `format=pdf` 时可传，通常为 `normal_export`
- `file_id` (string, 可选): `format=ap` 时必填，传 `wps.export` 返回的新 AP 文件 ID
- `extra_query` (object, 可选): `format=ap` 时可传，补充查询参数

---

## 2. wps.execute

### 功能说明

在在线文字文档中执行 JSAPI，提供对文档操作的**原子能力**，如：
- 读取/修改文档内容、段落、区间文本
- 设置段落格式（对齐、缩进、行间距）
- 设置字符格式（字体、大小、颜色、样式）
- 查找/替换文档内容
- 组合多种格式和内容操作

详细功能清单和使用场景请参考 [wps_execute/execute.md](wps_execute/execute.md)。

### 调用示例

```json
{
  "file_id": "file_xxx",
  "jsStr": "var doc = Application.ActiveDocument; if (!doc) { JSON.stringify({ok: false, message: \"no active document\", data: null}); } else { var range = doc.Paragraphs.Item(1).Range; range.Font.ColorIndex = wdRed; JSON.stringify({ok: true, message: \"success\", data: {Color: range.Font.ColorIndex}}); }"
}
```

### 参数说明

- `file_id` (string, 必填): 在线文字文件 ID
- `jsStr` (string, 必填): 要执行的完整 JSAPI 脚本字符串

### 使用原则（重要）

**何时使用**：
- ✅ **优先选择**：需要对文档进行内容、样式、属性等操作时（读取、修改、格式设置、查找替换等）
- ✅ 需要使用已定义的原子能力时

**使用要求**：
1. **严格遵循工作流**：必须按照 [wps_execute/execute.md](wps_execute/execute.md) 中的 **"使用工作流"** 步骤执行
2. **使用已有模板**：只能使用已提供的功能模板，禁止随意生成或自创脚本
3. **功能检查优先**：执行前必须在功能清单中确认功能是否支持，不支持的功能应明确告知用户
4. **组合操作规范**：多个操作组合时，参考 [combined-operations.md](wps_execute/references/combined-operations.md)

---

## 典型用途

| 场景 | 说明 |
|------|------|
| 空白文档创建 | 新建在线文字后再进入后续编辑流程 |
| 文档导出 | 通过 `wps.export`、`wps.export_image`、`wps.query_export` 完成 |
| AP 生成 | 通过 `wps.export(format=ap)` 与 `wps.query_export(format=ap)` 完成 |
| **文档操作自动化** | **通过 `wps.execute` 执行原子能力（内容、格式、查找替换等），这是文档操作的首选方式** |
