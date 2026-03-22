# Knowledge Base Skill

**Version**: v1.0.0
**Repository**: https://github.com/ThomasLiu/knowledge-base-skill

---

## 触发条件

当用户提到以下关键词时触发：

- "加入知识库" / "存到 KB" / "存入知识库"
- "knowledge base" / "知识库" / "KB"
- "记得这个" / "保存上下文" / "记忆"
- "检索知识库" / "查一下 KB"
- "OpenClaw/GitHub/HuggingFace 源码同步"

## 功能

### 1. Collect - 存储

```bash
kb store --title "标题" --content "内容" --source "manual"
```

### 2. Retrieve - 检索

```bash
kb search --query "关键词"
kb retrieve --topic-key "entry-key"
```

### 3. Recall - 对话前自动检索

在 `before_agent_start` hook 中自动调用，检索与当前对话相关的知识。

### 4. Capture - 对话后自动存储

在 `after_turn` hook 中自动调用，判断并存储重要内容。

## 使用方式

### 存储信息

```
用户: 把这个配置加入知识库
Agent: 使用 kb store 命令存储
```

### 检索信息

```
用户: 查一下知识库里关于 OpenClaw 的内容
Agent: 使用 kb search 查询并返回结果
```

### 自动 Hook

需要在 OpenClaw 配置 hooks：

```bash
# before_agent_start
hooks before_agent_start --context "用户消息"

# after_turn  
hooks after_turn --user "用户消息" --agent "Agent回复"
```

## 脚本列表

| 脚本 | 功能 |
|------|------|
| `scripts/storage.sh` | 核心存储 API |
| `scripts/retriever.sh` | 检索 + recall/capture |
| `scripts/hooks.sh` | OpenClaw Hooks 集成 |
| `scripts/lifecycle.sh` | 生命周期管理 |

## 依赖

- bash
- sqlite3
- python3

## 配置

```bash
# 私有 KB（默认）
export KNOWLEDGE_DB="$HOME/.openclaw/agents/current/knowledge.db"

# 共享 KB
export KNOWLEDGE_KB_MODE="shared"
export KNOWLEDGE_DB_SHARED="$HOME/.openclaw/shared/knowledge-bases/<kb-name>/knowledge.db"
```
