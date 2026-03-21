# Vidu异步任务处理流程

## 目录
- [任务类型](#任务类型)
- [异步任务处理流程](#异步任务处理流程)
- [任务状态说明](#任务状态说明)
- [查询任务接口](#查询任务接口)
- [使用示例](#使用示例)
- [注意事项](#注意事项)

## 任务类型

### 同步任务
- **TTS语音合成**（`audio-tts`）
  - 直接返回音频文件URL
  - 无需轮询

### 异步任务
- **生图**（`reference2image/nano`）
  - 返回task_id
  - 需轮询查询任务状态

- **生视频**（`reference2video`）
  - 返回task_id
  - 需轮询查询任务状态

## 异步任务处理流程

### 标准流程

```
1. 调用生成接口（生图/生视频）
   ↓
2. 获取 task_id
   ↓
3. 使用 vidu_query_task.py 轮询查询任务状态
   ↓
4. 等待 state 变为 "success" 或 "failed"
   ↓
5. 获取生成的资源URL（24小时有效期）
```

### 轮询策略

- **默认轮询间隔**：5秒
- **最大等待时间**：600秒（10分钟）
- **状态检查**：created → queueing → processing → success/failed

## 任务状态说明

| 状态值 | 说明 | 处理方式 |
|--------|------|----------|
| created | 任务创建成功 | 继续等待 |
| queueing | 任务排队中 | 继续等待 |
| processing | 任务处理中 | 继续等待 |
| success | 任务成功 | 返回结果URL |
| failed | 任务失败 | 抛出异常，检查err_code |

## 查询任务接口

### 脚本调用
```bash
# 单次查询
vidu_query_task.py --task_id "your_task_id"

# 轮询等待（推荐）
vidu_query_task.py --task_id "your_task_id" --wait
```

### 参数说明

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| --task_id | 是 | 任务ID | - |
| --wait | 否 | 是否等待任务完成（轮询模式） | false |
| --max_wait_time | 否 | 最大等待时间（秒） | 600 |
| --poll_interval | 否 | 轮询间隔（秒） | 5 |

### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 任务ID |
| state | String | 任务状态 |
| err_code | String | 错误码（失败时有值） |
| credits | Int | 消耗的积分数 |
| payload | String | 透传参数 |
| bgm | Bool | 是否使用BGM |
| off_peak | Bool | 是否使用错峰模式 |
| creations | Array | 生成物结果数组 |
| creations[].id | String | 生成物ID |
| creations[].url | String | 生成物URL（24小时有效） |
| creations[].cover_url | String | 生成物封面URL（24小时有效） |
| creations[].watermarked_url | String | 带水印生成物URL（24小时有效） |

## 使用示例

### 示例1：生成图片并等待完成

```bash
# 步骤1：创建生图任务
vidu_generate_image.py \
  --prompt "3d动漫风格，远景，鸟瞰机位，宏伟的魔法城堡" \
  --aspect_ratio "16:9" \
  --resolution "2K"

# 输出示例：
# {
#   "task_id": "your_task_id",
#   "state": "created",
#   ...
# }

# 步骤2：轮询等待任务完成
vidu_query_task.py --task_id "your_task_id" --wait

# 输出示例：
# [0s] 任务状态: created
# [5s] 任务状态: queueing
# [10s] 任务状态: processing
# [15s] 任务状态: processing
# [20s] 任务状态: success
#
# 任务完成！
# {
#   "id": "your_task_id",
#   "state": "success",
#   "creations": [
#     {
#       "id": "creation_id",
#       "url": "https://generated_image_url.jpg",
#       "cover_url": "https://cover_url.jpg",
#       "watermarked_url": "https://watermarked_url.jpg"
#     }
#   ]
# }
```

### 示例2：生成视频并等待完成

```bash
# 步骤1：创建生视频任务
vidu_generate_video.py \
  --images '["https://example.com/reference.jpg"]' \
  --prompt "3d动漫风格，中景，平视机位，中心构图，固定镜头。画面中，少年站在城堡门前。图1为[少年角色]。" \
  --duration 5 \
  --model "viduq2"

# 输出示例：
# {
#   "task_id": "your_task_id",
#   "state": "created",
#   ...
# }

# 步骤2：轮询等待任务完成
vidu_query_task.py --task_id "your_task_id" --wait --max_wait_time 600
```

### 示例3：批量处理多个任务

```bash
# 在脚本或程序中循环处理多个任务
for task_id in "${task_ids[@]}"; do
  echo "处理任务: $task_id"
  vidu_query_task.py --task_id "$task_id" --wait
  echo "任务 $task_id 完成"
done
```

## 注意事项

1. **URL有效期**
   - 所有生成物URL有效期仅为24小时
   - 需要及时下载或保存到本地存储

2. **轮询超时**
   - 默认最大等待时间600秒（10分钟）
   - 可根据实际情况调整 `--max_wait_time` 参数
   - 超时后会抛出异常

3. **任务失败处理**
   - 检查响应中的 `err_code` 字段
   - 根据 `err_code` 判断具体错误原因
   - 可能需要重试或调整参数后重新提交

4. **并发限制**
   - Vidu API可能有并发调用限制
   - 批量处理时建议控制并发数
   - 可使用队列机制管理多个任务

5. **积分消耗**
   - 每个任务消耗的积分在响应的 `credits` 字段中
   - 建议监控积分使用情况

6. **水印控制**
   - 可通过 `--watermark` 参数控制是否添加水印
   - 查询结果中包含 `watermarked_url` 和 `url` 两个版本
