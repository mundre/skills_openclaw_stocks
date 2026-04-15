---
name: fb-business-meal-skill
description: 商务用餐助手，支持工作餐、招待餐、订餐申请、餐标校验、多人用餐登记、订单管理、审批进度查询等功能。Invoke when user needs to arrange business meals, apply for dining, check meal policy, or manage meal orders.
version: 1.0.0
metadata: {"openclaw": {"emoji": "🍱", "category": "finance", "tags": ["商务用餐", "工作餐", "招待餐", "餐标", "审批"], "requires": {"bins": ["python3"]}, "required": true}}
---
# 商务用餐助手 (fb-business-meal-skill)

## 技能描述

商务用餐助手面向企业内部用餐管理场景，支持工作餐、客户招待餐、团队聚餐等业务流程。可完成用餐申请、餐标校验、餐厅与套餐选择、订单创建、发票补录、审批跟踪等操作，帮助企业实现用餐申请、费控和报销的闭环管理。

---

⚠️ 【重要约束】
- 必须填写用餐事由、用餐日期、人数、城市
- 招待餐必须填写客户名称或外部来访对象
- 超餐标、超人数阈值或超预算时必须走审批流程
- 不允许重复提交同一时间段、同一事由、同一参与人的用餐订单
- 已取消或过期订单不得重复核销
- 发票金额不得低于实际结算金额，不得重复关联报销

---

## 核心功能

### 1. 用餐申请
- 工作餐申请
- 招待餐申请
- 团队聚餐申请
- 预估金额填写
- 参与人登记
- 特殊需求备注

### 2. 餐标校验
- 按职级校验人均餐标
- 按城市等级校验标准
- 按场景校验预算上限
- 超标原因说明
- 自动识别是否需要审批

### 3. 餐厅与套餐选择
- 搜索支持企业订餐的餐厅
- 查看餐厅详情、起送价、包间条件
- 查看菜单与套餐
- 选择堂食/外送/包间
- 生成候选方案

### 4. 订单管理
- 创建用餐订单
- 查询订单详情
- 取消订单
- 查询审批状态
- 查询结算状态
- 导出用餐记录

### 5. 发票与报销关联
- 补录发票信息
- 校验发票与订单金额
- 关联报销单
- 查询核销状态
- 重复报销校验

### 6. 统计分析
- 月度用餐统计
- 部门用餐统计
- 人均用餐分析
- 招待餐占比分析
- 超标订单统计

## 触发场景

1. **发起用餐申请**
   - "帮我申请明天中午的工作餐"
   - "我要安排客户招待餐"
   - "给销售团队订一顿晚餐"
   - "创建一个商务宴请订单"

2. **查询餐标和合规**
   - "上海工作餐的人均标准是多少"
   - "这笔招待餐会不会超标"
   - "普通员工在北京的餐标是多少"
   - "这单是否需要审批"

3. **选择餐厅和套餐**
   - "推荐朝阳区适合商务宴请的餐厅"
   - "看看这家餐厅有哪些套餐"
   - "帮我找能开包间的餐厅"
   - "搜索人均200以内的工作餐"

4. **管理订单**
   - "查看我的用餐订单"
   - "取消刚才那笔商务用餐申请"
   - "查询订单BM202604110001详情"
   - "这笔用餐审批到哪一步了"

5. **发票与报销**
   - "给这笔用餐补录发票"
   - "把这笔招待餐关联到报销单"
   - "查询这笔餐费是否已核销"

## 用餐场景类型

| 场景类型 | 代码 | 说明 | 是否需审批 |
|:---|:---|:---|:---|
| 工作餐 | WORK_MEAL | 员工工作日正常用餐 | 否 |
| 加班餐 | OVERTIME_MEAL | 加班场景用餐 | 视金额而定 |
| 招待餐 | BUSINESS_ENTERTAINMENT | 客户拜访、商务接待 | 是 |
| 团队聚餐 | TEAM_DINING | 项目庆功、团队活动 | 是 |
| 会议茶歇 | MEETING_CATERING | 会议期间简餐、茶歇 | 视预算而定 |

## 餐标标准

### 按职级与城市等级

| 职级 | 一线城市工作餐 | 新一线工作餐 | 其他城市工作餐 | 招待餐建议人均 |
|:---|:---|:---|:---|:---|
| 高管 | ¥180/人 | ¥150/人 | ¥120/人 | ¥500/人 |
| 中层 | ¥120/人 | ¥100/人 | ¥80/人 | ¥350/人 |
| 普通员工 | ¥80/人 | ¥60/人 | ¥50/人 | ¥250/人 |

### 城市等级划分
- **一线城市**：北京、上海、广州、深圳
- **新一线城市**：杭州、南京、成都、武汉、西安、重庆、天津、苏州、青岛、长沙
- **其他城市**：上述以外城市

## 输入参数

### 用餐申请

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| meal_type | string | 是 | 用餐类型：WORK_MEAL / OVERTIME_MEAL / BUSINESS_ENTERTAINMENT / TEAM_DINING / MEETING_CATERING |
| city | string | 是 | 用餐城市 |
| meal_date | string | 是 | 用餐日期 |
| meal_time | string | 是 | 用餐时间 |
| reason | string | 是 | 用餐事由 |
| attendees | int | 是 | 用餐人数 |
| attendee_list | array | 否 | 参与人名单 |
| guest_list | array | 否 | 客户/外部人员名单（招待餐必填） |
| budget_amount | float | 否 | 预估预算金额 |
| dining_type | string | 否 | 堂食 / 外送 / 包间 |
| department | string | 否 | 申请部门 |
| project_code | string | 否 | 项目编码 |
| remarks | string | 否 | 备注 |

### 餐标校验

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| level | string | 是 | 职级：staff / manager / executive |
| city | string | 是 | 用餐城市 |
| meal_type | string | 是 | 用餐场景 |
| attendees | int | 是 | 用餐人数 |
| estimated_amount | float | 是 | 预估总金额 |

### 发票补录

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| order_id | string | 是 | 用餐订单号 |
| invoice_no | string | 是 | 发票号码 |
| invoice_code | string | 否 | 发票代码 |
| invoice_amount | float | 是 | 发票金额 |
| invoice_date | string | 是 | 开票日期 |
| seller_name | string | 否 | 销售方名称 |

## 输出格式

### 用餐申请结果

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "order_id": "BM202604110001",
    "meal_type": "BUSINESS_ENTERTAINMENT",
    "meal_type_name": "招待餐",
    "city": "北京",
    "meal_date": "2026-04-12",
    "meal_time": "18:30",
    "attendees": 6,
    "restaurant_name": "京宴·商务会馆",
    "budget_amount": 2400.00,
    "estimated_amount": 2280.00,
    "policy_check": {
      "within_policy": true,
      "need_approval": true,
      "warnings": ["招待餐默认进入审批流程"]
    },
    "approval_status": "pending",
    "create_time": "2026-04-11 15:30:00"
  }
}
```

### 餐标校验结果

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "meal_type": "WORK_MEAL",
    "city": "上海",
    "level": "staff",
    "attendees": 8,
    "estimated_amount": 520.00,
    "per_capita_amount": 65.00,
    "policy_limit": 80.00,
    "within_policy": true,
    "need_approval": false,
    "warnings": []
  }
}
```

### 订单详情示例

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "order_id": "BM202604110001",
    "status": "approved",
    "settlement_status": "pending_invoice",
    "restaurant_name": "京宴·商务会馆",
    "meal_type_name": "招待餐",
    "meal_date": "2026-04-12",
    "meal_time": "18:30",
    "attendees": 6,
    "actual_amount": 2268.00,
    "invoice_status": "not_uploaded",
    "approval_flow": [
      {"step": 1, "approver": "部门经理", "status": "approved"},
      {"step": 2, "approver": "行政采购", "status": "pending"}
    ]
  }
}
```

## 展示格式示例

### 餐厅推荐

```
🍱 北京商务用餐推荐

| 序号 | 餐厅名称 | 场景 | 人均 | 区域 | 特色 |
|:---:|---------|------|---:|------|------|
| 1 | 京宴·商务会馆 | 招待餐 | ¥380 | 朝阳区 | 包间充足 |
| 2 | 云海小馆 | 工作餐 | ¥88 | 海淀区 | 适合团队套餐 |
| 3 | 江南宴 | 团队聚餐 | ¥168 | 望京 | 可开专票 |

💡 回复"序号"查看详情
💡 回复"预订 序号"创建用餐申请
```

### 用餐申请成功

```
✅ 商务用餐申请已创建

═══════════════════════════════════════

📋 申请信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
订单号：BM202604110001
用餐类型：招待餐
日期时间：2026-04-12 18:30
人数：6人
餐厅：京宴·商务会馆
预算：¥2,400.00
预估金额：¥2,280.00

═══════════════════════════════════════

✅ 合规校验
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 在标准范围内
⚠️ 需进入审批流程

═══════════════════════════════════════

💡 操作提示
• 回复"审批进度"查看当前节点
• 回复"补录发票"补充结算信息
• 回复"取消订单"撤销本次申请
```

## API接口列表

| 接口名称 | 功能 | 参数 |
|:---|:---|:---|
| search_restaurants | 搜索餐厅 | city, meal_type, budget_per_capita |
| get_restaurant_detail | 查询餐厅详情 | restaurant_id |
| get_meal_package | 查询套餐 | restaurant_id |
| check_meal_policy | 校验餐标 | level, city, meal_type, attendees, estimated_amount |
| create_meal_order | 创建用餐订单 | meal_type, meal_date, meal_time, attendees, reason |
| get_meal_order_detail | 查询订单详情 | order_id |
| cancel_meal_order | 取消用餐订单 | order_id |
| upload_meal_invoice | 补录发票 | order_id, invoice_no, invoice_amount |
| submit_meal_approval | 提交审批 | order_id |
| get_meal_stats | 获取用餐统计 | start_date, end_date, department |

## 订单状态说明

| 状态 | 说明 |
|:---|:---|
| draft | 草稿 |
| pending | 待提交 |
| pending_approval | 待审批 |
| approved | 已通过 |
| rejected | 已驳回 |
| booked | 已下单 |
| completed | 已完成 |
| cancelled | 已取消 |
| closed | 已关闭 |

## 审批流程

### 标准流程

```
提交用餐申请
    ↓
部门负责人审批
    ↓
订单确认
    ↓
用餐完成
    ↓
发票补录与核销
```

### 超标流程

```
提交用餐申请（超餐标）
    ↓
部门负责人审批
    ↓
费控复核
    ↓
订单确认
    ↓
用餐完成
    ↓
发票补录与核销
```

## 合规检查规则

1. **餐标检查**
   - 人均金额不得超过城市与职级标准
   - 招待餐需校验招待对象和预算归属
   - 团队聚餐需校验活动类型和审批权限

2. **重复检查**
   - 同时段重复订单检查
   - 相同事由重复申请检查
   - 相同发票重复核销检查

3. **预算检查**
   - 部门预算余额检查
   - 项目预算可用额度检查
   - 超预算订单预警

4. **结算检查**
   - 发票金额与订单金额匹配
   - 发票日期有效性校验
   - 报销单关联状态检查
