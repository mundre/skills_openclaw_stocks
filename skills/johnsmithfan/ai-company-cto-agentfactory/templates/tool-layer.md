# Tool Layer Agent Template

> **层级**: Tool (L0)  
> **特性**: 原子能力单元，无状态，可复用  
> **Harness原则**: 标准化接口 / 模块化结构 / 通用化参数

---

## Frontmatter Template

```yaml
---
name: {skill_name}
slug: {skill_slug}
version: {version}
description: |
  {one_sentence_description}
metadata:
  standardized: true
  harness_layer: tool
  stateless: true
  idempotent: true
---
```

---

## Required Structure

### 1. When to Use

明确触发条件，使用 Markdown 列表：

```markdown
## When to Use

- 场景1：具体描述
- 场景2：具体描述
- 场景3：具体描述
```

### 2. Input/Output Schema

必须定义 JSON Schema：

```markdown
## Input Schema

```json
{
  "type": "object",
  "required": ["param1", "param2"],
  "properties": {
    "param1": {"type": "string", "description": "..."},
    "param2": {"type": "number", "description": "..."}
  }
}
```

## Output Schema

```json
{
  "type": "object",
  "required": ["result"],
  "properties": {
    "result": {"type": "string"},
    "metadata": {"type": "object"}
  }
}
```
```

### 3. Error Codes

标准化错误码表：

```markdown
## Error Codes

| Code | Message | HTTP Status |
|------|---------|-------------|
| E001 | Invalid input | 400 |
| E002 | Resource not found | 404 |
| E003 | Internal error | 500 |
```

### 4. Core Rules

3-7条核心规则：

```markdown
## Core Rules

1. 无状态设计 — 不依赖外部状态
2. 幂等性 — 相同输入产生相同输出
3. 输入验证 — 严格校验所有参数
4. 错误处理 — 返回标准化错误码
5. 最小权限 — 仅请求必要权限
```

### 5. Examples

使用示例：

```markdown
## Examples

### Example 1: Basic Usage

**Input:**
```json
{"param1": "value1"}
```

**Output:**
```json
{"result": "success"}
```
```

---

## Quality Gates (Tool Layer)

| Gate | Check | Threshold | Blocking |
|------|-------|-----------|----------|
| G0-1 | 无状态验证 | 100%幂等 | ✅ |
| G0-2 | 接口合规 | 0缺失字段 | ✅ |
| G0-3 | 测试覆盖 | ≥90% | ✅ |
| G0-4 | 安全扫描 | Critical/High=0 | ✅ |
| G0-5 | 性能基准 | P95≤500ms | ❌ |

---

## File Structure

```
{skill_name}/
├── SKILL.md              # 主文件（≤80行）
├── scripts/              # 实现脚本
│   └── {main_script}.py
├── tests/                # 测试套件
│   ├── test_unit.py      # 单元测试
│   └── test_golden.json  # 黄金测试集
├── references/           # 参考文档
│   └── api-reference.md
└── CHANGELOG.md          # 版本历史
```

---

## Example: PDF Skill

```yaml
---
name: PDF Processor
slug: pdf
version: 1.2.0
description: |
  PDF文件读写、合并、拆分、水印、OCR全流程处理。
  支持文本提取、表格识别、格式转换。
metadata:
  standardized: true
  harness_layer: tool
  stateless: true
  idempotent: true
---

# PDF Processor

## When to Use

- 需要读取PDF文件内容
- 需要合并多个PDF文件
- 需要拆分PDF页面
- 需要添加水印或签名
- 需要PDF OCR文字识别

## Input Schema

```json
{
  "type": "object",
  "required": ["action", "input_path"],
  "properties": {
    "action": {
      "type": "string",
      "enum": ["read", "merge", "split", "watermark", "ocr"]
    },
    "input_path": {"type": "string"},
    "output_path": {"type": "string"},
    "options": {"type": "object"}
  }
}
```

## Output Schema

```json
{
  "type": "object",
  "required": ["status"],
  "properties": {
    "status": {"type": "string", "enum": ["success", "error"]},
    "output_path": {"type": "string"},
    "metadata": {"type": "object"}
  }
}
```

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| E001 | File not found | 输入文件不存在 |
| E002 | Invalid PDF | 文件格式不正确 |
| E003 | Permission denied | 无读取/写入权限 |

## Core Rules

1. 始终验证输入文件存在性和可读性
2. 输出文件路径必须可写
3. 大文件使用流式处理（内存友好）
4. 临时文件使用后立即清理
5. 错误信息不包含敏感路径信息

## Examples

### Example 1: 提取PDF文本

**Input:**
```json
{
  "action": "read",
  "input_path": "./document.pdf",
  "options": {"extract_text": true}
}
```

**Output:**
```json
{
  "status": "success",
  "text": "提取的文本内容...",
  "page_count": 10
}
```
```
