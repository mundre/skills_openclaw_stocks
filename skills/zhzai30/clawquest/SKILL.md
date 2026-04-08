---
name: openclaw-mining-server
version: 0.1.0
description: 玩家通过龙虾发出挖矿指令后，服务端自动完成挖矿并返回收益结果，无需游戏在线。
metadata:
  openclaw:
    requires:
      env:
        - GAME_API_BASE_URL
        - REQUEST_TIMEOUT_MS
    emoji: "⛏️"
    homepage: ""
---

# openclaw-mining-server

挂机托管挖矿 Skill。玩家绑定账号后，通过龙虾发出指令，Skill 调用游戏服务端完成一局挖矿并返回收益结果，全程不需要游戏客户端在线。

## 工具列表

### server_mine

发起一次托管挖矿请求。

入参：
- `playerToken`（必填）：玩家绑定令牌
- `autoBuyStamina`（可选）：体力不足时是否自动购买，默认 false

出参：
- `staminaUsed`：本次消耗体力
- `staminaLeft`：剩余体力
- `rewards`：本次收益（gold、gem 等）
- `traceId`：追踪 ID

### get_player_status

查询玩家当前状态，用于决策是否发起挖矿。

入参：
- `playerToken`（必填）：玩家绑定令牌

出参：
- `stamina`：当前体力
- `diamond`：当前钻石
- `lastMineTime`：最近一次挖矿时间

## 配置

在环境变量中填写以下值：

| 变量名 | 说明 |
|---|---|
| `GAME_API_BASE_URL` | 游戏服务端 HTTP 地址 |
| `REQUEST_TIMEOUT_MS` | 请求超时时间（毫秒，默认 8000） |

## 安全说明

- 仅执行玩家已授权操作（挖矿、体力购买）
- 不涉及账号密码与真实资金
- 体力自动购买默认关闭，需玩家主动授权
