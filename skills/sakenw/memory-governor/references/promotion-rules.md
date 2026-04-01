# Promotion Rules

## 总原则

升级不是复制粘贴，而是提炼。

只有当一条信息已经从“发生过什么”变成“以后怎么判断 / 怎么做”时，才值得升格。

## 规则

### daily → MEMORY

满足任意两个条件时，才考虑从 `memory/YYYY-MM-DD.md` 升到 `MEMORY.md`：

- 两周后大概率仍然有效
- 在多个任务里重复出现
- 会影响未来判断或协作方式
- 已经从事件变成稳定模式

### correction → self-improving/memory

当一条纠错已经能抽象为可复用原则时，升级为通用执行经验。

例子：

- 纠错：别写客服腔
- 规则：默认直接、简洁、有判断

### self-improving/* → AGENTS

当经验会改变启动流程、协作边界、默认路由时，升级到 `AGENTS.md`。

### self-improving/* → TOOLS

当经验主要约束工具、命令、平台格式、配置时，升级到 `TOOLS.md`。

### self-improving/* → SOUL

当经验改变长期表达风格、判断方式、人格边界时，升级到 `SOUL.md`。

### session-state / working-buffer → 其他层

这两层默认不能直接升格。  
必须先提炼成稳定事实或复用规则，再进入长期层。

capture 阶段遇到歧义时，先看 [routing-precedence.md](routing-precedence.md)。

## 禁止升级的情况

- 原始长日志直接升到长期层
- 未验证的猜测升到长期层
- 临时恢复线索直接升到 `MEMORY.md`
- 项目局部事实直接升到全局规则
