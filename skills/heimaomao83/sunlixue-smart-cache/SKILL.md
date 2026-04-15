---
name: smart-cache
description: 本地智能缓存系统，为AI助手提供语义级别的请求缓存。当用户需要(1)减少重复API调用成本、(2)加速相似问题的响应、(3)创建本地缓存层来优化AI助手性能时使用此技能。支持精确匹配(L1)和语义相似匹配(L2)两种缓存模式。
---

# Smart Cache - 本地智能缓存系统

## 概述

Smart Cache是一个为OpenClaw/QClaw设计的本地智能缓存系统，通过缓存AI响应来减少API调用成本和响应时间。

**核心功能：**
- L1精确缓存：完全相同的请求直接返回缓存结果
- L2语义缓存：语义相似的请求返回相似结果
- 缓存管理：自动过期、容量限制、手动清理
- 成本追踪：记录节省的token和费用

## 快速开始

### 检查缓存状态

```python
python scripts/cache_manager.py status
```

### 查询缓存

```python
# 精确查询
python scripts/cache_manager.py query "你好，今天天气怎么样？"

# 语义查询（返回相似度 > 0.9 的结果）
python scripts/cache_manager.py query-semantic "今天天气如何？" --threshold 0.85
```

### 添加缓存

```python
python scripts/cache_manager.py add "你好" "你好！有什么可以帮助你的吗？"
```

### 清理缓存

```python
# 清理过期缓存
python scripts/cache_manager.py clean --expired

# 清理全部
python scripts/cache_manager.py clean --all

# 清理特定时间范围
python scripts/cache_manager.py clean --before "2024-01-01"
```

## 缓存模式

### L1 精确缓存 (Exact Cache)

适用于完全相同的请求。使用SHA256哈希作为key，O(1)查找时间。

**特点：**
- 100%准确率
- 零误判
- 适用于重复性问题

**示例：**
```
用户: "什么是Python？"
→ 缓存命中 → 直接返回缓存的回答
```

### L2 语义缓存 (Semantic Cache)

适用于语义相似但不完全相同的请求。使用向量嵌入计算相似度。

**特点：**
- 基于余弦相似度匹配
- 可配置阈值（默认0.85）
- 需要embedding模型支持

**示例：**
```
缓存: "今天天气怎么样？" → "今天晴天，气温25度..."
查询: "今天天气如何？"
→ 相似度 0.92 → 返回缓存的回答
```

## 配置

配置文件位于 `~/.qclaw/smart-cache/config.json`：

```json
{
  "cache_dir": "~/.qclaw/smart-cache/data",
  "l1_max_size": 10000,
  "l2_max_size": 5000,
  "ttl_hours": 168,
  "similarity_threshold": 0.85,
  "embedding_model": "text-embedding-3-small",
  "enable_cost_tracking": true
}
```

**配置说明：**
- `l1_max_size`: L1缓存最大条目数
- `l2_max_size`: L2缓存最大条目数
- `ttl_hours`: 缓存过期时间（小时）
- `similarity_threshold`: L2语义匹配阈值
- `embedding_model`: 用于语义匹配的embedding模型
- `enable_cost_tracking`: 是否启用成本追踪

## 成本追踪

查看节省的成本：

```python
python scripts/cache_manager.py stats
```

输出示例：
```
📊 缓存统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━
总请求数: 1,234
L1命中: 456 (37%)
L2命中: 189 (15%)
缓存未命中: 589 (48%)

💰 成本节省
━━━━━━━━━━━━━━━━━━━━━━━━━━━
节省Token: 89,234
估算节省: $0.27
```

## 集成到OpenClaw

### 方法1：作为MCP Server运行

```python
# 启动MCP服务器
python scripts/mcp_server.py --port 8080
```

然后在OpenClaw配置中添加MCP server。

### 方法2：直接API调用

```python
from scripts.cache_api import SmartCache

cache = SmartCache()

# 查询缓存
result = cache.query("用户的问题")
if result:
    print(f"缓存命中！相似度: {result.similarity}")
    print(f"回答: {result.response}")
else:
    # 调用实际API
    response = call_llm_api("用户的问题")
    # 存入缓存
    cache.store("用户的问题", response)
```

## 脚本说明

### scripts/cache_manager.py

主缓存管理工具，提供命令行接口：
- `status` - 查看缓存状态
- `query` - 精确查询
- `query-semantic` - 语义查询
- `add` - 添加缓存条目
- `clean` - 清理缓存
- `stats` - 查看统计信息

### scripts/cache_api.py

Python API模块，提供编程接口：
- `SmartCache` - 主缓存类
- `CacheEntry` - 缓存条目类
- `CacheStats` - 统计信息类

### scripts/mcp_server.py

MCP协议服务器，支持与其他AI工具集成。

## 最佳实践

1. **合理设置TTL**：根据内容更新频率设置过期时间
   - 事实性内容：7天
   - 时效性内容：1-24小时
   - 永久性内容：30天

2. **调整相似度阈值**：
   - 严格匹配：0.95
   - 常规使用：0.85
   - 宽松匹配：0.75

3. **定期清理**：
   ```bash
   # 每周清理一次过期缓存
   0 0 * * 0 python ~/.qclaw/skills/smart-cache/scripts/cache_manager.py clean --expired
   ```

4. **监控缓存效果**：
   - 命中率 > 30% 表示缓存有效
   - 命中率 < 10% 考虑调整阈值或TTL

## 故障排除

### 缓存未命中率高

1. 检查相似度阈值是否过高
2. 确认缓存容量是否足够
3. 检查TTL设置是否过短

### 语义匹配不准确

1. 尝试不同的embedding模型
2. 调整相似度阈值
3. 检查query预处理是否正确

### 磁盘空间问题

1. 减小缓存容量
2. 缩短TTL
3. 启用压缩存储

## 资源

### scripts/
- `cache_manager.py` - 命令行管理工具
- `cache_api.py` - Python API模块
- `mcp_server.py` - MCP协议服务器
- `embeddings.py` - 向量嵌入工具

### references/
- `api_reference.md` - API详细文档
- `algorithms.md` - 缓存算法说明

### assets/
- `config_template.json` - 配置文件模板
