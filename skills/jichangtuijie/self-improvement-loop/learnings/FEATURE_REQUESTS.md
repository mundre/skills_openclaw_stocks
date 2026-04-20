# FEATURE_REQUESTS.md — 功能需求

> 由 self-improvement-loop skill 管理。

---

## 模板格式

```markdown
## [FEAT-YYYYMMDD-NNN] feature
**Logged**: ISO-8601
**Status**: pending | resolved
**Pattern-Key**: <source>.feature.<identifier>

### 发生了什么
[缺少什么能力导致什么问题]

### 根因是什么
[为什么这个能力缺失]

### 下次如何避免
[如何确保这个能力被正确实现和验证]

*---*
```

---

## 示例（可删除）

## [FEAT-20260401-001] feature
**Logged**: 2026-04-01T00:00:00+08:00
**Status**: pending
**Pattern-Key**: workflow.auto-commit.conditional

### 发生了什么
auto-commit 脚本每次都提交所有变更，无法选择性忽略 .log 等临时文件，导致 commit 历史噪音大。

### 根因是什么
脚本设计时没有考虑 ignore 机制，没有预留扩展点。

### 下次如何避免
自动化脚本需要预留 ignore/exclude 扩展点，并明确记录哪些文件类型不应进入 commit。

*---*
