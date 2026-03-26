---
name: skill-knowledge-transfer
description: 九章技能间知识迁移引擎 - 实现不同技能间的知识共享和协同进化，支持案例复用、规则同步、模式迁移。构建技能正向演化飞轮。
---

# 九章技能间知识迁移引擎

实现技能生态内知识的自动流动和协同进化，构建"引擎越厉害→技能同步越厉害→越用越进化"的正向飞轮。

## 核心功能

### 1. 知识发现 (discover)
发现可迁移的知识：
- 跨技能相似案例识别
- 通用合规规则提取
- 共同法律问题发现
- 复用机会识别

### 2. 知识映射 (map)
建立知识映射关系：
- 概念对齐（术语标准化）
- 规则转换（场景适配）
- 案例迁移（领域适配）
- 依赖分析（影响评估）

### 3. 知识迁移 (transfer)
执行知识迁移：
- 案例复用（跨技能引用）
- 规则同步（批量更新）
- 模板共享（标准化输出）
- 最佳实践传播

### 4. 冲突检测 (detect)
检测迁移冲突：
- 法规冲突识别
- 场景不适用性
- 时效性差异
- 地域限制

### 5. 协同优化 (optimize)
协同优化技能生态：
- 知识图谱构建
- 技能关系网络
- 进化路径规划
- 资源分配建议

## 使用方法

```bash
# 发现可迁移知识
jiuzhang-cli transfer discover --source zhang-contract-review --target zhang-corporate-law

# 建立知识映射
jiuzhang-cli transfer map --skills zhang-ai-law,zhang-chip-law,zhang-data-privacy

# 执行案例迁移
jiuzhang-cli transfer cases --from zhang-litigation-strategy --to zhang-civil-litigation --filter "知识产权"

# 同步通用规则
jiuzhang-cli transfer rules --type compliance --scope all

# 检测迁移冲突
jiuzhang-cli transfer detect --migration-id mig_001

# 一键协同优化
jiuzhang-cli transfer optimize --ecosystem jiuzhang-legal
```

## 知识映射配置

`~/.jiuzhang/transfer.yaml`:
```yaml
mapping:
  concepts:
    - source: "算法备案"
      targets:
        - skill: zhang-ai-law
          term: "算法推荐备案"
        - skill: zhang-data-privacy
          term: "算法透明度"
          
    - source: "出口管制"
      targets:
        - skill: zhang-chip-law
          term: "EAR出口管制"
        - skill: zhang-cross-border-trade
          term: "技术出口管制"

  rules:
    - id: "data_minimal"
      description: "数据最小化原则"
      applicable:
        - zhang-data-privacy
        - zhang-ai-law
        - zhang-medical-law

transfer:
  auto_discover: true
  similarity_threshold: 0.85
  conflict_resolution: manual
  
sync:
  schedule: weekly
  backup_before: true
  rollback_enabled: true
```

## 知识图谱

`references/knowledge-graph.json`:

### 技能节点
```json
{
  "skills": [
    {"id": "zhang-ai-law", "category": "emerging_tech", "cases": 500},
    {"id": "zhang-chip-law", "category": "emerging_tech", "cases": 400},
    {"id": "zhang-data-privacy", "category": "compliance", "cases": 300}
  ]
}
```

### 关系边
```json
{
  "relations": [
    {"from": "zhang-ai-law", "to": "zhang-data-privacy", "type": "depends_on", "strength": 0.9},
    {"from": "zhang-chip-law", "to": "zhang-ai-law", "type": "similar_to", "strength": 0.7},
    {"from": "algorithm_filing", "to": "data_protection", "type": "related_concept", "strength": 0.8}
  ]
}
```

## 迁移模式

### 模式1: 案例复用
同一案例在多个技能中引用：
```
ALG-001 (算法备案违规案)
├── zhang-ai-law: 原始案例
├── zhang-data-privacy: 引用+数据合规视角
└── zhang-corporate-law: 引用+企业责任视角
```

### 模式2: 规则同步
通用规则批量同步到多个技能：
```
规则: "数据最小化原则"
├── zhang-data-privacy: 核心规则
├── zhang-ai-law: AI训练数据合规
├── zhang-medical-law: 患者数据保护
└── zhang-financial-law: 客户信息保护
```

### 模式3: 模板共享
标准化输出模板跨技能使用：
```
模板: "合规评估报告"
├── zhang-contract-review: 合同合规评估
├── zhang-ip-law: 知识产权评估
└── zhang-ma-law: 并购合规评估
```

## 迁移质量评估

| 维度 | 权重 | 评估标准 |
|------|------|----------|
| 准确性 | 30% | 迁移后内容与原意一致 |
| 适用性 | 25% | 适用于目标技能场景 |
| 完整性 | 20% | 信息无丢失 |
| 时效性 | 15% | 法规引用最新 |
| 无冲突 | 10% | 与目标技能现有知识无冲突 |

## 目录结构

```
skill-knowledge-transfer/
├── SKILL.md
├── scripts/
│   ├── discover.py     # 知识发现脚本
│   ├── map.py          # 知识映射脚本
│   ├── transfer.py     # 知识迁移脚本
│   ├── detect.py       # 冲突检测脚本
│   ├── optimize.py     # 协同优化脚本
│   └── visualize.py    # 知识图谱可视化
└── references/
    ├── knowledge-graph.json    # 知识图谱
    ├── mapping-rules.yaml      # 映射规则
    ├── templates/              # 迁移模板
    └── examples/               # 迁移示例
```

## 正向演化飞轮

```
用户反馈 → 数据上报 → AI分析 → 知识发现 → 跨技能迁移 → 协同优化 → 技能升级 → 更好服务 → 更多反馈
     ↑                                                                                          |
     └──────────────────────────────────────────────────────────────────────────────────────────┘
```

**关键指标：**
- 知识复用率: 目标 >60%
- 迁移准确率: 目标 >90%
- 技能协同度: 目标 >80%
- 生态进化速度: 目标 每周自动更新

---
**版本**: 1.0.0  
**作者**: 九章法律AI团队  
**分类**: infrastructure
