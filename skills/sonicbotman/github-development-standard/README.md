# GitHub Development Standard Skill

<div align="center">

**完整的 GitHub 项目开发标准流程**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/SonicBotMan/github-development-standard.svg)](https://github.com/SonicBotMan/github-development-standard)

**小白程序员的完整开发/执行/验收方法论**

</div>

---

## 📋 核心理念

> **一句话记住：先定义问题，再定义改法，再写代码，再做验证，最后才发布。**

---

## ✨ 特性

### 🎯 标准化开发流程

- ✅ **9 步开发流程** - 从读 issue 到复盘
- ✅ **4 层验证体系** - 语法/导入/行为/回归
- ✅ **15 项验收清单** - 质量保证
- ✅ **8 条编码纪律** - 避免常见错误

### 📝 完整模板

- ✅ 需求澄清模板
- ✅ 改动设计模板
- ✅ Commit message 模板
- ✅ Release note 模板

### 🔧 实用工具

- ✅ Diff 审查清单
- ✅ 改动量预估表
- ✅ 验收检查表

---

## 🚀 快速开始

### 安装

```bash
# 方式 1: 从 ClawHub 安装（推荐）
clawhub install github-development-standard

# 方式 2: 从 GitHub 克隆
git clone https://github.com/SonicBotMan/github-development-standard.git
cd github-development-standard
```

### 使用

1. **阅读 SKILL.md** - 理解完整流程
2. **使用模板** - 参考 `templates/` 目录
3. **查看示例** - 参考 `examples/` 目录
4. **执行验收** - 使用 `docs/checklist.md`

---

## 📚 文档

- [SKILL.md](./SKILL.md) - 核心技能定义
- [docs/quick-start.md](./docs/quick-start.md) - 快速开始
- [docs/workflow.md](./docs/workflow.md) - 9 步开发流程
- [docs/validation.md](./docs/validation.md) - 4 层验证体系
- [docs/checklist.md](./docs/checklist.md) - 15 项验收清单
- [docs/best-practices.md](./docs/best-practices.md) - 最佳实践

---

## 🎯 适用场景

| 场景 | 是否适用 |
|------|---------|
| Bug 修复 | ✅ 完美适用 |
| 小功能新增 | ✅ 完美适用 |
| 代码重构 | ✅ 完美适用 |
| 兼容性修复 | ✅ 完美适用 |
| 发布收尾 | ✅ 完美适用 |
| 大型项目开发 | ⚠️ 需要适配 |

---

## 📖 核心流程

### 9 步开发流程

```
1. 读 issue → 2. 写任务卡 → 3. 确定基线
     ↓
4. 列改动点 → 5. 编码 → 6. 本地验证
     ↓
7. 看 diff → 8. 写发布说明 → 9. 复盘
```

### 4 层验证体系

```
1. 语法验证 (py_compile)
2. 导入验证 (import)
3. 行为验证 (最小样例)
4. 回归验证 (旧功能)
```

### 15 项验收清单

```
A. 需求一致性 (3 项)
B. 技术正确性 (4 项)
C. 测试验证 (4 项)
D. 发布质量 (4 项)
```

---

## 💡 核心原则

### ✅ 必须做

- ✅ 先复制旧代码，再局部替换
- ✅ 改函数前，先通读输入/输出/副作用
- ✅ 涉及数据结构变化时，先搜所有使用点
- ✅ 一次提交只解决一个问题集合

### ❌ 禁止做

- ❌ 直接跳到第 3 步开始写代码
- ❌ 把"修 bug"当成"顺便重构"
- ❌ 不看旧版本，凭记忆重写
- ❌ 一边修 bug，一边改风格

---

## 📊 改动量预估

| 任务类型 | 预期改动量 |
|---------|-----------|
| 修 1 个小 bug | 5–30 行 |
| 修 1 组相关 bug | 20–80 行 |
| 小功能新增 | 30–150 行 |
| **超过 200 行** | **必须怀疑是否改多了** |

---

## 🔗 相关链接

- **GitHub**: https://github.com/SonicBotMan/github-development-standard
- **ClawHub**: https://clawhub.com/skills/github-development-standard
- **Issue 反馈**: https://github.com/SonicBotMan/github-development-standard/issues

---

## 📝 版本历史

### v1.0.0 (2026-03-13)

- ✅ 初始版本发布
- ✅ 完整的 9 步开发流程
- ✅ 4 层验证体系
- ✅ 15 项验收清单
- ✅ 完整模板和示例

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解详情。

---

## 📄 许可证

[MIT License](./LICENSE)

---

## 🙏 致谢

- 来源: [LobsterPress Issue #88](https://github.com/SonicBotMan/lobster-press/issues/88)
- 灵感: 工程流程最佳实践

---

**Made with ❤️ by SonicBotMan Team**
