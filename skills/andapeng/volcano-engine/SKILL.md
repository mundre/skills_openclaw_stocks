---
name: volcengine
description: Configure and use Volcano Engine (Volcengine) models including Doubao, GLM, Kimi, and DeepSeek. Use when: (1) Setting up Volcengine API access in OpenClaw, (2) Choosing between general vs coding endpoints, (3) Configuring model aliases for easy access, (4) Troubleshooting authentication or connection issues with Volcengine providers.
---

# Volcengine Skill

Configure and use Volcano Engine (Volcengine) models with OpenClaw. This skill covers both general-purpose models and specialized coding models through Volcengine's OpenAI-compatible API endpoints.

## Quick Start

### 1. Get API Key

1. Sign up at [Volcano Engine Console](https://console.volcengine.com/ark)
2. Navigate to **Access Key Management**
3. Create a new API key with appropriate permissions
4. Copy the API key (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`，**无需添加sk-前缀**)

### 2. Configure OpenClaw

#### Interactive setup (recommended)

```bash
openclaw onboard --auth-choice volcengine-api-key
```

Follow the prompts to enter your API key.

#### Manual config (openclaw.json)

Add to your `openclaw.json`:

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "volcengine": {
        "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
        "api": "openai-completions",
        "apiKey": "your-api-key-here",
        "models": [
          {
            "id": "doubao-seed-1-8-251228",
            "name": "Doubao Seed 1.8",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 0, "output": 0 },
            "contextWindow": 256000,
            "maxTokens": 8192
          },
          {
            "id": "glm-4-7-251222",
            "name": "GLM 4.7",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 0, "output": 0 },
            "contextWindow": 200000,
            "maxTokens": 8192
          }
        ]
      },
      "volcengine-plan": {
        "baseUrl": "https://ark.cn-beijing.volces.com/api/coding/v3",
        "api": "openai-completions",
        "apiKey": "your-api-key-here",
        "models": [
          {
            "id": "ark-code-latest",
            "name": "Ark Coding Plan",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0 },
            "contextWindow": 256000,
            "maxTokens": 8192
          }
        ]
      }
    }
  }
}
```

### 3. Set Model Aliases (Optional)

For easier access, add aliases to `agents.defaults.models`:

```json
{
  "agents": {
    "defaults": {
      "models": {
        "volcengine/doubao-seed-1-8-251228": {
          "alias": "Doubao"
        },
        "volcengine-plan/ark-code-latest": {
          "alias": "ArkCode"
        },
        "volcengine/glm-4-7-251222": {
          "alias": "GLM4"
        }
      }
    }
  }
}
```

## Available Models

### General Models (volcengine provider)

| Model ID | Name | Input | Context | Description |
|----------|------|-------|---------|-------------|
| `doubao-seed-1-8-251228` | Doubao Seed 1.8 | text, image | 256,000 | ByteDance's flagship model |
| `doubao-seed-code-preview-251028` | Doubao Seed Code Preview | text, image | 256,000 | Code-focused preview |
| `kimi-k2-5-260127` | Kimi K2.5 | text, image | 256,000 | Moonshot AI's model |
| `glm-4-7-251222` | GLM 4.7 | text, image | 200,000 | Zhipu AI's model |
| `deepseek-v3-2-251201` | DeepSeek V3.2 | text, image | 128,000 | DeepSeek's model |

### Coding Models (volcengine-plan provider)

| Model ID | Name | Input | Context | Description |
|----------|------|-------|---------|-------------|
| `ark-code-latest` | Ark Coding Plan | text | 256,000 | Optimized for coding tasks |
| `doubao-seed-code` | Doubao Seed Code | text | 256,000 | ByteDance's coding model |
| `glm-4.7` | GLM 4.7 Coding | text | 200,000 | Zhipu's coding model |
| `kimi-k2-thinking` | Kimi K2 Thinking | text | 256,000 | Moonshot's reasoning model |
| `kimi-k2.5` | Kimi K2.5 Coding | text | 256,000 | Moonshot's coding model |

## Usage Examples

### Using via CLI

```bash
# Use Doubao model
openclaw --model Doubao "Hello, summarize this text"

# Use Ark Code for programming
openclaw --model ArkCode "Write a Python function to sort a list"

# Use full model reference
openclaw --model volcengine/doubao-seed-1-8-251228 "Explain quantum computing"
```

### Setting Default Model

```bash
# Set Doubao as default
openclaw configure --set agents.defaults.model.primary volcengine/doubao-seed-1-8-251228

# Set Ark Code as default for coding tasks  
openclaw configure --set agents.defaults.model.primary volcengine-plan/ark-code-latest
```

## Advanced Configuration

### Environment Variable

For better security, use environment variables:

```bash
# Set in your shell profile
export VOLCANO_ENGINE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  # 火山引擎密钥无需添加sk-前缀

# Reference in config
"apiKey": "VOLCANO_ENGINE_API_KEY"
```

### Custom Base URL

If you need a different region:

```json
{
  "volcengine": {
    "baseUrl": "https://ark.cn-shanghai.volces.com/api/v3",
    // ... rest of config
  }
}
```

## Troubleshooting

### Common Issues

1. **Authentication failed**
   - Verify API key is correct
   - Check if key has necessary permissions
   - Ensure key is not expired

2. **Connection timeout**
   - Verify network connectivity to `ark.cn-beijing.volces.com`
   - Check firewall settings
   - Try different region endpoint

3. **Model not found**
   - Verify model ID spelling
   - Check if model is available in your region
   - Ensure you're using correct provider (volcengine vs volcengine-plan)

4. **Rate limiting**
   - Check API usage quotas
   - Implement retry logic with exponential backoff
   - Consider upgrading plan for higher limits

### Testing Connection

```bash
# Test with curl
curl -X POST https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Authorization: Bearer $VOLCANO_ENGINE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-1-8-251228",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Cost Management

Volcano Engine uses token-based pricing. Check the [official pricing page](https://www.volcengine.com/product/ark/pricing) for current rates.

To monitor usage:
1. Visit [Volcano Engine Console](https://console.volcengine.com/ark)
2. Navigate to **Billing Center**
3. Check **Usage Details**

## Best Practices

1. **Model Selection**
   - Use `volcengine-plan/*` for coding tasks
   - Use `volcengine/*` for general conversation
   - Consider context window size for long documents

2. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys periodically
   - **Quota Limit**: Each account supports up to 50 API Keys
   - **Permission Control**: Restrict keys to specific Model IDs or IP addresses
   - **Project Isolation**: Keys only work within their project space

3. **Error Handling**
   - Implement retry logic for transient failures (429, 500, 502, 503, 504)
   - Log errors for debugging
   - Set up alerts for quota limits
   - Handle sensitive content detection errors (400 series)
   - See [Error Codes](configuration.md#error-handling) for complete list

4. **Performance**
   - Use streaming for long responses
   - Adjust temperature for creativity vs consistency
   - Set appropriate max_tokens to control response length

5. **Authentication Methods**
   - **API Key** (Recommended for most users): Simple bearer token authentication
   - **Access Key** (Enterprise): HMAC-SHA256 signature-based auth for fine-grained permissions
   - See [Configuration Guide](configuration.md#authentication-methods) for details

## Documentation Validation

This skill has been validated against official Volcano Engine API Reference PDF (2026-04-15). Key validation findings:

### ✅ Verified Configuration
- **API Key Format**: Correct bearer token authentication
- **Base URL**: Verified Beijing region endpoint (`ark.cn-beijing.volces.com`)
- **Error Codes**: Complete mapping of official error codes
- **Security Practices**: Quota limits (50 API keys), permission controls, project isolation

### 📋 PDF-Verified Information
Based on high-priority page extraction from official PDFs:

1. **API Key Management**:
   - Maximum 50 API keys per account
   - Keys can be restricted to specific Model IDs and IP addresses
   - Project space isolation (no cross-project access)

2. **Error Handling**:
   - Complete error code mapping for 400, 429, 401/403 errors
   - Sensitive content detection categories
   - Rate limiting error details

3. **API Architecture**:
   - Dual-track API (Data Plane vs Control Plane)
   - API version `2024-01-01`
   - Regional endpoint configurations

### 🔍 Validation Methodology
1. **PDF Analysis**: Extracted 6 high-priority pages from `volcengine-api-reference.pdf`
2. **Cross-Reference**: Compared existing documentation against official specifications
3. **Gap Analysis**: Identified missing information and prioritized updates
4. **Continuous Updates**: Documentation updated based on official sources

**Validation Status**: ✅ **High Confidence** - Configuration aligns with official documentation

## API Architecture

Volcano Engine uses a dual-track API architecture:

### Data Plane API (数据面API)
- **Purpose**: Direct business data transmission and real-time interaction
- **Base URL**: `https://ark.cn-beijing.volces.com/api/v3`
- **Use Cases**: Chat API, Responses API, model inference
- **Authentication**: API Key (Bearer token) or Access Key (HMAC-SHA256)

### Control Plane API (管控面API)
- **Purpose**: System resource management and configuration
- **Base URL**: `https://ark.cn-beijing.volcengineapi.com/`
- **Use Cases**: API Key management, endpoint configuration, model customization
- **Authentication**: Access Key signature required

### API Version
Current API version: `2024-01-01`

## Resources

- [Volcano Engine Official Documentation](https://www.volcengine.com/docs/82379)
- [API Reference](https://www.volcengine.com/docs/82379/1263693)
- [Console](https://console.volcengine.com/ark)
- [Community Support](https://forum.volcengine.com/)

---
*Documentation validated against official Volcano Engine API Reference PDF (2026-04-15) - High confidence verification completed*
