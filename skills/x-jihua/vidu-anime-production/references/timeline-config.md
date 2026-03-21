# 时间轴配置格式

## 目录
- [格式概述](#格式概述)
- [字段说明](#字段说明)
- [完整示例](#完整示例)
- [生成方式](#生成方式)

## 格式概述
时间轴配置是用于指导视频音频拼接的JSON格式文件，包含所有视频片段、音频片段的时间顺序和同步信息。

## 字段说明

### 根级别字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| video_segments | Array | 是 | 视频片段数组 |
| audio_segments | Array | 否 | 音频片段数组（若使用viduq3且包含音频，此数组可为空） |
| background_music | String | 否 | 背景音乐URL |

### video_segments 数组元素

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| shot_id | String | 是 | 分镜编号，如 "shot_001" |
| url | String | 是 | 视频文件URL或本地路径 |
| duration | Float | 是 | 视频片段时长（秒） |
| start_time | Float | 是 | 在最终成片中的开始时间（秒） |
| transition | String | 否 | 转场效果，如：fade, dissolve, wipe, none |

### audio_segments 数组元素

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| dialogue_id | String | 是 | 对话ID，如 "dialogue_001" |
| url | String | 是 | 音频文件URL或本地路径 |
| duration | Float | 是 | 音频片段时长（秒） |
| start_time | Float | 是 | 在最终成片中的开始时间（秒） |
| speaker | String | 否 | 说话人角色名称 |
| volume | Float | 否 | 音量，默认1.0，范围0.0-2.0 |

## 完整示例

```json
{
  "video_segments": [
    {
      "shot_id": "shot_001",
      "url": "https://generated_video_url_001.mp4",
      "duration": 3.5,
      "start_time": 0.0,
      "transition": "none"
    },
    {
      "shot_id": "shot_002",
      "url": "https://generated_video_url_002.mp4",
      "duration": 2.0,
      "start_time": 3.5,
      "transition": "fade"
    },
    {
      "shot_id": "shot_003",
      "url": "https://generated_video_url_003.mp4",
      "duration": 4.0,
      "start_time": 5.5,
      "transition": "dissolve"
    }
  ],
  "audio_segments": [
    {
      "dialogue_id": "dialogue_001",
      "url": "https://generated_audio_url_001.mp3",
      "duration": 2.8,
      "start_time": 0.5,
      "speaker": "主角",
      "volume": 1.0
    }
  ],
  "background_music": "https://background_music_url.mp3"
}
```

## 生成方式

### 从小分镜表生成时间轴配置

```python
def generate_timeline_from_storyboard(storyboard_data, model="viduq3"):
    """
    从小分镜表生成时间轴配置

    Args:
        storyboard_data: 小分镜表数据
        model: 使用的模型（viduq3 或 viduq2）

    Returns:
        dict: 时间轴配置JSON
    """
    video_segments = []
    audio_segments = []
    current_time = 0.0

    for shot in storyboard_data.get("storyboard", []):
        shot_id = shot.get("shot_id")
        duration = shot.get("duration", 0)
        video_url = shot.get("generated_video_url")
        dialogue = shot.get("dialogue")
        audio_url = shot.get("generated_audio_url")
        
        # 添加视频片段
        if video_url:
            video_segments.append({
                "shot_id": shot_id,
                "url": video_url,
                "duration": duration,
                "start_time": current_time,
                "transition": "none"
            })

        # 添加音频片段
        # 仅当使用 viduq2 且有 TTS 音频时添加
        # viduq3 音频已包含在视频中，无需添加 audio_segments
        if model == "viduq2" and dialogue and audio_url:
            audio_start = current_time + 0.3
            audio_duration = duration - 0.5

            audio_segments.append({
                "dialogue_id": f"dialogue_{shot_id}",
                "url": audio_url,
                "duration": audio_duration,
                "start_time": audio_start,
                "speaker": shot.get("speaker"),
                "volume": 1.0
            })

        # 累计时间
        current_time += duration

    return {
        "video_segments": video_segments,
        "audio_segments": audio_segments,
        "background_music": ""
    }
```

### 注意事项

1. **音频处理差异**
   - **viduq3**: 视频文件本身包含对话和音效。通常不需要 `audio_segments`，除非需要叠加额外的背景旁白或BGM。
   - **viduq2**: 视频文件是无声的（或仅有BGM）。必须通过 `audio_segments` 添加 TTS 生成的对话音频。

2. **时间连续性**
   - 确保视频片段的时间轴连续，无间隙。

3. **音频同步**
   - 若使用外部音频（viduq2），音频开始时间应比视频稍晚，给画面留出展示时间。

4. **URL有效期**
   - Vidu生成的视频和音频URL有效期24小时。
