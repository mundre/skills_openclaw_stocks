# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- 未来功能规划

---

## [1.0.0] - 2026-03-13

### Added

#### 🎯 核心特性

- ✅ **完整的 9 步开发流程**
  - Step 1: 读 issue（只理解，不改代码）
  - Step 2: 写"5行任务卡"（目标、边界、影响范围、非目标）
  - Step 3: 确定基线版本（从哪个 tag/文件开始改）
  - Step 4: 列改动点（只列具体改动）
  - Step 5: 编码（最小修改）
  - Step 6: 本地验证（4层测试：语法、导入、行为、回归）
  - Step 7: 看 diff（确认没偏题、没改过头）
  - Step 8: 写发布说明（修复项、验证项、未变更项）
  - Step 9: 最后复盘

- ✅ **4 层验证体系**
  - Layer 1: 语法验证（`py_compile`）
  - Layer 2: 导入验证
  - Layer 3: 行为验证（最小样例）
  - Layer 4: 回归验证

- ✅ **15 项验收清单**
  - A. 需求一致性（3项）
  - B. 技术正确性（4项）
  - C. 测试验证（4项）
  - D. 发布质量（4项）

- ✅ **8 条编码纪律**
  1. 先复制旧代码，再局部替换，不要凭记忆重写
  2. 改函数前，先通读函数的输入、输出、副作用
  3. 涉及数据结构变化时，先搜所有使用点
  4. 不要同时改逻辑和风格
  5. 不要在 bug fix 里做重构
  6. 不要修改未被需求要求的行为
  7. 不要在没有验证前说"修好了"
  8. 不要让 release note 超前于实际代码

#### 📝 完整模板

- ✅ **需求澄清模板**
  - 任务类型
  - 问题现象
  - 正确行为
  - 影响范围
  - 非目标

- ✅ **改动设计模板**
  - 目标文件
  - 目标函数
  - 需要修改
  - 不应修改
  - 风险点
  - 验证方式

- ✅ **Commit Message 模板**
- ✅ **Release Note 模板**

#### 📚 文档

- ✅ SKILL.md - 完整的开发标准
- ✅ README.md - 项目介绍
- ✅ CONTRIBUTING.md - 贡献指南
- ✅ CHANGELOG.md - 版本历史
- ✅ docs/ - 详细文档
- ✅ examples/ - 实战示例
- ✅ templates/ - 模板文件

#### 🎓 能力训练

- ✅ 精准改动能力
- ✅ 验证能力
- ✅ 一致性能力
- ✅ 收敛能力

### Changed

- N/A

### Deprecated

- N/A

### Removed

- N/A

### Fixed

- N/A

### Security

- N/A

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-13 | 初始版本发布 |

---

**Format**: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
**Versioning**: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
