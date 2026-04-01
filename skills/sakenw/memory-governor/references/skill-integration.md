# Skill Integration

## 目标

让多个 skill 服从同一套记忆规则，但不强迫它们共享同一种实现。

这份文档解决的问题是：

- 多个 skill 都在“写点什么”
- 它们各自有自己的路径和写法
- 但全局上不能各自发明记忆定义

## 核心原则

### 1. 统一 contract

所有 skill 都应共享这些定义：

- 记忆类型
- target classes
- 默认路由
- 升级规则
- 排除规则

### 2. 不统一 implementation

所有 skill 不必统一这些东西：

- 内部函数命名
- 内部目录布局
- 交互方式
- 下游工具适配方式
- 自己的执行流程

### 3. skill 只声明，不越权

每个 skill 可以声明：

- 自己会产出哪些信息类型
- 默认映射到哪些 target classes
- 当前环境里优先使用哪个 adapter
- 哪些信息只应该提炼后再写

每个 skill 不应自行定义：

- 新的全局记忆层
- 新的长期记忆标准
- 与内核冲突的升级规则

## 推荐接入方式

每个会写记忆的 skill，都应该在自己的 `SKILL.md` 或 reference 里明确：

1. 它会产生哪些 memory types
2. 这些类型默认映射到哪些 target classes
3. 当前环境优先使用哪些 adapter
4. 哪些内容绝不能直接写入长期层
5. stateful target 用 append、replace 还是 merge
6. 它依赖 `memory-governor` 的哪些规则

## 建议模板

可以在其他 skill 里用类似这样的声明：

```markdown
## Memory Contract

This skill follows `memory-governor`.

Typical outputs:
- project facts -> `project_facts`
- temporary recovery hints -> `working_buffer`
- reusable workflow lessons -> `reusable_lessons`

This skill does not define its own global memory rules.
```

## 典型对接关系

### `inbox-processor`

- 可以继续做 inbox 分类
- 但“稳定内容”“项目事实”“临时线索”的定义应服从内核

### `record-router`

- 可以继续做 Notion / OmniFocus 流转
- 但不能自行定义“长期记忆”的标准

### `notion-personal`

- 可以继续定义什么适合进 Notion
- 但它定义的是外脑沉淀规则，不是全局记忆规则

### `second-brain-claw`

- 可以继续做捕获、沉淀、执行分流
- 但上游“什么算记忆、写到哪一层”应由 `memory-governor` 约束

## 适配器思路

后续如果进入 Phase 2，可以为各 skill 增加轻量 adapter，而不是重写它们本身。

adapter 的职责：

- 把 skill 的输出映射到标准 memory types
- 把 memory types 映射到 target classes
- 调用统一路由规则
- 标记哪些内容需要提炼，哪些内容只能短存
- 对 stateful target 应遵守 canonical write semantics

## 禁止事项

- 不把 `memory-governor` 变成下游写入总线
- 不要求所有 skill 重构成同一种文件结构
- 不为了一致性而打断已有有效工作流
