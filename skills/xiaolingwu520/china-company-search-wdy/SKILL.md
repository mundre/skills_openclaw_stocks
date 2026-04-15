---
name: wendaoyun
description: 问道云企业信息查询工具，支持通过问道云 API 查询企业基本信息、经营信息、财务信息、舆情信息、企业各类风险指标等功能，当用户需要查询企业相关信息时触发。
---

# 问道云 (WenDaoYun) 企业信息查询

## 配置说明

1. 获取 API Key：打开 https://open.wintaocloud.com/home，登录后在个人中心或开发者中心获取
2. 一个用户可以拥有多个 API Key
3. 配置文件（任选其一）：
   - `~/.config/wendao-yun/config.json`
   - 工作空间根目录 `wendao-yun-config.json`
   格式：`{ "api_key": "你的Key" }`
4. 或设置环境变量：`export WENDAOYUN_API_KEY=你的Key`
5. 每日调用额度 200 次

> ⚠️ API Key 属于敏感信息，请妥善保管，不要泄露给他人。发现泄露请及时在问道云开放平台作废。

---

## 查询流程

所有查询都遵循：搜索企业 → 用户确认 → 查询详情

第 1 步：用户提出需求（如"查腾讯的行政处罚"）
第 2 步：调用 `fuzzy-search-org` 搜索企业，列出前 5 条；如果 total 超过 5 条，告知用户可以"查下一页或指定页码"
第 3 步：**必须等待用户确认具体企业**，不要跳过！
第 4 步：调用对应详细信息接口

---

## 接口速查

| 用户说法 | 接口 | 状态 |
|----------|------|------|
| 查询 XX 企业 | `fuzzy-search-org` | ✅ |
| XX 的行政处罚 | `get-punishments` | ✅ |
| XX 是不是老赖 / 失信被执行人 | `get-dishonest` | ⏳ |
| XX 经营异常 | `get-abnormal` | ✅ |
| XX 股权质押 | `get-equity-pledge` | ✅ |
| XX 环保处罚 | `get-environmental-penalties` | ✅ |
| XX 欠税公告 | `get-tax-notice` | ✅ |
| XX 简易注销 | `get-simple-cancel` | ✅ |
| XX 土地抵押 | `get-land-mortgage` | ✅ |
| XX 清算信息 | `get-clear-info` | ✅ |
| XX 公示催告 | `get-public-inform` | ✅ |
| XX 劳动仲裁送达报告 | `get-labour-arb` | ✅ |
| XX 担保信息 | `get-gua-info` | ✅ |
| XX 开庭公告 | `get-open-court-arb` | ✅ |
| XX 税收违法 | `get-tax-violation` | ⏳ |

---

## API 基础信息

- **Base URL**: `https://h5.wintaocloud.com/prod-api/api/invoke`
- **认证**: Header 填写 `Authorization: Bearer {api_key}`
- **请求方式**: 全部 GET
- **金额字段**: punishAmount、assureAmount、mortgageAmount 等单位为**分**，展示时÷100换算为元
- **金额字段可能返回 null，展示时应显示"未知"而非 null**

---

## fuzzy-search-org - 企业模糊搜索

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 关键词（最少 2 字符） |
| pageNum | integer | 否 | 页码，默认 1，每页 5 条 |

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| orgId | string | 企业ID |
| orgName | string | 企业名称 |
| usCreditCode | string | 统一社会信用代码 |
| incDate | string | 成立日期 |
| legalName | string | 法定代表人 |
| status | string | 企业状态（存续/在业等） |
| address | string | 企业地址 |

**使用说明**：结果可能很多（如"腾讯"返回近万条），始终只展示前 5 条，展示时必须包含序号、企业全称、法定代表人、成立日期、状态。必须询问用户确认。

---

## get-punishments - 行政处罚

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 企业全称 |
| pageNum | integer | 否 | 页码，默认 1 |
| pageSize | integer | 否 | 每页条数，默认 10，最大 20 |

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| punishNo | string | 行政处罚决定文书号 |
| illegalFact | string | 违法事实 |
| punishResult | string | 处罚结果 |
| unitName | string | 作出处罚单位名称 |
| punishTime | string | 处罚日期 |
| punishAmount | integer | 处罚金额（单位：分，换算需÷100才是元）|

---

## get-abnormal - 经营异常

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 企业全称 |

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|------|
| department | string | 列入部门 |
| abnormalDate | string | 列入日期 |
| abnormalReason | string | 列入原因 |
| removeDepartment | string | 移出部门 |
| removeDate | string | 移出日期 |
| removeReason | string | 移出原因 |

---

## 以下接口请求参数均同 get-equity-pledge

> searchKey（必填，string）、pageNum（否，integer）、pageSize（否，integer，默认10，最大20）

### get-equity-pledge - 股权质押

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| pledgeeNameList | list | 质权人列表 [{name, type}] |
| riskState | string | 股权质押状态 |
| publicTime | string | 公告日期 |
| pledgeName | string | 出质人名称 |

### get-environmental-penalties - 环保处罚

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| punishBehavior | string | 违法事实 |
| punishAmount | integer | 处罚金额（单位：分） |
| punishInstitution | string | 作出处罚单位名称 |
| publishDate | string | 发布日期 |
| punishDate | string | 处罚日期 |
| punishNumber | string | 环保处罚决定书文号 |

### get-tax-notice - 欠税公告

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| taxDepartment | string | 发布单位 |
| publishDate | string | 发布日期 |
| taxCategory | string | 欠税税种 |
| newOwnTaxBalance | integer | 当前发生新欠税余额（单位：分） |
| ownTaxBalance | integer | 欠税余额（单位：分） |

### get-simple-cancel - 简易注销

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| result | string | 简易注销结果 |
| publicDate | string | 公告日期 |
| regInstitute | string | 登记机关 |
| usCreditCode | string | 统一社会信用代码 |
| orgName | string | 企业名称 |
| objectionList | list | 异议信息 [{objectionDate, content, objectionName}] |
| promiseUrl | string | 全体投资人承诺书Url |

### get-land-mortgage - 土地抵押

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| mortgageAmount | integer | 抵押金额（单位：分） |
| mortgageBeginTime | string | 抵押开始日期 |
| mortgageEndTime | string | 抵押结束日期 |
| mortgageArea | string | 抵押面积 |
| address | string | 地址 |

### get-public-inform - 公示催告

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| publishAuthority | string | 发布机关名称 |
| billType | string | 票据类型 |
| faceValue | integer | 票面金额 |
| publishDate | string | 公告日期 |
| orgName | string | 企业名称 |
| billNumber | string | 票据号 |

### get-labour-arb - 劳动仲裁送达报告

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| publishDate | string | 公告日期 |
| applicantName | string | 原告名称 |
| respondentName | string | 被告名称 |
| caseNo | string | 案号 |

### get-gua-info - 担保信息

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| assureAmount | integer | 担保金额（单位：分，换算需÷100才是元） |
| assureBeginTime | string | 担保起始日 |
| assureEndTime | string | 担保终止日 |
| assureTerm | string | 担保期限（年） |
| assureName | string | 担保方式 |
| currency | string | 币种 |
| performState | string | 履行状态 |
| isRpt | string | 是否关联交易 |
| assuredEntityName | string | 被担保方名称 |
| assureEntityName | string | 担保方名称 |
| reportDate | string | 报告期 |
| transactionDate | string | 交易日期 |
| assureDealTime | string | 处理日期 |

### get-open-court-arb - 开庭公告（劳动仲裁）

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| courtOpenTime | string | 开庭日期 |
| caseReason | string | 案由 |
| plaintiffName | string | 原告名称 |
| defendantName | string | 被告名称 |
| caseNo | string | 案号 |
| undertakeDept | string | 承办部门名称 |
| dataOpenCourtId | long | 开庭公告ID |

---

## get-clear-info - 清算信息

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string | 是 | 企业全称 |

**响应字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| liquidationLeader | string | 清算组负责人名称 |
| liquidationMembers | string | 清算组成员 |

---

## 待接入接口

- `get-dishonest` - 失信被执行人
- `get-tax-violation` - 税收违法

---

## 关键原则

- ✅ 所有详细查询都必须先搜索、再确认、后查询
- ❌ 不要在未确认企业时直接调用详细信息接口
- ⚠️ 金额字段单位为分，展示时需÷100换算为元；返回 null 时显示"未知"
