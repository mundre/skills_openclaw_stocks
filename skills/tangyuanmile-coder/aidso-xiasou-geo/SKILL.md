---
name: AIDSO_虾搜GEO
description: |
  AIDSO_虾搜GEO - GEO品牌诊断、知识库、GEO内容生产。

  **当以下情况时使用此 Skill**：
  (1) 用户要发起或查询品牌 GEO 诊断：如「帮我做一个XX的GEO诊断报告」「查一下XX的GEO表现」
  (2) 用户要管理知识库：如「建知识库」「加到知识库」
  (3) 用户要生成 GEO 优化内容：如「GEO内容生产」
user-invocable: true
metadata: {"openclaw":{"emoji":"🦐","baseUrl":"https://api.aidso.com","homepage":"https://geo.aidso.com","optionalEnv":["AIDSO_GEO_API_KEY"]}}
---

# AIDSO_虾搜GEO Skill

## ⚠️ Agent 必读约束

### 🌐 站点与域名
- API 主域名：`https://api.aidso.com`
- 官网：`https://geo.aidso.com`
- API key 获取地址：`https://geo.aidso.com/setting?type=apiKey&platform=GEO`
- 诊断结果查看页：`https://geo.aidso.com/completeAnalysis`

> 所有业务 API 请求必须使用 AIDSO 的正式 API 域名。  
> 官网链接仅用于用户查看、获取 API key、购买积分或查看结果。

### 🔑 API key 绑定规则
AIDSO GEO 能力依赖用户已绑定的 API key。

**每次调用任何 AIDSO GEO 相关 API 前，先检查当前用户是否已保存 API key。**

- 若已保存：直接继续执行用户原本请求
- 若未保存：进入 API key 绑定流程
- 若后端返回 `401`、`invalid token`、`鉴权失败`、明确表示 API key 无效：清空已保存 API key，并要求用户重新绑定

> ⚠️ 当前绑定流程 **不做预验证**。  
> 用户输入 API key 后，**直接保存**。  
> 后续任意真实业务请求都会自动携带该 API key。  
> 若 API key 不正确，由后端返回错误后再提示用户重新绑定。

**API key 绑定的完整规则见：** `references/apikey.md`

### 🔒 安全规则
- 不要主动展示用户已保存的完整 API key
- 不要在回复中回显完整 API key
- 不要要求用户重复输入已保存的 API key
- API key 仅用于调用 AIDSO GEO 相关接口
- 若用户未绑定 API key，不要尝试调用任何需要鉴权的业务接口

### 🧭 总体执行原则
1. 先做意图识别，再路由到对应模块
2. 命中具体能力后，读取对应 `references/*.md` 获取完整规则和接口说明
3. 业务处理必须严格基于后端返回，不自行猜测品牌不存在、报告失败、内容生成失败等结论
4. 所有 JSON 返回都按 UTF-8 解析
5. 后台返回的错误文案应尽量原样返回给用户
6. 若出现“积分不足”，在原始后台文案后追加购买提示：
   `请前往 https://geo.aidso.com 购买积分`

---

## 指令路由表

> 匹配指令后， 用 **read 工具** 读取对应的 `references/xxx.md` 获取完整 API 文档。

| 指令 | 角色 | 说明 | 详细文档 |
|------|------|------|---------|
| `/aidso config` 或「绑定 API key」 | ⚙️ 配置 | 绑定、更新、重绑 API key | [references/apikey.md](references/apikey.md) |
| `/aidso diagnosis` 或「GEO诊断」 | 📊 诊断官 | 品牌诊断、结果轮询、报告返回 | [references/diagnosis.md](references/diagnosis.md) |
| `/aidso knowledge` 或「品牌知识库」 | 📚 知识管理员 | 品牌知识库CRUD | [references/knowledge.md](references/knowledge.md) |
| `/aidso content` 或「GEO内容生产」 | ✍️ 内容生产官 | 根据品牌 + 问题 + 平台生成 GEO 优化内容 | [references/content.md](references/content.md) |

---

## 自然语言路由

```
「配置/绑定/连接爱搜」              → /aidso config
「GEO诊断」相关                    → /aidso diagnosis
「品牌知识库」相关                     → /aidso knowledge
「生产内容/优化」相关               → /aidso content
```

**决策原则**：优先匹配最具体的意图。

## API 路由表

> > ⚠️ **构造请求时必须使用下表中的完整路径**，Base URL 为 `https://api.aidso.com`。如果收到 404，说明路径不对，请对照此表检查。

### GEO诊断

| 方法 | 路径 | 说明 | 详细文档 |
|------|------|------|----------|
| GET | `/openapi/skills/band_report/md?brandName={brandName` | GEO诊断 | [references/diagnosis.md](references/diagnosis.md) |

### 品牌知识库

| 方法 | 路径 | 说明 | 详细文档 |
|------|------|------|----------|
| POST | `/openapi/skills/save_content/md` | 品牌知识库 | [references/knowledge.md](references/knowledge.md) |

### GEO内容生产

| 方法 | 路径 | 说明 | 详细文档 |
|------|------|------|----------|
| POST | `/openapi/skills/run_realtime_report` | 品牌知识库 | [references/content.md](references/content.md) |

---

## 鉴权方式

所有 AIDSO GEO 相关请求都使用用户已绑定的 API key。

请求头格式：`x-api-key: {用户已绑定的_api_key}`

## 通用错误处理

```json
{
    "code": XXX,
    "msg": "XXXX"
}
```

| 错误码 | 说明 | 处理方式 |
|--------|------|---------|
| 401 | 鉴权失败 | 检查 API Key ，或重新绑定 |
| 405 | 积分不足 | 引导充积分：请前往https://geo.aidso.com 购买积分 |
| 405 | 其他错误 | 返回后台 `msg` |

## 首次API Key配置成功后回复

✅ AIDSO_虾搜GEO 配置完成！
凭证已写入 openclaw.json，服务已自动热加载生效。
现在你可以使用以下功能了：
🔍 GEO诊断 — 「帮我做一个 XX 的GEO诊断」「做一个 XX 的品牌GEO报告」
📚 品牌知识库 — 「上传品牌知识库」「把品牌介绍加入知识库」
📝 GEO生产内容 - 「GEO优化」

试试说吧！