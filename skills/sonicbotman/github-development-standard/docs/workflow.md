# 9 步开发流程详解

---

## Step 1: 读 Issue（只理解，不改代码）

### 目标
- 理解问题
- 明确需求
- 不做任何假设

### 要点
- ✅ 仔细阅读 issue 描述
- ✅ 理解问题现象
- ✅ 理解预期行为
- ❌ 不要凭记忆猜测
- ❌ 不要急着看代码

### 示例

```text
Issue #56: summary 变量覆盖问题

问题：
- compress() 循环中 summary 变量被覆盖
- 只保留最后一个工具的摘要
- 前面的全部丢失

预期：
- 所有工具的摘要都要保留
- 合并输出
```

---

## Step 2: 写"5行任务卡"

### 模板

```text
【任务类型】Bug 修复 / 功能新增 / 重构 / 兼容性修复
【目标】一句话描述这次修复/新增的内容
【边界】只修改哪些文件/函数
【非目标】明确不打算改的内容
【影响范围】受影响的模块/功能
```

### 要点
- ✅ 目标明确
- ✅ 边界清晰
- ✅ 非目标明确
- ❌ 不要模糊表述
- ❌ 不要说"顺便"

### 示例

```text
【任务类型】Bug 修复
【目标】修复 compress() 中 summary 变量覆盖问题
【边界】只修改 scripts/xxx.py 的 compress() 函数
【非目标】不修改 CLI、不重构其他函数、不新增文件
【影响范围】compress() 函数、输出显示
```

---

## Step 3: 确定基线版本

### 命令

```bash
# 查看可用版本
git tag | sort -V | tail -5

# 基于 release 版本开始
git checkout v1.2.4

# 创建新文件（避免直接修改原文件）
cp scripts/xxx.py scripts/xxx_fixed.py
```

### 要点
- ✅ 从官方 release 开始
- ✅ 创建新文件（如 xxx_fixed.py）
- ✅ 确认基线版本号
- ❌ 不要从"本地改动了一半"的版本继续
- ❌ 不要凭记忆重写

### 验证

```bash
# 确认当前版本
git describe --tags
# 输出：v1.2.4

# 检查文件是否存在
ls -la scripts/xxx_fixed.py
```

---

## Step 4: 列改动点

### 模板

```text
【改动点 1】
位置：scripts/xxx.py 第 XX 行
修改前：<old code>
修改后：<new code>
原因：<为什么这样改>

【改动点 2】
位置：scripts/xxx.py 第 YY 行
修改前：<old code>
修改后：<new code>
原因：<为什么这样改>
```

### 要点
- ✅ 只列具体改动
- ✅ 说明修改原因
- ✅ 预估改动量
- ❌ 不要说"重构"、"优化"等模糊词
- ❌ 不要列非目标改动

### 示例

```text
【改动点 1】
位置：scripts/xxx_fixed.py 第 145 行
修改前：summary = tool['summary']
修改后：summary_parts.append(tool['summary'])
原因：避免覆盖，改用列表收集

【改动点 2】
位置：scripts/xxx_fixed.py 第 150 行
修改前：print(summary)
修改后：summary = "\n".join(summary_parts); print(summary)
原因：合并列表为字符串后输出

【预估改动量】8-12 行
```

---

## Step 5: 编码（最小修改）

### 8 条编码纪律

1. **先复制旧代码，再局部替换，不要凭记忆重写**
2. **改函数前，先通读函数的输入、输出、副作用**
3. **涉及数据结构变化时，先搜所有使用点**
4. **不要同时改逻辑和风格**
5. **不要在 bug fix 里做重构**
6. **不要修改未被需求要求的行为**
7. **不要在没有验证前说"修好了"**
8. **不要让 release note 超前于实际代码**

### 流程

```python
# 1. 复制旧代码
def compress(input_file, output_file):
    # 旧代码...
    for tool in tools:
        summary = tool['summary']  # ← 问题代码
    print(summary)

# 2. 修改
def compress(input_file, output_file):
    # 旧代码...
    summary_parts = []  # ← 新增
    for tool in tools:
        summary_parts.append(tool['summary'])  # ← 修改
    summary = "\n".join(summary_parts)  # ← 新增
    print(summary)
```

### 要点
- ✅ 最小修改原则
- ✅ 保留原有结构
- ✅ 复用已有变量
- ❌ 不要重写整个函数
- ❌ 不要改代码风格

---

## Step 6: 本地验证（4 层测试）

### Layer 1: 语法验证

```bash
python3 -m py_compile scripts/xxx_fixed.py
# 无输出 = 通过
```

### Layer 2: 导入验证

```bash
python3 -c "from scripts.xxx_fixed import compress; print('OK')"
# 输出：OK
```

### Layer 3: 行为验证

```python
# 构造最小样例
test_data = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "World"}
]

# 调用
result = compress(test_data)

# 验证
assert 'summary' in result
assert len(result['summary']) > 0
```

### Layer 4: 回归验证

```bash
# 运行已有测试
python3 -m pytest tests/

# 手动测试核心流程
python3 scripts/xxx_fixed.py test.jsonl -o /tmp/test.jsonl
```

### 要点
- ✅ 必须通过 4 层验证
- ✅ 每层都要有输出
- ❌ 不要跳过任何一层

---

## Step 7: 看 diff

### 3 件事

#### 1. 改动量是否匹配任务规模

| 任务类型 | 预期改动量 |
|---------|-----------|
| 修 1 个小 bug | 5–30 行 |
| 修 1 组相关 bug | 20–80 行 |
| 小功能新增 | 30–150 行 |
| **超过 200 行** | **必须怀疑是否改多了** |

```bash
git diff --stat scripts/xxx_fixed.py
# 输出：1 file changed, 8 insertions(+), 1 deletion(-)
# 判断：8 行，符合预期
```

#### 2. 是否改到了非目标区域

```bash
git diff scripts/xxx_fixed.py | grep "^+" | grep -v "^+++"
# 检查每一行，确认都是目标改动
```

#### 3. 发布说明是否和 diff 一致

```bash
# release note 说"修复了 summary 覆盖问题"
# diff 里必须能找到对应修改
```

---

## Step 8: 写发布说明

### Commit Message 模板

```
fix: 修复 summary 变量覆盖问题

问题：
- compress() 循环中 summary 变量被覆盖
- 只保留最后一个工具的摘要

修复：
- 改用 summary_parts 列表收集
- 循环结束后合并为字符串

影响范围：
- scripts/xxx_fixed.py compress() 函数
- 第 145-155 行

验证：
- ✅ 语法检查通过
- ✅ 导入检查通过
- ✅ 行为验证通过
- ✅ 回归测试通过

非修改：
- 不修改 CLI 参数
- 不修改其他函数
- 不修改 parser 结构

Closes #56
```

### Release Note 模板

```markdown
## v1.2.4-hotfix1 (2026-03-13)

### 修复内容

- **Bug #56**: 修复 summary 变量覆盖问题
  - 问题：compress() 循环中 summary 变量被覆盖
  - 修复：改用列表收集，最后合并
  - 位置：scripts/xxx_fixed.py compress() 函数

### 影响范围

- scripts/xxx_fixed.py
- compress() 函数（第 145-155 行）

### 验证

- ✅ 语法检查通过
- ✅ 导入检查通过
- ✅ 行为验证通过
- ✅ 回归测试通过

### 已知不变更

- ❌ 不修改 CLI 参数
- ❌ 不修改其他统计逻辑
- ❌ 不新增文件
```

---

## Step 9: 最后复盘

### 复盘模板

```text
### 做得好的地方
1. ...
2. ...

### 可以改进的地方
1. ...
2. ...

### 学到的经验
1. ...
2. ...
```

### 示例

```text
### 做得好的地方
1. ✅ 最小修改 - 只改了 9 行代码
2. ✅ 目标明确 - 只修 Bug #56，没有夹带私货
3. ✅ 验证完整 - 4 层验证全部通过

### 可以改进的地方
1. ⚠️ 测试用例 - 可以添加单元测试
2. ⚠️ 代码注释 - 可以添加注释说明

### 学到的经验
1. 变量覆盖很隐蔽 - 在循环中赋值同一变量容易出错
2. 列表收集更安全 - 用 append() 避免 overwriting
```

---

## 📊 流程检查表

| 步骤 | 检查项 | 状态 |
|------|--------|------|
| 1 | 我理解了 issue 描述 | ☐ |
| 2 | 我写了"5行任务卡" | ☐ |
| 3 | 我确定了基线版本 | ☐ |
| 4 | 我列出了具体改动点 | ☐ |
| 5 | 我遵守了 8 条编码纪律 | ☐ |
| 6 | 我通过了 4 层验证 | ☐ |
| 7 | 我检查了 diff（3件事） | ☐ |
| 8 | 我写了清晰的发布说明 | ☐ |
| 9 | 我完成了复盘 | ☐ |

---

**遵守流程，质量保证** 💕
