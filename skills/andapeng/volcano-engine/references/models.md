# Volcengine Models Reference

Complete list of available models on Volcano Engine platform.

## General Models (volcengine provider)

Endpoint: `https://ark.cn-beijing.volces.com/api/v3`

| Model ID | Full Name | Provider | Input | Context | Max Output | Reasoning | Notes |
|----------|-----------|----------|-------|---------|------------|-----------|-------|
| `doubao-seed-1-8-251228` | Doubao Seed 1.8 | volcengine | text, image | 256,000 | 8,192 | No | ByteDance's flagship model, multilingual support |
| `doubao-seed-code-preview-251028` | Doubao Seed Code Preview | volcengine | text, image | 256,000 | 8,192 | No | Early access to coding capabilities |
| `kimi-k2-5-260127` | Kimi K2.5 | volcengine | text, image | 256,000 | 8,192 | No | Moonshot AI, strong reasoning |
| `glm-4-7-251222` | GLM 4.7 | volcengine | text, image | 200,000 | 8,192 | No | Zhipu AI, good Chinese understanding |
| `deepseek-v3-2-251201` | DeepSeek V3.2 | volcengine | text, image | 128,000 | 8,192 | No | DeepSeek, cost-effective |

## Coding Models (volcengine-plan provider)

Endpoint: `https://ark.cn-beijing.volces.com/api/coding/v3`

| Model ID | Full Name | Provider | Input | Context | Max Output | Reasoning | Notes |
|----------|-----------|----------|-------|---------|------------|-----------|-------|
| `ark-code-latest` | Ark Coding Plan | volcengine-plan | text | 256,000 | 8,192 | No | Optimized for programming tasks |
| `doubao-seed-code` | Doubao Seed Code | volcengine-plan | text | 256,000 | 8,192 | No | ByteDance's specialized coding model |
| `glm-4.7` | GLM 4.7 Coding | volcengine-plan | text | 200,000 | 8,192 | No | Zhipu AI coding variant |
| `kimi-k2-thinking` | Kimi K2 Thinking | volcengine-plan | text | 256,000 | 8,192 | Yes | Moonshot's reasoning model |
| `kimi-k2.5` | Kimi K2.5 Coding | volcengine-plan | text | 256,000 | 8,192 | No | Moonshot coding variant |
| `doubao-seed-code-preview-251028` | Doubao Seed Code Preview | volcengine-plan | text | 256,000 | 8,192 | No | Same as general but on coding endpoint |

## Model Selection Guide

### By Use Case

| Task Type | Recommended Model | Alternative | Why |
|-----------|------------------|-------------|-----|
| **General Chat** | `doubao-seed-1-8-251228` | `glm-4-7-251222` | Balanced performance, multilingual |
| **Code Generation** | `ark-code-latest` | `doubao-seed-code` | Optimized for programming |
| **Code Review** | `kimi-k2-thinking` | `ark-code-latest` | Better reasoning capabilities |
| **Chinese Content** | `glm-4-7-251222` | `doubao-seed-1-8-251228` | Native Chinese understanding |
| **Multimodal** | `doubao-seed-1-8-251228` | `kimi-k2-5-260127` | Image + text support |
| **Cost-sensitive** | `deepseek-v3-2-251201` | `glm-4-7-251222` | Lower cost per token |

### By Context Length

| Context Needed | Recommended Model | Context Window |
|----------------|------------------|----------------|
| **Short (<50K)** | Any | All models support |
| **Medium (50-128K)** | `deepseek-v3-2-251201` | 128,000 |
| **Long (128-200K)** | `glm-4-7-251222` | 200,000 |
| **Very Long (200K+)** | `doubao-seed-1-8-251228` | 256,000 |

## Model Capabilities

### Multimodal Support

Models with **image** input can process:
- PNG, JPEG, WebP images
- Base64 encoded images
- Image URLs (if accessible)
- Combined text and image prompts

### Reasoning Capabilities

Only `kimi-k2-thinking` has explicit reasoning support. However, all models have some reasoning ability for their primary tasks.

### Language Support

- **Doubao models**: Strong Chinese, good English, basic other languages
- **GLM models**: Excellent Chinese, moderate English
- **Kimi models**: Good Chinese and English
- **DeepSeek models**: Strong English, good Chinese

## API Parameters

All models support standard OpenAI-compatible parameters:

```json
{
  "model": "doubao-seed-1-8-251228",
  "messages": [...],
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 2048,
  "stream": false
}
```

### Token Usage Details

Response includes detailed token usage:

```json
{
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150,
    "completion_tokens_details": {
      "reasoning_tokens": 20
    }
  }
}
```

- **prompt_tokens**: Input tokens consumed
- **completion_tokens**: Output tokens generated
- **reasoning_tokens**: Tokens used for reasoning chain (reasoning models only)

### Streaming Responses

Enable streaming for real-time output:

```json
{
  "model": "doubao-seed-1-8-251228",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": true
}
```

Streaming responses return `chat.completion.chunk` objects with incremental content.

### Recommended Settings

| Task | Temperature | Max Tokens | Notes |
|------|-------------|------------|-------|
| Creative writing | 0.8-1.0 | 1024-4096 | Higher for more varied output |
| Code generation | 0.2-0.5 | 2048-8192 | Lower for more deterministic code |
| Analysis | 0.3-0.7 | 512-2048 | Balanced for accuracy |
| Translation | 0.1-0.3 | Same as input | Low for faithful translation |

## Rate Limits

Check current rate limits in the [Volcano Engine Console](https://console.volcengine.com/ark). Typical limits:

- Free tier: 100 requests/hour
- Basic tier: 1000 requests/hour
- Professional tier: Custom limits

## Version History

Models are periodically updated. Check for new versions in:
1. Volcano Engine Console
2. [API Documentation](https://www.volcengine.com/docs/82379)
3. OpenClaw provider updates

### Recent Updates

- **2026-03**: Added `kimi-k2-5-260127`
- **2025-12**: Added `glm-4-7-251222`
- **2025-12**: Added `deepseek-v3-2-251201`
- **2025-10**: Added coding models endpoint

## Troubleshooting Model Issues

### "Model not found" Error

1. Verify model ID spelling (case-sensitive)
2. Check if model exists in your region
3. Ensure correct provider endpoint
4. Try listing available models via API

### Poor Performance

1. Adjust temperature (lower = more deterministic)
2. Increase max_tokens if responses are cut off
3. Provide clearer instructions in system prompt
4. Try different model for specific task

### High Latency

1. Check network connection to Beijing region
2. Reduce request size (fewer tokens)
3. Use streaming for long responses
4. Contact support if persistent
