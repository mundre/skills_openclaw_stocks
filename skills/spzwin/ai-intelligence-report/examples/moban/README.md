# moban — 使用说明

## 什么时候使用

- 用户需要浏览可用模版 -> `list-moban.py`
- 用户需要查看某个模版章节结构 -> `moban-detail.py`
- 用户需要新建一份新模版 -> `create-moban.py`
- 用户需要更新已有模版结构或提示词 -> `update-moban.py`
- 用户需要发布或下架模版 -> `change-moban-state.py`
- 用户需要删除废弃模版 -> `delete-moban.py`

## 标准流程

1. 鉴权预检（先读取 `cms-auth-skills/SKILL.md`，按规则准备 `access-token`）
2. 获取模版列表并确认目标 `mobanId`
3. 查看模版详情，确认是否用于后续报告生成
4. 需要新模版时，准备 `MOBAN_NAME` 与 `MOBAN_SECTION_LIST`，调用 `create-moban.py`
5. 需要调整已有模版时，准备 `MOBAN_ID`、`MOBAN_NAME` 与 `MOBAN_SECTION_LIST`，调用 `update-moban.py`
6. 需要发布或下架模版时，准备 `MOBAN_ID` 与 `MOBAN_STATE`（`1` 上架，`0` 下架），调用 `change-moban-state.py`
7. 需要删除模版时，先确认目标 `MOBAN_ID` 后调用 `delete-moban.py`
