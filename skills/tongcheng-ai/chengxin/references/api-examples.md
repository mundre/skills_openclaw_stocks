# API 调用示例

_同程程心 API 调用参考_

---

本技能**仅**通过 `scripts/` 下各 `*-query.js` 调用程心资源接口;须按 SKILL.md 将用户意图映射到对应脚本并传入结构化参数(及 `--channel` / `--surface`)。

## 🚂 火车票专用 API（train-query.js）

### 基础调用

```bash
node scripts/train-query.js [参数] --channel <渠道> --surface <界面>
```

### 合法参数组合

| 组合 | 参数示例 | 说明 |
|------|---------|------|
| 出发地 + 目的地 | `--departure "北京" --destination "上海"` | 按城市查询 |
| 车次号 | `--train-number "G1234"` | 精确查车次 |
| 出发站 + 到达站 | `--departure-station "北京南站" --arrival-station "上海虹桥站"` | 精确站点查询 |

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--departure <城市>` | 视情况 | 出发地城市 |
| `--destination <城市>` | 视情况 | 目的地城市 |
| `--departure-station <站>` | 视情况 | 出发站（精确） |
| `--arrival-station <站>` | 视情况 | 到达站（精确） |
| `--train-number <车次>` | 视情况 | 车次号（如 G1234） |
| `--extra <补充信息>` | 可选 | 额外信息（日期、偏好等） |
| `--channel <渠道>` | 可选 | 通信渠道 |
| `--surface <界面>` | 可选 | 交互界面 |

### extra 参数示例

| extra 值 | 说明 |
|---------|------|
| `"明天"` | 明天的车次 |
| `"高铁"` | 只查高铁 |
| `"动车"` | 只查动车 |
| `"一等座"` | 优先一等座 |
| `"明天 高铁 赏花专线"` | 多条件组合 |

### 调用示例

```bash
# 北京到上海，明天的高铁
node scripts/train-query.js \
  --departure "北京" \
  --destination "上海" \
  --extra "明天 高铁" \
  --channel webchat \
  --surface webchat

# 查询特定车次
node scripts/train-query.js \
  --train-number "G1234" \
  --channel webchat \
  --surface webchat

# 站到站精确查询
node scripts/train-query.js \
  --departure-station "北京南站" \
  --arrival-station "上海虹桥站" \
  --channel webchat \
  --surface webchat
```

---

## 📤 响应结构

### 成功响应

```json
{
  "code": "0",
  "data": {
    "data": {
      "trainData": { ... },
      "flightData": { ... },
      "hotelData": { ... },
      "sceneryData": { ... },
      "tripData": { ... }
    }
  }
}
```

### 无结果

```json
{
  "code": "1",
  "message": "无结果"
}
```

### 错误响应

```json
{
  "code": "3",
  "message": "鉴权失败"
}
```

---

_同程旅行 · 让旅行更简单，更快乐_
