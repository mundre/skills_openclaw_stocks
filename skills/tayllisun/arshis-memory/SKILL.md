---
name: Arshis-memory-pro
description: Advanced memory management system with multi-provider LLM support (SiliconFlow/DashScope/Jina/OpenAI/Cohere/Voyage/Google/Claude/Ollama), auto-failover, hybrid retrieval, and self-evolution.
version: 3.1.0
author: Arshis
license: MIT-0
---

# Arshis-memory-pro v3.0.0

**Advanced Memory Management System with Multi-Provider Support**

---

## 🎯 New Features in v3.0.0

### 1. Multi-Provider LLM Support 🌍

**Supported Providers**:
- ✅ **SiliconFlow** (Default)
  - Embedding: BAAI/bge-m3 (1024 dim)
  - Rerank: BAAI/bge-reranker-v2-m3
  - LLM: Qwen/Qwen2.5-72B-Instruct

- ✅ **DashScope** (Alibaba)
  - Embedding: text-embedding-v3 (1536 dim)
  - Rerank: gte-rerank
  - LLM: qwen-max

- ✅ **OpenAI** (Optional)
  - Embedding: text-embedding-3-small (1536 dim)
  - LLM: gpt-4o-mini

- ✅ **Claude** (Optional)
  - LLM: claude-3-5-sonnet-20241022

- ✅ **Ollama** (Local)
  - Embedding: nomic-embed-text (768 dim)
  - LLM: qwen2.5:7b

### 2. Auto-Failover 🔄

**Automatic Provider Switching**:
- ✅ Primary provider fails → Auto-switch to backup
- ✅ Configurable priority order
- ✅ Timeout protection
- ✅ Health check monitoring

**Configuration Example**:
```json
{
  "embedding": {
    "provider": "auto",
    "autoFailover": true,
    "providers": {
      "siliconflow": { "priority": 1 },
      "dashscope": { "priority": 2 },
      "openai": { "priority": 3 }
    }
  }
}
```

### 3. Environment Variable Support 🔐

**Secure API Key Management**:
```json
{
  "embedding": {
    "providers": {
      "dashscope": {
        "apiKey": "${DASHSCOPE_API_KEY}"
      },
      "openai": {
        "apiKey": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

**Usage**:
```bash
export DASHSCOPE_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

---

## 📊 Core Features (Unchanged)

### 1. Hybrid Retrieval
- Vector similarity (70%) + BM25 (30%)
- Cross-Encoder reranking
- +15-20% accuracy improvement

### 2. Smart Extraction
- Auto-summary (20 chars)
- Auto-keywords (3-5)
- Auto-categorization
- Importance scoring (0-1)

### 3. Lifecycle Management
- Weibull decay model
- Category-specific decay rates
- Knowledge: 2%/year
- Characters: 10%/year
- Preferences: 30%/year
- Events: 90% decay

### 4. Self-Evolution
- Auto feedback collection
- Parameter optimization
- Pattern learning
- Continuous improvement

### 5. Short-Term Memory
- 50 items max
- 2-hour expiry
- Auto-expire
- Priority filtering

### 6. Dreaming Mode
- Sleep memory consolidation
- Morning brief
- Creative incubation

---

## 🔧 Configuration

### Multi-Provider Config

**File**: `/root/.openclaw/data/memory-custom-config-multi.json`

**Quick Start**:
```bash
# Copy multi-provider template
cp memory-custom-config-multi.json memory-custom-config.json

# Edit configuration
nano memory-custom-config.json

# Set environment variables
export DASHSCOPE_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

### Provider Priority

**Default Order**:
1. SiliconFlow (Primary)
2. DashScope (Backup)
3. OpenAI (Optional)
4. Claude (Optional)
5. Ollama (Local)

**Change Priority**:
```json
{
  "embedding": {
    "providers": {
      "dashscope": { "priority": 1 },
      "siliconflow": { "priority": 2 }
    }
  }
}
```

---

## 📈 Performance Comparison

| Provider | Embedding Speed | LLM Speed | Cost | Accuracy |
|---|---|---|---|---|
| **SiliconFlow** | Fast | Fast | Low | High |
| **DashScope** | Fast | Fast | Medium | High |
| **OpenAI** | Medium | Medium | High | Very High |
| **Claude** | N/A | Slow | Very High | Very High |
| **Ollama** | Slow | Slow | Free | Medium |

---

## 🎯 Usage Examples

### Example 1: Store Memory

```python
from memory_core import MemoryAPI

api = MemoryAPI()

# Store with auto-provider
api.store("User prefers coffee over tea", 0.8, "preference")

# Auto-failover if primary fails
# Falls back to secondary provider
```

### Example 2: Recall Memory

```python
# Search with hybrid retrieval
results = api.recall("What does user like to drink?", limit=5)

# Results ranked by:
# 1. Vector similarity
# 2. BM25 keyword match
# 3. Cross-Encoder rerank
```

### Example 3: Provider Status

```python
# Check provider health
status = api.get_provider_status()

# Output:
# {
#   "siliconflow": "healthy",
#   "dashscope": "healthy",
#   "openai": "unavailable"
# }
```

---

## 🔍 Troubleshooting

### Issue 1: Provider Fails

**Symptom**: API timeout/error

**Solution**:
```json
{
  "embedding": {
    "autoFailover": true,
    "timeout": 30
  }
}
```

### Issue 2: API Key Error

**Symptom**: 401 Unauthorized

**Solution**:
```bash
# Check environment variable
echo $DASHSCOPE_API_KEY

# Update config
"apiKey": "${DASHSCOPE_API_KEY}"
```

### Issue 3: Slow Response

**Symptom**: High latency

**Solution**:
```json
{
  "embedding": {
    "providers": {
      "siliconflow": { "priority": 1 },
      "ollama": { "priority": 2 }
    }
  }
}
```

---

## 📝 Version History

### v3.0.0 (2026-04-22)
- ✅ Multi-provider LLM support
- ✅ Auto-failover mechanism
- ✅ Environment variable support
- ✅ Provider health monitoring
- ✅ Configurable priority order

### v2.0.0 (2026-04-15)
- ✅ Self-evolution system
- ✅ Short-term memory
- ✅ Dreaming mode
- ✅ Hybrid retrieval

### v1.0.0 (2026-04-13)
- ✅ Initial release
- ✅ Basic memory storage
- ✅ Vector retrieval

---

## 🦊 Support

**GitHub**: https://github.com/Arshis/Arshis-Memory-Pro  
**Issues**: https://github.com/Arshis/Arshis-Memory-Pro/issues  
**Author**: Arshis  
**License**: MIT-0

---

*Arshis-memory-pro v3.0.0*  
*Make memory management more professional, efficient, and provider-agnostic!*
