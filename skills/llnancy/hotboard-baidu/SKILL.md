---
name: hotboard-baidu
description: 获取 百度热搜 热榜数据
license: Apache-2.0
metadata: {"openclaw":{"requires":{"bins":["hotboard-baidu"]},"install":[{"id":"hotboard-baidu","kind":"uv","package":"hotboard-baidu","bins":["hotboard-baidu"],"label":"Install hotboard-baidu from PyPI"}]}}
allowed-tools: ["Bash(hotboard-baidu:*)"]
---

# 百度热搜 热榜

获取 百度热搜 热榜数据。

## 使用方式

直接调用 CLI 命令：

```bash
hotboard-baidu
```

## 参数

- `--format`: 输出格式（可选，默认 markdown）
  - markdown: Markdown 格式
  - json: JSON 格式

## 示例

获取热榜（Markdown 格式）：

```bash
hotboard-baidu
```

获取 JSON 格式：

```bash
hotboard-baidu --format json
```

## 输出格式

Markdown 格式包含标题、热度、链接等信息。
JSON 格式返回结构化数据。
