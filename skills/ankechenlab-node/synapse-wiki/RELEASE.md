# Synapse Skills v1.0.0 发布说明

**发布日期**: 2026-04-08
**版本**: v1.0.0 (初始公开发布)

---

## 概述

Synapse Skills 是基于 Karpathy LLM Wiki 模式的知识库管理系统 + Pipeline 代码交付工作流的 OpenClaw Skill 封装。

包含两个独立但可协同工作的技能：
- **synapse-wiki** — 持久化 Wiki 构建 + 增量知识积累
- **synapse-code** — Pipeline + Synapse 整合工作流

---

## 安装方式

### 方式 1：使用安装脚本（推荐）

```bash
# 安装 synapse-wiki
cd ~/path/to/synapse-wiki
./install.sh

# 安装 synapse-code
cd ~/path/to/synapse-code
./install.sh
```

### 方式 2：手动复制

```bash
# 安装 synapse-wiki
cp -r synapse-wiki ~/.claude/skills/

# 安装 synapse-code
cp -r synapse-code ~/.claude/skills/
```

### 方式 3：使用 OpenClaw 安装（如果有 .skill 文件）

```bash
claude skill install synapse-wiki.skill
claude skill install synapse-code.skill
```

---

## 快速开始

### synapse-wiki

```bash
# 1. 初始化新知识库
/synapse-wiki init ~/my-wiki "AI 学习知识库"

# 2. 摄取资料
/synapse-wiki ingest ~/my-wiki raw/articles/article.md

# 3. 查询知识
/synapse-wiki query ~/my-wiki "LLM Wiki 的核心思想"

# 4. 健康检查
/synapse-wiki lint ~/my-wiki
```

### synapse-code

```bash
# 1. 初始化项目
/synapse-code init ~/my-project

# 2. 运行 Pipeline
/synapse-code run my-project "实现登录功能"

# 3. 检查状态
/synapse-code status ~/my-project
```

---

## 配置说明

### synapse-code 配置

编辑 `~/.claude/skills/synapse-code/config.json`:

```json
{
  "pipeline": {
    "workspace": "~/pipeline-workspace",
    "enabled": true,
    "auto_log": true
  },
  "paths": {
    "pipeline_script": "~/pipeline-workspace/pipeline.py",
    "pipeline_summary": "/tmp/pipeline_summary.json"
  },
  "gitnexus": {
    "enabled": true
  }
}
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SKIP_GITNEXUS_CHECK` | 跳过 GitNexus 检查 | `false` |

---

## 依赖要求

### synapse-wiki
- Python 3.x ✓

### synapse-code
- Python 3.x ✓
- GitNexus CLI（可选）: `npm install -g gitnexus`
- Pipeline workspace（需要用户自行配置）

---

## 主要特性

### 三层架构

```
<wiki-root>/
├── raw/       ← 原始资料层（LLM 只读）
├── wiki/      ← Wiki 知识层（LLM 编写）
└── outputs/   ← 探索产出层
```

### 核心操作

| 操作 | 说明 |
|------|------|
| **Ingest** | 摄取源文件创建 Wiki 页面 |
| **Query** | 查询知识并综合答案 |
| **Lint** | 健康检查（死链接、孤立页面等） |

---

## 测试报告

### 基线测试

| 技能 | 测试项 | 结果 |
|------|--------|------|
| synapse-wiki | init, ingest, lint, query | **4/4 通过** |
| synapse-code | init_syntax, infer, status | **3/3 通过** |

### 测试方式

```bash
# synapse-wiki
cd ~/.claude/skills/synapse-wiki
python3 tests/baseline_test.py

# synapse-code
cd ~/.claude/skills/synapse-code
python3 tests/baseline_test.py
```

---

## 升级路径

### 从 v0.1.0 升级到 v1.0.0

v1.0.0 引入了配置化支持，如果你有旧版本：

1. 备份现有配置（如果有）
2. 重新安装：`./install.sh`
3. 复制 `config.template.json` 为 `config.json`
4. 根据需要修改配置

---

## 已知问题

1. **synapse-code 依赖外部 Pipeline**
   - 需要用户自行配置 `~/pipeline-workspace/`
   - 解决：未来版本将提供独立的 Pipeline 安装包

2. **GitNexus 为可选依赖**
   - 某些功能（影响分析）需要 GitNexus
   - 解决：安装 `npm install -g gitnexus`

---

## 反馈与支持

- GitHub Issues: （待添加）
- 文档：详见 `README.md`
- 开发日记：详见 `DEVELOPMENT_JOURNAL.md`

---

## 贡献者

- Initial work: Anke
- Based on: [Karpathy llm-wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

---

## 许可证

MIT License
