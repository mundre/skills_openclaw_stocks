# POST https://cwork-api.mediportal.com.cn/ai-report/moban/mobanDetail

## 作用

读取指定模版的章节结构、子章节和提示词配置。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `mobanId` | string | 是 | 模版 ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["mobanId"],
  "properties": {
    "mobanId": { "type": "string" }
  }
}
```

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "resultMsg": { "type": ["string", "null"] },
    "data": { "type": "object" }
  }
}
```

## 脚本映射
- `../../scripts/moban/moban-detail.py`
