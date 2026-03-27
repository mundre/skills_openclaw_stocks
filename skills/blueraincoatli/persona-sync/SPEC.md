# Persona Sync — SPEC.md

## Concept

Persona Sync keeps your AI companion's persona — SOUL.md, IDENTITY.md, MEMORY.md, memory logs — synchronized across all your OpenClaw instances, using a private GitHub repo as the storage backend.

---

## File Structure

```
~/.openclaw/persona-store/   # Local persona store (git working dir)
├── .gitauth                 # GitHub auth (username=xxx,token=TOKEN)
├── .git/                    # Git repo
├── sync.log                 # Operation log
├── state.json               # Sync state (version, timestamps)
└── memory.jsonl             # Structured memory log (append-only)
```

Persona source files (SOUL.md, IDENTITY.md, etc.) live in the OpenClaw workspace directory, managed by the user.

---

## Authentication

**Important: Token is never embedded in URLs** — stored securely via `git credential helper`.

`.gitauth` format:
```
username=YOUR_GITHUB_USERNAME,token=YOUR_PERSONAL_ACCESS_TOKEN
```

Security notes:
- Token stored in `~/.git-credentials` (mode 0600), never in `.git/config`
- Token never appears in git log or git config
- PAT should have minimal scope: `repo` scope only

---

## memory.jsonl Format

```jsonl
{"ts":"2026-03-26T22:00:00+08:00","agent":"main","type":"memory","content":"和Ray讨论了盒马自动化","tags":["shopping","hema"]}
{"ts":"2026-03-26T22:05:00+08:00","agent":"main","type":"interaction","role":"user","content":"今天想做什么菜"}
{"ts":"2026-03-26T22:05:30+08:00","agent":"main","type":"interaction","role":"assistant","content":"红烧肉不错"}
```

Field description:
- `ts` — ISO 8601 timestamp
- `agent` — Source agent ID
- `type` — `memory` or `interaction`
- `role` — `user` or `assistant` (only for interaction type)
- `content` — Content text
- `tags` — Optional tag array

---

## state.json Format

```json
{
  "last_sync": "2026-03-26T22:00:00+08:00",
  "last_entry": "2026-03-26T22:05:30+08:00",
  "version": 42,
  "agents": ["main", "quas", "rao2"]
}
```

---

## Workflow

### On startup (pull)
1. `git pull --ff-only` (fallback to `pull --rebase` if ff-only fails)
2. Read all entries from `memory.jsonl`
3. Rebuild current persona from entries

### After conversation (push)
1. Append memory entry to `memory.jsonl`
2. Update `state.json` (timestamp, version)
3. `git add .` → `git commit` → `git push`

### Conflict Resolution
- Non-fast-forward push → auto `pull --rebase` → push again

---

## Dependencies

- `git`
- `python3` (cross-platform) or `bash` (Linux only)
- GitHub PAT (stored in `~/.openclaw/persona-store/.gitauth`)

---

## Security Principles

1. Token never in remote URL or .git/config
2. Use `git credential helper store` for credential storage
3. `.gitauth` file permissions: 0600
4. PAT scope limited to `repo` (private repos only)

---

---

# Persona Sync — 技术规格

## 概念

Persona Sync 让 AI 伙伴的人格（SOUL.md / IDENTITY.md / MEMORY.md / memory 日志）在多个 OpenClaw 实例之间同步，通过 GitHub 私有仓库作为存储后端。

---

## 文件结构

```
~/.openclaw/persona-store/   # 本地人格仓库（git 工作区）
├── .gitauth                 # GitHub 认证信息（username=xxx,token=TOKEN）
├── .git/                    # Git 仓库
├── sync.log                 # 操作日志
├── state.json               # 同步状态（版本号、时间戳）
└── memory.jsonl             # 结构化记忆流水（append-only）
```

人格源文件（SOUL.md、IDENTITY.md 等）实际存储在 OpenClaw workspace 目录，由用户自行管理。

---

## 认证

**重要：Token 不内嵌在 URL 中**，而是通过 `git credential helper` 安全存储。

`.gitauth` 格式：
```
username=YOUR_GITHUB_USERNAME,token=YOUR_PERSONAL_ACCESS_TOKEN
```

安全说明：
- Token 存储在 `~/.git-credentials`（mode 0600），不在 `.git/config` 中
- Token 不会写入 git log 或 git config
- 建议 PAT 设置最小权限：仅私有仓库读写（`repo` 范围）

---

## memory.jsonl 格式

```jsonl
{"ts":"2026-03-26T22:00:00+08:00","agent":"main","type":"memory","content":"和Ray讨论了盒马自动化","tags":["shopping","hema"]}
{"ts":"2026-03-26T22:05:00+08:00","agent":"main","type":"interaction","role":"user","content":"今天想做什么菜"}
{"ts":"2026-03-26T22:05:30+08:00","agent":"main","type":"interaction","role":"assistant","content":"红烧肉不错"}
```

字段说明：
- `ts` — ISO 8601 时间戳
- `agent` — 来源 agent ID
- `type` — `memory`（记忆）或 `interaction`（对话）
- `role` — `user` 或 `assistant`（仅 interaction 类型）
- `content` — 内容文本
- `tags` — 可选标签数组

---

## state.json 格式

```json
{
  "last_sync": "2026-03-26T22:00:00+08:00",
  "last_entry": "2026-03-26T22:05:30+08:00",
  "version": 42,
  "agents": ["main", "quas", "rao2"]
}
```

---

## 工作流程

### 启动时（pull）
1. `git pull --ff-only`（若失败则 `pull --rebase`）
2. 读取 `memory.jsonl` 所有 entry
3. 根据 entry 重建当前人格数据

### 对话后（push）
1. 将本次对话的 memory entry 追加到 `memory.jsonl`
2. 更新 `state.json`（时间戳、版本号）
3. `git add .` → `git commit` → `git push`

### 冲突处理
- 若 push 报 non-fast-forward：自动 `pull --rebase` → 再 `push`

---

## 依赖

- `git`
- `python3`（跨平台版）或 `bash`（Linux 版）
- GitHub Personal Access Token（存于 `~/.openclaw/persona-store/.gitauth`）

---

## 安全原则

1. Token 不写入 remote URL，不写入 `.git/config`
2. 使用 `git credential helper store` 存储凭证
3. `.gitauth` 文件权限 0600
4. PAT 建议限制为私有仓库最小权限（`repo` scope）
