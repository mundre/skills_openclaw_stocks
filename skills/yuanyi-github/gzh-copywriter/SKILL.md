---
name: gzh-copywriter
description: 为公众号内容创作打造的文章生成工具，基于全网超过1000条爆款文章，精准总结相关的热门文章的结构、风格、行文等，提炼核心流量密码与创作要点，高效产出爆款文章。
dependency:
  python:
    - requests>=2.28.0
---

# 公众号爆款内容分析与文案生成

## 使用说明（入口）

本技能的完整执行规范已抽离到引用文档，不在本文件直接展开。

在执行任务前，必须先读取并严格遵循：

- `references/usage_and_trigger.md`（自我介绍、触发场景、任务目标）
- `references/workflow.md`（完整任务流程与创作规范）
- `references/output_template.md`（输出模板与禁止项）
- `references/gzh_trend_data_format.md`（接口数据结构说明）

## 强制要求

- 禁止跳过引用文档中的任一步骤与校验项。
- 爆款数据仅允许通过脚本接口获取，禁止使用其他来源替代核心分析数据。
- 脚本调用统一使用：`scripts/fetch_gzh_trends.py`。
