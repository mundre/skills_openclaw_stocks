# Hui-Yi README / 使用速查

Hui-Yi 是一个**冷记忆（cold memory）管理 skill**。

它不是拿来记当天杂事的，也不是拿来堆所有资料的。
它的目标很单纯：

**把低频但高价值、以后还可能用得上的信息，整理进 `memory/cold/`，并在真正需要时再召回。**

---

## 一句话判断：什么时候用？

用 Hui-Yi 的典型场景：

- 你想把某条经验、决策、背景知识长期留档
- 你想问“之前这个问题我们是怎么处理的？”
- 你想定期清理、合并、压缩冷记忆
- 你想把近期 daily notes 里真正值得长期保留的内容冷却下来

**不要用 Hui-Yi 的场景：**

- 今天刚发生的临时事项 → `memory/YYYY-MM-DD.md`
- 高频个人/项目背景 → `MEMORY.md`
- 工具路径、设备名、环境坑点 → `TOOLS.md`
- 新错误、新纠正、还没验证过的 lesson → `.learnings/`

一句话：

**近期的放 warm，长期低频的才放 cold。**

---

## 冷记忆目录长什么样

```text
memory/
├── cold/
│   ├── index.md
│   ├── tags.json
│   ├── retrieval-log.md
│   ├── _template.md
│   ├── <topic>.md
│   └── <project>/<topic>.md   # 可选项目命名空间
├── heartbeat-state.json

skills/hui-yi/
├── SKILL.md
├── README.md
├── manifest.yaml
├── references/
└── scripts/
```

其中最重要的是：

- `memory/cold/index.md`：人眼快速扫的总索引
- `memory/cold/tags.json`：结构化检索元数据
- `memory/cold/_template.md`：新 note 模板
- `memory/cold/retrieval-log.md`：记录召回是否有用

---

## 四个最常用脚本

这些脚本现在是 **Python 版，Linux / macOS / Windows 通用**。

### 1) 搜索冷记忆

```bash
python skills/hui-yi/scripts/search.py <keyword>
```

例子：

```bash
python skills/hui-yi/scripts/search.py heartbeat
python skills/hui-yi/scripts/search.py json
```

用途：
- 在 `index.md` 和 `tags.json` 里搜索关键词
- 适合“我记得以前写过这类经验，但忘了 note 名字”这种场景

---

### 2) 重建 index / tags

```bash
python skills/hui-yi/scripts/rebuild.py
```

用途：
- 从 `memory/cold/*.md` note 文件重新生成 `index.md` 和 `tags.json`
- 同时刷新 `heartbeat-state.json` 里的 `coldMemory.lastIndexRefresh`
- 当 index / tags 不一致、格式坏了、或者你手工改过 note 后，用这个同步

**注意：**
这是“元数据重建器”，不是内容生成器。
它会以 note 文件内容为准重建索引。

---

### 3) 查看 cooling 状态

```bash
python skills/hui-yi/scripts/cool.py status
```

用途：
- 查看 `heartbeat-state.json` 里的 `coldMemory` 状态
- 看上次 scan / archive / index refresh / summary 是什么

如果要按 `lastArchive` 增量扫描当前待 cooling 的 daily notes：

```bash
python skills/hui-yi/scripts/cool.py scan
```

如果一轮 cooling 做完，要记录结果：

```bash
python skills/hui-yi/scripts/cool.py done <reviewed> <archived> <merged>
```

例子：

```bash
python skills/hui-yi/scripts/cool.py done 5 2 1
```

意思是：
- reviewed 5 条 daily notes
- archived 2 条新冷记忆
- merged 1 条进旧 note

---

### 4) 做 confidence 老化检查

```bash
python skills/hui-yi/scripts/decay.py --dry-run
```

用途：
- 看哪些 note 因为 `last_verified` 太久没更新，应该降低 confidence

正式执行：

```bash
python skills/hui-yi/scripts/decay.py
```

规则：
- `high` 超过 90 天 → `medium`
- `medium` 超过 90 天 → `low`
- `low` 超过 180 天 → 标记为 stale 候选

建议先 dry-run，再决定要不要正式跑。

---

## 最常见工作流

### 工作流 A：我想找以前的经验

1. 先看当前对话 / recent memory / `MEMORY.md`
2. 还不够，再搜冷记忆：

```bash
python skills/hui-yi/scripts/search.py <keyword>
```

3. 找到相关 note 后，只读最相关的 1-3 条
4. 用总结，不要把 raw note 整块倒出来

---

### 工作流 B：我想新增一条冷记忆

1. 先判断它到底是不是 cold：
   - 30 天后还可能有用？
   - 是可复用经验、稳定事实、长期背景吗？
2. 先查 `index.md`，看是不是已有 note
3. 没有就复制 `_template.md` 新建
4. 写完后执行：

```bash
python skills/hui-yi/scripts/rebuild.py
```

这样 `index.md` 和 `tags.json` 会同步更新。

---

### 工作流 C：定期 cooling daily notes

1. 扫描：

```bash
python skills/hui-yi/scripts/cool.py scan
```

2. 从 recent daily notes 中挑真正值得长期保存的内容
3. 路由到正确文件：
   - 高频背景 → `MEMORY.md`
   - 工具/路径 → `TOOLS.md`
   - 新错误 → `.learnings/`
   - 低频长期知识 → `memory/cold/`
4. 更新/新建 cold note
5. 重建：

```bash
python skills/hui-yi/scripts/rebuild.py
```

6. 记录本次 cooling：

```bash
python skills/hui-yi/scripts/cool.py done <reviewed> <archived> <merged>
```

---

## 一条好 cold note 应该长什么样

至少应该有：

- `TL;DR`
- `Memory type`
- `Semantic context`
- `Triggers`
- `Use this when`
- `Confidence`
- `Last verified`
- `Related tags`

经验类 note 最值钱的通常是：

- `Decisions / lessons`
- 为什么这么做
- 什么不要做

不是把过程流水账全倒进去。

---

## 设计原则

Hui-Yi 的核心不是“记得越多越好”，而是：

**archive less, but archive better**

也就是：
- 少存一点
- 但要存得更准、更能复用、更方便以后召回

冷记忆不是仓库，是压缩过的长期经验层。

---

## 注意事项

- 不要把 secrets、token、密码写进 cold memory
- 不要把当天临时状态塞进 cold memory
- 不要重复建一堆相似 note，优先 merge
- 不要在没必要时把整个冷记忆翻出来通读
- `index.md` 是主检索面，`tags.json` 是辅助检索面
- helper 脚本是辅助，不是硬依赖；没脚本时也可以手工维护

---

## 文件说明：去哪看更详细的内容

- `SKILL.md`：完整行为规则
- `references/cold-memory-schema.md`：note / index / tags 的格式规范
- `references/examples.md`：完整示例
- `references/heartbeat-cooling-playbook.md`：定期 cooling 流程

---

## 当前推荐命令速查

```bash
python skills/hui-yi/scripts/search.py <keyword>
python skills/hui-yi/scripts/rebuild.py
python skills/hui-yi/scripts/cool.py status
python skills/hui-yi/scripts/cool.py scan
python skills/hui-yi/scripts/cool.py done <reviewed> <archived> <merged>
python skills/hui-yi/scripts/decay.py --dry-run
```

如果你只记 3 条，就记这 3 条：

```bash
python skills/hui-yi/scripts/search.py <keyword>
python skills/hui-yi/scripts/rebuild.py
python skills/hui-yi/scripts/cool.py status
```
