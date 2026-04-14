# 荞麦饼 Skills (QiaoMai) v1.0.2

**智能体增强工具：记忆管理、知识图谱、报告生成**

---

## 快速开始

### 安装

```
openclawmp install qiaomai-skills
```

### 使用

```
使用 qiaomai-skills 进行记忆检索
使用 qiaomai-skills 生成报告
使用 qiaomai-skills 构建知识图谱
```

---

## 功能特性

| 模块 | 功能 |
|------|------|
| **记忆系统** | 多层记忆架构，支持向量检索 |
| **知识图谱** | 动态知识图谱构建与查询 |
| **报告生成** | 多格式报告自动生成 |
| **类案检索** | 基于语义的相似案例检索 |

---

## Python API

```python
from qiaomai_skills import Memory, KnowledgeGraph, ReportGenerator

# 记忆检索
memory = Memory()
results = memory.search(query="关键词", top_k=5)

# 知识图谱
kg = KnowledgeGraph()
kg.add_entity(name="实体", type="概念")

# 报告生成
report = ReportGenerator()
report.generate(data=results, format="markdown")
```

---

## 配置说明

### 可选配置

通过环境变量配置（非必需）：

```bash
# 记忆后端选择（默认: memory）
export QIAOMAI_MEMORY_BACKEND="memory"

# 知识图谱后端（默认: memory）
export QIAOMAI_KG_BACKEND="memory"

# 日志级别（默认: info）
export QIAOMAI_LOG_LEVEL="info"
```

### 可选 API 密钥

```bash
# OpenAI API（用于增强功能）
export OPENAI_API_KEY=""

# Perplexity API（用于搜索增强）
export PERPLEXITY_API_KEY=""

# Grok API（用于代码生成）
export GROK_API_KEY=""
```

---

## 依赖说明

### 必需依赖
- Python >= 3.8
- 标准库（无第三方强制依赖）

### 可选依赖
```bash
# 向量检索加速
pip install faiss-cpu

# 图数据库
pip install networkx
```

---

## 项目结构

```
qiaomai-skills/
├── SKILL.md          # 本文件
├── core/             # 核心模块
│   ├── memory.py     # 记忆系统
│   ├── knowledge_graph.py
│   ├── report.py
│   └── case_search.py
└── data/             # 数据存储
```

---

## 安全说明

- 本 Skill 仅通过 OpenClaw 平台标准接口调用
- 不直接执行系统命令
- 不访问用户敏感文件
- 配置存储在用户目录下（`~/.qiaomai/`）

---

## 许可

MIT License

---

**荞麦饼 Skills v1.0.2**  
*度量衡 - 标准源自最佳实践*
