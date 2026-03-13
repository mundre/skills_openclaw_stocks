# Release Note 模板

---

## 版本信息

```text
版本号：vX.Y.Z
发布日期：YYYY-MM-DD
发布类型：
☐ Major（重大更新）
☐ Minor（功能新增）
☐ Patch（Bug 修复）
☐ Hotfix（紧急修复）
```

---

## 修复内容（如果是 Patch/Hotfix）

### Bug 修复

```markdown
### 修复内容

- **Bug #1**: <简短描述>
  - 问题：<问题描述>
  - 影响：<影响范围>
  - 修复：<修复方案>
  - 位置：<文件/函数>

- **Bug #2**: <简短描述>
  - 问题：<问题描述>
  - 影响：<影响范围>
  - 修复：<修复方案>
  - 位置：<文件/函数>
```

---

## 新增功能（如果是 Minor）

### 功能新增

```markdown
### 新增内容

- **Feature #1**: <功能名称>
  - 描述：<功能描述>
  - 用途：<使用场景>
  - 配置：<配置方式>
  - 示例：<使用示例>

- **Feature #2**: <功能名称>
  ...
```

---

## 重大变更（如果是 Major）

### 重大变更

```markdown
### Breaking Changes

- **变更 1**: <变更描述>
  - 旧版本：<旧行为>
  - 新版本：<新行为>
  - 迁移指南：<如何升级>

- **变更 2**: <变更描述>
  ...
```

---

## 影响范围

```markdown
## 影响范围

### 修改文件
- scripts/xxx.py - <修改说明>
- docs/xxx.md - <修改说明>

### 修改函数
- compress() - <修改说明>
- _generate_summary() - <修改说明>

### 新增文件
- scripts/new_feature.py - <说明>
- docs/new_feature.md - <说明>
```

---

## 验证结果

```markdown
## 验证

### 自动化测试
- ✅ 语法检查通过（py_compile）
- ✅ 导入检查通过（python -c）
- ✅ 单元测试通过（pytest tests/）
- ✅ 覆盖率 > 80%

### 手动验证
- ✅ 最小样例验证通过
- ✅ 核心流程验证通过
- ✅ 边界情况验证通过
- ✅ 回归测试通过

### Diff 审查
- ✅ 改动量匹配任务规模
- ✅ 没有非目标区域修改
- ✅ Release note 与代码一致
```

---

## 已知不变更

```markdown
## 已知不变更

### 不修改的文件
- scripts/other.py
- tests/legacy.py

### 不修改的功能
- CLI 参数
- 摘要生成逻辑
- 序列化格式
```

---

## 升级指南

```markdown
## 升级指南

### 方式 1：直接替换

\`\`\`bash
# 下载最新版本
git pull origin main

# 或下载 release
wget https://github.com/OWNER/REPO/archive/vX.Y.Z.tar.gz

# 替换文件
cp scripts/xxx.py /path/to/your/scripts/
\`\`\`

### 方式 2：Docker

\`\`\`bash
docker pull username/repo:latest
docker-compose up -d
\`\`\`

### 配置修改

如果有配置变更，在这里说明：

\`\`\`yaml
# 新增配置项
new_feature:
  enabled: true
  option: value
\`\`\`
```

---

## 已知问题

```markdown
## 已知问题

### Issue #XX
- **描述**：<问题描述>
- **影响**：<影响范围>
- **临时方案**：<临时解决方案>
- **计划**：<计划何时修复>

### Issue #YY
...
```

---

## 下一步计划

```markdown
## 下一步计划

### v(X+1).Y.Z
- [ ] <计划 1>
- [ ] <计划 2>

### v(X+2).Y.Z
- [ ] <长期计划>
```

---

## 致谢

```markdown
## 致谢

感谢以下贡献者：
- @user1 - <贡献内容>
- @user2 - <贡献内容>

感谢社区反馈：
- Issue #XX - <反馈内容>
```

---

## 完整示例

```markdown
## v1.2.4-hotfix1 (2026-03-11)

### 修复内容

- **Bug #56**: 修复 summary 变量覆盖问题
  - 问题：compress() 循环中 summary 变量被覆盖
  - 影响：只保留最后一个工具的摘要，前面的全部丢失
  - 修复：改用列表收集，最后合并
  - 位置：scripts/lobster_press_v124.py compress() 函数

### 影响范围

**修改文件：**
- scripts/lobster_press_v124.py

**修改函数：**
- compress() (第 145-155 行)

**新增文件：**
- 无

### 验证

- ✅ 语法检查通过
- ✅ 导入检查通过
- ✅ 最小样例验证通过
- ✅ 回归测试通过

### 已知不变更

- ❌ 不修改 CLI 参数
- ❌ 不修改其他统计逻辑
- ❌ 不修改摘要生成函数
- ❌ 不新增文件

### 升级指南

\`\`\`bash
# 直接替换
cp scripts/lobster_press_v124.py scripts/lobster_press_v152.py

# 无需其他配置修改
\`\`\`

### 已知问题

暂无

### 致谢

- Issue #56 - @reporter 反馈问题
```

---

**参考**：
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
