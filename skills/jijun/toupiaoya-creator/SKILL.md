---
name: toupiaoya-creator
description: 免费投票制作,在线投票生成工具,微信投票免费创建,快速制作活动投票,企业投票制作平台,学校评选投票系统,快捷流畅的投票工具,投票链接生成器,简单投票制作教程,粉丝互动投票制作,投票制作小程序

summary: 投票鸭技能，支持模板检索与投票作品创建。模板检索优先使用 `scripts/toupiaoya_cli.py`（Python 调用）。
read_when:
  - 用户提到投票、评选、拉票、模板挑选
  - 需要通过 Python 脚本检索投票模板
  - 需要通过 HTTP 创建投票作品
---

# 投票鸭技能说明

## 前置条件

1. 模板查询脚本依赖 `requests`。
2. 创建接口需准备 `briefTitle` 与 `briefDesc`。

## 查询投票类模板（推荐：Python 调用）

### 命令示例

```bash
python scripts/toupiaoya_cli.py search \
  --keywords "摄影大赛" \
  --pageNo 1 \
  --pageSize 10 \
  --sortBy "common_total|desc" \
  --color "紫色"
```

### 参数说明（对应 `toupiaoya_cli.py`）

- `--keywords`：关键词（可选）
- `--pageNo`：页码，默认 `1`
- `--pageSize`：每页条数，默认 `10`
- `--sortBy`：排序，默认 `common_total|desc`
- `--color`：颜色筛选（可选，例：紫色/蓝色/粉色）

### 输出示例

```json
{
  "total": 123,
  "end": false,
  "results": [
    {
      "templateId": 1234,
      "title": "模板标题",
      "link": "https://www.toupiaoya.com/mall/detail-h5e/<templateId>",
      "description": "模板描述",
      "pv": 9999
    }
  ]
}
```

若 `total == 0`，脚本返回 `{}`。对话输出时建议展示前 3-5 个模板的标题、链接、描述和热度。

## 创建投票作品

使用 `scripts/toupiaoya_cli.py create` 。

### 请求体

必填：

- `briefTitle`：封面标题
- `briefDesc`：封面简介

可选：

- `detailTitle`: 详细的标题，不超过20字
- `detailDesc` : 详细的描述，例如规则，投票时间等介绍
- `voteType`：`imageVote` | `textVote`(默认) | `videoVote`
- `timeStart`、`timeEnd`：格式 `yyyy-MM-dd HH:mm`
- `groupList`
- `templateId`（默认 `19980321`代表空白模版），可以使用搜索出的templateId
- 单双选控制：默认单选；传 `--multi` 表示多选。

说明：不传 `timeStart/timeEnd` 时，服务内部按“开始=当前，结束=当前+10天”处理。

### 命令示例
文字选项投票, 多选：
```bash
python scripts/toupiaoya_cli.py create \
  --briefTitle "年度最佳作品投票" \
  --briefDesc "封面简介：本次活动由某某主办。" \
  --detailTitle "年度最佳作品投票" \
  --detailDesc "投票规则：每人每天可投一次。" \
  --voteType "textVote" \
  --templateId 19980321 \
  --multi \
  --groupList '[{"groupName":"默认组","choices":[{"name":"作品1"},{"name":"作品2"}]}]'
```

图片投票：
```bash
python scripts/toupiaoya_cli.py create \
  --briefTitle "年度最佳作品投票" \
  --briefDesc "封面简介：本次活动由某某主办。" \
  --detailTitle "年度最佳作品投票" \
  --detailDesc "投票规则：每人每天可投一次。" \
  --voteType "imageVote" \
  --templateId 19980321 \
  --groupList '[{"groupName":"主推","choices":[{"name":"作品1","cover":"https://example.com/p1.png"},{"name":"作品2","cover":"https://example.com/p2.png"}]}]'
```

## 返回值解析

统一形态：

```json
{ "success": true|false, "code": 200|..., "msg": "...", "data": ... }
```

成功常见：

1. 含 `scene_uuid`
   - `editUrl`: `https://www.toupiaoya.com/indesign?id=<scene_uuid>`,代表编辑链接
   - `previewUrl`: `https://forms.ebdan.net/ls/<code>`, 代表手机预览链接
2. `id == 0` 分支
   - 仅返回工具层 `data`（无 `scene_uuid`）
   - 预览链接可拼：`https://forms.ebdan.net/ls/` + `data.code`

失败常见：

- 404（业务异常）


