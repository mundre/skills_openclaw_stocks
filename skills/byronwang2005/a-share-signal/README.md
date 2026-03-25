# A-Share Signal

`a-share-signal` 是一个用于分析A股交易机会的 Skill。本Skill中涉及的理论方法，完全来自一名作者线下认识的一线游资，其在妖股捕捉方面有极强的实战经验。

> 相关内容仅用于研究交流与策略参考，不构成任何投资建议。

## 功能简介

- 基于筹码分布、三周期共振、优化 KDJ、威科夫与缠论等框架分析 A 股
- 结合用户自定义评分规则，输出结构化判断、参与条件、缠论+威科夫约束下的目标价与应对方案
- 默认采用 `mx-skills -> AkShare/BaoShare` 的数据获取优先级
- 限流视为常见现象，同一数据源内至少换 3 种方法尝试后，才能回退到下一个数据源
- 输出结果必须标注数据来源；任何未获取或不完整的数据都需要明确警告用户
- 适合把近期行情数据快速转成更清晰的交易决策参考

## 数据源建议

推荐优先安装并配置 `mx-skills`，这样可以更方便地获取个股行情、财务、公告、研报等数据。若用户尚未安装 `mx-skills`，应在实际取数前先建议其去官网获取并配置 key。

- 下载地址: [ai.eastmoney.com/mxClaw](https://ai.eastmoney.com/mxClaw)
- 使用顺序: `mx-skills` 优先，若未安装或无法覆盖所需字段，再回退到 `AkShare/BaoShare`

## 同步与开源

本仓库会随本人真实使用的skills库持续实时更新，并同步开源发布在：

- GitHub: [byronwang2005/a-share-signal](https://github.com/byronwang2005/a-share-signal)
- ClawHub: [clawhub.ai/byronwang2005/a-share-signal](https://clawhub.ai/byronwang2005/a-share-signal)

## 兼容性

本Skill兼容主流 Agent / Coding Agent 生态，包括但不限于：

- OpenClaw
- Claude Code
- Codex
- OpenCode
