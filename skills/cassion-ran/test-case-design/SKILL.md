---
name: test-case-design
description: This skill should be used when generating test cases, writing test cases, designing test cases, supplementing exception scenarios and boundary values, designing complex interaction test cases, outputting standardized test cases, compatibility testing, adaptation testing, API testing, security testing, UI visual testing, mobile/App/mini-program/H5/desktop/PC Web testing, linkage testing, or routing testing. Only focuses on writing test cases, does not involve test plans, test strategies, or test automation scripts.
---

## 加载指引

> **逐步披露原则**：先读 SKILL.md 获取全貌，再按场景关键词加载对应 references 文件。无需一次加载全部。

## 输出要求

### 输出规则
- **未指明平台** → 只生成通用测试用例（功能、安全、接口、联动、路由、UI、兼容性）
- **指明平台** → 生成通用用例 + 该平台专项用例

### 输出格式
- 默认格式：Excel 表格
- 标准用例结构：用例编号 + 测试标题 + 测试类型 + 功能模块 + 用例级别 + 预置条件 + 测试步骤 + 预期结果

## 能力边界
✅ 可生成：功能测试、边界值、异常场景、接口、安全意识、UI视觉用例
❌ 不可生成：测试方案、测试策略、测试计划、渗透测试执行、漏洞扫描、性能压测、自动化脚本

## 指令映射表

| 关键词触发 | 加载文件 | 备注 |
|-----------|---------|------|
| "测试用例"、"写用例"、"设计用例"（通用） | references/core-capabilities/common-testing.md + references/templates/common-rules.md | large file: common-testing.md |
| "移动端测试"、"App 测试" | references/core-capabilities/common-testing.md + references/platform/mobile-app.md + references/templates/common-rules.md | large file: common-testing.md |
| "小程序测试" | references/core-capabilities/common-testing.md + references/platform/mini-program.md + references/templates/common-rules.md | large file: common-testing.md |
| "移动 Web 测试"、"H5 测试" | references/core-capabilities/common-testing.md + references/platform/mobile-web.md + references/templates/common-rules.md | large file: common-testing.md |
| "桌面端测试"、"桌面应用测试" | references/core-capabilities/common-testing.md + references/platform/desktop.md + references/templates/common-rules.md | large file: common-testing.md |
| "PC Web 测试"、"Web 端测试" | references/core-capabilities/common-testing.md + references/platform/pc-web.md + references/templates/common-rules.md | large file: common-testing.md, pc-web.md |
| "联动测试" | references/core-capabilities/common-testing.md (第三部分) | large file: grep "## 第三部分" |
| "路由测试"、"跳转测试" | references/core-capabilities/common-testing.md (第四部分) | large file: grep "## 第四部分" |
| "UI 测试"、"视觉测试"、"界面测试" | references/core-capabilities/common-testing.md (第五部分) | large file: grep "## 第五部分" |
| "接口测试"、"API 测试" | references/core-capabilities/common-testing.md (第六部分) | large file: grep "## 第六部分" |
| "安全测试" | references/core-capabilities/common-testing.md (第七部分) | large file: grep "## 第七部分" |
| "边界值"、"异常场景" | references/core-capabilities/common-testing.md (第一部分) | grep "## 第一部分" |
| "兼容性测试"、"适配测试" | references/core-capabilities/common-testing.md (兼容性) | grep "兼容性" |
| "可访问性测试" | references/platform/mobile-app.md + references/checklists/mobile-app-checklist.md | grep "可访问性" |
| "功能测试" | references/examples/common.md (一、功能测试) | large file: grep "一、功能测试" |
| 检查清单（通用） | references/checklists/common-checklist.md | |
| 检查清单（平台专项） | references/checklists/mobile-app-checklist.md / mobile-web-checklist.md / pc-web-checklist.md / desktop-checklist.md / mini-program-checklist.md | |
| 示例参考 | references/examples/common.md + references/examples/{platform}.md | large file: examples/common.md |

## 文件结构

> **注意**：本 skill 无 scripts/ 和 assets/ 目录，所有内容均通过 references/ 提供。

```
references/
├── templates/               # 模板规则（已整合）
│   └── common-rules.md       # 用例模板+测试类型+优先级+编号
├── core-capabilities/       # 通用测试能力（已整合）
│   └── common-testing.md    # 所有通用测试能力
├── platform/               # 平台专项用例（保持分开）
│   ├── mobile-app.md        # 移动端App
│   ├── mobile-web.md        # 移动端Web
│   ├── pc-web.md           # PC Web
│   ├── desktop.md          # 桌面端
│   └── mini-program.md     # 小程序
├── checklists/             # 检查清单
│   ├── common-checklist.md # 通用检查清单
│   ├── mobile-app-checklist.md
│   ├── mobile-web-checklist.md
│   ├── pc-web-checklist.md
│   ├── desktop-checklist.md
│   └── mini-program-checklist.md
└── examples/              # 示例参考
    ├── common.md          # 通用测试示例（功能/联动/路由/UI/接口/安全）
    ├── mobile-app.md      # 移动端App示例
    ├── mobile-web.md      # 移动端Web示例
    ├── pc-web.md         # PC Web示例
    ├── desktop.md        # 桌面端示例
    └── mini-program.md   # 小程序示例
```
