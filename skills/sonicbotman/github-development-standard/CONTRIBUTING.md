# CONTRIBUTING.md

## 🤝 贡献指南

感谢你考虑为 GitHub Development Standard 做出贡献！

---

## 📋 如何贡献

### 1. 报告 Bug

如果你发现了 bug，请 [创建 Issue](https://github.com/SonicBotMan/github-development-standard/issues/new)
包含：
- Bug 描述
- 处现步骤
- 预期行为
- 实际行为

### 2. 建议新功能

如果你有新功能建议
请 [创建 Feature Request](https://github.com/SonicBotMan/github-development-standard/issues/new)
包含：
- 功能描述
- 使用场景
- 预期收益

### 3. 提交代码

1. **Fork 项目**
2. **创建分支** (`git checkout -b feature/AmazingFeature`)
3. **遵守本 Skill 的开发标准**（ irony! 😄）
4. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
5. **推送到分支** (`git push origin feature/AmazingFeature`)
6. **创建 Pull Request**

---

## ✅ 代码规范

### 遵守本 Skill 的标准

**是的，我们用这个 Skill 本身的标准来开发这个 Skill！**

- ✅ 先定义问题，再写代码
- ✅ 最小修改原则
- ✅ 4 层验证
- ✅ Diff 审查
- ✅ 验收清单

### 风格指南

- **Markdown**: 使用标准 Markdown 格式
- **文档**: 中英文双语
- **示例**: 提供可运行的示例
- **注释**: 关键逻辑添加注释

---

## 🧪 测试

### 本 Skill 的测试

```bash
# 验证 SKILL.md 格式
python3 -c "import yaml; yaml.safe_load(open('SKILL.md'))"

# 验证文档完整性
ls README.md docs/ examples/ templates/
```

---

## 📖 文档规范

### 中英文同步

**必须遵守中英文文档同步更新规则：**

1. 修改 `README.md` 后，必须同步修改 `docs/README_EN.md`
2. 修改 `SKILL.md` 后，确保英文版同步
3. 新增示例时，提供中英文说明

---

## 🎯 开发流程

### 使用本 Skill 的标准流程

1. ✅ **读 issue** - 理解需求
2. ✅ **写"5行任务卡"** - 明确目标
3. ✅ **确定基线版本** - 从哪个版本开始
4. ✅ **列改动点** - 明确改动范围
5. ✅ **编码** - 最小修改
6. ✅ **本地验证** - 4 层测试
7. ✅ **看 diff** - 确认没偏题
8. ✅ **写发布说明** - 文档同步
9. ✅ **最后复盘** - 总结经验

---

## 📞 联系方式

- **GitHub Issues**: https://github.com/SonicBotMan/github-development-standard/issues
- **Discord**: [OpenClaw Community](https://discord.gg/clawd)

---

**感谢你的贡献！** 💕
