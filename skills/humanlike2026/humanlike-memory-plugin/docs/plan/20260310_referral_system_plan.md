---
title: 邀请裂变功能设计方案
author: jianghaibo
date: 2026-03-10
status: draft
word_count: 15766
---

# 邀请裂变功能设计方案

## 一、需求概述

为 Human-Like Memory 产品实现"邀请裂变"增长机制：

- 每个注册用户拥有**唯一邀请码**
- 用户通过**固定分享链接**（含邀请码）邀请好友注册
- 提供**一键复制**邀请链接功能
- 新老用户在满足条件后各获得 **1000 积分**奖励
- 奖励触发条件：新用户的**记忆操作（添加+检索）累计达到 100 条**
- 每个用户通过邀请获得的积分**上限 5000 分**
- 关键数值通过**环境变量**配置

## 二、系统架构概览

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  OpenClaw    │────▶│  Memory Server   │────▶│  Auth Adapter   │
│  Plugin      │     │  (Python)        │     │  (Go/gRPC)      │
│  (Node.js)   │     │                  │     │                 │
│              │     │  - 记忆 API       │     │  - 用户注册/登录 │
│  [新增]       │     │  - 积分系统       │     │  [新增]          │
│  邀请码展示    │     │  - 操作计数       │     │  邀请码生成/绑定  │
│  一键复制      │     │  - 奖励发放       │     │  邀请关系存储     │
└──────────────┘     └──────────────────┘     └─────────────────┘
```

## 三、方案选型分析

### 3.1 邀请码存储位置

| 方案 | 优势 | 劣势 | 结论 |
|------|------|------|------|
| **A: Auth Adapter (Go)** | 与用户表天然关联；注册时立即生成 | 需改 Go 代码 + protobuf | ✅ **推荐** |
| B: Memory Server (Python) | Python 开发快；积分逻辑集中 | 用户表在 Auth Adapter 的 MySQL 中，需要跨服务查询 | ❌ |
| C: 独立微服务 | 职责清晰 | 过度设计，增加运维成本 | ❌ |

**结论：选方案 A — 邀请码存储在 Auth Adapter 的 MySQL 中。**

理由：
1. 邀请码与用户强绑定，Auth Adapter 已有 `aisocial_users` 表和 MySQL 连接
2. 注册时立即生成邀请码，无需跨服务调用
3. 邀请关系（谁邀请了谁）是用户级数据，属于 Auth Adapter 的职责范围

### 3.2 奖励发放位置

奖励（积分）发放逻辑放在 **Memory Server** 中。

理由：
1. 积分系统（`credits` 模块）已在 Memory Server 中实现
2. 记忆操作计数（触发奖励的条件）也在 Memory Server 中
3. Auth Adapter 只负责存储邀请关系，Memory Server 负责判定和发放

### 3.3 服务间通信方式

Auth Adapter ↔ Memory Server 通信：

| 方案 | 描述 | 结论 |
|------|------|------|
| **A: HTTP API 调用** | Memory Server 通过 HTTP 调用 Auth Adapter 查询邀请关系 | ✅ **推荐** |
| B: gRPC 直连 | 强类型，但需要 Python gRPC client | 过重 |
| C: 共享数据库 | 直接读 Auth Adapter 的 MySQL | 破坏服务边界 |

**选方案 A：Auth Adapter 新增 HTTP REST 端点供 Memory Server 调用。**

## 四、数据模型设计

### 4.1 Auth Adapter 侧（MySQL）

#### 表 `aisocial_users` — 新增字段

```sql
ALTER TABLE aisocial_users ADD COLUMN invite_code VARCHAR(16) UNIQUE AFTER avatar_url;
ALTER TABLE aisocial_users ADD COLUMN invited_by BIGINT UNSIGNED DEFAULT NULL AFTER invite_code;
```

- `invite_code`: 用户的唯一邀请码（8 位大写字母+数字，如 `HLM8A2X9`）
- `invited_by`: 邀请人的 uid（NULL = 自然注册）

#### 表 `aisocial_invite_records` — 新增

```sql
CREATE TABLE aisocial_invite_records (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    inviter_uid BIGINT UNSIGNED NOT NULL,       -- 邀请人 UID
    invitee_uid BIGINT UNSIGNED NOT NULL UNIQUE, -- 被邀请人 UID（一人只能被邀请一次）
    invite_code VARCHAR(16) NOT NULL,            -- 使用的邀请码
    status      TINYINT NOT NULL DEFAULT 0,      -- 0=已注册, 1=条件达成, 2=已发放奖励
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reward_at   DATETIME DEFAULT NULL,           -- 奖励发放时间
    INDEX idx_inviter (inviter_uid),
    INDEX idx_status  (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4.2 Memory Server 侧（MongoDB）

#### 集合 `invite_progress` — 新增

```javascript
{
    tenant_id: "mp_xxxx...",     // API Key 前缀（与积分系统一致）
    user_uid: 123456,            // 用户 UID
    memory_op_count: 0,          // 记忆操作计数（add + search）
    threshold_reached: false,    // 是否达到阈值
    threshold_reached_at: null,  // 达到阈值时间
    created_at: ISODate(),
    updated_at: ISODate()
}
```

索引：
- `tenant_id` + `user_uid`（唯一）

## 五、邀请码生成规则

```
格式: HLM + 5位随机字符（大写字母 + 数字，排除 0/O/1/I/L 易混淆字符）
字符池: ABCDEFGHJKMNPQRSTUVWXYZ23456789
示例: HLM8A2X9, HLMKN5P3
```

- 前缀 `HLM` = Human-Like Memory 品牌标识
- 生成时机：**用户注册成功后立即生成**（在 `SignUpWithVerifiedSubject` 中）
- 唯一性：数据库 UNIQUE 约束 + 冲突时重试（最多 3 次）

## 六、核心流程设计

### 6.1 注册时绑定邀请关系

```
用户点击邀请链接 → https://human-like.me/register?invite=HLM8A2X9
                                                      ↓
前端注册页面保存 invite_code 到 URL/localStorage
                                                      ↓
注册成功后 → Auth Adapter:
  1. 生成新用户的邀请码
  2. 查询 invite_code 对应的邀请人 UID
  3. 写入 invited_by 字段
  4. 写入 aisocial_invite_records (status=0)
  5. 返回注册结果（含 invite_code）
```

### 6.2 记忆操作计数 & 奖励触发

```
新用户每次调用 Memory API（add/search）
         ↓
Memory Server 检查:
  1. 该用户是否有邀请关系（调 Auth Adapter HTTP API）
  2. 如果有 → 累加 invite_progress.memory_op_count
  3. 如果 count >= INVITE_REWARD_THRESHOLD（默认 100）
     且 threshold_reached == false
     → 标记 threshold_reached = true
     → 调 Auth Adapter 更新 invite_records.status = 1
     → 给新用户积分 +INVITE_REWARD_CREDITS（默认 1000）
     → 检查邀请人积分上限，若未超 INVITE_MAX_CREDITS（默认 5000）
       → 给邀请人积分 +INVITE_REWARD_CREDITS
     → 更新 invite_records.status = 2
     → 飞书通知
```

### 6.3 流程优化 — 减少跨服务调用

**关键优化：缓存邀请关系**

Memory Server 首次查询某用户的邀请关系后，缓存在 `invite_progress` 集合中（含 `inviter_uid` 字段），后续无需重复调用 Auth Adapter。

```javascript
// invite_progress 完整结构（含缓存字段）
{
    tenant_id: "mp_xxxx...",
    user_uid: 123456,
    inviter_uid: 789012,         // 缓存的邀请人 UID（从 Auth Adapter 获取后写入）
    inviter_tenant_id: "mp_yyyy", // 缓存的邀请人 tenant_id
    has_inviter: true,           // 是否有邀请关系
    memory_op_count: 0,
    threshold_reached: false,
    threshold_reached_at: null,
    reward_granted: false,       // 奖励是否已发放
    reward_granted_at: null,
    created_at: ISODate(),
    updated_at: ISODate()
}
```

这样，只在**新用户首次操作**时查一次 Auth Adapter，后续全部走本地 MongoDB。

## 七、API 设计

### 7.1 Auth Adapter 新增 HTTP 端点

Auth Adapter 当前只有 gRPC。需要新增一个轻量 HTTP 层用于服务间通信。

#### `GET /internal/v1/invite/relation?invitee_uid={uid}`

查询某用户的邀请关系。

**请求**：
```
GET /internal/v1/invite/relation?invitee_uid=123456
X-Internal-Secret: {shared_secret}
```

**响应**：
```json
{
    "has_inviter": true,
    "inviter_uid": 789012,
    "invite_code": "HLM8A2X9",
    "created_at": "2026-03-10T12:00:00Z"
}
```

#### `PUT /internal/v1/invite/record/{invitee_uid}/status`

更新邀请记录状态。

**请求**：
```json
{
    "status": 2,
    "reward_at": "2026-03-10T15:00:00Z"
}
```

#### `GET /internal/v1/invite/stats?inviter_uid={uid}`

查询邀请人的统计信息（已邀请人数、已发放奖励次数）。

**响应**：
```json
{
    "inviter_uid": 789012,
    "total_invited": 8,
    "rewarded_count": 5,
    "total_credits_earned": 5000
}
```

### 7.2 Memory Server 新增端点

#### `GET /plugin/v1/invite/info`

插件获取当前用户的邀请信息。

**请求**：
```
GET /plugin/v1/invite/info
x-api-key: mp_xxxxxx
```

**响应**：
```json
{
    "success": true,
    "invite_code": "HLM8A2X9",
    "invite_link": "https://human-like.me/register?invite=HLM8A2X9",
    "stats": {
        "total_invited": 3,
        "rewarded_count": 2,
        "total_credits_earned": 2000,
        "max_credits": 5000,
        "remaining_credits": 3000
    }
}
```

### 7.3 插件侧 API 调用

插件新增 `getInviteInfo()` 方法，调用 Memory Server 的 `/plugin/v1/invite/info`。

## 八、环境变量配置

### Memory Server `.env`

```bash
# 邀请裂变配置
INVITE_REWARD_THRESHOLD=100      # 新用户触发奖励的记忆操作数
INVITE_REWARD_CREDITS=1000       # 每次邀请奖励积分
INVITE_MAX_CREDITS=5000          # 每个用户通过邀请获得的积分上限
```

### Auth Adapter ConfigMap

```yaml
invite:
  code_prefix: "HLM"
  code_length: 8
  internal_secret: "${INVITE_INTERNAL_SECRET}"
```

## 九、OpenClaw 插件侧实现

### 9.1 邀请码展示 & 一键复制

插件无独立 UI 界面（纯后端 hook 插件），邀请码展示有两种方案：

| 方案 | 描述 | 结论 |
|------|------|------|
| **A: 通过 AI 对话展示** | 用户说"我的邀请码"时，插件注入邀请信息到回复 | ✅ **推荐** |
| B: Dashboard Web 页面 | 在 human-like.me 网页展示 | 已有框架，后续可补 |

**方案 A 实现思路：**

在 `recallHandler` 中增加邀请码意图检测：

```javascript
// 检测邀请相关意图
const INVITE_KEYWORDS = [
    "邀请码", "invite code", "邀请链接", "invite link",
    "分享链接", "推荐码", "referral", "邀请好友"
];

function isInviteQuery(prompt) {
    const lower = prompt.toLowerCase();
    return INVITE_KEYWORDS.some(kw => lower.includes(kw));
}
```

当检测到邀请意图时：
1. 调用 `/plugin/v1/invite/info` 获取邀请信息
2. 将邀请信息格式化为 prependContext 注入到 LLM 提示词中
3. LLM 自然生成包含邀请码和链接的回复

**注入格式：**

```markdown
# 邀请信息

用户正在查询邀请相关信息，请根据以下数据回复：

- 邀请码: HLM8A2X9
- 邀请链接: https://human-like.me/register?invite=HLM8A2X9
- 已邀请: 3 人
- 已获得奖励: 2000 积分
- 奖励上限: 5000 积分
- 剩余可获得: 3000 积分

请告诉用户邀请码和邀请链接，提示他们可以复制链接分享给朋友。每邀请一位好友并使用记忆功能满 100 次，双方各获 1000 积分。
```

### 9.2 一键复制实现

OpenClaw 插件运行在 LLM 对话环境中，无法直接操作剪贴板。**一键复制由前端 Web Dashboard 实现**，插件侧通过对话展示可复制的文本格式。

## 十、反作弊方案

### 10.1 成本收益分析

| 风险 | 概率 | 影响 | 防御成本 | 结论 |
|------|------|------|----------|------|
| 批量注册刷邀请码 | 中 | 积分膨胀 | 低 | ✅ 需防御 |
| 自己邀请自己（同一人多邮箱） | 中 | 积分膨胀 | 中 | ✅ 基础防御 |
| 机器人刷记忆操作数 | 低 | 积分膨胀 + 资源消耗 | 高 | ⚠️ 基础限频即可 |
| 邀请码买卖/分享 | 低 | 可接受 | 高 | ❌ 不防御 |

### 10.2 防御措施（Phase 1 — 低成本）

#### 1. 积分上限硬控

最核心的防线：每用户邀请积分上限 5000 分。即使所有其他防御失效，损失也可控（5000 积分 ≈ ¥10 成本）。

#### 2. 同 IP / 设备指纹关联检测

在 Auth Adapter 注册时记录 IP（已有 HTTP 层可获取）：
- 同一 IP 在 24 小时内注册 > 3 个账号 → 标记异常
- 异常账号的邀请奖励暂缓发放，人工审核

**实现成本：低**（注册时多记一个 IP 字段，加一条查询）

#### 3. 记忆操作质量校验

在计数时做基础校验：
- **去重**：相同内容的 add 请求在 10 分钟内不重复计数
- **最低内容长度**：add 的 message 总长度 < 20 字符不计数
- **频率限制**：单用户每小时最多计 50 次操作（超出部分不计入进度）

**实现成本：低**（在 Memory Server 计数逻辑中加几个 if）

#### 4. 延迟发放

奖励不在达到阈值时立即发放，而是**延迟 24 小时**。期间如果检测到异常可撤销。

**实现成本：低**（加一个 `reward_scheduled_at` 字段，定时任务扫描发放）

### 10.3 暂不实施的高成本方案

- 手机号绑定验证（增加注册摩擦，Phase 1 不做）
- 行为序列分析 / ML 模型（ROI 不足）
- 图形验证码（影响用户体验）

### 10.4 监控 & 告警

通过飞书通知（已有基础设施）：
- 单日邀请奖励发放 > 10 次 → 通知
- 单用户 1 小时内记忆操作 > 100 次 → 通知
- 同一 IP 注册 > 3 个账号 → 通知

## 十一、实施计划

### Phase 1: Auth Adapter 改造（~6h）

| 序号 | 任务 | 预估 |
|------|------|------|
| 1.1 | MySQL 表结构变更（新增字段 + 新表） | 0.5h |
| 1.2 | 邀请码生成逻辑 | 1h |
| 1.3 | 注册流程集成（绑定邀请关系） | 1.5h |
| 1.4 | 新增 HTTP internal API（3 个端点） | 2h |
| 1.5 | 单元测试 | 1h |

### Phase 2: Memory Server 改造（~8h）

| 序号 | 任务 | 预估 |
|------|------|------|
| 2.1 | `invite` 模块骨架（models, repository, service） | 2h |
| 2.2 | 记忆操作计数集成（add/search 时累加） | 2h |
| 2.3 | 奖励触发 & 发放逻辑 | 2h |
| 2.4 | `/plugin/v1/invite/info` API 端点 | 1h |
| 2.5 | 飞书告警集成 | 0.5h |
| 2.6 | 单元测试 | 0.5h |

### Phase 3: OpenClaw 插件改造（~4h）

| 序号 | 任务 | 预估 |
|------|------|------|
| 3.1 | `getInviteInfo()` API 方法 | 1h |
| 3.2 | 邀请意图检测 | 0.5h |
| 3.3 | 邀请信息注入到对话上下文 | 1h |
| 3.4 | 环境变量配置 | 0.5h |
| 3.5 | 测试 & 调试 | 1h |

### Phase 4: 联调 & 上线（~2h）

| 序号 | 任务 | 预估 |
|------|------|------|
| 4.1 | 三端联调 | 1h |
| 4.2 | K8s ConfigMap 配置 | 0.5h |
| 4.3 | 部署上线 | 0.5h |

**总计：~20h**

## 十二、关键决策待确认

| # | 问题 | 建议 | 状态 |
|---|------|------|------|
| 1 | 邀请码前缀用 `HLM` 还是其他？ | HLM (Human-Like Memory) | 待确认 |
| 2 | 奖励发放是否需要延迟 24h？ | Phase 1 先即时发放，观察数据后决定 | 待确认 |
| 3 | Auth Adapter HTTP internal API 的认证方式？ | 共享 secret (简单有效) | 待确认 |
| 4 | 记忆操作计数是否需要区分 add 和 search？| 不区分，统一计数 | 待确认 |
| 5 | 新用户注册奖励（100 积分）与邀请奖励是否叠加？| 叠加（注册 100 + 邀请达标 1000） | 待确认 |

## 十三、风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Auth Adapter Go 代码改动引入 bug | 中 | 高（影响注册） | 充分单测 + 灰度发布 |
| 跨服务调用延迟 | 低 | 中 | 缓存邀请关系，减少调用 |
| 积分系统被刷 | 低 | 中 | 积分上限 + IP 检测 + 告警 |
| 邀请码冲突 | 极低 | 低 | DB UNIQUE + 重试机制 |

---

**执行人：jianghaibo**
**创建时间：2026-03-10**
**版本：v1.0 (Draft)**
