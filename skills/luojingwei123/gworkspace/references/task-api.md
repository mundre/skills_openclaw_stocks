# 批注任务 API

## 触发条件

Discord 频道消息包含「批注任务」和 `/api/tasks` URL 时自动触发。

## 完整流程

### 1. 查询待办任务

使用 `gworkspace_tasks` tool（传入 guild_id 或 channel_id）：

```
gworkspace_tasks(guild_id="1234567890")
```

返回示例：
```json
{
  "tasks": [{
    "task_id": "task_xxx",
    "filename": "文件名.docx",
    "file_id": "f_xxx",
    "original_text": "需要修改的原文",
    "instruction": "批注指令（如：删除这段话）",
    "status": "pending"
  }]
}
```

如果 tasks 为空，不需要做任何事。

### 2. 认领任务

```
gworkspace_claim_task(workspace_id="ws_xxx", task_id="task_xxx", claimed_by="吕沛2号")
```

- 成功 → `success: true`
- 409 → 已被其他龙虾认领，**跳过**

### 3. 读取文件并修改

根据 `instruction` 修改文件内容：
- **删除这段话** → 找到 original_text 对应内容，删除
- **扩写** → 扩展对应段落
- **修改为...** → 替换内容

**重要：只改指定部分，保留其余内容不变。**

### 4. 标记完成

```
gworkspace_complete_task(workspace_id="ws_xxx", task_id="task_xxx", result_summary="已删除指定段落")
```

### 5. 回复

在 Discord 频道回复：
```
✅ 批注任务处理完毕
- [任务1] 文件名.docx → 已完成修改（v2）
```
