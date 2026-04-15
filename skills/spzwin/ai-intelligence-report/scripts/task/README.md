# 脚本清单 — task

## 共享依赖

- `cms-auth-skills/SKILL.md` — 统一鉴权入口，执行前先按该技能准备 `access-token`

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `start-task.py` | `POST /ai-report/task/startTask` | 创建报告任务 |
| `check-task.py` | `POST /ai-report/task/checkTask` | 查询任务进度 |
| `list-task-by-page.py` | `POST /ai-report/task/listTaskByPage` | 分页查询报告列表 |
| `task-detail-v2.py` | `POST /ai-report/task/taskDetailV2` | 获取报告详情 |
| `update-question-result.py` | `POST /ai-report/task/updateQuestionResult` | 手工覆盖子章节内容 |
| `list-result-version.py` | `POST /ai-report/task/listResultVersion` | 查询子章节历史版本 |

## 使用方式

```bash
# 设置环境变量
export XG_USER_TOKEN="your-access-token"

# 创建任务
export MOBAN_ID="模板ID"
export TASK_NAME="报告名称"
# 可选：目录ID（不设置时由后端默认规则处理）
# export TASK_DIR_ID="目录ID"
python3 scripts/task/start-task.py

# 查询进度
export TASK_ID="报告ID"
python3 scripts/task/check-task.py

# 报告列表分页（可选：通过环境变量传入额外参数）
export PAGE_NUM=0
export PAGE_SIZE=10
export REPORT_TYPE=1
export DEL_FLAG=0
python3 scripts/task/list-task-by-page.py

# 获取报告详情
python3 scripts/task/task-detail-v2.py

# 章节编辑与版本查询
export QUESTION_ID="子章节ID"
export RESULT="新的章节内容"
python3 scripts/task/update-question-result.py
python3 scripts/task/list-result-version.py
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范
3. **入参定义以** `openapi/` 文档为准
