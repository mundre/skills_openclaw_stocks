---
name: cn-ppt-outline
description: "PPT大纲生成助手。输入主题或内容，自动生成PPT大纲、分页结构、每页要点。支持工作汇报、产品发布、培训课件、商业计划等多种场景。输出可直接导入PPT软件。"
metadata:
  openclaw:
    emoji: 📑
    category: productivity
    tags:
      - ppt
      - presentation
      - outline
      - office
      - chinese
scope:
  - "根据主题生成PPT大纲结构"
  - "分页设计（每页标题+要点）"
  - "多种场景模板（汇报/发布/培训/计划）"
  - "导出Markdown/PowerPoint格式"
  - "设计建议（配色/排版/图表）"
install: |
  pip install python-pptx
env:
  OPENAI_API_KEY: "可选，用于AI增强内容生成。不配置则使用模板生成。"
entry:
  script: scripts/ppt_outline.py
  args: []
---

# PPT大纲生成助手

## 功能
- 输入主题 → 自动生成完整PPT大纲
- 分页设计：每页标题 + 3-5个要点
- 多种场景：工作汇报、产品发布、培训课件、商业计划
- 导出格式：Markdown大纲、PowerPoint文件
- 设计建议：配色方案、排版建议、图表推荐

## 使用方法

### 生成大纲
```bash
# 工作汇报
python scripts/ppt_outline.py generate "Q1季度销售工作总结" --type report

# 产品发布
python scripts/ppt_outline.py generate "智能水杯新品发布" --type product

# 培训课件
python scripts/ppt_outline.py generate "新员工入职培训" --type training

# 商业计划
python scripts/ppt_outline.py generate "AI教育创业计划" --type business
```

### 导出PPT文件
```bash
python scripts/ppt_outline.py generate "主题" --type report --export ppt --output 汇报.pptx
```

### 查看模板
```bash
python scripts/ppt_outline.py templates
```

## 场景类型

| 类型 | 适用场景 | 结构特点 |
|------|---------|---------|
| report | 工作汇报/总结 | 回顾→成果→问题→计划 |
| product | 产品发布/介绍 | 痛点→方案→产品→优势→行动 |
| training | 培训课件 | 目标→理论→案例→练习→总结 |
| business | 商业计划 | 市场→方案→模式→团队→融资 |
| proposal | 方案建议 | 背景→问题→方案→收益→风险 |

## 输出格式

### Markdown大纲
```markdown
# Q1季度销售工作总结

## 第1页：封面
- 标题：Q1季度销售工作总结
- 副标题：回顾与展望

## 第2页：目录
- 1. 季度回顾
- 2. 核心成果
- 3. 问题分析
- 4. 下季度计划

## 第3页：季度回顾
- 时间跨度：2024年1-3月
- 市场环境：整体向好
- 团队状态：满编运转
...
```

### PowerPoint文件
直接生成.pptx文件，包含：
- 预设版式（标题页、内容页、结束页）
- 分页结构
- 占位符文本

## 设计建议

### 配色方案
- **商务蓝**：#1E3A5F + #4A90D9 + #E8F4F8
- **活力橙**：#FF6B35 + #F7C59F + #FFF3E6
- **专业绿**：#2E7D32 + #66BB6A + #E8F5E9

### 排版原则
- 每页不超过6行文字
- 每行不超过15个字
- 使用图标代替文字
- 留白不少于30%

### 图表推荐
- 对比数据：柱状图
- 趋势变化：折线图
- 占比分布：饼图
- 流程步骤：流程图
