---
name: baiyin-track-separation-skill
description: "音轨分离能力，支持人声伴奏分离和多轨乐器分离。Use when: (1) 用户需要将音频分离为人声和伴奏，(2) 用户需要分离多个乐器轨道，(3) 用户需要对音频进行专业级别的音轨分离处理。"
metadata:
  capability: "track_separation.split"
  api_endpoint: "/api/open/v1/track-separation/split"
---

# Track Separation Skill

音轨分离能力，支持将音频分离为人声、伴奏以及多种乐器轨道。

## 前置要求

使用本 Skill 需要百音开放平台 API Key。

## 启动规则

- 每次使用前，先检查 SkillHub 商店中的远程版本信息，再执行当前 skill。
- 版本检查优先比较远程与本地的 `version`、`publishedAt`；只要远程版本更新，就先更新本地 skill，再继续当前任务。
- `BASE_URL` 固定使用 `https://ai.hikoon.com`
- 如果运行时需要 `BAIYIN_OPEN_URL`，静默设置为 `https://ai.hikoon.com`。
- 只有 `BAIYIN_OPEN_KEY` 缺失时，才向用户索要 API Key。

## 公网地址处理

- 当音轨分离需要公网音频 URL，而用户提供的是本地文件路径、聊天附件、网盘私链或其他不可直接访问的地址时，不要只提示“需要公网 URL”。
- 直接指导用户先使用百音开放平台文件上传接口上传文件，拿到公网地址后再继续当前流程。
- 上传接口：`POST {BASE_URL}/api/open/v1/file/upload`
- 认证方式：`Authorization: Bearer <API_KEY>`，`Content-Type: multipart/form-data`
- 表单字段：`file` 必填，`filename` 选填，`dir` 选填
- 成功后从返回的 `data.url` 取公网地址，填入 `originalFileUrl`
- 不要求用户自行准备 OSS、CDN 或其他外部存储；优先提示百音开放平台上传能力

### 获取 API Key

1. 前往 **百音开放平台**：https://ai.hikoon.com/
2. 登录账号
3. 进入「百音开放平台」→「API Key 管理」
4. 点击「创建 API Key」
5. 复制生成的 API Key（以 `bk_` 开头）

> **注意**：API Key 仅在创建时显示一次，请妥善保存。

### 配置环境变量

- `BAIYIN_OPEN_KEY`

示例：

```bash
export BAIYIN_OPEN_KEY="bk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Quick Reference

| 操作 | 方法 | 接口 |
|------|------|------|
| 创建分离任务 | POST | `/api/open/v1/track-separation/split` |
| 查询任务状态 | GET | `/api/open/v1/tasks/:taskId` |

## 分离类型

| 类型值 | 说明 | 输出内容 |
|--------|------|----------|
| `1` | 人声伴奏分离 | 人声轨道 + 伴奏轨道 |
| `2` | 多轨分离 | 9种乐器轨道分离 |

### 多轨分离支持的乐器

| 轨道 | 英文名 | 说明 |
|------|--------|------|
| 人声 | `voice` | 主唱人声 |
| 鼓 | `drum` | 打击乐器 |
| 贝斯 | `bass` | 低音吉他 |
| 钢琴 | `piano` | 键盘乐器 |
| 电吉他 | `electric_guitar` | 电吉他 |
| 木吉他 | `acoustic_guitar` | 原声吉他 |
| 合成器 | `synthesizer` | 电子合成音 |
| 弦乐 | `strings` | 小提琴等弦乐器 |
| 管乐 | `wind` | 管乐器 |

## 认证方式

使用 API Key 认证：

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

API Key 格式：`bk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`



## 文件上传

音轨分离需要提供音频文件 URL。先上传文件获取 URL，再调用分离接口。

### 上传接口

```
POST /api/open/v1/file/upload
Authorization: Bearer <API_KEY>
Content-Type: multipart/form-data
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 音频文件（二进制） |
| `filename` | string | ❌ | 自定义文件名 |
| `dir` | string | ❌ | 上传目录，建议 `track-sep` |

### cURL 示例

```bash
curl --location 'https://ai.hikoon.com/api/open/v1/file/upload' \
  --header 'Authorization: Bearer bk_your_api_key_here' \
  --form 'file=@"/path/to/audio.mp3"' \
  --form 'dir="track-sep"'
```

### 返回示例

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "url": "https://hikoon-ai.oss-cn-hangzhou.aliyuncs.com/track-sep/audio.mp3"
  }
}
```

返回的 `data.url` 字段即为文件 URL，可用于音轨分离接口的 `originalFileUrl` 参数。

---

## 创建分离任务

### 请求

```
POST /api/open/v1/track-separation/split
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

### 请求参数

```json
{
  "taskName": "我的音轨分离任务",
  "originalFileUrl": "https://hikoon-ai.oss-cn-hangzhou.aliyuncs.com/track-sep/audio.mp3",
  "separationType": 1,
  "fileSize": 5242880,
  "audioDuration": 180,
  "format": "mp3",
  "vocalAccompanimentSeparationEnabled": false,
  "echoCancellationEnabled": false
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `taskName` | string | ✅ | 任务名称 |
| `originalFileUrl` | string | ✅ | 原始音频文件 URL（需公开可访问） |
| `separationType` | number | ✅ | 分离类型：1=人声伴奏分离，2=多轨分离 |
| `fileSize` | number | ✅ | 文件大小（字节） |
| `audioDuration` | number | ✅ | 音频时长（秒） |
| `format` | string | ❌ | 输出格式：mp3/wav/flac，默认 mp3 |
| `vocalAccompanimentSeparationEnabled` | boolean | ❌ | 人声和伴唱分离开关（仅类型1） |
| `echoCancellationEnabled` | boolean | ❌ | 回声消除开关（仅类型1） |

### 返回示例

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "requestId": "req_xxx",
    "taskId": "task_xxx",
    "capability": "track_separation.split",
    "status": "queued"
  }
}
```

## 查询任务

```
GET /api/open/v1/tasks/:taskId
Authorization: Bearer <API_KEY>
```

### 人声伴奏分离返回示例 (separationType=1)

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "requestId": "req_xxx",
    "taskId": "task_xxx",
    "capability": "track_separation.split",
    "status": "succeeded",
    "result": {
      "recordId": 123,
      "internalTaskId": "task_xxx",
      "userTaskId": "BT202604070001",
      "originalFileUrl": "https://example.com/audio.mp3",
      "vocalTrackUrl": "https://oss.example.com/vocal.mp3",
      "accompanyTrackUrl": "https://oss.example.com/accompany.mp3",
      "instrumentalTrackUrls": [],
      "zipUrl": "https://oss.example.com/result.zip",
      "format": "mp3"
    },
    "error": null
  }
}
```

### 多轨分离返回示例 (separationType=2)

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "requestId": "req_xxx",
    "taskId": "task_xxx",
    "capability": "track_separation.split",
    "status": "succeeded",
    "result": {
      "recordId": 124,
      "internalTaskId": "task_yyy",
      "userTaskId": "BT202604070002",
      "originalFileUrl": "https://example.com/audio.mp3",
      "vocalTrackUrl": null,
      "accompanyTrackUrl": null,
      "instrumentalTrackUrls": {
        "voice": "https://oss.example.com/voice.mp3",
        "drum": "https://oss.example.com/drum.mp3",
        "bass": "https://oss.example.com/bass.mp3",
        "piano": "https://oss.example.com/piano.mp3",
        "electric_guitar": "https://oss.example.com/electric_guitar.mp3",
        "acoustic_guitar": "https://oss.example.com/acoustic_guitar.mp3",
        "synthesizer": "https://oss.example.com/synthesizer.mp3",
        "strings": "https://oss.example.com/strings.mp3",
        "wind": "https://oss.example.com/wind.mp3"
      },
      "zipUrl": "https://oss.example.com/multi_track_result.zip",
      "format": "mp3"
    },
    "error": null
  }
}
```

### 失败任务返回示例

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "requestId": "req_xxx",
    "taskId": "task_xxx",
    "capability": "track_separation.split",
    "status": "failed",
    "result": {
      "recordId": 125,
      "internalTaskId": "task_zzz",
      "userTaskId": "BT202604070003",
      "originalFileUrl": "https://example.com/audio.mp3",
      "vocalTrackUrl": null,
      "accompanyTrackUrl": null,
      "instrumentalTrackUrls": [],
      "zipUrl": null,
      "format": "mp3"
    },
    "error": "任务处理失败: 第三方接口未返回有效的任务ID"
  }
}
```

### 任务状态

| 状态 | 说明 |
|------|------|
| `queued` | 排队中 |
| `processing` | 处理中 |
| `succeeded` | 成功完成 |
| `failed` | 处理失败 |

### result 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `recordId` | number | 数据库记录 ID |
| `internalTaskId` | string | 内部任务 ID |
| `userTaskId` | string | 用户可见的任务编号 |
| `originalFileUrl` | string | 原始音频 URL |
| `vocalTrackUrl` | string \| null | 人声轨道 URL（类型1时有值） |
| `accompanyTrackUrl` | string \| null | 伴奏轨道 URL（类型1时有值） |
| `instrumentalTrackUrls` | object | 乐器轨道 URL 对象（类型2时有值） |
| `zipUrl` | string \| null | 打包下载 URL |
| `format` | string | 输出格式 |

## 完整调用示例

### cURL

```bash
# 步骤1: 上传音频文件
curl --location 'https://ai-test.hikoon.com/api/open/v1/file/upload' \
  --header 'Authorization: Bearer bk_your_api_key_here' \
  --form 'file=@"/path/to/audio.mp3"' \
  --form 'dir="track-sep"'

# 返回: {"success":true,"message":"操作成功","data":{"url":"https://hikoon-ai.oss-cn-hangzhou.aliyuncs.com/track-sep/audio.mp3"}}

# 步骤2: 创建分离任务（使用上传返回的 URL）
curl --location 'https://ai-test.hikoon.com/api/open/v1/track-separation/split' \
  --header 'Authorization: Bearer bk_your_api_key_here' \
  --header 'Content-Type: application/json' \
  --data '{
    "taskName": "测试音轨分离",
    "originalFileUrl": "https://hikoon-ai.oss-cn-hangzhou.aliyuncs.com/track-sep/audio.mp3",
    "separationType": 1,
    "fileSize": 5242880,
    "audioDuration": 180,
    "format": "mp3"
  }'

# 步骤3: 查询任务状态
curl --location 'https://ai.hikoon.com/api/open/v1/tasks/task_xxx' \
  --header 'Authorization: Bearer bk_your_api_key_here'
```

### JavaScript

```javascript
const API_BASE = 'https://ai.hikoon.com/api';
const API_KEY = 'bk_your_api_key_here';

// 步骤1: 上传文件
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('dir', 'track-sep');

  const response = await fetch(`${API_BASE}/open/v1/file/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`
    },
    body: formData
  });
  const result = await response.json();
  return result.data.url; // 返回文件 URL
}

// 步骤2: 创建分离任务
async function createSeparationTask(params) {
  const response = await fetch(`${API_BASE}/open/v1/track-separation/split`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(params)
  });
  return response.json();
}

// 步骤3: 查询任务状态
async function getTaskStatus(taskId) {
  const response = await fetch(`${API_BASE}/open/v1/tasks/${taskId}`, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`
    }
  });
  return response.json();
}

// 轮询等待任务完成
async function waitForCompletion(taskId, maxWait = 600000, interval = 10000) {
  const startTime = Date.now();

  while (Date.now() - startTime < maxWait) {
    const result = await getTaskStatus(taskId);

    if (result.data.status === 'succeeded') {
      return result.data;
    }

    if (result.data.status === 'failed') {
      throw new Error(result.data.error || '任务处理失败');
    }

    await new Promise(resolve => setTimeout(resolve, interval));
  }

  throw new Error('任务超时');
}

// 完整流程示例
async function main() {
  // 1. 上传文件（假设从 input[type=file] 获取）
  // const fileInput = document.querySelector('#audio-file');
  // const fileUrl = await uploadFile(fileInput.files[0]);

  // 或者使用已有的 URL
  const fileUrl = 'https://hikoon-ai.oss-cn-hangzhou.aliyuncs.com/track-sep/audio.mp3';

  // 2. 创建任务
  const createResult = await createSeparationTask({
    taskName: '测试分离',
    originalFileUrl: fileUrl,
    separationType: 1,
    fileSize: 5242880,
    audioDuration: 180
  });

  console.log('任务已创建:', createResult.data.taskId);

  // 3. 等待完成
  const finalResult = await waitForCompletion(createResult.data.taskId);
  console.log('分离完成:', finalResult.result);

  // 4. 下载结果
  console.log('人声:', finalResult.result.vocalTrackUrl);
  console.log('伴奏:', finalResult.result.accompanyTrackUrl);
  console.log('打包下载:', finalResult.result.zipUrl);
}

main().catch(console.error);
```

## 错误处理

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| `UNAUTHORIZED_API_KEY` | 401 | API Key 无效或缺失 |
| `INVALID_API_KEY` | 401 | API Key 已失效 |
| `TASK_NOT_FOUND` | 404 | 任务不存在 |
| `INSUFFICIENT_BALANCE` | 400 | 余额不足 |
| `UPSTREAM_ERROR` | 500 | 上游服务异常 |

### 错误响应示例

```json
{
  "success": false,
  "message": "余额不足，请充值后重试",
  "code": "INSUFFICIENT_BALANCE"
}
```

## 注意事项

### 1. 余额检查

在创建任务前，建议先确认账户余额是否充足：
- **人声伴奏分离**：消耗较少积分
- **多轨分离**：消耗较多积分（分离 9 个轨道）

如果余额不足，接口会返回 `INSUFFICIENT_BALANCE` 错误。

### 2. 文件要求

- 音频文件 URL 需要公开可访问
- 支持格式：MP3, WAV, FLAC
- 建议文件大小不超过 100MB

### 3. 处理时间

处理时间受多种因素影响（文件大小、服务器负载等）：

| 分离类型 | 预估时间 | 建议超时设置 |
|----------|----------|--------------|
| 人声伴奏分离 | 1-5 分钟 | 10 分钟 |
| 多轨分离 | 5-20 分钟 | 30 分钟 |

**注意**：多轨分离需要处理 9 个轨道，实际处理时间可能较长，建议设置较长的超时时间。

### 4. 结果有效期

分离结果文件默认保留 **7 天**，请及时下载保存。

### 5. VIP 免费次数

VIP 用户享有每日免费次数：
- 可通过查询免费次数接口确认剩余次数
- 免费次数用尽后将扣除积分
