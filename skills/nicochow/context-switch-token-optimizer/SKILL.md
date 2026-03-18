---
name: context-switch-token-optimizer
description: >-
  智能对话上下文切换与 Token 优化。分析对话主题连续性以管理上下文、在话题间切换并节省 Token。
  适用于多任务对话、项目工作流、学习研究等需管理上下文与 Token 使用的场景。
---

# Context Switch Token Optimizer

## 技能描述
智能对话上下文切换和Token优化技能，通过分析对话主题连续性来自动管理上下文，确保相关对话的连续性，同时在不同话题间高效切换以节省Token使用。

## 核心功能

### 🔄 上下文切换管理

#### 1. 对话主题总结
- **每次回复后**：总结本轮对话的一句话主题
- **主题提取**：从对话内容中提取核心关键词和意图
- **主题存储**：将主题保存在对话上下文中

#### 2. 主题连续性判断（三级动作机制）

系统采用三级上下文动作机制，根据主题相似度智能判断：

- **上下文为空**：
  - 搜索历史相关记忆（memory/topic）
  - 如有匹配，渐进加载该记忆，以其主题作为上下文
  - 如无匹配，将本轮对话主题作为新上下文

- **上下文存在**：根据相似度计算，执行以下三种动作之一：
  
  **1. `continuous` - 保持连续**
  - 相似度 ≥ `similarity_threshold` (默认 0.7)
  - 与上一轮高度相关，保持完整上下文，不压缩
  
  **2. `drift_compress` - 渐变漂移压缩**
  - 相似度在 `continuity_threshold` (默认 0.35) 和 `similarity_threshold` 之间
  - 对话连续但主题已漂移，压缩与当前主题弱相关的历史轮
  - 例如：美伊战争 → 对股票影响 → 股票基本面
  - 压缩「战争」段为短摘要，保留但不丢弃
  
  **3. `switch` - 硬切换**
  - 相似度 < `continuity_threshold` (默认 0.35)
  - 与上一轮几乎无关，清理上下文，重新开始

### 📝 主题管理

#### 主题格式
```json
{
  "current_topic": "记忆管理技能优化",
  "topic_history": [
    {
      "topic": "记忆管理技能设计",
      "timestamp": "2026-03-17 10:00",
      "tokens_used": 1500
    },
    {
      "topic": "飞书权限问题处理", 
      "timestamp": "2026-03-17 09:30",
      "tokens_used": 800
    }
  ],
  "memory_context": {
    "related_memory": "memory/topic/memory-manager/SUMMARY.md",
    "last_accessed": "2026-03-17 10:15",
    "relevance_score": 0.85
  }
}
```

#### 主题相关性算法
```python
def calculate_topic_similarity(current_topic, previous_topic):
    """计算主题相似度"""
    # 关键词重叠度
    current_keywords = extract_keywords(current_topic)
    previous_keywords = extract_keywords(previous_topic)
    
    overlap = len(set(current_keywords) & set(previous_keywords))
    max_length = max(len(current_keywords), len(previous_keywords))
    
    # 时间衰减因子
    time_factor = calculate_time_decay()
    
    similarity = (overlap / max_length) * time_factor
    return similarity

def should_switch_context(current_topic, previous_topic):
    """判断是否需要切换上下文"""
    similarity = calculate_topic_similarity(current_topic, previous_topic)
    
    if similarity > 0.7:  # 高相关性，保持连续
        return False
    elif similarity < 0.3:  # 低相关性，需要切换
        return True
    else:  # 中等相关性，用户判断
        return user_preference_check()
```

### 💾 Token优化策略

#### 1. 上下文清理策略
```python
class ContextManager:
    def __init__(self):
        self.token_budget = 80000
        self.compression_threshold = 56000
        
    def manage_context(self, current_topic, previous_context=None):
        """管理上下文"""
        # 1. 检查当前Token使用
        current_tokens = self.calculate_current_tokens()
        
        # 2. 生成主题总结
        topic_summary = self.summarize_topic(current_topic)
        
        # 3. 判断是否需要切换
        if previous_context is None:
            # 上下文为空，搜索历史记忆
            return self.handle_empty_context(topic_summary)
        else:
            # 判断主题连续性
            if self.is_topic_switch(topic_summary, previous_context):
                return self.handle_topic_switch(topic_summary)
            else:
                return self.handle_continuous_context(topic_summary, previous_context)
```

#### 2. 渐进加载策略
```python
def progressive_memory_loading(self, topic_summary):
    """渐进加载相关记忆"""
    # 1. 搜索相关记忆文件
    related_memories = self.search_related_memories(topic_summary)
    
    # 2. 按相关性排序
    sorted_memories = self.sort_by_relevance(related_memories, topic_summary)
    
    # 3. 渐进加载
    loaded_content = []
    current_tokens = 0
    
    for memory in sorted_memories:
        memory_tokens = self.estimate_tokens(memory)
        
        if current_tokens + memory_tokens < self.compression_threshold:
            # 加载头部摘要
            headline = self.load_memory_headline(memory)
            loaded_content.append(headline)
            current_tokens += memory_tokens
        else:
            # 跳过或只加载核心部分
            core_content = self.load_memory_core(memory)
            loaded_content.append(core_content)
            break
    
    return loaded_content
```

### 🔍 搜索与匹配

#### 1. 历史记忆搜索
```python
def search_related_memories(self, topic_summary):
    """搜索相关记忆文件"""
    # 1. 提取关键词
    keywords = self.extract_keywords(topic_summary)
    
    # 2. 搜索topic目录
    search_results = []
    topic_dir = Path("memory/topic")
    
    for file_path in topic_dir.glob("*.md"):
        content = file_path.read_text()
        score = self.calculate_relevance_score(content, keywords)
        
        if score > 0.5:  # 相关性阈值
            search_results.append({
                'file': file_path,
                'score': score,
                'content': content
            })
    
    # 3. 按相关性排序
    return sorted(search_results, key=lambda x: x['score'], reverse=True)
```

#### 2. 关键词提取算法
```python
def extract_keywords(self, text):
    """提取关键词"""
    # 1. 分词和词性标注
    words = self.tokenize(text)
    
    # 2. 过滤停用词
    filtered_words = self.filter_stopwords(words)
    
    # 3. TF-IDF加权
    keywords = self.calculate_tfidf(filtered_words)
    
    # 4. 返回Top N关键词
    return keywords[:5]  # 取前5个最重要的关键词
```

### 📊 监控与报告

#### 1. Token使用监控
```python
def monitor_token_usage(self):
    """监控Token使用情况"""
    usage = {
        'current_tokens': self.calculate_current_tokens(),
        'context_tokens': self.calculate_context_tokens(),
        'memory_tokens': self.calculate_memory_tokens(),
        'budget_percentage': self.calculate_budget_percentage(),
        'switch_count': self.get_switch_count(),
        'avg_tokens_per_topic': self.calculate_avg_tokens_per_topic()
    }
    
    # 检查是否需要优化
    if usage['budget_percentage'] > 70:
        self.trigger_optimization(usage)
    
    return usage
```

#### 2. 主题切换报告
```python
def generate_switch_report(self):
    """生成主题切换报告"""
    report = {
        'last_switch': self.get_last_switch_time(),
        'switch_reason': self.get_switch_reason(),
        'context_efficiency': self.calculate_context_efficiency(),
        'token_savings': self.calculate_token_savings(),
        'memory_hit_rate': self.calculate_memory_hit_rate()
    }
    
    return report
```

## 🎯 使用场景

### 1. 日常对话管理
- **连续对话**: 保持上下文连续性，避免重复解释
- **话题切换**: 智能识别新话题，重新加载相关记忆
- **Token优化**: 自动清理不相关内容，节省内存

### 2. 项目工作流
- **多任务切换**: 在不同项目间智能切换
- **进度保持**: 保持之前的工作状态和上下文
- **相关记忆**: 自动加载相关项目资料

### 3. 学习和研究
- **主题研究**: 深入单一主题，保持上下文连续
- **知识关联**: 发现不同主题间的关联性
- **记忆管理**: 高效管理大量学习资料

## 🔧 配置选项

### 配置文件
```json
{
  "context_switch": {
    "similarity_threshold": 0.7,
    "time_decay_factor": 0.95,
    "max_topic_history": 10,
    "memory_relevance_threshold": 0.5
  },
  "token_optimization": {
    "token_limit": 80000,
    "compression_threshold": 56000,
    "context_cleanup_threshold": 0.8,
    "memory_load_limit": 2000
  },
  "memory_search": {
    "max_search_results": 5,
    "keyword_limit": 5,
    "search_depth": 2,
    "file_types": ["*.md"]
  }
}
```

### 环境变量
- `CONTEXT_SWITCH_LOG_LEVEL`: 日志级别 (DEBUG/INFO/WARNING/ERROR)
- `TOKEN_OPTIMIZER_ENABLED`: 是否启用Token优化 (true/false)
- `MEMORY_SEARCH_DEPTH`: 搜索深度 (1-3)
- `CONTEXT_HISTORY_SIZE`: 上下文历史大小 (5-20)

---

**维护**: Hermosa  
**版本**: v1.0  
**最后更新**: 2026-03-17