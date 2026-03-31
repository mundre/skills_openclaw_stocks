---
name: paper-lark-report
description: "全自动科研论文日报/周报生成。通过 arXiv RSS 抓取最新论文，arXiv API 获取完整摘要，LLM 语义评分筛选，生成基于原文的学术报告，推送飞书 Wiki。"
license: MIT
tags:
  - research
  - arxiv
  - paper
  - daily-report
  - weekly-report
  - feishu
  - lark
config:
  - name: research_direction
    type: string
    required: true
    description: 研究方向描述，LLM 据此筛选论文和评分
  - name: feishu_root
    type: string
    required: true
    description: 飞书 Wiki 目录链接，报告将创建在此目录下
  - name: max_daily_papers
    type: number
    required: false
    default: 5
    description: 日报精选论文数量上限
author: OpenClaw
---

# paper-lark-report

全自动科研论文日报/周报生成 Skill。抓取 arXiv 论文，arXiv API 精读全文，LLM 语义评分筛选，生成学术化报告，推送飞书 Wiki。

**Perfect for:**
- 科研人员持续追踪特定研究方向
- AI/ML 研究者跟踪最新预印本
- 需要结构化文献报告的团队

## 核心设计

### 先筛选，后精读，再生成

```
1. 抓取 arXiv RSS（候选论文）
2. arXiv API 批量获取完整摘要
3. LLM 语义相关性评分（基于完整摘要）
4. 筛选 Top N
5. LLM 基于原文生成报告（无幻觉）
6. 推送飞书 Wiki
7. 注册去重
```

### 设计原则

- **避免幻觉**：基于 arXiv API 完整摘要（300-800字）生成，各字段有据可查。
- **纯语义评分**：无需 CCF、无需引用数，LLM 读标题+摘要后与研究方向语义匹配。
- **周六生成周报**：日报周一至周五产出，周六汇总生成周报，横向比较跨论文规律

## 评分机制

| 评分 | 含义 |
|------|------|
| 9-10 | 直接解决研究方向核心问题 |
| 7-8 | 高度相关，涉及核心问题关键方面 |
| 5-6 | 相关，非核心 |
| <5 | 不相关 |

筛选 Top N（默认 5），需有 1-2 篇达 8 分以上。

## 使用示例

### 触发指令

```
"生成今日研究日报"
"生成本周研究周报"
"帮我追踪最新的 multi-agent 系统论文"
```

### 执行流程

**日报**：
1. `python3 scripts/paper_lark_report.py`
2. 检查 `skip`：
   - `no_paper_reason` 有值 → 推送"今日无合适论文"提示
   - `existing_doc` 有值 → 报告现有文档链接
3. 读取 `data/daily_papers.json` + 模板
4. LLM 筛选论文（最多 5 篇）
5. 创建飞书文档
6. 调用 `python3 scripts/paper_lark_report.py --save-daily "{date}" "data/daily_papers.json"` 保存精选论文
7. 调用 `--register-daily-doc` 注册文档

**周报**：
1. `python3 scripts/paper_lark_report.py --weekly`
2. 读取周一至周五的日报归档
3. 检查 `skip`：
   - `no_paper_reason` 有值 → 推送"本周无日报数据，跳过周报"提示
   - 否则正常生成
4. 读取 `data/weekly_papers.json` + 模板
5. 创建飞书文档
5. 创建文档

## 配置

```yaml
# config.yaml
research_direction: "Security-constrained governance for enterprise multi-agent..."
feishu_root: "https://my.feishu.cn/wiki/G0UnwO95BiCWVxkXF7pc4gtJnv0"
max_daily_papers: 5

venue_rss:
  - name: "arXiv cs.AI"
    url: "http://export.arxiv.org/rss/cs.AI"
  - name: "arXiv cs.LG"
    url: "http://export.arxiv.org/rss/cs.LG"
  - name: "arXiv cs.MA"
    url: "http://export.arxiv.org/rss/cs.MA"
  - name: "arXiv cs.CL"
    url: "http://export.arxiv.org/rss/cs.CL"
```

## Cron 配置

```bash
# 日报：周一至周五 12:00
openclaw cron add --name "paper-daily" --cron "0 12 * * 1-5" \
  --tz "Asia/Shanghai" --session isolated --timeout 900 \
  --message "使用 paper-lark-report skill，生成今日研究日报并推送到飞书"

# 周报：每周六 12:00
openclaw cron add --name "paper-weekly" --cron "0 12 * * 6" \
  --tz "Asia/Shanghai" --session isolated --timeout 600 \
  --message "使用 paper-lark-report skill，生成本周研究周报并推送到飞书"
```

## 目录结构

```
paper-lark-report/
├── SKILL.md
├── config.yaml
├── scripts/
│   └── paper_lark_report.py  # 抓取脚本（RSS + arXiv API）
├── templates/
│   ├── daily_report.md
│   ├── daily_report_prompt.md
│   ├── weekly_report.md
│   └── weekly_report_prompt.md
└── data/
    ├── daily_papers.json    # 当日候选论文
    ├── doc_registry.json    # 文档注册表（去重）
    ├── processed_ids.json   # 已处理 paper ID
    └── processed_log/      # 日报归档
```

## 依赖

- Python 3.12+
- pyyaml
- 飞书 Bot（需文档创建权限）
