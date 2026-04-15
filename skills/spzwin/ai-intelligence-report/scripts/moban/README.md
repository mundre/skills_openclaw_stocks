# 脚本清单 — moban

## 共享依赖

- `cms-auth-skills/SKILL.md` — 统一鉴权入口，执行前先按该技能准备 `access-token`

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `list-moban.py` | `POST /ai-report/moban/listMobanByPageV2` | 模版列表检索 |
| `moban-detail.py` | `POST /ai-report/moban/mobanDetail` | 模版详情查看 |
| `create-moban.py` | `POST /ai-report/moban/saveMoban` | 新建模版 |
| `update-moban.py` | `POST /ai-report/moban/updateMoban` | 编辑模版 |
| `change-moban-state.py` | `POST /ai-report/moban/changeMobanState` | 模版发布/下架 |
| `delete-moban.py` | `POST /ai-report/moban/delMoban` | 删除模版 |

## 使用方式

```bash
# 设置环境变量
export XG_USER_TOKEN="your-access-token"

# 查询模版列表
export MOBAN_PAGE_NUM=0
export MOBAN_PAGE_SIZE=10
python3 scripts/moban/list-moban.py

# 查询模版详情
export MOBAN_ID="模板ID"
python3 scripts/moban/moban-detail.py

# 新建模版（sectionList 必填，JSON 字符串）
export MOBAN_NAME="创新药尽调模版"
export MOBAN_SECTION_LIST='[{"name":"项目概览","questionList":[{"title":"项目基本信息","content":"请总结项目背景与核心价值","prompt":"按业务、技术、竞争格局三个维度展开"}]}]'
python3 scripts/moban/create-moban.py

# 编辑模版（mobanId + sectionList 必填，JSON 字符串）
export MOBAN_ID="moban_1001"
export MOBAN_NAME="创新药尽调模版（更新版）"
export MOBAN_SECTION_LIST='[{"name":"项目概览","questionList":[{"title":"项目基本信息","prompt":"重点补充适应症市场空间"}]}]'
python3 scripts/moban/update-moban.py

# 模版发布/下架（1 上架，0 下架）
export MOBAN_ID="moban_1001"
export MOBAN_STATE=1
python3 scripts/moban/change-moban-state.py

# 删除模版
export MOBAN_ID="moban_1001"
python3 scripts/moban/delete-moban.py
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范
3. **入参定义以** `openapi/` 文档为准
