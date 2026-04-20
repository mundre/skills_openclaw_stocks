> **说明**：本文为《drama-ai-studio》技能中单个 HTTP 接口的完整说明。

### 6.4 PUT /openapi/drama/{play_id}/assets/{asset_id}

更新已有资产的名称、类型、描述、来源集数、**提示词**等。请求体 **至少提供一个**可更新字段；仅允许修改**未软删除**的资产。

**路径参数（Path）：**

| 参数       | 必填 | 类型   | 说明     |
|------------|------|--------|----------|
| `play_id`  | 是   | int    | 剧目 ID  |
| `asset_id` | 是   | string | 资产 ID  |

**请求体（JSON）：** 以下字段均为可选，但 **不能全部省略**（至少传一项）。

```json
{
  "name": "角色A（改名）",
  "type": 2,
  "description": "新的描述；传空字符串可清空",
  "source_episode_nos": [1, 3],
  "prompt": "更新后的资产主提示词；传空字符串可清空",
}
```

**字段说明**：参考 §6.1 和 §6.3

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": "1",
    "type": 2,
    "name": "角色A（改名）",
    "description": "新的描述",
    "prompt": "…",
    "deleted": false,
    "operation_time": "2025-01-01T12:00:00"
  }
}
```

**错误响应示例：** 参数缺失（未提供任何可更新字段）、资产不存在或已删除、类型非法等，返回 `code=-1` 及 `msg` / `data.error` 说明（HTTP 状态码以网关为准，常见为 400/500）。
