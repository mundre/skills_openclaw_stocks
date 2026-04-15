---
name: ai-intelligence-report
description: AI情报助手技能包，覆盖模版检索与报告任务场景（创建、查询、章节编辑、版本查询）。
skillcode: ai-intelligence-report
dependencies:
  - cms-auth-skills
---

# AI情报助手 — 索引

本文件提供能力宪章、能力树与按需加载规则。详细参数与流程见各模块 `openapi/` 与 `examples/`。

**当前版本**: v1.6

**能力概览（3 块能力）**：
- `moban`：模版列表检索、模版详情查看、模版新建、模版编辑、模版发布/下架、模版删除
- `task`：任务创建、进度查询、报告详情、任务列表、章节改写、版本历史
- `capability`：能力咨询与边界说明（回答“你能做什么/不能做什么”）

**接口版本**: 所有业务接口统一使用 `https://cwork-api.mediportal.com.cn/ai-report/*` 前缀，鉴权类型按接口文档声明执行（本 skill 当前业务接口均为 `access-token`）。

统一规范：
- 认证与鉴权：`cms-auth-skills/SKILL.md`
- 通用约束：`cms-auth-skills/SKILL.md`

授权依赖：
- 当接口声明需要 `appKey` 或 `access-token` 时，先尝试读取 `cms-auth-skills/SKILL.md`
- 如果已安装，直接按 `cms-auth-skills/SKILL.md` 中的鉴权规则准备对应 `appKey` 或 `access-token`
- 如果未安装，先执行 `npx clawhub@latest install cms-auth-skills --force`
- 如果上面的安装方式不可用，再执行 `npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force`
- 安装完成后，再继续执行需要鉴权的操作

输入完整性规则（强制）：
1. 模版场景至少提供分页信息（`pageNum`、`pageSize`）或明确 `mobanId`
2. 生成报告至少提供 `mobanId`、`taskName`
3. 查询详情或进度需提供 `taskId`
4. 章节改写与版本查询需提供 `questionId`

建议工作流（简版）：
1. 读取 `SKILL.md` 与 `cms-auth-skills/SKILL.md`，明确能力范围、鉴权与安全约束。
2. 识别用户意图并路由模块：`moban`、`task`、`capability`，先打开对应 `api-index.md`。
3. 确认具体接口后，加载对应 endpoint 文档获取入参、出参与 Schema。
4. 补齐用户必需输入；若是能力咨询场景，仅返回标准能力边界，不执行脚本。
5. 参考 `examples/moban/README.md`、`examples/task/README.md`、`examples/capability/README.md` 组织话术与流程。
6. 对有接口的场景执行对应 Python 脚本，输出 JSON 结果并做最小必要信息提取。

脚本使用规则（强制）：
1. 每个 `openapi/moban/*.md`、`openapi/task/*.md` 都必须有对应脚本。
2. 所有业务脚本输出必须为 JSON 格式。
3. 脚本必须可独立命令行执行。
4. 仅允许生产域名与生产协议。
5. 出错重试间隔 1 秒，最多 3 次，禁止无限重试。
6. 严禁虚构工具名或命令（例如 `oracle template query`）。若环境受限，只能说明受限条件与补齐步骤。

能力咨询标准回复（强制）：
1. 当用户问“你可以做什么/你能做什么/你支持哪些操作/你是谁”时，必须路由到 `capability`。
2. `capability` 仅返回本 skill 的真实能力，不得扩展到未定义工具或外部命令。
3. 输出必须包含三段：能做什么、不能做什么、下一步引导（查模版、发起任务、查进度、改章节）。
4. 能力咨询场景禁止执行脚本，也禁止先下“环境变量缺失”的结论。

意图路由与加载规则（强制）：
1. 模版选择与推荐 -> `moban`
2. 报告生成、进度与详情 -> `task`
3. 章节手改与版本追溯 -> `task`
4. 能力咨询与自我介绍 -> `capability`
5. 超出上述范围（如 chat 对话建模版）不在本 skill 范围内

宪章（必须遵守）：
1. 本 skill 仅覆盖 `docs/AI情报agent说明(1).md` 与 `docs/ai情报agent_定义规范.md` 定义场景。
2. 不暴露 token、内部主键等敏感信息。
3. 不猜测缺失参数，必须追问补齐。
4. 不执行越权与危险操作。
5. 章节编辑保存前，必须先向用户展示编辑后的完整内容并等待明确确认。
6. 不杜撰不存在的命令、MCP 工具、CLI 工具或环境变量缺失结论。
7. 鉴权失败时，只能按 `cms-auth-skills/SKILL.md` 的鉴权规则检查，并明确已检查到哪一步、下一步缺什么。

模块路由与能力索引：

| 用户意图（示例） | 模块 | 能力摘要 | 接口文档 | 示例模板 | 脚本 |
|---|---|---|---|---|---|
| 找可用模版、按关键词筛选模版 | `moban` | 模版检索 | `./openapi/moban/api-index.md` | `./examples/moban/README.md` | `./scripts/moban/list-moban.py` |
| 查看模版章节结构 | `moban` | 模版详情 | `./openapi/moban/api-index.md` | `./examples/moban/README.md` | `./scripts/moban/moban-detail.py` |
| 新建模版（定义章节与提示词） | `moban` | 模版新建 | `./openapi/moban/api-index.md` | `./examples/moban/README.md` | `./scripts/moban/create-moban.py` |
| 编辑已有模版（更新结构与提示词） | `moban` | 模版编辑 | `./openapi/moban/api-index.md` | `./examples/moban/README.md` | `./scripts/moban/update-moban.py` |
| 模版发布/下架（控制模版可见状态） | `moban` | 模版状态切换 | `./openapi/moban/api-index.md` | `./examples/moban/README.md` | `./scripts/moban/change-moban-state.py` |
| 删除废弃模版 | `moban` | 模版删除 | `./openapi/moban/api-index.md` | `./examples/moban/README.md` | `./scripts/moban/delete-moban.py` |
| 发起报告任务 | `task` | 创建任务 | `./openapi/task/api-index.md` | `./examples/task/README.md` | `./scripts/task/start-task.py` |
| 查询任务进度和报告详情 | `task` | 进度与详情 | `./openapi/task/api-index.md` | `./examples/task/README.md` | `./scripts/task/check-task.py` |
| 手动修改某个章节并看版本历史 | `task` | 章节编辑 | `./openapi/task/api-index.md` | `./examples/task/README.md` | `./scripts/task/update-question-result.py` |
| 你可以做什么、你能做什么、你是谁 | `capability` | 能力边界说明 | `./openapi/capability/api-index.md` | `./examples/capability/README.md` | `./scripts/capability/README.md` |

能力树（实际目录结构）：
```text
ai-intelligence-report/
├── SKILL.md
├── openapi/
│   ├── moban/
│   │   ├── api-index.md
│   │   ├── list-moban.md
│   │   ├── moban-detail.md
│   │   ├── create-moban.md
│   │   ├── update-moban.md
│   │   ├── change-moban-state.md
│   │   └── delete-moban.md
│   ├── capability/
│   │   └── api-index.md
│   └── task/
│       ├── api-index.md
│       ├── start-task.md
│       ├── check-task.md
│       ├── task-detail-v2.md
│       ├── list-task-by-page.md
│       ├── update-question-result.md
│       └── list-result-version.md
├── examples/
│   ├── moban/README.md
│   ├── capability/README.md
│   └── task/README.md
└── scripts/
    ├── capability/
    │   └── README.md
    ├── moban/
    │   ├── README.md
    │   ├── list-moban.py
    │   ├── moban-detail.py
    │   ├── create-moban.py
    │   ├── update-moban.py
    │   ├── change-moban-state.py
    │   └── delete-moban.py
    └── task/
        ├── README.md
        ├── start-task.py
        ├── check-task.py
        ├── task-detail-v2.py
        ├── list-task-by-page.py
        ├── update-question-result.py
        └── list-result-version.py
```
