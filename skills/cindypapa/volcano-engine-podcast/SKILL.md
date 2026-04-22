---
name: volcano-engine-podcast
description: 生成火山引擎豆包语音播客（PodcastTTS）。输入主题文本，自动生成双人对话式播客音频。触发关键词：豆包语音播客、生成播客、语音播客。
version: 1.1.0
author: xiaohe + kamei
license: MIT
metadata:
  openclaw:
    homepage: https://github.com/Cindypapa/volcano-engine-podcast
    requires:
      bins:
        - python3
      packages:
        - websockets>=14.0
---

# 火山引擎豆包语音播客生成

基于火山引擎 PodcastTTS API，输入主题文本，AI 自动生成双人对话播客音频（含片头音乐、多轮对话、片尾结束）。

---

## 🎯 触发条件

用户提到以下关键词时触发：
- "用豆包语音播客帮我生成..."
- "生成语音播客"
- "豆包播客"
- "PodcastTTS"

---

## 🔄 收到请求后流程

**⚠️ 重要：收到用户请求后，必须先询问是否有参考资料！**

### 步骤 1：询问参考资料

```
用户：用豆包语音播客帮我生成XX主题的语音播客

助手回复：
收到！请选择资料来源：

1️⃣ **有参考资料**
   - 请发送相关文档、链接或已有内容
   - 我会基于资料生成播客

2️⃣ **没有参考资料**
   - 直接按你提供的主题生成播客
   - AI 会自动扩展内容

请回复 "1" 或 "2"，或直接发送资料（文档/链接）
```

### 步骤 2：生成播客

- **有资料**：先读取资料内容，整合后生成播客
- **无资料**：直接使用主题文本生成播客

### 步骤 3：发送音频

生成完成后，**必须把 MP3 文件发送给用户**：

```
<qqvoice>/root/.openclaw/media/qqbot/downloads/播客名称.mp3</qqvoice>
```

---

## 📋 配置

火山引擎播客 API 配置：

```json
// ~/.openclaw/config.json
{
  "volc_podcast": {
    "appid": "3398567544",
    "access_key": "your_access_key",
    "secret_key": "your_secret_key"
  }
}
```

---

## 🔧 调用方式

### 快速调用（推荐）

```python
import asyncio
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills/volcano-engine-podcast/scripts")
from generate_podcast import PodcastGenerator

async def generate_podcast(text, output_name="podcast"):
    gen = PodcastGenerator(
        appid="3398567544",
        access_token="your_token",
    )
    
    result = await gen.generate(
        text=text,
        output_dir=f"/tmp/{output_name}",
        encoding="mp3",
        use_head_music=True,
    )
    
    if result["success"]:
        # 复制到发送目录
        import shutil
        src = result["final_files"][0]
        dst = f"/root/.openclaw/media/qqbot/downloads/{output_name}.mp3"
        shutil.copy(src, dst)
        return dst
    
    return None

# 使用
audio_path = await generate_podcast("今天来聊聊AI编程助手", "AI编程助手播客")
```

---

## 📊 返回结果

```python
{
    "success": True,
    "duration": 135.99,           # 播客时长（秒）
    "final_files": ["...mp3"],    # 最终音频文件
    "texts": [...],               # 对话文本列表
    "usage": {                    # Token 消耗
        "input_text_tokens": 1245,
        "output_audio_tokens": 3217,
        "total_tokens": 4462
    }
}
```

---

## ⚙️ 参数说明

| 参数 | 默认 | 说明 |
|------|------|------|
| `text` | 必填 | 输入主题文本 |
| `encoding` | mp3 | 音频格式 |
| `use_head_music` | True | 片头音乐 |
| `use_tail_music` | False | 片尾音乐 |

---

## 📝 注意事项

1. 每次调用消耗 audio token
2. 对话角色由 AI 自动分配（男女双人对话）
3. 音频采样率 24kHz
4. 生成后必须发送 MP3 给用户