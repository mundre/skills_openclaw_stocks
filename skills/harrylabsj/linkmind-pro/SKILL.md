---
name: linkmind
description: LinkMind 知识连接引擎 Phase 2 - 本地化知识中枢 CLI 工具，支持 storage adapter 抽象层和 OpenAI-compatible embedding provider。
---

# LinkMind 知识连接引擎 (Phase 2)

LinkMind 是一个本地化知识连接引擎，将异构内容沉淀为统一知识单元，建立可解释的节点连接网络，并支持带证据的查询回答。

## Phase 2 新增功能

- **Storage Adapter 抽象层**：`JsonStorageAdapter`（默认，保持兼容）+ `SqliteStorageAdapter`（基于 better-sqlite3）
- **Embedding Provider 抽象层**：`MockProvider`（离线测试）+ `OpenAICompatibleProvider`（接入 OpenAI/vLLM/Ollama）
- **向量相似度召回**：余弦相似度 ranker，与关键词召回结果合并去重
- **渐进升级**：Phase 1 JSON 方案完全兼容，无需迁移

## 核心功能

- **摄入 (ingest)**: 读取本地文本文件，切分为语义友好的段落片段，抽取概念节点，建立片段-概念、片段-片段邻接连接
- **查询 (query)**: 支持关键词/概念查询 + 向量相似度召回，返回答案摘要、证据片段列表、相关概念节点、统计概览
- **状态 (status)**: 查看当前工作空间统计信息
- **重置 (reset)**: 清空工作空间

## 架构模块

| 模块 | 职责 | 状态 |
|------|------|------|
| `storage-adapters/` | StorageAdapter 接口 + JSON/SQLite 双实现 | ✅ Phase 2 |
| `embedding-providers/` | EmbeddingProvider 接口 + Mock/OpenAI 双实现 | ✅ Phase 2 |
| `retriever` | 关键词召回 + 向量召回双层检索，余弦相似度 ranker | ✅ Phase 2 |
| `unit-builder` | 文档切分为 fragment，抽取 fragment.conceptNames | ✅ MVP |
| `link-builder` | fragment↔concept、fragment↔fragment 邻接连接 | ✅ MVP |
| `answer-composer` | 组装 answer + evidence + relatedConcepts | ✅ MVP |
| `ingest-normalizer` | 原始文件标准化为 Document | ✅ MVP |
| `guardrails` | 空查询、空结果边界处理 | ✅ MVP |

## 技术栈

- 零外部依赖（pure Node.js built-ins）
- 本地 JSON 文件存储（`data/workspace.json`）
- 可选 SQLite 存储（`better-sqlite3`）
- 数据模型: Document → Fragment → Concept + LinkEdge

## 安装与运行

```bash
cd skills/linkmind

# 构建
npm run build

# 运行 CLI
node dist/index.js --help
```

## 使用方法

### 摄入文档
```bash
node dist/index.js ingest --file examples/sample-note.md --title "我的笔记" --sourceType note
```

### 查询知识
```bash
node dist/index.js query --q "知识连接"
node dist/index.js query --q "knowledge" --limit 5
```

### 查看状态
```bash
node dist/index.js status
```

### 重置工作空间
```bash
node dist/index.js reset
```

## 存储适配器 (Storage Adapter)

### JsonStorageAdapter（默认）
- 数据存储在 `data/workspace.json`
- 完全向后兼容 Phase 1
- 零配置开箱即用

### SqliteStorageAdapter
- 需要安装：`npm install better-sqlite3`
- 数据存储在 `data/db.sqlite`
- 支持事务批量写入，性能更高

```js
import { createStorageAdapter } from './src/storage-adapters/index.js';

const adapter = createStorageAdapter('sqlite');
await adapter.init();
await adapter.saveDocument({ id: 'doc_1', title: 'Test', ... });
```

## Embedding Provider

### MockProvider（默认，离线可用）
```js
import { createEmbeddingProvider } from './src/embedding-providers/index.js';

const provider = createEmbeddingProvider('mock', { dimension: 1536 });
const [vec] = await provider.embed(['hello world']);
```

### OpenAICompatibleProvider
```js
const provider = createEmbeddingProvider('openai', {
  baseURL: 'https://api.openai.com/v1',   // 或 vLLM/Ollama 地址
  apiKey: 'sk-xxx',
  model: 'text-embedding-3-small',
  dimension: 1536
});
const vectors = await provider.embed(['hello', 'world']);
```

## 检索流程 (Retriever)

查询时使用双层召回：

1. **关键词召回**（keyword）：基于 `normalizeConcept` + concept 名称匹配
2. **向量召回**（vector）：余弦相似度（可选，需配置 embedding provider）
3. **合并去重**：取最高分，结果标记 `source: 'keyword' | 'vector' | 'hybrid'`

```js
import { retrieve } from './src/retriever.js';

const results = await retrieve({
  fragments,
  query: 'knowledge graph',
  embeddingProvider: mockProvider,  // 传 null 则仅关键词召回
  limit: 10
});
// results: [{ fragmentId, documentId, documentTitle, score, text, source }]
```

## 数据模型

### Document
```json
{
  "id": "doc_xxxxx",
  "type": "document",
  "title": "我的笔记",
  "sourceType": "note",
  "sourceUri": "/path/to/file.md",
  "importedAt": "2026-04-04T...",
  "status": "active"
}
```

### Fragment
```json
{
  "id": "frag_xxxxx",
  "type": "fragment",
  "documentId": "doc_xxxxx",
  "index": 0,
  "text": "LinkMind 是...",
  "summary": "LinkMind 是...",
  "conceptNames": ["linkmind", "知识连接", "知识中枢"]
}
```

### Concept
```json
{
  "id": "concept_xxxxx",
  "type": "concept",
  "name": "LinkMind",
  "normalizedName": "linkmind",
  "salience": 0.67
}
```

### LinkEdge
```json
{
  "id": "link_xxxxx",
  "type": "mentions",
  "fromId": "frag_xxxxx",
  "fromType": "fragment",
  "toId": "concept_xxxxx",
  "toType": "concept",
  "score": 2
}
```

## 自测方法

```bash
cd skills/linkmind
node tests/smoke-test.js
```

## 目录结构

```
skills/linkmind/
├── SKILL.md
├── README.md
├── package.json
├── src/
│   ├── index.js              # CLI 入口
│   ├── retriever.js          # 双层检索
│   ├── storage-adapters/
│   │   ├── StorageAdapter.js     # 接口契约
│   │   ├── JsonStorageAdapter.js # JSON 文件实现
│   │   ├── SqliteStorageAdapter.js # SQLite 实现
│   │   └── index.js              # Factory
│   ├── embedding-providers/
│   │   ├── EmbeddingProvider.js        # 接口契约
│   │   ├── MockProvider.js             # 随机向量（测试用）
│   │   ├── OpenAICompatibleProvider.js # OpenAI 兼容 API
│   │   └── index.js                    # Factory
│   └── utils/
│       └── nlp.js             # normalizeConcept 工具
├── dist/
│   └── index.js
├── data/
│   └── workspace.json
├── tests/
│   └── smoke-test.js         # Phase 2 覆盖 38 项检查
└── examples/
    └── sample-note.md
```

## Phase 2 交付清单

- [x] StorageAdapter 接口契约
- [x] JsonStorageAdapter（向后兼容）
- [x] SqliteStorageAdapter（基于 better-sqlite3）
- [x] EmbeddingProvider 接口契约
- [x] MockProvider（确定性随机、缓存、L2归一化）
- [x] OpenAICompatibleProvider（支持自定义 baseURL/apiKey/model）
- [x] retriever.js：关键词+向量双层召回 + 余弦相似度 ranker + merge 去重
- [x] smoke-test.js Phase 2 全覆盖（38项检查全部通过）
- [x] SKILL.md 更新

## 待后续实现

- ⏳ index.js 接入 adapter 层（DI 注入，支持 --storage=json|sqlite）
- ⏳ 向量批量预计算 + 离线向量存储
- ⏳ 图数据库存储（Neo4j）
- ⏳ Web/开放 API 接口
- ⏳ 多种来源接入（飞书、Notion、URL 抓取）
- ⏳ 证据冲突检测
