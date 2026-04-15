# POST https://cwork-api.mediportal.com.cn/ai-report/moban/updateMoban

## 作用

编辑已有模版，更新名称、章节结构和提示词内容。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `mobanId` | string | 是 | 模版 ID |
| `name` | string | 否 | 模版名称 |
| `desc` | string | 否 | 模版描述 |
| `dirId` | string | 否 | 目录 ID |
| `mobanTypeId` | string | 否 | 模版类型 ID（已废弃） |
| `prompt` | string | 否 | 任务级提示词 |
| `editNote` | string | 否 | 改动日志 |
| `public` | number | 否 | 公开状态：`0` 不公开，`1` 公开 |
| `thirdSystem` | string | 否 | 第三方系统标识 |
| `doSummary` | number | 否 | 是否总结：`0` 不总结，`1` 最后一章总结，`2` 第一章总结 |
| `summaryPrompt` | string | 否 | 总结提示词 |
| `aiType` | string | 否 | AI 类型 |
| `requireContext` | array | 否 | 上下文字段（`string[]`） |
| `sectionList` | array | 否 | 章节结构 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["mobanId"],
  "properties": {
    "mobanId": { "type": "string", "minLength": 1 },
    "name": { "type": ["string", "null"] },
    "desc": { "type": ["string", "null"] },
    "dirId": { "type": ["string", "null"] },
    "mobanTypeId": { "type": ["string", "null"] },
    "prompt": { "type": ["string", "null"] },
    "editNote": { "type": ["string", "null"] },
    "public": { "type": ["number", "null"], "enum": [0, 1, null] },
    "thirdSystem": { "type": ["string", "null"] },
    "doSummary": { "type": ["number", "null"], "enum": [0, 1, 2, null] },
    "summaryPrompt": { "type": ["string", "null"] },
    "aiType": { "type": ["string", "null"] },
    "requireContext": {
      "type": ["array", "null"],
      "items": { "type": "string" }
    },
    "sectionList": {
      "type": "array",
      "minItems": 0,
      "items": {
        "type": "object",
        "required": [],
        "properties": {
          "name": { "type": "string", "minLength": 1 },
          "prompt": { "type": ["string", "null"] },
          "questionList": {
            "type": "array",
            "minItems": 0,
            "items": {
              "type": "object",
              "required": [],
              "properties": {
                "title": { "type": "string", "minLength": 1 },
                "content": { "type": ["string", "null"] },
                "prompt": { "type": ["string", "null"] },
                "withNet": { "type": ["boolean", "null"] },
                "dataSrc": {
                  "type": ["object", "null"],
                  "properties": {
                    "srcType": { "type": ["string", "null"] },
                    "docList": {
                      "type": ["array", "null"],
                      "items": {
                        "type": "object",
                        "properties": {
                          "name": { "type": ["string", "null"] },
                          "fileId": { "type": ["string", "null"] },
                          "docType": { "type": ["number", "null"] }
                        }
                      }
                    },
                    "customSrcId": { "type": ["string", "null"] },
                    "mcpServerIdList": { "type": ["string", "null"] },
                    "originDoc": { "type": ["boolean", "null"] }
                  }
                }
              }
            }
          }
        }
      }
    }
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
    "data": { "type": ["object", "null"] }
  }
}
```

## 脚本映射
- `../../scripts/moban/update-moban.py`
