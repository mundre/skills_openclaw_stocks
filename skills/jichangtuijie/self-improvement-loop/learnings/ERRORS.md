# ERRORS.md — 命令 / 集成错误记录

> 由 self-improvement-loop skill 管理。

---

## 模板格式

```markdown
## [ERR-YYYYMMDD-NNN] error
**Logged**: ISO-8601
**Status**: pending | resolved
**Pattern-Key**: <source>.error.<identifier>

### 发生了什么
[具体场景，说清楚在什么情况下、哪个环节出了问题]

### 根因是什么
[为什么会发生，不是表面现象，是结构性原因]

### 下次如何避免
[抽象成一条可操作的原则，可以迁移到类似情况]

*---*
```

---

## 示例（可删除）

## [ERR-20260401-001] error
**Logged**: 2026-04-01T00:00:00+08:00
**Status**: resolved
**Pattern-Key**: tool.hook.keyword.missing

### 发生了什么
Hook 把 "能不能帮我做某事" 当作错误关键词处理了，错误地发送了通知。

### 根因是什么
handler.js 的 ERROR_KEYWORDS 中不应包含 "能不能"，这是功能请求而非错误，但关键词匹配是字面匹配，没有语义判断。

### 下次如何避免
关键词列表要区分"错误信号词"和"功能请求词"，避免字面匹配的误判。

*---*
