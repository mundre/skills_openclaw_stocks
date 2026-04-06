# BlueAI 图像生成指南

## 概述

BlueAI 代理支持多种图像生成模型，其中 Gemini 图像模型通过 **Chat Completions** 接口生图（非传统 Images API），使用方式与普通对话一致，模型在回复中直接返回 base64 编码的图片。

## Gemini 图像生成模型

| 模型ID | 上下文 | 特点 | 推荐场景 |
|--------|--------|------|---------|
| `gemini-3.1-flash-image-preview` | 131K | Flash 速度，成本低 | 快速原型、批量生图 |
| `gemini-3-pro-image-preview` | 65K | Pro 品质，细节更好 | 高质量创意图 |
| `gemini-2.5-flash-image` | 32K | 支持图编辑 | 图像编辑/修改 |

## 使用方式

### 通过 Chat Completions 接口

Gemini 图像模型走标准 `/v1/chat/completions` 端点，**不需要**用 `/v1/images/generations`。

```bash
curl -s https://bmc-llm-relay.bluemediagroup.cn/v1/chat/completions \
  -H "Authorization: Bearer $BLUEAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-flash-image-preview",
    "messages": [
      {"role": "user", "content": "画一只穿着宇航服的猫，卡通风格"}
    ],
    "max_tokens": 4096
  }'
```

### 响应格式

模型返回的 `content` 是 Markdown 格式，图片以 base64 嵌入：

```
![image](data:image/png;base64,iVBORw0KGgo...)
```

有时也会伴随文字描述。

### 提取图片（Python）

```python
import json, base64, re, urllib.request

def generate_image(prompt, model="gemini-3.1-flash-image-preview", api_key=""):
    """通过 Gemini 图像模型生成图片，返回 PNG bytes"""
    url = "https://bmc-llm-relay.bluemediagroup.cn/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )
    resp = urllib.request.urlopen(req, timeout=120)
    data = json.loads(resp.read())
    content = data["choices"][0]["message"]["content"]

    # 提取 base64 图片
    match = re.search(r'data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)', content)
    if match:
        return base64.b64decode(match.group(2)), match.group(1)
    return None, None

# 用法
img_bytes, fmt = generate_image("一只穿宇航服的猫", api_key="sk-xxx")
if img_bytes:
    with open(f"output.{fmt}", "wb") as f:
        f.write(img_bytes)
```

## 与 OpenAI 图像模型的区别

| 特性 | Gemini 图像模型 | GPT Image / DALL-E |
|------|----------------|-------------------|
| 接口 | `/v1/chat/completions` | `/v1/images/generations` |
| 输入 | 对话消息（可多轮） | 单次 prompt |
| 输出 | Markdown 中嵌 base64 | JSON 中 b64_json 或 url |
| 图片编辑 | ✅ 发送图片+指令即可 | 需要 mask 参数 |
| 多轮对话 | ✅ 可基于上文迭代修改 | ❌ 每次独立 |
| 中文 prompt | ✅ 原生支持 | ⚠️ 效果一般 |

## Prompt 技巧

1. **明确风格**：「卡通风格」「写实照片」「水彩画风」「赛博朋克风」
2. **指定细节**：颜色、构图、光线、背景
3. **中文直接写**：Gemini 对中文 prompt 理解很好，不需要翻译成英文
4. **迭代修改**：可以在多轮对话中要求「把背景换成蓝色」「加一顶帽子」

## 图片编辑（gemini-2.5-flash-image / gemini-3-pro-image-preview）

支持发送图片 + 修改指令：

```json
{
  "model": "gemini-3-pro-image-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,<原图base64>"}},
        {"type": "text", "text": "把背景改成星空"}
      ]
    }
  ],
  "max_tokens": 4096
}
```

## OpenClaw 配置

添加到 `openclaw.json`：

```json
{
  "id": "gemini-3.1-flash-image-preview",
  "name": "Gemini 3.1 Flash Image",
  "api": "openai-completions",
  "reasoning": false,
  "input": ["text", "image"],
  "cost": {"input": 0.15, "output": 3.5},
  "contextWindow": 131072,
  "maxTokens": 32768
}
```

或使用脚本：
```bash
python3 scripts/add_model.py gemini-3.1-flash-image-preview
python3 scripts/add_model.py gemini-3-pro-image-preview
openclaw gateway restart
```

## 测试

```bash
python3 scripts/test_model.py gemini-3.1-flash-image-preview --image-gen
python3 scripts/test_model.py gemini-3-pro-image-preview --image-gen
```
