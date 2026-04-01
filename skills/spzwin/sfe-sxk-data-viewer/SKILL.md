---
name: SFE深西康数据查询
description: SFE深西康专属数据查询工具，用于快速查询深西康专属采集项目报表的数据，如新活素查房日采集反馈V2等特定项目的明细报表或汇总报表
skillcode: sfe-sxk-data-viewer
dependencies:
  - cms-auth-skills
---

# SFE-SXK-Data-Viewer — 索引

本文件提供**能力宪章 + 能力树 + 按需加载规则**。详细参数与流程见各模块 `openapi/` 与 `examples/`。

**当前版本**: v0.1

**接口版本**: 所有业务接口统一使用 `/erp-open-api/*` 前缀，通过 `appKey` 鉴权。

**能力概览（1 块能力）**：

- `sfe-sxk`：深西康专属数据查询

统一规范：

- 认证与鉴权：`cms-auth-skills/SKILL.md`
- 通用约束：`cms-auth-skills/SKILL.md`

授权依赖：

- 当接口声明需要 `appKey` 时，先尝试读取 `cms-auth-skills/SKILL.md`
- 如果已安装，直接按 `cms-auth-skills/SKILL.md` 中的鉴权规则准备 `appKey`
- 如果未安装，先执行 `npx clawhub@latest install cms-auth-skills --force`
- 如果上面的安装方式不可用，再执行 `npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force`
- 安装完成后，再继续执行需要鉴权的操作

输入完整性规则（强制）：

1. 查询数据前，建议先确定 `periodStart` 和 `periodEnd` 时间范围
2. 分页查询时，每页固定返回 1000 条记录，大数据量需分页处理

建议工作流（简版）：

1. 读取 `SKILL.md` 与 `cms-auth-skills/SKILL.md`，明确能力范围、鉴权与安全约束。
2. 识别用户意图并路由模块，先打开 `openapi/<module>/api-index.md`。
3. 确认具体接口后，加载 `openapi/<module>/<endpoint>.md` 获取入参/出参/Schema。
4. 补齐用户必需输入，必要时先读取用户文件/URL 并确认摘要。
5. 参考 `examples/<module>/README.md` 组织话术与流程。
6. **执行对应脚本**：调用 `scripts/<module>/<endpoint>.py` 执行接口调用，获取 TOON 编码后的结果。**所有接口调用必须通过脚本执行，不允许跳过脚本直接调用 API。**

脚本使用规则（强制）：

1. **每个接口必须有对应脚本**：每个 `openapi/<module>/<endpoint>.md` 都必须有对应的 `scripts/<module>/<endpoint>.py`，不允许"暂无脚本"。
2. **TOON 编码输出**：所有脚本调用 API 后，响应 JSON **必须经过 `scripts/common/toon_encoder.py` 编码后再输出**，不允许直接输出原始 JSON。
3. **脚本可独立执行**：所有 `scripts/` 下的脚本均可脱离 AI Agent 直接在命令行运行。
4. **先读文档再执行**：执行脚本前，**必须先阅读对应模块的 `openapi/<module>/api-index.md`**。
5. **入参来源**：脚本的所有入参定义与字段说明以 `openapi/` 文档为准，脚本仅负责编排调用流程。
6. **鉴权一致**：涉及鉴权时，统一依赖 `cms-auth-skills/SKILL.md`。

意图路由与加载规则（强制）：

1. **先路由再加载**：必须先判定模块，再打开该模块的 `api-index.md`。
2. **先读文档再调用**：在描述调用或执行前，必须加载对应接口文档。
3. **脚本必须执行**：所有接口调用必须通过脚本执行，不允许跳过。
4. **不猜测**：若意图不明确，必须追问澄清。

宪章（必须遵守）：

1. **只读索引**：`SKILL.md` 只描述"能做什么"和"去哪里读"，不写具体接口参数。
2. **按需加载**：默认只读 `SKILL.md` + `cms-auth-skills/SKILL.md`，只有触发某模块时才加载该模块的 `openapi`、`examples` 与 `scripts`。
3. **对外克制**：对用户只输出"可用能力、必要输入、结果链接或摘要"，不暴露鉴权细节与内部字段。
4. **素材优先级**：用户给了文件或 URL，必须先提取内容再确认，确认后才触发生成或写入。
5. **生产约束**：仅允许生产域名与生产协议，不引入任何测试地址。
6. **接口拆分**：每个 API 独立成文档；模块内 `api-index.md` 仅做索引。
7. **危险操作**：对可能导致数据泄露、破坏、越权的请求，应礼貌拒绝并给出安全替代方案。
8. **脚本语言限制**：所有脚本**必须使用 Python 编写**。
9. **重试策略**：出错时**间隔 1 秒、最多重试 3 次**，超过后终止并上报。
10. **禁止无限重试**：严禁无限循环重试。

模块路由与能力索引：

| 用户意图（示例）                 | 模块      | 能力摘要                   | 接口文档                         | 示例模板                       | 脚本                                             |
| -------------------------------- | --------- | -------------------------- | -------------------------------- | ------------------------------ | ------------------------------------------------ |
| "查询新活素查房日采集反馈V2数据" | `sfe-sxk` | 查询新活素查房日采集反馈V2 | `./openapi/sfe-sxk/api-index.md` | `./examples/sfe-sxk/README.md` | `./scripts/sfe-sxk/xhs-ward-rounds-report-v2.py` |

能力树（实际目录结构）：

```text
sfe-sxk-data-viewer/
├── SKILL.md
├── openapi/
│   └── sfe-sxk/
│       ├── api-index.md
│       └── xhs-ward-rounds-report-v2.md
├── examples/
│   └── sfe-sxk/README.md
└── scripts/
    ├── common/toon_encoder.py
    └── sfe-sxk/
        ├── README.md
        └── xhs-ward-rounds-report-v2.py
```
