# planning — AI 内容规划

> 对应 CSO Web 端 `/planning` 页面，AI 自动生成月度内容规划方案，支持任务进度监控、规划详情查看与导出。

---

## 工作流程

```
enterprises → generate → watch（监控进度）→ get（查看详情）→ export txt
```

---

## 命令速查

| 命令 | 说明 |
|------|------|
| `planning enterprises` | 查询企业目录（生成前先选企业） |
| `planning content-types` | 查询可用内容类型（post / video） |
| `planning generate` | 创建规划生成任务 |
| `planning watch <taskId>` | 监听生成任务进度（SSE 实时推送） |
| `planning list` | 查询规划任务列表 |
| `planning get <planId>` | 获取规划详情 |
| `planning regenerate <planId>` | 对已有规划重新生成 |
| `planning task cancel <taskId>` | 取消任务 |
| `planning task retry <taskId>` | 重试失败/取消的任务 |
| `planning task delete <taskId>` | 删除任务 |
| `planning export txt` | 导出规划为 TXT（Markdown 表格格式） |

---

## 示例：生成月度规划

```bash
# Step 1：查企业列表，获取 enterpriseId
siluzan-cso planning enterprises

# Step 2：发起生成任务
siluzan-cso planning generate \
  --enterprise-id <id> \
  --year-month 2026-05 \
  --content-types post,video \
  --marketing-goal "提升品牌曝光" \
  --key-products "新品 A" \
  --freq-unit week --freq-count 3

# Step 3：监控生成进度（taskId 来自 generate 输出）
siluzan-cso planning watch <taskId>

# Step 4：查看规划详情（planId 来自 list 输出）
siluzan-cso planning get <planId>

# Step 5：导出为 TXT 文件
siluzan-cso planning export txt --plan-id <planId> --output plan.md
```

---

## generate 主要参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--enterprise-id` | ✅ | 企业 ID |
| `--year-month` | ✅ | 规划月份，格式 `YYYY-MM` |
| `--content-types` | ✅ | 内容类型，逗号分隔：`post`（图文）/ `video`（视频） |
| `--marketing-goal` | — | 营销目标（自然语言描述） |
| `--key-products` | — | 重点产品 |
| `--target-markets` | — | 目标市场 |
| `--key-events` | — | 重要节点/活动 |
| `--content-tone` | — | 内容风格（如"专业严肃"/"轻松活泼"） |
| `--freq-unit` | — | 发布频率单位：`week` / `month` |
| `--freq-count` | — | 发布频率数量（与 `--freq-unit` 同时使用） |
| `--watch` | — | 生成后自动监听进度，无需单独执行 watch |

---

## planning list — 查询任务列表

```bash
# 查所有规划任务
siluzan-cso planning list

# 按企业筛选
siluzan-cso planning list --enterprise-id <id>

# 按月份筛选
siluzan-cso planning list --year-month 2026-05
```
