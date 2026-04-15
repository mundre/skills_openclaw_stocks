---
name: baiyin-image-generate-skill
description: 图片生成能力，支持百音开放平台文生图和图生图调用。Use when: (1) 用户希望通过百音开放平台生成图片，(2) 用户希望基于参考图生成变体或重绘，(3) 用户希望查询图片任务进度并返回最终图片链接。
metadata:
  capability: "image.generate"
  api_endpoint: "/api/open/v1/image/generate"
---

# Image Generate Skill

图片生成能力，支持通过百音开放平台发起图片生成任务、查询任务状态，并返回最终图片链接。

## 前置要求

- `BAIYIN_OPEN_KEY`

## 启动规则

- 每次使用前，先检查 SkillHub 商店中的远程版本信息，再执行当前 skill。
- 版本检查优先比较远程与本地的 `version`、`publishedAt`；只要远程版本更新，就先更新本地 skill，再继续当前任务。
- `BASE_URL` 固定使用 `https://ai.hikoon.com`
- 如果运行时需要 `BAIYIN_OPEN_URL`，静默设置为 `https://ai.hikoon.com`。
- 只有 `BAIYIN_OPEN_KEY` 缺失时，才向用户索要 API Key。

## 公网地址处理

- 当图生图或其他参数需要公网图片 URL，而用户提供的是本地文件路径、聊天附件、网盘私链或其他不可直接访问的地址时，不要只提示“需要公网 URL”。
- 直接指导用户先使用百音开放平台文件上传接口上传文件，拿到公网地址后再继续当前流程。
- 上传接口：`POST {BASE_URL}/api/open/v1/file/upload`
- 认证方式：`Authorization: Bearer <API_KEY>`，`Content-Type: multipart/form-data`
- 表单字段：`file` 必填
- 开放平台上传接口不支持自定义文件名，也不支持自定义文件夹；文件名与目录均由服务端自动处理
- 成功后从返回的 `data.url` 取公网地址，填入当前模型真实支持的参考图字段
- 不要求用户自行准备 OSS、CDN 或其他外部存储；优先提示百音开放平台上传能力

## 认证方式

使用 API Key 认证：

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

## 接口列表

- 查询图片模型列表：`GET {BASE_URL}/api/open/v1/image/models`
- 查询模型参数：`GET {BASE_URL}/api/open/v1/image/models/{modelCode}/params`
- 创建任务：`POST {BASE_URL}/api/open/v1/image/generate`
- 查询任务：`GET {BASE_URL}/api/open/v1/tasks/{taskId}`

## 首要前提

图片生成任务开始前，必须先确定 `modelCode`。

- 如果用户还没有提供 `modelCode`，先调用模型列表接口并让用户选择 `modelCode`
- 在 `modelCode` 未明确前，不要继续收集其他参数，也不要创建任务
- 只有 `modelCode` 明确后，才进入该模型参数展示与后续参数选择步骤
- 即使调用接口支持 `modelId`，此 skill 对外统一要求优先以 `modelCode` 作为第一步输入

可直接对用户使用的引导语示例：

- `开始生成前需要先选 modelCode。我先给你列出当前可用的图片模型。`
- `你还没提供 modelCode，我先调用图片模型列表接口，把可选模型列给你。`

## 参数展示原则

在 `modelCode` 确认后，下一步必须先列出该模型真实支持的参数，再让用户选择。

- 只能展示该 `modelCode` 对应的真实参数
- 参数名、可选值、取值范围、是否必填，都应来自模型配置、模型元数据、专门的参数定义源或平台返回信息
- 查询到参数后，必须把参数按步骤展示给用户，并让用户一步一步选择；不要由 AI 自己直接拼出一整套参数
- 对于有枚举值、范围值、布尔开关或多选项的参数，必须先展示可选范围，再等用户确认
- 除 `prompt` 这类用户自然语言输入外，不要替用户自动决定某个具体参数值
- 不允许 skill 自行猜测某个模型支持的参数
- 不允许 skill 自行为用户补出某个模型未确认支持的参数
- 如果当前上下文拿不到该 `modelCode` 的参数定义，先告诉用户“暂时无法确认该模型支持哪些参数”，不要继续瞎编

## 参数交互规则

- `GET /api/open/v1/image/models/{modelCode}/params` 返回后，必须先展示该模型支持的参数，再开始收集参数值
- 参数收集必须按步骤进行，一次只处理一个参数维度，或一组强相关参数；不要把一整套参数一次性替用户定好
- 对每个参数都要明确区分：
  - 是否必填
  - 可选值列表、取值范围或输入格式
  - 当前是否已经由用户明确指定
- 如果某个参数本质上是“参考图输入”，可以对用户解释成“参考图”或“参考图片”，但真正提交时必须使用该模型真实支持的参数名
- 如果某个参数只有一个合法值，可以告知用户该值固定并直接使用，但不要把多个参数一起静默带过
- 如果某个参数有多个合法值，而用户尚未明确指定，必须先问用户选哪个，不能由 AI 按经验、审美或常见默认值代选
- 当用户只表达了创意目标，而没有明确技术参数时，先继续逐项展示支持的参数，让用户选；不要把“常见组合”直接作为最终请求
- 在所有必填参数和用户关心的可选参数确认前，不要创建任务

## 参数来源要求

当前百音开放平台代码里已确认存在的开放接口只有：

- `GET /api/open/v1/image/models`
- `GET /api/open/v1/image/models/{modelCode}/params`
- `POST /api/open/v1/image/generate`
- `GET /api/open/v1/tasks/{taskId}`

因此本 skill 必须遵守以下规则：

- 如果用户还没选 `modelCode`，必须先调用 `GET /api/open/v1/image/models`
- 用户选定 `modelCode` 后，必须再调用 `GET /api/open/v1/image/models/{modelCode}/params`
- 该接口返回的 `data.params` 就是后续参数选择的唯一依据
- 如果该接口调用失败，或返回为空，或没有可用参数定义，就停止，不要继续往下收集参数
- 不允许把通用图片模型的常见字段，当作当前 `modelCode` 的真实参数定义

对用户的标准回复建议：

- `已确认 modelCode，但当前无法获取这个模型的参数定义，暂时不能继续创建请求。请先检查模型参数查询接口是否可用。`

可直接对用户使用的引导语示例：

- `已确认 modelCode = flux-dev。请先看这个模型当前支持的参数项，我再根据你的选择组装请求。`
- `这个模型支持的参数需要按真实配置来选，我先列出可选项，你确认后我再继续。`

## 核心模式

根据用户表达自动判断生成模式。除非信息不足以执行，否则不要强迫用户使用接口字段名来描述需求。

- 文生图
  - 用户通过文字描述场景、角色、海报、商品图、插画风格或视觉概念
  - 传 `prompt`
  - 一般不传参考图字段
- 图生图
  - 用户希望基于参考图做重绘、变体、换风格、增强或受控生成
  - 传 `prompt`
  - 传当前模型真实支持的参考图字段
  - 单图字段的值是可公网访问的图片 URL 字符串
  - 多图字段的值必须是图片 URL 数组；只要该字段语义是多图，例如 `multi_image`、`images`、`image_urls`，就必须传数组，不能传单个字符串，也不能把多个 URL 拼成逗号分隔字符串
  - 参考图字段可能是 `img`、`single_image`、`multi_image` 或其他模型参数定义中明确存在的字段；必须以 `GET /api/open/v1/image/models/{modelCode}/params` 的返回为准

## 请求体

对外使用时，先确认 `modelCode`，再继续后续参数整理。

底层接口层面 `modelId` 和 `modelCode` 至少传一个，但本 skill 的对外交互要求是优先先拿到 `modelCode`，然后先查模型参数接口，再继续后续步骤。

```json
{
  "prompt": "a white cat sitting by the window, warm morning light, cinematic",
  "modelCode": "flux-dev",
  "single_image": "https://example.com/reference.jpg",
  "multi_image": [
    "https://example.com/reference-1.jpg",
    "https://example.com/reference-2.jpg"
  ],
  "aspect_ratio": "1:1",
  "resolution": "1024x1024",
  "params": {
    "seed": 12345
  }
}
```

## 参数说明

- `prompt`
  - 必填
  - 图片生成提示词
- `modelId`
  - 选填，`modelCode` 存在时可不传
  - 统一图片模型 ID
- `modelCode`
  - 选填，`modelId` 存在时可不传
  - 统一图片模型编码
- 参考图字段
  - 选填
  - 真实字段名必须来自当前模型参数定义
  - 对用户可以说“参考图”或“参考图片”，但不要强迫用户说接口字段名
  - 单图字段值必须是可公网访问的图片 URL 字符串
  - 多图字段值必须是可公网访问的图片 URL 数组
- `aspect_ratio`
  - 选填
  - 宽高比，例如 `1:1`、`4:3`、`3:4`、`16:9`、`9:16`
- `resolution`
  - 选填
  - 分辨率，例如 `512x512`、`768x768`、`1024x1024`
- `params`
  - 选填
  - 模型附加参数，透传给底层模型

## `data.params` 解释规则

- 图片模型参数查询接口只返回 `data.model` 和 `data.params`
- `data.params` 已经是多个套餐聚合、去重后的结果；不要再向用户展示套餐、分组或 group 概念
- 每个参数项至少关注：
  - `name`
  - `type`
  - `required`
  - `values`
- `type=enum`
  - 按 `values` 展示可选值
  - 用户未明确选择前，不要替用户代选
- `type=asset`
  - 表示资源参数
  - 当 `values` 返回 `0`、`1`、`2` 时，分别表示：`0` 不支持、`1` 可选、`2` 必填
  - 只有当值为 `1` 或 `2` 时，才继续收集对应资源 URL
  - 当值为 `2` 时，必须向用户收集该资源；缺失时不能创建任务
  - 当值为 `0` 时，不要向用户展示或收集该资源参数

## 参数策略

- 始终保留用户在 `prompt` 里的核心视觉意图。
- 对外交互时，第一步必须先拿到 `modelCode`。
- 如果用户没给 `modelCode`，先查模型列表接口，把可选模型列给用户选。
- 即使调用方已经知道 `modelId`，此 skill 也应先要求用户确认 `modelCode`，再继续后续流程。
- `modelCode` 明确后，如有需要，再由调用方在实现层映射到内部 `modelId`。
- `modelCode` 明确后，必须先调用模型参数查询接口，再列出该模型支持的真实参数给用户选择。
- 模型参数一旦查到，后续参数值应由用户逐步选择或明确输入，不允许 AI 自己瞎组装整套参数。
- 只有当该模型参数定义中明确存在参考图相关字段，且用户明确要求参考图生成，才传对应字段。
- 只有当该模型明确支持 `batchSize` 时，且用户明确要求多张结果，才传 `batchSize`。
- 只有当该模型明确支持 `aspect_ratio` 和 `resolution` 时，才允许收集这些参数。
- `params` 里的字段也必须来自该模型已知支持的参数定义，不能自行杜撰。
- 不要虚构参考图 URL。
- 不要把“常见模型可能支持什么”当作“当前模型一定支持什么”。

## 映射规则

- 场景、风格、情绪、灯光、构图、镜头语言、时代感、材质和画风要合并成一条干净的 `prompt`。
- 用户指定具体模型时，按调用方能力映射到 `modelId` 或 `modelCode`。
- 用户说“给我 4 个方案”“出 3 张不同版本”时，只有该模型明确支持批量数量参数，才设置 `batchSize`。
- 用户请求海报、壁纸、竖版封面、横幅等内容时，只有该模型明确支持宽高比参数，才允许设置 `aspect_ratio`。
- 用户说“参考这张图”“基于这张图重绘”“把这张照片转成某种风格”时，先根据模型真实参数定义识别参考图字段，再把 URL 填入那个字段。
- 用户说“参考这几张图”“用多张图融合”“多图参考”时，如果该模型参数定义对应的是多图字段，提交时必须传 URL 数组，例如 `"multi_image": ["url1", "url2"]`，不要传 `"multi_image": "url1,url2"`。
- 用户给出 seed、guidance 或其他模型控制项时，只有在该模型参数定义中存在这些字段时，才放到 `params`。

## 追问最小化

只有在以下情况才追问：

- 用户尚未提供 `modelCode`
- 模型列表接口尚未调用
- 已拿到 `modelCode`，但还未调用模型参数查询接口
- 已调用模型参数查询接口，但还未向用户展示该模型支持的真实参数列表
- 用户输入不足以形成可执行的 `prompt`
- 用户要做图生图，但没有提供可公网访问的图片 URL
- 用户要查进度或取结果，但上下文里没有可用的 `taskId`
- 当前模型参数查询接口不可用，或返回中没有参数定义

以下情况不要追问：

- `modelCode` 已明确且模型参数表已经展示后，再按参数表继续收集值
- 不要基于经验替用户假定模型支持哪些参数
- 不要因为“通常图片模型会支持”就默认当前模型也支持

## 工作流

1. 判断用户要的是图片生成，而不是视频生成或数字人能力。
2. 如果用户未提供 `modelCode`，先调用 `GET /api/open/v1/image/models`。
3. 把接口返回的可用图片模型列表展示给用户选择 `modelCode`。
4. 用户选定 `modelCode` 后，调用 `GET /api/open/v1/image/models/{modelCode}/params`。
5. 如果接口调用失败，或返回中没有可用参数定义，明确告知无法确认该模型参数，停止继续猜测。
6. 将接口返回的该模型真实参数列表展示给用户选择。
7. 按步骤逐项向用户展示参数，并让用户一步一步选择；不要替用户一次性决定整套参数。
8. 在参数选择过程中，再判断是文生图还是图生图，并收集对应字段。
9. 收集 `prompt` 和用户明确给出的技术约束；技术参数只采用用户已确认的值。
10. 仅使用该接口确认支持且已由用户确认的字段组装请求体；如实现层需要，可再映射到内部 `modelId`。
11. 创建任务。
12. 返回 `taskId`、`requestId` 和当前 `status`。
13. 用户追问进度或结果时，调用任务查询接口。
14. 任务成功后，优先返回 `imageUrl`，有多张时再返回完整 `images`。

## 创建任务返回示例

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "requestId": "req_xxx",
    "taskId": "task_xxx",
    "capability": "image.generate",
    "status": "queued"
  }
}
```

## 查询任务返回示例

图片任务成功后会归一化为如下结构：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "requestId": "req_xxx",
    "taskId": "task_xxx",
    "capability": "image.generate",
    "status": "succeeded",
    "result": {
      "taskId": 1903,
      "internalTaskId": "hk_ai_task_001",
      "modelId": 701,
      "imageUrl": "https://cdn.example.com/image/result-1.jpg",
      "images": [
        "https://cdn.example.com/image/result-1.jpg",
        "https://cdn.example.com/image/result-2.jpg"
      ],
      "progress": 100,
      "raw": [
        {
          "image": "https://cdn.example.com/image/result-1.jpg"
        }
      ]
    },
    "error": null,
    "billing": null
  }
}
```

## 状态说明

- `queued`：已受理，等待执行
- `processing`：生成中
- `succeeded`：生成成功
- `failed`：生成失败

轮询时回复要简短，优先返回状态。

## 输出格式

- 创建任务后返回：
  - 简短确认语
  - `taskId`
  - 当前 `status`
  - 必要时补充本次解析出的关键参数
- 轮询时返回：
  - 当前 `status`
  - 可用时返回 `progress`
- 成功后返回：
  - 优先返回 `imageUrl`
  - 多图时再返回完整 `images`

## 错误处理

- 创建任务返回 `400` 时，说明请求参数不合法或当前模型不支持这些参数。
- 创建任务返回 `401` 时，说明 Open API Key 无效或当前环境未配置。
- 查询任务返回 `404` 或 `TASK_NOT_FOUND` 时，说明任务不存在，或不属于当前 API Key 所属用户。
- 后端提示模型不存在或未启用时，提示调用方更换 `modelId` 或 `modelCode`。
- 任务状态为 `failed` 时，优先透传后端 `error` 字段。

## 交互约束

- 用户第一次提出图片生成需求时，优先检查是否已经提供 `modelCode`。
- 如果没有 `modelCode`，只做一件事：先调用 `GET /api/open/v1/image/models`，把可选模型列出来让用户选。
- `modelCode` 确认后，下一步只做一件事：先调用 `GET /api/open/v1/image/models/{modelCode}/params` 获取参数定义，再展示给用户选。
- 在参数列表未确认前，不要继续追问提示词细节、尺寸、风格、参考图、数量等次级参数。
- 在 `modelCode` 缺失时，不要擅自用默认模型继续执行。
- 在拿不到参数定义时，不要靠经验补参数，不要猜模型能力。
- 只有在 `modelCode` 已确认且参数列表已展示后，才继续后续图片生成流程。

## 模型列表返回使用规则

调用 `GET /api/open/v1/image/models` 后：

- 使用 `data.rows` 作为可选图片模型列表
- 至少向用户展示 `modelCode` 和 `modelName`
- 有 `desc` 或 `generalNotes` 时，一并展示，帮助用户选择
- 在用户未选定 `modelCode` 前，不要继续进入参数选择步骤

## 参数查询返回使用规则

调用 `GET /api/open/v1/image/models/{modelCode}/params` 后：

- 使用 `data.model` 展示模型基础信息
- 使用 `data.params` 作为对用户展示的参数列表
- `data.params` 已是服务端聚合去重后的结果，调用方不需要也不允许再向用户暴露套餐或分组概念
- 资源参数如果返回 `0/1/2`，按 `0` 不支持、`1` 可选、`2` 必填解释
- 在 `data.params` 为空时，明确告知当前无法确认模型支持的参数，停止继续猜测

## 示例

示例 1：

- 用户：`生成一张日出时白猫坐在窗边的电影感海报`
- 正确回复：
  - `你还没提供 modelCode。我先调用 /api/open/v1/image/models 获取当前可用的图片模型列表，再让你选。`

示例 2：

- 用户：`modelCode 用 flux-dev，生成一张日出时白猫坐在窗边的电影感海报`
- 正确回复：
  - `已确认 modelCode = flux-dev。下一步我会先调用 /api/open/v1/image/models/flux-dev/params 获取这个模型的参数定义；拿到后我会把支持的参数项列给你选。`

示例 3：

- 用户：`用这张商品图生成一张干净的电商主图`
- 正确回复：
  - `你还没提供 modelCode。我先调用 /api/open/v1/image/models，把可选模型列给你选。`

示例 4：

- 用户：`modelCode 用 flux-dev，用这张商品图生成一张干净的电商主图`
- 正确回复：
  - `已确认 modelCode = flux-dev。我先调用 /api/open/v1/image/models/flux-dev/params，确认支持哪些参数后，再列出来给你选。`

示例 5：

- 用户：`modelCode 用 flux-dev`
- 当前拿不到该模型参数定义时的正确回复：
  - `已确认 modelCode = flux-dev，但当前无法通过 /api/open/v1/image/models/flux-dev/params 获取这个模型的参数定义，暂时不能继续创建请求。请先检查该接口是否可用。`

示例 6：

- 用户：`我要生成图片，但是不知道选哪个模型`
- 下一步：
  - 调用 `GET {BASE_URL}/api/open/v1/image/models`
  - 把返回的 `rows` 展示给用户选 `modelCode`

示例 7：

- 用户：`modelCode 用 flux-dev`
- 参数查询接口成功后的下一步：
  - 调用 `GET {BASE_URL}/api/open/v1/image/models/flux-dev/params`
  - 把返回的 `data.params` 展示给用户选择

示例 8：

- 用户：`帮我查询 task_123456 的最终图片`
- 操作：
  - 调用 `GET {BASE_URL}/api/open/v1/tasks/task_123456`
  - 如果 `status = succeeded`，返回 `imageUrl` 和 `images`
