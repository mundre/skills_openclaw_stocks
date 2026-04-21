---
name: last30days-zh
description: 通过 AIsa 执行网页、多源或近 30 天研究检索。触发条件：当用户需要搜索、研究、比对或趋势归纳时使用。支持多源检索与结构化输出。
author: AIsa
version: 1.0.0
license: MIT
user-invocable: true
primaryEnv: AISA_API_KEY
requires:
  bins:
  - python3
  - bash
  env:
  - AISA_API_KEY
metadata:
  aisa:
    emoji: 🔎
    requires:
      bins:
      - python3
      - bash
      env:
      - AISA_API_KEY
    primaryEnv: AISA_API_KEY
    compatibility:
    - openclaw
    - claude-code
    - hermes
  openclaw:
    emoji: 🔎
    requires:
      bins:
      - python3
      - bash
      env:
      - AISA_API_KEY
    primaryEnv: AISA_API_KEY
---

# Last30days Zh

通过 AIsa 执行网页、多源或近 30 天研究检索。触发条件：当用户需要搜索、研究、比对或趋势归纳时使用。支持多源检索与结构化输出。

## 适用场景

- 用户需要网页、多源或近 30 天研究检索。
- 用户需要竞品研究、趋势扫描或结构化搜索结果。
- 用户希望用一个技能覆盖多来源检索。

## 高意图工作流

- 先搜索再归纳最近动态。
- 对两个产品做近期对比研究。
- 把多来源结果整理成结构化输出。

## 快速命令

- `python3 scripts/last30days.py --help`
- `bash scripts/run-last30days.sh --help`

## 配置

- 需要 `AISA_API_KEY` 才能访问 AIsa API。
- 使用公开包里的相对 `scripts/` 路径。
- 如果脚本提供显式鉴权参数，优先使用该参数。

## 示例请求

- 研究 OpenAI Agents SDK 最近 30 天讨论
- 比较 OpenClaw 和 Codex 最近的反馈
- 搜索某个品牌最近一周的社区反应

## 边界说明

- 不要把开发测试脚本当成公开功能。
- 不要承诺未实际返回的来源。
- 如果某些来源超时，要按真实情况说明。
