# 4 层验证体系详解

---

## 概述

**4 层验证**是确保代码质量的核心方法：

| 层级 | 名称 | 验证内容 | 耗时 |
|------|------|----------|------|
| Layer 1 | 语法验证 | 代码能否编译/解析 | 1 秒 |
| Layer 2 | 导入验证 | 模块能否正确导入 | 1 秒 |
| Layer 3 | 行为验证 | 核心功能是否正常 | 5-30 分钟 |
| Layer 4 | 回归验证 | 旧功能是否仍然正常 | 5-30 分钟 |

**⚠️ 所有 4 层必须全部通过，才能发布。**

---

## Layer 1: 语法验证

### 目标
确保代码没有语法错误。

### Python

```bash
# 方式 1: py_compile
python3 -m py_compile scripts/xxx.py
# 无输出 = 通过

# 方式 2: ast 检查
python3 -c "import ast; ast.parse(open('scripts/xxx.py').read())"
# 无输出 = 通过
```

### Shell

```bash
# 语法检查
bash -n scripts/xxx.sh
# 无输出 = 通过
```

### 常见错误

```python
# ❌ 括号不匹配
def func(
    pass

# ❌ 缩进错误
if True:
print("error")

# ❌ 字符串未闭合
s = "hello
```

### 要点
- ✅ 每次保存后立即检查
- ✅ 无输出才是通过
- ❌ 不要跳过这一步

---

## Layer 2: 导入验证

### 目标
确保模块可以被正确导入。

### 单模块

```bash
python3 -c "from scripts.xxx import FuncName; print('OK')"
# 输出：OK
```

### 完整导入

```bash
python3 -c "import scripts.xxx; print(dir(scripts.xxx))"
# 输出模块的所有公开函数/类
```

### 常见错误

```python
# ❌ 循环导入
# a.py
from b import func_b

# b.py
from a import func_a

# ❌ 导入不存在的模块
import non_existent_module

# ❌ 相对导入错误
from . import sibling_module
```

### 要点
- ✅ 验证所有公开接口
- ✅ 检查是否有 ImportError
- ❌ 不要假设导入一定成功

---

## Layer 3: 行为验证（核心）

### 目标
验证修复/新增的功能是否正常工作。

### 最小样例原则

**构造最小输入，验证核心行为：**

```python
# test_fix.py
import sys
sys.path.insert(0, '.')
from scripts.xxx_fixed import compress
import tempfile
import json

# 1. 构造最小样例
test_data = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "World"}
]

# 2. 写入临时文件
with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
    for msg in test_data:
        f.write(json.dumps(msg) + '\n')
    input_file = f.name

output_file = input_file.replace('.jsonl', '_compressed.jsonl')

# 3. 调用函数
try:
    compress(input_file, output_file, strategy='light', dry_run=True)
    print("✅ 行为验证通过")
except Exception as e:
    print(f"❌ 行为验证失败: {e}")
    raise

# 4. 验证输出
with open(output_file, 'r') as f:
    result = json.loads(f.read())
    
assert 'summary' in result, "缺少 summary 字段"
assert len(result['summary']) > 0, "summary 为空"
print("✅ 输出验证通过")
```

### 验证步骤

1. **构造最小输入**
   - 足够小（2-10 行）
   - 覆盖修复点
   - 边界情况

2. **执行函数**
   - 使用修复后的代码
   - 观察输出

3. **验证输出**
   - 检查关键字段
   - 检查数据类型
   - 检查边界情况

### 验证清单

```text
☐ 输入最小样例，输出不为空
☐ 输入最小样例，关键字段存在
☐ 输入边界值，不崩溃
☐ 输入错误值，有合理错误提示
```

### 要点
- ✅ 最小样例原则
- ✅ 覆盖修复点
- ✅ 验证输出格式
- ❌ 不要用复杂样例测试
- ❌ 不要跳过这一层

---

## Layer 4: 回归验证

### 目标
确保旧功能仍然正常工作。

### 自动化测试

```bash
# 运行已有测试套件
python3 -m pytest tests/

# 或使用 unittest
python3 -m unittest discover tests/
```

### 手动测试

```text
【手动测试清单】
☐ 核心流程 A 仍然正常
☐ 核心流程 B 仍然正常
☐ 边界情况 C 仍然正常
☐ 错误处理 D 仍然正常
```

### 示例

```python
# test_regression.py
import sys
sys.path.insert(0, '.')
from scripts.xxx_fixed import compress

def test_old_feature():
    """测试旧功能：压缩单个会话"""
    result = compress("test.jsonl", "test_out.jsonl")
    assert result['status'] == 'success'
    assert result['ratio'] > 0
    print("✅ 回归测试通过")

def test_cli():
    """测试 CLI：参数解析"""
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/xxx_fixed.py", "--help"],
        capture_output=True
    )
    assert result.returncode == 0
    print("✅ CLI 回归测试通过")

if __name__ == "__main__":
    test_old_feature()
    test_cli()
```

### 要点
- ✅ 运行所有已有测试
- ✅ 手动测试核心流程
- ✅ 检查边界情况
- ❌ 不要假设旧功能一定正常

---

## 完整示例：4 层验证流程

```bash
#!/bin/bash
# verify.sh - 完整的 4 层验证

echo "=== Layer 1: 语法验证 ==="
python3 -m py_compile scripts/xxx_fixed.py
if [ $? -eq 0 ]; then
    echo "✅ Layer 1 通过"
else
    echo "❌ Layer 1 失败"
    exit 1
fi

echo "=== Layer 2: 导入验证 ==="
python3 -c "from scripts.xxx_fixed import compress; print('OK')"
if [ $? -eq 0 ]; then
    echo "✅ Layer 2 通过"
else
    echo "❌ Layer 2 失败"
    exit 1
fi

echo "=== Layer 3: 行为验证 ==="
python3 test_fix.py
if [ $? -eq 0 ]; then
    echo "✅ Layer 3 通过"
else
    echo "❌ Layer 3 失败"
    exit 1
fi

echo "=== Layer 4: 回归验证 ==="
python3 -m pytest tests/ -v
if [ $? -eq 0 ]; then
    echo "✅ Layer 4 通过"
else
    echo "❌ Layer 4 失败"
    exit 1
fi

echo "=== 所有 4 层验证通过 ✅ ==="
```

---

## 常见错误

### 错误 1: 跳过 Layer 1

```bash
# ❌ 直接运行
python3 scripts/xxx.py

# 问题：语法错误在运行时才暴露
```

**正确做法：**
```bash
# ✅ 先检查语法
python3 -m py_compile scripts/xxx.py
python3 scripts/xxx.py
```

### 错误 2: 跳过 Layer 3

```bash
# ❌ 只测试导入
python3 -c "from scripts.xxx import func"

# 问题：导入成功不代表功能正确
```

**正确做法：**
```bash
# ✅ 构造最小样例测试
python3 test_fix.py
```

### 错误 3: Layer 3 用复杂样例

```python
# ❌ 复杂样例（1000 行）
test_data = load_large_file("big_test.jsonl")  # 1000 行
result = compress(test_data)

# 问题：
# 1. 难以定位问题
# 2. 测试慢
# 3. 输出难以验证
```

**正确做法：**
```python
# ✅ 最小样例（2-10 行）
test_data = [
    {"role": "user", "content": "A"},
    {"role": "assistant", "content": "B"}
]
result = compress(test_data)
assert len(result['summary']) > 0
```

---

## 速查表

| 层级 | 命令 | 通过标志 | 失败处理 |
|------|------|----------|----------|
| Layer 1 | `python3 -m py_compile xxx.py` | 无输出 | 修复语法错误 |
| Layer 2 | `python3 -c "import xxx"` | 输出 OK | 修复导入错误 |
| Layer 3 | `python3 test_fix.py` | 输出 ✅ | 修复逻辑错误 |
| Layer 4 | `pytest tests/` | 全部通过 | 检查副作用 |

---

**4 层验证，层层把关** 💕
