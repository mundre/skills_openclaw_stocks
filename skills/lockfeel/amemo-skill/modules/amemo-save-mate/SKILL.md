---
name: amemo-save-mate
description: amemo 保存 AI 助手记忆模块，更新/追加长期记忆。
---

# amemo-save-mate — 保存助手记忆

## 接口信息

- **路由**: POST https://skill.amemo.cn/save-mate
- **Bean**: MateBean
- **Content-Type**: application/json

## 请求参数

> **注意**：服务端要求所有字段必须存在。`userToken` 和 `mateMemory` 必填且有值。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userToken | str | **是** | 用户登录凭证 |
| mateMemory | str | **是** | 要保存的记忆内容（不能为空） |

## 请求示例

```bash
# 保存记忆
curl -X POST https://skill.amemo.cn/save-mate \
  -H "Content-Type: application/json" \
  -d '{"userToken": "<token>", "mateMemory": "用户喜欢 Python，常用 FastAPI 框架"}'
```

## 响应示例

```json
{"code": 200, "desc": "success", "data": "..."}
```

## 注意事项

- `userToken` 和 `mateMemory` 都必须有值，不能为空
- 与 `amemo-init-mate` 不同，此接口用于追加/更新记忆，而非重置
- 必须携带有效的 userToken

## 执行流程（由主模块调度）

### 执行步骤

```
1. 识别触发词（保存永久记忆/永久记住/记住这个）
    ↓
2. 检查 userToken 是否存在
    ├── 无 token → 引导登录流程
    ↓
3. 确认 MEMORY.md 是否已更新
    ├── 未更新 → 提示用户先完成编辑
    ↓
4. 读取 memory/MEMORY.md 文件内容
    ↓
5. 调用 POST /save-mate 接口
    ↓
6. 返回保存结果
```

### 保存触发场景

**场景一：用户刚说完"永久记住 XXX"**
```
用户：永久记住我喜欢喝美式咖啡
    ↓
系统识别触发词，等待用户确认或自动补充到 MEMORY.md
    ↓
用户完成 MEMORY.md 编辑（如通过其他工具）
    ↓
用户说"保存永久记忆"
    ↓
系统读取 MEMORY.md 内容
    ↓
调用 /save-mate 同步到服务器
```

**场景二：用户主动保存**
```
用户：保存永久记忆
    ↓
系统读取当前 MEMORY.md 内容
    ↓
调用 /save-mate 同步到服务器
```

### 成功提示模板

```
✅ 永久记忆已保存！

已同步 {lines} 行记忆内容到云端

记忆概要：
• 偏好设置：{preferences_summary}
• 工作习惯：{habits_summary}
• 技术栈：{tech_summary}

您的记忆将在所有设备间同步。
```

### 失败处理

**MEMORY.md 不存在时：**
```
⚠️ 暂无本地记忆可保存

请先：
1. 使用「刷新助手记忆」获取云端记忆
2. 或直接编辑 memory/MEMORY.md 添加内容

然后再说「保存永久记忆」
```

**读取失败时：**
```
⚠️ 无法读取本地记忆文件

请检查 memory/MEMORY.md 是否存在且可读。
```

**接口调用失败时：**
```
⚠️ 记忆保存失败

错误信息：{error_message}

请检查网络连接后重试。
```
