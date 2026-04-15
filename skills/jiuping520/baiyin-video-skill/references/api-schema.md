# API 接口结构参考

## 目录

- [/video/config 响应结构](#videoconfig-响应结构)
- [能力标记详解](#能力标记详解)
- [方案与 children_id 的对应方式](#方案与-children_id-的对应方式)
- [DTO 字段参考](#dto-字段参考)
- [/video/generate 请求体示例](#videogenerate-请求体示例)
- [/tasks/{taskId} 响应结构](#taskstaskid-响应结构)

---

## /video/config 响应结构

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "modelName": "可灵 视频模型",
      "desc": "支持文生视频与图生视频",
      "children": [
        {
          "children_id": 11,
          "prompt": 2,
          "first_frame": 1,
          "last_frame": 0,
          "multi_image": 0,
          "audio": 0,
          "video": 0,
          "duration": ["5", "10"],
          "resolution": ["720", "1080"],
          "widescreen": ["16:9", "9:16", "1:1"]
        }
      ]
    }
  ]
}
```

## 能力标记详解

每个 child 上的能力标记取值：
- `0` = 不支持（不要发送这个字段）
- `1` = 可选（用户可以提供，也可以不提供）
- `2` = 必填（必须提供，否则任务失败）

后端归一化为整数能力标记的字段：`prompt`、`first_frame`、`last_frame`、`multi_image`、`audio`、`video`。

**`last_frame` 的实际含义：**
- `last_frame: 0` → 该方案为**首帧**模式，不支持结束帧
- `last_frame: 1` → 该方案为**首尾帧**模式，结束帧可选
- `last_frame: 2` → 该方案为**首尾帧**模式，结束帧必填

**`single_image` 说明：**
`single_image` 是**单图参考模式**的能力标记，与 `first_frame`（首帧/首尾帧）是不同的生成类型。`/video/config` 当前不将其归一化为整数能力标记，解析脚本通过检测字段是否存在且 `≥ 1` 来判断是否支持该模式。提交时使用 DTO 的 `single_image` 字段传图片 URL。

child 对象中的非标记字段（`duration`、`widescreen`、`resolution`）是允许值数组，数组长度 > 1 时需要让用户选择，= 1 时静默应用。

---

## 方案与 children_id 的对应方式

- 如果同一模型下多个方案只是在时长 / 分辨率上不同，那么每个组合都是一个独立的 `children_id`。用户选择的时长和分辨率决定使用哪个 `children_id`。
- 如果某个模型的一个方案里包含多值数组（例如 `duration: ["5","10","15"]`），那么 `children_id` 是固定的，用户选中的值作为参数发送。

---

## DTO 字段参考

| 字段 | 类型 | 用户可见名称 |
|---|---|---|
| `model_id` | number | （不展示） |
| `children_id` | number | （不展示） |
| `prompt` | string | **提示词** |
| `first_frame` | string | 起始帧 |
| `last_frame` | string | 结束帧 |
| `single_image` | string | 参考图 |
| `multi_image` | string[] | 参考图 |
| `duration` | number | 时长（第 3 步收集） |
| `resolution` | string | 分辨率（第 3 步收集） |
| `widescreen` | string | 画面比例（第 3 步收集） |
| `audio` | string | 音频 |
| `video` | string | 参考视频 |

---

## /video/generate 请求体示例

### 文生视频（最小请求体）

```json
{
  "model_id": 1,
  "children_id": 11,
  "prompt": "海边黄昏，镜头缓慢推进",
  "widescreen": "16:9",
  "resolution": "1080",
  "duration": 5
}
```

### 图生视频

```json
{
  "model_id": 1,
  "children_id": 11,
  "prompt": "海边黄昏，一个女孩在散步",
  "first_frame": "https://cdn.example.com/start.jpg",
  "widescreen": "16:9",
  "resolution": "720",
  "duration": 5
}
```

### 首尾帧

```json
{
  "model_id": 1,
  "children_id": 12,
  "prompt": "从日出到黄昏的过渡",
  "first_frame": "https://cdn.example.com/start.jpg",
  "last_frame": "https://cdn.example.com/end.jpg",
  "resolution": "1080",
  "duration": 10
}
```

### 多图参考

```json
{
  "model_id": 1,
  "children_id": 13,
  "prompt": "两个角色在森林里对话",
  "multi_image": [
    "https://cdn.example.com/ref1.jpg",
    "https://cdn.example.com/ref2.jpg"
  ],
  "widescreen": "16:9",
  "resolution": "1080"
}
```

---

## /tasks/{taskId} 响应结构

```json
{
  "success": true,
  "data": {
    "requestId": "req_xxx",
    "taskId": "task_xxx",
    "capability": "video.generate",
    "status": "processing",
    "result": {
      "taskId": 902,
      "internalTaskId": "hk_ai_task_xxx",
      "modelId": 1,
      "imageUrl": null,
      "images": [],
      "videoUrl": "https://cdn.example.com/video/result.mp4",
      "videos": ["https://cdn.example.com/video/result.mp4"],
      "progress": 85,
      "raw": [{ "video": "https://cdn.example.com/video/result.mp4" }]
    },
    "error": null,
    "billing": null
  }
}
```
