---

**wininsales-crm Skill 完整描述**

---

```
---
name: wininsales-crm
description: 赢在销客CRM能力集成，支持客户管理全流程。用于：(1) 客户录入 - 添加新客户信息（支持自动工商查询补全），(2) 客户查重 - 检查客户是否已存在，(3) 跟进录入 - 记录客户跟进情况，(4) 客户分析 - 查看客户数据统计分析，(5) 团队业绩分析 - 查看团队或个人销售数据。当用户提到CRM、客户管理、录入客户、查看客户、跟进记录、客户分析、团队业绩时使用此skill。
---

# 赢在销客CRM (WininSales CRM)

## 概述

此skill集成了赢在销客CRM的MCP API，提供客户管理全流程能力。

## 首次使用 - 获取授权

首次使用需要获取授权token：

1. 引导用户访问：https://www.wininsales.com/
2. 用户需要扫码登录或注册账号
3. 授权后获取token，格式类似：xxx_xxxx_xxxxxxxx
4. 将token拼接完整MCP地址：https://www.wininsales.com/mcp_api/mcp?token={用户token}

## Token 安全存储建议

**重要**：需要保存用户的token以便后续使用。

### 推荐方式
- 记录在 TOOLS.md 本地文件中（不上传云端）
- 或使用 1Password/Keychain 等密码管理器管理

### 安全注意事项
- Token 只保存于本地，不要分享给他人
- 定期（如每1-2个月）更换一次 Token
- 如发现 Token 泄露，立即在赢在销客后台重置

## MCP API 调用方式

通过 HTTP POST 请求调用 MCP API：

MCP地址：https://www.wininsales.com/mcp_api/mcp?token={token}

调用示例（curl）：

curl -s "https://www.wininsales.com/mcp_api/mcp?token={token}" \
  -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"工具名称","arguments":{参数},"id":1}'

## 智能工作流

### 客户录入智能流程（含工商查询）

用户：添加客户/录入客户
Step 1: 询问客户名称（必填）
Step 2: 【自动查重】调用 SearchExistingCustomers
  ├─ 查到重复 → 告知用户已有该客户，提供客户ID，结束流程
  └─ 无重复 → 继续 Step 3
Step 3: 【自动工商查询】调用 CompanyBusinessRegistrationInquiry
  ├─ 查到工商信息 → 展示信息，进入 Step 4
  └─ 未查到 → 进入 Step 4（手动补充）
Step 4: 【收集必填信息】补充联系人信息
  - 联系人姓名（必填）
  - 联系人性别（必填：1男/0女/2未知）
  - 归属代理商（如有）
  - 意向等级（默认D）
  - 企业电话、手机、邮箱（可选）
  - 备注（可选）
Step 5: 【格式化预览·必须确认】将待录入数据整理成表格，发给用户确认

📋 请确认以下录入信息：

【客户基本信息】
- 公司名称：xxx
- 联系人：xxx（性别：男/女/未知）
- 归属代理商：xxx（如有）
- 意向等级：D级（潜在客户）

【补充信息（选填）】
- 电话：xxx
- 邮箱：xxx
- 备注：xxx

请回复「确认录入」后再提交！
  ├─ 用户确认 → 进入 Step 6
  └─ 用户修改 → 收集修改后的信息，重新展示预览（Step 5）
Step 6: 【提交录入】确认后再调用 CreateNewBusinessCustomer
Step 7: 【结果反馈】
  ├─ 成功 → 告知用户"客户录入成功"
  └─ 失败 → 告知错误原因，询问是否重试

### 跟进录入智能流程

用户：添加跟进/记录拜访
Step 1: 确认客户名称
Step 2: 调用 SearchExistingCustomers 获取客户ID
  ├─ 多个结果 → 让用户选择具体客户
  └─ 唯一结果 → 获取 company_id
Step 3: 收集跟进信息
  - 往来方式（必选：面访/电话/微信/QQ/邮件/其他）
  - 时间（必填，格式：YYYY-MM-DD HH:MM）
  - 内容（必填）
  - 意向等级（必填，默认D）
Step 4: 如果是面访
  - 询问结束时间（默认开始后4小时）
  - 询问拜访地址
Step 5: 【格式化预览·必须确认】整理跟进内容发给用户确认

📋 请确认以下跟进信息：

- 客户名称：xxx
- 往来方式：面访/电话/微信/...
- 时间：YYYY-MM-DD HH:MM
- 意向等级：D级
- 拜访地址：xxx（面访必填）
- 跟进内容：xxx

请回复「确认录入」后再提交！
  ├─ 用户确认 → 进入 Step 6
  └─ 用户修改 → 收集修改后的信息，重新展示预览（Step 5）
Step 6: 调用 AddCustomerVisit 提交（以 customer_level 参数传入意向等级）

### 客户分析智能流程

用户：分析客户/查看客户数据
Step 1: 确认客户名称
Step 2: 调用 AnalyzeCustomers
  - analysis_type 可选：客户、联系人、往来记录、商机记录、合同记录
  - 建议默认用 "all" 获取全部分析
Step 3: 格式化输出结果
  - 隐藏敏感信息（如完整手机号用 **** 代替）
  - 用表格呈现结构化数据
  - 汇总关键指标

### 业绩分析智能流程

用户：查看业绩/团队数据
Step 1: 确认分析范围
  - 个人还是团队？（默认：个人）
  - 时间范围？（默认：本周）
Step 2: 确定时间范围
  - 本周：当前日期往前推到周一
  - 上周：上周一至周日
  - 本月：本月1日至今日
  - 自定义：用户指定
Step 3: 调用 EmployeeAnalysis
  - scope: "个人" 或 "团队"
  - analysis_type: 销售合同（默认）、客户、往来、报价单等
Step 4: 汇总输出
  - 列出每人/每团队业绩
  - 计算总计/平均值
  - 按业绩排序

## API 参考

### 1. SearchExistingCustomers - 客户查重/查询

调用：
curl -s "https://www.wininsales.com/mcp_api/mcp?token={token}" \
  -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"SearchExistingCustomers","arguments":{"query":"客户名/电话/联系人"},"id":1}'

参数：
| 参数 | 必填 | 说明 |
|------|------|------|
| query | ✅ | 查询关键词，优先：客户名称 > 电话 > 联系人 |

返回：客户列表（含 customer_id、contact_id）

### 2. CompanyBusinessRegistrationInquiry - 工商信息查询

用途：根据公司名称查询工商注册信息（天眼查数据）

调用：
curl -s "https://www.wininsales.com/mcp_api/mcp?token={token}" \
  -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"CompanyBusinessRegistrationInquiry","arguments":{"tyc_keyword":"公司名称"},"id":2}'

参数：
| 参数 | 必填 | 说明 |
|------|------|------|
| tyc_keyword | ✅ | 企业全称 |

返回字段（可用于自动填充）：
| 字段 | 说明 |
|------|------|
| companyName | 公司名 |
| juridicalPerson | 法定代表人 |
| registedCapital | 注册资本 |
| registedDate | 成立日期 |
| companyStatUs | 经营状态 |
| address | 注册地址 |
| actualAddress | 实际地址 |
| industry | 所属行业 |
| products | 主营业务 |
| creditCode | 统一社会信用代码 |
| webSites | 官网 |
| staffNumber | 企业规模 |

### 3. CreateNewBusinessCustomer - 客户录入

参数：
| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| company_name | ✅ | string | 客户名称 |
| contact_contact_name | ✅ | string | 联系人姓名 |
| contact_sex | ✅ | string | 性别：1男/0女/2未知 |

可选参数（可用工商信息自动填充）：
- tel - 企业电话
- contact_phone - 联系人手机（11位手机号）
- contact_email - 联系人邮箱
- contact_wechat - 联系人微信
- address - 企业地址（来自工商 address/actualAddress）
- region - 区域
- industry - 行业（来自工商 industry）
- scope - 规模（来自工商 staffNumber）
- level - 意向等级
- source - 客户来源
- label - 标签数组
- memo - 备注（可填入主营业务）

### 4. AddCustomerVisit - 跟进录入

参数：
| 参数 | 必填 | 说明 |
|------|------|------|
| company_id | ✅ | 客户ID（来自SearchExistingCustomers） |
| type | ✅ | 往来方式：VisitType.1(面访)/2(电话)/3(邮件)/4(QQ)/5(微信)/6(其他)/105(企业微信) |
| expect_start_time | ✅ | 开始时间 YYYY-MM-DD HH:MM |
| memo | ✅ | 往来内容 |

可选：
- contact_id - 联系人ID
- expect_end_time - 结束时间（面访必填）
- visit_address - 面访地址

### 5. AnalyzeCustomers - 客户分析

参数：
| 参数 | 必填 | 说明 |
|------|------|------|
| customer | ✅ | 客户名称 |
| analysis_type | ✅ | 类型：客户/联系人/往来记录/商机记录/合同记录/all |

### 6. EmployeeAnalysis - 业绩分析

参数：
| 参数 | 必填 | 说明 |
|------|------|------|
| employee_name | ✅ | 员工姓名 |
| start_time | ✅ | 开始日期 YYYY-MM-DD |
| end_time | ✅ | 结束日期 YYYY-MM-DD |
| scope | ✅ | 个人/团队 |
| analysis_type | - | 分析类型，默认：销售合同 |

## 客户录入最佳实践

### 工商查询成功时的字段映射

| 工商字段 | CRM字段 | 处理方式 |
|---------|---------|----------|
| companyName | company_name | 直接使用 |
| juridicalPerson | contact_contact_name | 建议作为默认联系人 |
| registedCapital | - | 填入备注 |
| registedDate | - | 填入备注 |
| address | address | 直接使用 |
| actualAddress | - | 填入备注（实际地址） |
| industry | industry | 直接使用 |
| products | memo | 填入备注（主营业务） |
| creditCode | - | 填入备注 |
| webSites | url | 直接使用 |
| staffNumber | scope | 直接使用 |

### 客户录入确认话术示例

📋 请确认以下录入信息：

【客户基本信息】
- 公司名称：上海淳宏国际物流有限公司
- 联系人：顾莉（性别：未知）
- 归属代理商：上海回声网络
- 意向等级：D级（潜在客户）

【补充信息（选填）】
- 电话：13816034370
- 地址：上海市东大名路359号

请回复「确认录入」后再提交！

### 跟进录入确认话术示例

📋 请确认以下跟进信息：

- 客户名称：上海淳宏国际物流有限公司
- 往来方式：微信
- 时间：2026-04-01 14:00
- 意向等级：D级
- 跟进内容：线上沟通，客户主动约访

请回复「确认录入」后再提交！

## API 已知问题与解决方案

1. CreateNewBusinessCustomer 电话冲突：如果客户电话已在系统中被其他客户使用，API会报错"此公司电话已存在"，此时应去掉 contact_phone 字段单独录入客户，再在跟进备注中补充电话信息
2. 跟进录入意向等级：必须用 customer_level 参数（如 customer_level: "D"），不能用 level
3. 跟进录入无意向等级报错：如果遇到"请补充意向等级信息"错误，说明该客户尚未设置意向等级，需要在 AddCustomerVisit 的 arguments 中加 customer_level 字段
4. CreateNewBusinessCustomer 必填字段：系统可能动态要求不同字段（如客户来源、往来方式、标签等），遇到报错时按提示补充对应字段

## 常见场景速查

| 场景 | 工具 | 关键参数 |
|------|------|----------|
| 查客户是否存在 | SearchExistingCustomers | query |
| 查工商信息 | CompanyBusinessRegistrationInquiry | tyc_keyword |
| 录入新客户 | CreateNewBusinessCustomer | company_name, contact_contact_name, contact_sex |
| 添加跟进记录 | AddCustomerVisit | company_id, type, expect_start_time, memo |
| 查看客户数据 | AnalyzeCustomers | customer, analysis_type |
| 查看团队业绩 | EmployeeAnalysis | employee_name, start_time, end_time, scope |

## 注意事项

1. 必须先查重 - 录入客户前必须调用 SearchExistingCustomers
2. 工商查询优先 - 录入新客户时，先尝试查询工商信息自动填充
3. 【强制】先确认再录入 - 所有写入操作（客户录入、跟进记录等）必须先将数据整理成表格发给用户确认，用户回复「确认录入」后才真正提交 API
4. 隐私保护 - 输出时隐藏敏感信息（完整手机号用 **** 代替）
5. 错误处理 - API失败时告知用户具体原因，不要隐瞒
6. 时间格式 - 必须严格遵循 YYYY-MM-DD HH:MM 格式
7. 只读操作无需确认 - 查询客户、分析业绩、查工商等读取操作可直接执行，无需确认步骤
```

需要我帮你做什么？