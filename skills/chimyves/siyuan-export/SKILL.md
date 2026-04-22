---
name: siyuan-export
description: "思源笔记文档导出工具。将思源笔记文档导出为 Word(docx) 格式，支持按文档 ID 或路径导出，图片自动打包进文档（单个文件输出）。支持单个文档导出和批量导出子文档。触发词：导出文档、导出 Word、siyuan export、思源导出、批量导出、导出子文档"
version: "1.1.0"
author: Matrix for Neo
---

# 思源笔记文档导出 (siyuan-export)

通过思源笔记原生 API 将文档导出为 **Word(.docx)**，返回结构化 JSON 结果。支持单文档和批量子文档导出。

## 核心特性

| 特性 | 说明 |
|------|------|
| **双定位** | 支持文档 ID 或人类可读路径 |
| **批量导出** | `--children` 一键导出文档下所有子文档（含嵌套） |
| **单文件输出** | 图片资源自动内嵌（`removeAssets=true`），不产生外挂目录 |
| **JSON 输出** | 结构化结果，方便大模型解析 |
| **零依赖** | 仅使用 Python 标准库 |

## 前置条件

1. 思源笔记正在运行
2. 已配置 `config.json`（技能目录下）：
   ```json
   {"baseURL": "http://127.0.0.1:6806", "token": "你的API Token", "timeout": 10000}
   ```
   Token 获取：思源笔记 → 设置 → 关于 → 复制 Token

## 使用方法

```bash
# 按 ID 导出单个文档到桌面（最常用）
python scripts/siyuan_export.py --doc-id <ID>

# 按路径导出，指定输出目录
python scripts/siyuan_export.py --path "/AI/AIGC/绘画" --output C:/output

# 导出文档下所有子文档
python scripts/siyuan_export.py --doc-id <ID> --children --output C:/Desktop/Midjourney

# 导出文档本身 + 所有子文档
python scripts/siyuan_export.py --doc-id <ID> --children --include-self --output C:/Desktop/Midjourney

# 纯 JSON 输出（供程序调用）
python scripts/siyuan_export.py --doc-id <ID> --json
```

### 参数说明

| 参数 | 缩写 | 必选 | 说明 |
|------|------|:----:|------|
| `--doc-id` | `-i` | 二选一 | 文档 ID（如 `20260404211618-s3bjc3l`） |
| `--path` | `-p` | 二选一 | 文档路径（如 `/AI/AIGC/绘画`） |
| `--children` | `-c` | 否 | 批量模式：导出该文档下所有子文档 |
| `--include-self` | | 否 | 批量模式时同时导出父文档本身（需配合 `--children`） |
| `--output` | `-o` | 否 | 输出**目录**路径（默认：桌面），API 会在该目录下以文档标题命名生成文件 |
| `--json` | | 否 | 仅输出 JSON，无 stderr 提示 |

## 返回值

### 单文档导出

成功：

```json
{
  "success": true,
  "data": {
    "path": "C:/Users/10941/Desktop/P02：设置解析.docx",
    "size_bytes": 3544783,
    "size_kb": 3461.7
  }
}
```

### 批量子文档导出

成功：

```json
{
  "success": true,
  "data": {
    "total": 16,
    "success_count": 16,
    "fail_count": 0,
    "output_dir": "C:/Users/10941/Desktop/Midjourney教程",
    "details": [
      {"id": "...", "title": "P01：认识界面", "result": {"success": true, "data": {"path": "...", "size_kb": 1234.5}}},
      ...
    ]
  }
}
```

失败：

```json
{
  "success": false,
  "error": "api_error",
  "message": "具体错误信息"
}
```

## API 接口

| 本脚本 | 思源 API | 参数 |
|--------|---------|------|
| 单文档导出 | `POST /api/export/exportDocx` | `id` + `savePath`（目录）+ `removeAssets=true` |
| 获取子文档列表 | `POST /api/query/sql` | SQL 查询 `hpath LIKE` 匹配子路径 |

## 文件结构

```
siyuan-export/
├── SKILL.md
├── config.json         # 配置文件（需手动填写 token）
└── scripts/
    └── siyuan_export.py
```
