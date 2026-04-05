# Vision API Configuration

## Supported Providers

### 1. GPT-5.4-Mini (Default, Recommended)

Best balance of accuracy and cost.

```json
{
  "provider": "gpt-5.4-mini",
  "baseUrl": "https://api.gpt.ge/v1",
  "apiKey": "sk-xxx",
  "model": "gpt-5.4-mini"
}
```

Cost: ~$0.03 per task (10-20 screenshots)

### 2. GPT-5.4 CUA (Most Accurate)

OpenAI's dedicated Computer Use Agent model.

```json
{
  "provider": "gpt-5.4-cua",
  "baseUrl": "https://api.openai.com/v1",
  "apiKey": "sk-xxx",
  "model": "computer-use-preview"
}
```

Cost: ~$0.15 per task

### 3. Gemini 3.1 Pro (Cheapest)

Google's vision model, good for basic tasks.

```json
{
  "provider": "gemini",
  "apiKey": "xxx",
  "model": "gemini-3.1-pro"
}
```

Cost: ~$0.01 per task

### 4. Local Model (Free)

Using Ollama with a local vision model.

```json
{
  "provider": "local",
  "baseUrl": "http://localhost:11434",
  "model": "llama3.2-vision"
}
```

Cost: Free (requires GPU)

## API Call Format

The vision API is called with a screenshot + prompt:

```python
{
  "model": "<model>",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "<analysis_prompt>"},
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,<screenshot>"}}
    ]
  }],
  "max_tokens": 1500
}
```

## Prompt Templates

See `scripts/vision/prompt_templates/` for the prompt engineering details.
