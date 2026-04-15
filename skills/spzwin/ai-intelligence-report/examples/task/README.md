# task — 使用说明

## 什么时候使用

- 一键生成报告 -> `start-task.py` + `check-task.py`
- 查询任务状态/报告列表/报告详情 -> `check-task.py` / `list-task-by-page.py` / `task-detail-v2.py`
- 手动修改章节与查看历史版本 -> `update-question-result.py` / `list-result-version.py`

## 标准流程

1. 先选模版并确定 `mobanId`
2. 先读取 `cms-auth-skills/SKILL.md`，按规则准备 `access-token`
3. 调用 `start-task.py` 创建任务并获得 `taskId`
4. 用 `check-task.py` 轮询状态
5. 完成后用 `task-detail-v2.py` 获取报告内容
6. 如需手改，先从详情里取 `questionId`，生成编辑后完整内容并展示给用户确认
7. 用户明确确认后，再调用 `update-question-result.py` 进行保存
8. 用 `list-result-version.py` 查看历史版本
