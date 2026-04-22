---
name: huo15-influencer-video-skill
displayName: 火15 AI带货视频生成
description: 通过火山方舟Ark API调用Seedance 2.0，产品图一键生成第一人称带货短视频。支持自定义人物、动作、场景，默认传统服饰中年女性展示产品。触发词：生成视频、带货视频、产品视频、拍视频。
version: 1.0.0
aliases:
  - 带货视频
  - AI视频生成
  - 产品视频
---

# 火15 AI 带货视频生成 Skill

> 通过火山方舟 Ark API 调用 Seedance 2.0，产品图 → 第一人称带货短视频

---

## ⚠️ 安全规则

1. 每次生成前**必须**告知用户预估费用
2. 用户确认后才可提交任务
3. 单次最大时长 15 秒，默认 5 秒
4. 优先使用最省 Token 的配置

---

## 一、API 凭证

| 参数 | 值 |
|------|---|
| API Key | 环境变量 `ARK_API_KEY`（从方舟控制台获取） |
| 模型 | `doubao-seedance-2-0-260128` |
| 端点 | `https://ark.cn-beijing.volces.com/api/v3` |
| 认证 | `Authorization: Bearer {ARK_API_KEY}` |

---

## 二、计费

```
Token = 秒数 × 720 × 1280 × 24 / 1024
费用 = Token × ¥46 / 1,000,000
```

| 时长 | Token | 费用 |
|------|-------|------|
| 4秒 | ~86,400 | ¥3.97 |
| **5秒** | **~108,000** | **¥4.97** |
| 10秒 | ~216,000 | ¥9.94 |
| 15秒 | ~324,000 | ¥14.90 |

---

## 三、提示词规范

### 固定模板

```
第一人称视角带货短视频。一位身穿中式传统服饰的中年女性，手持图片中的产品，{展示动作}。{灯光和环境}。
```

### 默认提示词（无需用户额外描述）

```
第一人称视角带货短视频。一位身穿中式传统服饰的中年女性，手持图片中的产品，面带微笑展示给镜头。柔和暖色灯光，背景干净简约。
```

### 规则

1. **视角**：固定第一人称，不改
2. **人物**：默认"身穿中式传统服饰的中年女性"，用户可覆盖
3. **产品**：固定说"图片中的产品"，不用文字描述产品，让 AI 从 `reference_image` 自动识别
4. **动作**：默认"面带微笑展示给镜头"，用户可自定义
5. **环境**：默认"柔和暖色灯光，背景干净简约"

### 用户自定义时的拼接逻辑

用户只需提供变化的部分，Agent 自动拼接：

```python
# 默认值
VIEW = "第一人称视角带货短视频"
CHARACTER = "一位身穿中式传统服饰的中年女性"
PRODUCT = "手持图片中的产品"
ACTION = "面带微笑展示给镜头"
SCENE = "柔和暖色灯光，背景干净简约"

# 拼接
prompt = f"{VIEW}。{CHARACTER}，{PRODUCT}，{ACTION}。{SCENE}。"
```

用户可能的自定义示例：
- "换成年轻男性" → 覆盖 CHARACTER
- "放在桌子上展示" → 覆盖 ACTION
- "户外自然光" → 覆盖 SCENE
- "加上点头动作" → 追加到 ACTION

---

## 四、API 调用

### 4.1 创建任务

```bash
POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
Authorization: Bearer {API_KEY}
Content-Type: application/json
```

### 标准请求体（产品图做参考）

```json
{
    "model": "doubao-seedance-2-0-260128",
    "content": [
        {
            "type": "text",
            "text": "第一人称视角带货短视频。一位身穿中式传统服饰的中年女性，手持图片中的产品，面带微笑展示给镜头。柔和暖色灯光，背景干净简约。"
        },
        {
            "type": "image_url",
            "image_url": {"url": "data:image/jpeg;base64,{BASE64}"},
            "role": "reference_image"
        }
    ],
    "ratio": "9:16",
    "duration": 5,
    "watermark": false
}
```

### 产品图做首帧（视频从产品图开始）

```json
{
    "model": "doubao-seedance-2-0-260128",
    "content": [
        {
            "type": "text",
            "text": "第一人称视角带货短视频。一位身穿中式传统服饰的中年女性，手持图片中的产品，面带微笑展示给镜头。柔和暖色灯光，背景干净简约。"
        },
        {
            "type": "image_url",
            "image_url": {"url": "data:image/jpeg;base64,{BASE64}"},
            "role": "first_frame"
        }
    ],
    "ratio": "9:16",
    "duration": 5,
    "watermark": false
}
```

### 全要素（图+视频+音频参考）

```json
{
    "model": "doubao-seedance-2-0-260128",
    "content": [
        {"type": "text", "text": "提示词"},
        {"type": "image_url", "image_url": {"url": "产品图URL"}, "role": "reference_image"},
        {"type": "video_url", "video_url": {"url": "参考视频URL"}, "role": "reference_video"},
        {"type": "audio_url", "audio_url": {"url": "背景音乐URL"}, "role": "reference_audio"}
    ],
    "generate_audio": true,
    "ratio": "9:16",
    "duration": 10,
    "watermark": false
}
```

### 返回

```json
{"id": "cgt-20260414xxxxx-xxxxx"}
```

### 4.2 查询任务

```bash
GET https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}
Authorization: Bearer {API_KEY}
```

### 返回（成功）

```json
{
    "id": "cgt-xxx",
    "status": "succeeded",
    "content": {
        "video_url": "https://...mp4?签名..."
    },
    "usage": {"total_tokens": 108900},
    "resolution": "720p",
    "duration": 5,
    "framespersecond": 24
}
```

> ⚠️ `content` 是 **dict**，不是 list。`content.video_url` 直接是字符串。

`status`: `running` → `succeeded` / `failed`

### 4.3 视频续写

请求加 `"return_last_frame": true`，返回含 `content.last_frame_url`，可作为下段视频的 `first_frame`。

---

## 五、顶层参数速查

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `model` | string | - | `doubao-seedance-2-0-260128` |
| `content` | array | - | text + 图/视频/音频 |
| `ratio` | string | `9:16` | 竖屏带货固定 9:16 |
| `duration` | int | 5 | 时长 4~15 秒 |
| `watermark` | bool | false | 不加水印 |
| `generate_audio` | bool | false | 生成配套音频 |
| `return_last_frame` | bool | false | 返回最后一帧 |

> ⚠️ 参数在**顶层**，不在 `extra` 里！

---

## 六、content 中的 role

| role | 用途 | 推荐场景 |
|------|------|---------|
| `reference_image` | 多模态参考 | **默认用这个**，AI 保持产品外观一致性 |
| `first_frame` | 视频首帧 | 视频必须从这张图开始 |
| `last_frame` | 视频尾帧 | 指定结束画面 |
| `reference_video` | 视频参考 | 运动风格参考 |
| `reference_audio` | 音频参考 | 背景音乐/声音风格 |

---

## 七、Python 完整工具函数

```python
import base64, json, time, requests, os

ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
assert ARK_API_KEY, "请设置环境变量 ARK_API_KEY"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
HEADERS = {
    "Authorization": f"Bearer {ARK_API_KEY}",
    "Content-Type": "application/json"
}

# 默认提示词组件
DEFAULT_VIEW = "第一人称视角带货短视频"
DEFAULT_CHARACTER = "一位身穿中式传统服饰的中年女性"
DEFAULT_PRODUCT = "手持图片中的产品"
DEFAULT_ACTION = "面带微笑展示给镜头"
DEFAULT_SCENE = "柔和暖色灯光，背景干净简约"


def build_prompt(character=None, action=None, scene=None):
    """构建提示词，用户只需覆盖想改的部分"""
    c = character or DEFAULT_CHARACTER
    a = action or DEFAULT_ACTION
    s = scene or DEFAULT_SCENE
    return f"{DEFAULT_VIEW}。{c}，{DEFAULT_PRODUCT}，{a}。{s}。"


def estimate_cost(duration=5):
    """预估费用"""
    tokens = duration * 720 * 1280 * 24 / 1024
    cost = tokens * 46 / 1000000
    return tokens, cost


def generate_video(image_path, duration=5, output="output.mp4",
                   character=None, action=None, scene=None,
                   role="reference_image"):
    """一键生成带货视频

    Args:
        image_path: 产品图路径
        duration: 时长 4~15 秒（默认 5）
        output: 输出文件名
        character: 自定义人物（默认传统服饰中年女性）
        action: 自定义动作（默认微笑展示）
        scene: 自定义场景（默认暖光简约）
        role: 图片角色（默认 reference_image）
    """
    prompt = build_prompt(character, action, scene)
    tokens, cost = estimate_cost(duration)
    print(f"提示词: {prompt}")
    print(f"预估: {tokens:,.0f} Token ≈ ¥{cost:.2f}")

    # 读取产品图
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(image_path)[1].lstrip(".")
    if ext == "jpg":
        ext = "jpeg"

    body = {
        "model": "doubao-seedance-2-0-260128",
        "content": [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/{ext};base64,{img_b64}"},
                "role": role
            }
        ],
        "ratio": "9:16",
        "duration": duration,
        "watermark": False
    }

    # 提交
    resp = requests.post(
        f"{BASE_URL}/contents/generations/tasks",
        headers=HEADERS, json=body
    )
    result = resp.json()
    if "id" not in result:
        print(f"❌ 提交失败: {result}")
        return None

    task_id = result["id"]
    print(f"✅ task_id: {task_id}")

    # 轮询（每 10 秒查一次，最多 15 分钟）
    for _ in range(90):
        time.sleep(10)
        r = requests.get(
            f"{BASE_URL}/contents/generations/tasks/{task_id}",
            headers=HEADERS
        )
        data = r.json()
        status = data.get("status", "?")
        print(f"  [{time.strftime('%H:%M:%S')}] {status}")

        if status == "succeeded":
            video_url = data["content"]["video_url"]
            vr = requests.get(video_url, stream=True)
            with open(output, "wb") as f:
                for chunk in vr.iter_content(8192):
                    f.write(chunk)
            actual_tokens = data["usage"]["total_tokens"]
            actual_cost = actual_tokens * 46 / 1000000
            print(f"\n✅ {output} ({os.path.getsize(output)/1024/1024:.1f}MB)")
            print(f"   Token: {actual_tokens:,} | 费用: ¥{actual_cost:.2f}")
            return output
        elif status == "failed":
            print(f"❌ 失败: {data}")
            return None

    print("⏰ 超时（15 分钟）")
    return None


# 使用示例
if __name__ == "__main__":
    # 最简调用 — 只需产品图
    generate_video("产品图.jpg", output="带货视频.mp4")

    # 自定义人物
    generate_video("产品图.jpg", character="一位年轻时尚的中国女性", output="年轻版.mp4")

    # 自定义动作
    generate_video("产品图.jpg", action="缓缓转动产品展示各角度细节", output="转动版.mp4")

    # 10 秒长视频
    generate_video("产品图.jpg", duration=10, output="10秒版.mp4")
```

---

## 八、Agent 工作流

当用户说"帮我生成一个带货视频"时：

1. **获取产品图**：用户提供图片路径
2. **确认参数**：时长（默认5秒）、是否自定义人物/动作/场景
3. **告知费用**：`estimate_cost(duration)` 并等用户确认
4. **生成视频**：`generate_video(image_path, ...)`
5. **交付结果**：告知文件路径、实际费用

### 对话示例

```
用户: 帮我用这张图生成带货视频
Agent: 收到！将为您生成 5 秒竖屏带货视频。
       预估费用：~108,000 Token ≈ ¥4.97
       确认生成吗？
用户: 好的
Agent: [调用 generate_video] → 视频已生成：xxx.mp4 (1.9MB)，实际费用 ¥5.01
```

---

## 九、常见问题

### Q: ModelNotOpen 错误
A: 方舟控制台 → 在线推理 → 推理接入点，创建 `doubao-seedance-2-0-260128` 的接入点。

### Q: 生成多久？
A: 5 秒 ≈ 3~6 分钟，10 秒 ≈ 7~10 分钟。

### Q: 图片怎么传？
A: `data:image/jpeg;base64,...` data URI，无需先上传。

### Q: reference_image 和 first_frame 区别？
A: `reference_image` AI 参考产品外观自由创作（**推荐**）；`first_frame` 视频必须从这张图开始。
