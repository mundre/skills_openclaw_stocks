# API Key 绑定配置

## 概述

使用API Key 为用户绑定 AIDSO GEO 服务访问权限。适用于「配置 AIDSO」「连接 AIDSO」等场景，也是首次使用时自动触发的流程.

> ⚠️ 当前绑定流程 **不做预验证**。  
> 用户输入 API key 后，系统会**直接保存**。  
> 后续任意 API 请求都会自动携带该 API key。  
> 若 API key 不正确，后端会返回错误，此时再提示用户重新绑定。

---

## 自动触发条件

每次调用任何 AIDSO GEO 相关 API 前，先检查 `API_KEY` 是否存在。若不存在， **自动发起 API Key 绑定流程** （无需用户主动说"配置"），告知用户需要先绑定才能使用。

绑定完成后，继续执行用户原本的请求。

---

## 手动绑定入口

当用户表达以下意图时，进入 API key 绑定流程：

- 配置 API key
- 绑定 API key
- 绑定爱搜账号
- 连接爱搜 GEO
- 重新绑定
- 更换 API key

---

## API Key 获取地址

请提示用户前往以下地址获取 API Key:

`https://geo.aidso.com/setting?type=apiKey&platform=GEO`

---

## 绑定流程

### 1. 步骤 1： 提示用户输入 API Key

当检测到用户尚未绑定 API Key 时，回复：

> 首次使用需要绑定爱搜账号，请输入你在后台创建的 API key 完成绑定。  
> 获取地址：https://geo.aidso.com/setting?type=apiKey&platform=GEO

首次绑定时，可附加欢迎文案：

> 欢迎使用 AIDSO 虾搜 GEO 技能。  
> 后续将持续支持品牌诊断、知识库、GEO内容生产等能力，欢迎关注后续更新。
>
> ---
>
> ### 步骤 2：接收用户输入并直接保存

当用户输入任意非空字符串作为 API key 时：

- **不要在绑定阶段调用接口做预验证**
- **不要因为格式不确定而拒绝保存**
- 直接将该 API key 保存到当前 skill 配置中
- 保存成功后，告知用户绑定完成
- 若用户当前原本正在执行某个请求，则绑定完成后继续执行原请求

---

### 步骤 3：写入配置

将用户输入的 API key 长久保存到 OpenClaw 配置中。

建议配置结构如下：

```json
{
  "skills": {
    "entries": {
      "aidso-xiasou-geo-diagnosis": {
        "apiKey": "用户输入的_api_key"
      }
    }
  }
}
```

## 绑定成功后的回复模板

如果用户只是单独完成绑定，没有紧接着执行其他动作，回复：

> 绑定成功，以后可直接使用 AIDSO GEO 技能。
> 试试输入「品牌诊断」「知识库」「GEO内容生产」
> 如有其他自定义需求，可前往官网查看：http://geo.aidso.com

如果用户是在执行某个动作过程中完成绑定，则回复：

> 绑定成功，下面继续处理你的请求。

然后继续执行原请求。

## API Key 失效处理

如果任意 AIDSO GEO API 返回以下情况之一：

- HTTP 401
- invalid token
- 鉴权失败
- 明确表示 API key 错误、无效、失效

则必须执行以下处理：

1. 清空当前已保存的 API key
2. 不继续执行当前请求
3. 提示用户重新输入正确的 API key

回复模板：

> 当前绑定的 API key 已失效或不正确，请重新输入你在后台创建的 API key 完成绑定。
> 获取地址：https://geo.aidso.com/setting?type=apiKey&platform=GEO

## 适配说明

本配置文档适用于以下 AIDSO GEO 相关能力：

- 品牌诊断
- 知识库
- GEO内容生产
- 后续新增的其他 GEO 能力

这些能力在执行前都应统一检查 API Key 是否已绑定。