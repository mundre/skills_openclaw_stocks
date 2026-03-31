# 日报生成指南

> **核心原则**：只做摘要的拆解，不做额外补充。严禁编造。

---

## 筛选标准

| 评分 | 含义 |
|------|------|
| 9-10 | 直接解决研究方向核心问题 |
| 7-8 | 高度相关 |
| 5-6 | 相关 |
| <5 | 不相关 |

选出 Top 5，需有 1-2 篇达 8 分以上。

---

## 执行步骤

1. 读取 `data/daily_papers.json`（候选论文，含完整摘要）
2. 根据摘要筛选相关性最高的论文
3. 按模板生成报告
4. 使用 `feishu_create_doc` 创建飞书文档
5. **保存精选论文**：将选中的论文写入 `data/selected_papers.json`
   ```json
   {
     "date": "2026-03-28",
     "papers": [
       {
         "title": "论文标题",
         "paper_id": "arXiv ID",
         "posted_date": "2026-03-28",
         "authors": ["作者列表"],
         "arxiv_url": "https://arxiv.org/...",
         "relevance_score": 9,
         "abstract_full": "完整摘要",
         "motivation": "研究动机",
         "core_innovation": "核心创新"
       }
     ]
   }
   ```
6. 调用保存命令：`python3 scripts/paper_lark_report.py --save-daily "2026-03-28" "data/selected_papers.json"`
7. 调用注册命令：`python3 scripts/paper_lark_report.py --register-daily-doc "<doc_id>" "<doc_url>" "<title>"`

---

## 论文分析：只做拆解

| 字段 | 要求 |
|------|------|
| `motivation` | **严格从摘要提取** |
| `core_innovation` | **严格从摘要提取** |

---

## 严禁事项

- ❌ 编造方法细节
- ❌ 补充实验数据
- ❌ 推测意图
