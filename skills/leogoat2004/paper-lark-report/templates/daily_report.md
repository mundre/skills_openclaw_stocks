# 科研日报 | {{date}}

<callout emoji="📡" background-color="light-blue">
**paper-lark-report** | 研究方向：{{research_direction}}
</callout>

---

## 今日概览

| 统计项 | 数值 |
|--------|------|
| 📅 日期 | {{date}} |
| 📚 候选论文 | {{total_papers}} 篇 |
| ✨ 精选论文 | {{selected_papers}} 篇 |

---

{% for paper in papers %}

## {{ forloop.counter }}. {{ paper.title }}

{% if paper.relevance_score >= 8 %}
<callout emoji="⭐" background-color="light-green">
**相关性：{{paper.relevance_score}}/10** — 高度相关
</callout>
{% elif paper.relevance_score >= 6 %}
<callout emoji="📎" background-color="light-yellow">
**相关性：{{paper.relevance_score}}/10** — 相关
</callout>
{% endif %}

| 字段 | 内容 |
|------|------|
| **arXiv ID** | `{{ paper.paper_id }}` |
| **发布日期** | {{ paper.posted_date }} |
| **作者** | {{ paper.authors }} |
| **链接** | [arXiv]({{ paper.arxiv_url }}) · [PDF]({{ paper.pdf_url }}) |

---

### 【摘要】

{{ paper.abstract_full }}

---

### 【研究动机】

> 从上方摘要中提取：本文要解决什么问题？为什么重要？

{{ paper.motivation }}

---

### 【核心创新】

> 从上方摘要中提取：本文的核心贡献是什么？与现有方法有何不同？

{{ paper.core_innovation }}

---

<hr>
{% endfor %}

<callout emoji="📌" background-color="pale-gray">
**数据来源**：arXiv

*本报告由 AI 自动生成，分析基于论文摘要，未补充额外信息。*
</callout>
