---
name: beijing-signed-price-tracker
description: Track configured Beijing Housing Commission new-home projects from bjjs.zjw.beijing.gov.cn project-detail URLs, read project signed-unit counts and average price, crawl building tables including “查看更多” and paginated lists, treat both “已签约” and “网上联机备案” as signed units, estimate the implied average price per m² of newly signed rooms from changes between the previous and current project summaries, persist rows into a Feishu spreadsheet as the single source of truth, and send Feishu DM notifications when new rows are added. Use when asked to monitor one or more Beijing pre-sale projects, update a project mapping, sync newly signed rooms into a Feishu sheet, infer newly signed average price, verify duplicate insertion behavior, or notify on updates.
---

# Beijing Signed Price Tracker

使用 `scripts/tracker.js` 维护多个地块名到北京住建委项目详情链接的映射，并把新发现的“已签约 / 网上联机备案”房屋写入**飞书表格**。

## 核心文件

- `projects.json`：项目映射 + 飞书表格配置
- `scripts/tracker.js`：抓取、解析、估算、写入、排序主脚本

## 满足的规则

1. 允许配置多个地块名到北京住建委项目详情链接的映射；同一地块名也可以绑定多个项目详情链接，并在同步时合并处理。
2. 从项目详情页提取：
   - 已签约套数
   - 成交均价（￥/M2）
3. 从楼盘表页面提取每套房的：
   - 销售楼号
   - 自然楼层
   - 房号
   - 销售状态
4. 如果项目详情页有“查看更多”，继续抓取 `pageId=411612` 楼盘表列表页。
5. 如果楼盘表列表页有多页，依次处理全部页。
6. 将 `已签约` 与 `网上联机备案` 统一视为签约房屋。
7. 历史账本只以飞书表格为准。
8. 从飞书表格中按地块名反向解析该地块上次查询结果；如果不存在，则上次已签约套数与上次成交均价都按 `0` 处理。
9. 公式：

   `估计新签约均价 = (本次已签约套数 * 本次项目成交均价 - 上次已签约套数 * 上次项目成交均价) / (本次已签约套数 - 上次已签约套数)`

10. 飞书表格列固定为：

   `地块名,销售楼号,自然楼层,房号,估计成交价,更新时间,项目已签约套数,项目成交均价`

11. 每次同步时，先判断房屋是否已在飞书表格中出现；如果已存在则不重复追加，如果不存在才按公式计算并新增一行。
12. 写入时只在表格底部追加新行；历史行内容不回写、不改值。排序允许调整行顺序。
13. 如果任意地块本次有新增行，则向配置好的飞书私聊 open_id 发送通知，通知内容就是本次新增的那些行。
14. 更新时间统一使用 `YYYY-MM-DD HH:MM:SS`。
15. 追加完成后，对整张表按以下优先级排序：
    - 地块名
    - 更新时间
    - 销售楼号
    - 自然楼层
    - 房号

## 飞书表格约束

- 飞书表格是**唯一真实数据源**。
- 首次使用时，如果表格为空，脚本会自动写入表头。
- 如果表格首行不是预期表头，脚本会报错停止，避免破坏历史数据。
- 如果飞书应用没有该表格权限，脚本会提示你在文档右上角添加文档应用。

## 历史账本约束

- 去重、历史快照、排序、最终结果都以飞书表格内容为准。

## 状态颜色

`scripts/tracker.js` 按楼盘表颜色识别状态：

- `#FF0000` → 已签约
- `#d2691e` → 网上联机备案
- `#FFCC99` → 已预订
- `#33CC00` → 可售
- `#CCCCCC` → 不可售
- `#ffff00` → 已办理预售项目抵押
- `#00FFFF` → 资格核验中

只有 `已签约` 和 `网上联机备案` 会进入飞书表格。

## 配置文件格式

`projects.json` 示例：

```json
{
  "feishu": {
    "sheetUrl": "https://my.feishu.cn/sheets/Y944sbj2khtLcNtb7jec7MIrnxd",
    "spreadsheetToken": "Y944sbj2khtLcNtb7jec7MIrnxd",
    "sheetId": "eee767",
    "sheetTitle": "Sheet1",
    "appId": "cli_xxx",
    "appSecret": "xxx",
    "notifyUserOpenId": "ou_xxx"
  },
  "projects": [
    {
      "name": "清樾府04地块",
      "url": "http://bjjs.zjw.beijing.gov.cn/eportal/ui?pageId=320794&projectID=8138177&systemID=2&srcId=1"
    }
  ]
}
```

也可以通过环境变量覆盖：

- `FEISHU_SHEET_URL`
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_NOTIFY_USER_OPEN_ID`

## 命令

```bash
node scripts/tracker.js set-feishu --sheet-url "https://my.feishu.cn/sheets/Y944sbj2khtLcNtb7jec7MIrnxd" --app-id "cli_xxx" --app-secret "xxx" --notify-user-open-id "ou_xxx"
node scripts/tracker.js add --name "清樾府04地块" --url "http://bjjs.zjw.beijing.gov.cn/eportal/ui?pageId=320794&projectID=8138177&systemID=2&srcId=1"
# 同一地块名重复 add 新链接时，脚本会把链接追加到该地块配置下
node scripts/tracker.js list
node scripts/tracker.js sync
node scripts/tracker.js sync --name "清樾府04地块"
```

也可以临时同步一个未写入配置的项目：

```bash
node scripts/tracker.js sync --name "临时项目" --url "http://bjjs.zjw.beijing.gov.cn/eportal/ui?pageId=320794&projectID=8138177&systemID=2&srcId=1" --sheet-url "https://my.feishu.cn/sheets/Y944sbj2khtLcNtb7jec7MIrnxd" --app-id "cli_xxx" --app-secret "xxx"
```

## 实施要求

- 先使用项目详情页统计值作为总量基准，再扫描楼盘表找具体房号。
- 必须处理“查看更多”和分页，不能只依赖项目详情页第一页展示的部分楼栋。
- 如果 `签约套数变化` 与 `本次发现的新房号数` 不一致，输出警告，但仍按当前楼盘表结果判断哪些房号需要新增。
- 如果项目总签约套数下降，不回滚历史数据，只报告异常。
- 如果楼盘表出现历史没有的新房号，但项目总签约套数没有增加，则跳过这些房号并给出警告，避免估价失真。
- 默认顺序抓取，避免高频并发请求。
- 排序通过脚本在读取全部账本后统一重写已排序区间完成。

## 通知规则

- 只有在本次同步确实追加了新行时，才发送飞书私聊通知。
- 通知内容就是新增行本身，按表头字段输出。
- 如果没有新增行，则不发送通知。
- 通知目标由 `feishu.notifyUserOpenId`（或环境变量 `FEISHU_NOTIFY_USER_OPEN_ID`）控制。
