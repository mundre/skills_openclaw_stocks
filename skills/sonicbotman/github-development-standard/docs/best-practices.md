# 最佳实践

---

## 8 条编码纪律

### 1. 先复制旧代码，再局部替换，不要凭记忆重写

**❌ 错误做法：**
```python
# 凭记忆重写
def compress(messages):
    # 我记得大概是这个逻辑...
    result = []
    for msg in messages:
        result.append(process(msg))
    return result
```

**✅ 正确做法：**
```python
# 先复制旧代码
def compress(messages):
    # 旧代码（完整复制）
    result = []
    for msg in messages:
        if msg['role'] == 'user':
            result.append(process_user(msg))
        else:
            result.append(process_assistant(msg))
    return result

# 然后局部替换
def compress(messages):
    result = []
    for msg in messages:
        if msg['role'] == 'user':
            result.append(process_user(msg))  # ← 保持不变
        else:
            result.append(process_assistant(msg))
    
    # ← 新增逻辑
    summary = generate_summary(result)
    
    return result
```

---

### 2. 改函数前，先通读函数的输入、输出、副作用

**检查清单：**
```text
【函数】compress(messages)
【输入】messages: List[Dict], 每个 Dict 包含 role, content
【输出】Dict: {summary: str, kept: int, removed: int}
【副作用】
  - 读取文件系统？否
  - 写入文件？是（如果指定 output_file）
  - 调用外部 API？否
【依赖】
  - process_user()
  - process_assistant()
  - generate_summary()
```

**如何通读：**
1. 看函数签名（输入/输出）
2. 看函数内部调用的其他函数
3. 看是否有文件/网络操作
4. 看是否有全局变量依赖

---

### 3. 涉及数据结构变化时，先搜所有使用点

**场景：修改数据结构**

```python
# 修改前
stats = {
    'kept': len(kept),
    'removed': len(removed)
}

# 修改后（新增字段）
stats = {
    'kept': len(kept),
    'removed': len(removed),
    'content_preserved': len(kept_older) + len(kept_recent)  # 新增
}
```

**必须搜索：**
```bash
# 搜索所有使用点
grep -r "stats\[" .
grep -r "stats\." .
grep -r "stats\.get" .
grep -r "stats\[.kept.\]" .
grep -r "stats\[.removed.\]" .
```

**验证：**
- ✅ 所有读取点都能处理新字段
- ✅ 所有写入点都正确设置新字段
- ✅ 序列化/反序列化兼容

---

### 4. 不要同时改逻辑和风格

**❌ 错误做法：**
```python
# 同时改逻辑和风格
-def compress(messages):
+def compress_messages(message_list):  # 改名 + 改逻辑
-    result = []
-    for msg in messages:
-        result.append(process(msg))
-    return result
+    return [process_message(msg) for msg in message_list]  # 列表推导式
```

**问题：**
- 无法判断是改名导致的问题，还是改逻辑导致的问题
- diff 审查困难

**✅ 正确做法：**
```python
# 分两步：先改逻辑，再改风格
# Step 1: 只改逻辑
def compress(messages):
    result = []
    for msg in messages:
-       result.append(process(msg))
+       result.append(process_with_summary(msg))  # 只改逻辑
    return result

# Step 2: 只改风格（单独 commit）
def compress(messages):
-   result = []
-   for msg in messages:
-       result.append(process_with_summary(msg))
-   return result
+   return [process_with_summary(msg) for msg in messages]
```

---

### 5. 不要在 bug fix 里做重构

**场景：修复 Bug #56**

```text
【任务】修复 summary 变量覆盖问题
【非目标】不重构其他函数
```

**❌ 错误做法：**
```python
# 在修复 bug 的同时，顺便重构了 compress() 函数
def compress(messages):
    # 修复 bug
    summary_parts = []
    for msg in messages:
        summary_parts.append(msg['summary'])
    summary = "\n".join(summary_parts)
    
    # 顺便重构（❌）
    stats = Statistics(
        kept=len(kept),
        removed=len(removed)
    )
    
    # 顺便优化（❌）
    if ENABLE_CACHE:
        cache.set(summary, stats)
    
    return summary
```

**问题：**
- 代码审查困难
- 如果出问题，不知道是 bug fix 的问题，还是重构的问题
- 违反最小修改原则

**✅ 正确做法：**
```python
# 只修复 bug，不做任何重构
def compress(messages):
    # 修复 bug
    summary_parts = []
    for msg in messages:
        summary_parts.append(msg['summary'])
    summary = "\n".join(summary_parts)
    
    # 保持原有逻辑不变
    stats = {
        'kept': len(kept),
        'removed': len(removed)
    }
    
    return summary
```

---

### 6. 不要修改未被需求要求的行为

**场景：Issue 说"修复 summary 覆盖问题"**

**❌ 错误做法：**
```python
def compress(messages):
    # 修复 summary 覆盖（✅）
    summary_parts = []
    for msg in messages:
        summary_parts.append(msg['summary'])
    summary = "\n".join(summary_parts)
    
    # 顺便修改输出格式（❌）
-   return summary
+   return f"Summary: {summary}"  # 修改了输出格式
```

**问题：**
- 修改了未被要求的行为
- 可能破坏现有调用方
- 违反最小修改原则

**✅ 正确做法：**
```python
def compress(messages):
    summary_parts = []
    for msg in messages:
        summary_parts.append(msg['summary'])
    summary = "\n".join(summary_parts)
    
-   return summary
+   return summary  # 保持原有输出格式
```

---

### 7. 不要在没有验证前说"修好了"

**❌ 错误做法：**
```python
# 修改代码
summary_parts = []
for msg in messages:
    summary_parts.append(msg['summary'])
summary = "\n".join(summary_parts)

# 直接说"修好了"（❌）
print("✅ 已修复")
```

**问题：**
- 没有验证
- 不知道是否真的修好了
- 可能还有其他问题

**✅ 正确做法：**
```python
# 修改代码
summary_parts = []
for msg in messages:
    summary_parts.append(msg['summary'])
summary = "\n".join(summary_parts)

# 4 层验证
python3 -m py_compile scripts/xxx.py  # Layer 1
python3 -c "from scripts.xxx import compress"  # Layer 2
python3 test_fix.py  # Layer 3
python3 -m pytest tests/  # Layer 4

# 全部通过后才能说"修好了"
print("✅ 已修复并验证")
```

---

### 8. 不要让 release note 超前于实际代码

**场景：Release Note 已经写好了**

**❌ 错误做法：**
```markdown
## v1.2.5 (即将发布)

### 新增功能
- 支持 JSON 输出（❌ 代码还没写）
- 支持并发处理（❌ 代码还没写）
```

**问题：**
- Release note 超前于代码
- 如果代码没写完，发布时会不一致
- 误导用户

**✅ 正确做法：**
```markdown
## v1.2.5 (开发中)

### 已完成
- ✅ 支持 JSON 输出
- ✅ 支持并发处理

### 进行中
- 🔄 性能优化

### 计划中
- 📝 支持 YAML 输出
```

**原则：**
- Release note 只写已经完成的代码
- 未完成的写在 TODO 或 Roadmap
- 发布时确保 Release note 与代码一致

---

## 其他最佳实践

### 1. 改动量预估

| 任务类型 | 预期改动量 | 超过则怀疑 |
|---------|-----------|-----------|
| 修 1 个小 bug | 5–30 行 | > 50 行 |
| 修 1 组相关 bug | 20–80 行 | > 150 行 |
| 小功能新增 | 30–150 行 | > 300 行 |

**如果改动量超过预期：**
1. 停下
2. 检查是否改多了
3. 检查是否夹带了重构
4. 考虑拆分任务

---

### 2. Commit 原则

**一个 commit 只解决一个问题集合**

```bash
# ❌ 一个 commit 包含多个不相关的修改
git commit -m "fix: 修复 bug #56, 顺便优化性能, 重构了 compress()"

# ✅ 分开 commit
git commit -m "fix: 修复 summary 变量覆盖问题 (#56)"
git commit -m "perf: 优化 compress() 性能"
git commit -m "refactor: 重构 compress() 函数"
```

---

### 3. 分支管理

```bash
# 为每个 issue 创建独立分支
git checkout -b fix/issue-56-summary-overwrite

# 修改完成后
git add scripts/xxx_fixed.py
git commit -m "fix: 修复 summary 变量覆盖问题 (#56)"

# 推送到远程
git push origin fix/issue-56-summary-overwrite

# 创建 PR
gh pr create --title "修复 #56: summary 变量覆盖问题" --body "..."
```

---

### 4. 代码审查

**审查自己的代码（diff 审查 3 件事）：**

1. **改动量是否匹配任务规模**
   ```bash
   git diff --stat
   # 判断：改动量是否合理
   ```

2. **是否改到了非目标区域**
   ```bash
   git diff | grep "^+" | grep -v "^+++"
   # 检查每一行，确认都是目标改动
   ```

3. **发布说明是否和 diff 一致**
   - Release note 说的每一项，diff 里都要能找到

---

### 5. 文档同步

**修改代码后，必须同步更新：**
- [ ] README.md（如果有功能变化）
- [ ] CHANGELOG.md
- [ ] 代码注释（如果有接口变化）
- [ ] 使用文档（如果有使用方式变化）

---

### 6. 版本号规范

**遵循 Semantic Versioning：**
- **Major (X.0.0)**: 不兼容的 API 变化
- **Minor (1.Y.0)**: 新增功能，向后兼容
- **Patch (1.0.Z)**: Bug 修复，向后兼容

**示例：**
```text
v1.2.4 → v1.2.5 (Bug 修复)
v1.2.5 → v1.3.0 (新功能)
v1.3.0 → v2.0.0 (重大变更)
```

---

### 7. 回滚计划

**发布前，准备回滚方案：**
```bash
# 记录当前版本
git tag v1.2.4

# 发布新版本
git tag v1.2.5
git push origin v1.2.5

# 如果出问题，立即回滚
git checkout v1.2.4
```

---

## 速查表

| 原则 | 检查项 |
|------|--------|
| 最小修改 | 改动量 < 200 行 |
| 单一职责 | 一个 commit 一个问题 |
| 先验证后说 | 4 层验证通过 |
| 不夹带私货 | 只改 issue 要求的内容 |
| 文档同步 | README + CHANGELOG + 注释 |
| 可回滚 | 记录上一个版本 |

---

**遵守最佳实践，质量保证** 💕
