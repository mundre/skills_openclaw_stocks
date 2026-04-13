---
name: socialepoch-wa-scrm
description: 官方原生对接 SocialEpoch WhatsApp SCRM 开放API，零代码实现全类型消息收发、发送WhatsApp消息,客户管理、用户画像，聊天记录、WebHook 回调，消息记录查询，号码在线查询，号码状态查询等操作。
version: 1.0.5
author: SocialEpoch
tools: [Fetch, Config]
metadata:
  emoji: 📱
---

# SocialEpoch WhatsApp SCRM 智能助手
官方原生对接 SocialEpoch WhatsApp SCRM 开放API，零代码实现全类型消息收发、发送WhatsApp消息,客户管理、用户画像，聊天记录、WebHook 回调，消息记录查询，号码在线查询，号码状态查询等操作。

---

## 【1】发送文字消息（type=1）
### 触发词
发送WA消息 | 发WhatsApp | 发送文字消息

### 参数提取
sendWhatsApp, friendWhatsApp, text

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/gsTask/assign/soCreate
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "name": "wa-msg-text",
  "sendType": 1,
  "targetType": 1,
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "content": [
    {
      "type": 1,
      "text": "{{text}}",
      "sort": 0
    }
  ]
}
```

### 返回
✅ 文字消息发送成功
发送账号：{{sendWhatsApp}}
目标客户：{{friendWhatsApp}}
消息内容：{{text}}
任务ID：{{data.taskId}}

---

## 【2】发送图片消息（type=2）
### 触发词
发送图片 | 发WA图片 | 发送图片消息

### 参数提取
sendWhatsApp, friendWhatsApp, imageUrl, imageCaption

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/gsTask/assign/soCreate
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "name": "wa-msg-image",
  "sendType": 1,
  "targetType": 1,
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "content": [
    {
      "type": 2,
      "imageUrl": "{{imageUrl}}",
      "caption": "{{imageCaption}}",
      "sort": 0
    }
  ]
}
```

### 返回
✅ 图片消息发送成功
图片链接：{{imageUrl}}
备注：{{imageCaption}}
任务ID：{{data.taskId}}

---

## 【3】发送音频消息（type=3）
### 触发词
发送音频 | 发WA语音 | 发送语音消息

### 参数提取
sendWhatsApp, friendWhatsApp, audioUrl

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/gsTask/assign/soCreate
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "name": "wa-msg-audio",
  "sendType": 1,
  "targetType": 1,
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "content": [
    {
      "type": 3,
      "audioUrl": "{{audioUrl}}",
      "sort": 0
    }
  ]
}
```

### 返回
✅ 音频消息发送成功
音频链接：{{audioUrl}}
任务ID：{{data.taskId}}

---

## 【4】发送文件消息（type=4）
### 触发词
发送文件 | 发文档 | 发送附件

### 参数提取
sendWhatsApp, friendWhatsApp, fileUrl, fileName

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/gsTask/assign/soCreate
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "name": "wa-msg-file",
  "sendType": 1,
  "targetType": 1,
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "content": [
    {
      "type": 4,
      "fileUrl": "{{fileUrl}}",
      "fileName": "{{fileName}}",
      "sort": 0
    }
  ]
}
```

### 返回
✅ 文件消息发送成功
文件名：{{fileName}}
文件链接：{{fileUrl}}
任务ID：{{data.taskId}}

---

## 【5】发送视频消息（type=5）
### 触发词
发送视频 | 发WA视频 | 发送视频消息

### 参数提取
sendWhatsApp, friendWhatsApp, videoUrl, videoCaption

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/gsTask/assign/soCreate
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "name": "wa-msg-video",
  "sendType": 1,
  "targetType": 1,
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "content": [
    {
      "type": 5,
      "videoUrl": "{{videoUrl}}",
      "caption": "{{videoCaption}}",
      "sort": 0
    }
  ]
}
```

### 返回
✅ 视频消息发送成功
视频链接：{{videoUrl}}
备注：{{videoCaption}}
任务ID：{{data.taskId}}

---

## 【6】发送名片消息（type=6）
### 触发词
发送名片 | 发联系人 | 发送个人名片

### 参数提取
sendWhatsApp, friendWhatsApp, cardName, cardPhone, cardCompany, cardPosition

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/gsTask/assign/soCreate
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "name": "wa-msg-card",
  "sendType": 1,
  "targetType": 1,
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "content": [
    {
      "type": 6,
      "name": "{{cardName}}",
      "phone": "{{cardPhone}}",
      "company": "{{cardCompany}}",
      "position": "{{cardPosition}}",
      "sort": 0
    }
  ]
}
```

### 返回
✅ 名片消息发送成功
姓名：{{cardName}}
电话：{{cardPhone}}
公司：{{cardCompany}}
任务ID：{{data.taskId}}

---

## 【7】发送名片超链（type=10）
### 触发词
发送名片超链 | 发个人超链 | 发送名片链接

### 参数提取
sendWhatsApp, friendWhatsApp, cardLinkName, cardLinkUrl, cardLinkDesc, cardLinkImgUrl

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/gsTask/assign/soCreate
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "name": "wa-msg-card-link",
  "sendType": 1,
  "targetType": 1,
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "content": [
    {
      "type": 10,
      "name": "{{cardLinkName}}",
      "url": "{{cardLinkUrl}}",
      "desc": "{{cardLinkDesc}}",
      "imgUrl": "{{cardLinkImgUrl}}",
      "sort": 0
    }
  ]
}
```

### 返回
✅ 名片超链发送成功
名称：{{cardLinkName}}
链接：{{cardLinkUrl}}
任务ID：{{data.taskId}}

---

## 【8】发送分流超链（type=11）
### 触发词
发送分流超链 | 发活动链接 | 发送分流链接

### 参数提取
sendWhatsApp, friendWhatsApp, flowLinkTitle, flowLinkUrl, flowId, flowLinkDesc, flowLinkImgUrl

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/gsTask/assign/soCreate
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "name": "wa-msg-flow-link",
  "sendType": 1,
  "targetType": 1,
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "content": [
    {
      "type": 11,
      "title": "{{flowLinkTitle}}",
      "url": "{{flowLinkUrl}}",
      "flowId": {{flowId}},
      "desc": "{{flowLinkDesc}}",
      "imgUrl": "{{flowLinkImgUrl}}",
      "sort": 0
    }
  ]
}
```

### 返回
✅ 分流超链发送成功
标题：{{flowLinkTitle}}
链接：{{flowLinkUrl}}
分流ID：{{flowId}}
任务ID：{{data.taskId}}

---

## 【9】查询聊天记录
### 触发词
查询聊天记录 | 查看对话 | 获取历史消息

### 参数提取
sendWhatsApp, friendWhatsApp, pageNum, pageSize

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/chat/record
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "pageNum": {{pageNum}},
  "pageSize": {{pageSize}}
}
```

---

## 【10】获取客户列表
### 触发词
获取客户列表 | 查询客户 | 我的客户

### 参数提取
sendWhatsApp, pageNum, pageSize

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/customer/list
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "sendWhatsApp": "{{sendWhatsApp}}",
  "pageNum": {{pageNum}},
  "pageSize": {{pageSize}}
}
```

---

## 【11】更新客户标签/备注
### 触发词
设置客户标签 | 设置备注 | 打标签

### 参数提取
sendWhatsApp, friendWhatsApp, remark, tags

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/customer/update
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "sendWhatsApp": "{{sendWhatsApp}}",
  "friendWhatsApp": "{{friendWhatsApp}}",
  "remark": "{{remark}}",
  "tags": {{tags}}
}
```

---

## 【12】查询账号在线状态
### 触发词
查询账号状态 | WA是否在线

### 参数提取
whatsapp

```fetch
method: GET
url: {{API_BASE}}/group-dispatch-api/whatsapp/queryWhatsAppStatus
headers:
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
query:
  whatsapp: {{whatsapp}}
```

---

## 【13】查询消息发送状态
### 触发词
查询消息状态 | 消息是否成功

### 参数提取
taskId

```fetch
method: GET
url: {{API_BASE}}/group-dispatch-api/gsTask/queryExecuteStatus
headers:
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
query:
  taskId: {{taskId}}
```

---

## 【14】设置 WebHook 回调
### 触发词
设置回调 | 配置WebHook | 开启消息推送

### 参数提取
callbackUrl

```fetch
method: POST
url: {{API_BASE}}/group-dispatch-api/callback/set
headers:
  Content-Type: application/json
  tenantId: {{tenantId}}
  ApiKey: {{ApiKey}}
body:
{
  "url": "{{callbackUrl}}",
  "enable": true
}
```
---

## 通用说明
1.  所有API请求均严格对照SocialEpoch WhatsApp SCRM官方文档，确保接口路径、参数、请求头完全正确；
2.  用户仅需配置tenantId、ApiKey（API_BASE默认国内环境，无需修改），即可使用所有功能；
3.  所有触发词支持自然语言模糊匹配，用户无需输入固定格式，只需表达核心需求即可（如：“用8613800138000给8613900139000发消息，内容是你好”）；
4.  若API返回错误，将自动提示错误原因（如：“账号离线，无法发送消息”“ApiKey错误，鉴权失败”），无需用户查看接口文档。
