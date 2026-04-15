# 安全和隐私声明

## 🔐 安全信息

### 认证方式

本技能使用 **X-API-Key** 认证方式调用 Digilifeform API。

- **API Key 来源** - 用户在 https://datu.digilifeform.com 注册账户后获取
- **API Key 存储** - 在 ClawHub 中作为环境变量 `DATU_API_KEY` 存储
- **API Key 安全** - 仅在调用 API 时使用，不会被记录或分享

### 请求头格式

所有 API 请求需要在请求头中包含 API Key：

```
X-API-Key: your_api_key_here
```

### 外部 API 调用

本技能调用以下外部服务：

| 服务 | 用途 | 数据类型 |
|------|------|--------|
| https://datu.digilifeform.com/api/datu/create | 生成大图 | 文案文本、文件内容 |
| https://datu.digilifeform.com/api/edit/create | 修图 | 图片、修改指令 |
| https://datu.digilifeform.com/api/tasks/{id} | 查询状态 | 任务ID |

### 文件上传

支持上传以下文件类型：
- 文本：TXT、Markdown
- 文档：PDF、Word（.doc/.docx）
- 图片：PNG、JPG、WebP、GIF

**限制：**
- 最大文件大小：100MB
- 支持的格式见上方

---

## 📋 数据隐私

### 数据收集

本技能收集以下数据：
- 用户输入的文案内容
- 上传的文件内容
- 生成的海报
- API 调用日志（用于故障排查）

### 数据使用

- ✅ 用于生成用户请求的海报
- ✅ 用于改进服务质量（匿名统计）
- ❌ 不用于训练 AI 模型
- ❌ 不与第三方共享
- ❌ 不用于广告或营销

### 数据保留

| 数据类型 | 保留期限 | 删除方式 |
|--------|--------|--------|
| 生成的海报 | 30 天 | 自动删除 |
| 上传的文件 | 任务完成后 | 立即删除 |
| API 日志 | 90 天 | 自动删除 |
| 账户信息 | 账户存在期间 | 用户可申请删除 |

### 用户权利

- 📥 **数据导出** - 可导出你的账户数据
- 🗑️ **数据删除** - 可申请删除账户及相关数据
- 🔍 **数据查询** - 可查看你的使用记录和生成历史
- ⚙️ **隐私设置** - 可在账户设置中调整隐私选项

---

## 🛡️ 安全建议

### 使用前检查

- [ ] 确认 https://datu.digilifeform.com 是官方网站（检查 TLS 证书）
- [ ] 验证 API Key 来自官方账户
- [ ] 阅读完整的隐私政策：https://datu.digilifeform.com/privacy
- [ ] 确认你理解数据处理方式

### 最佳实践

1. **先用测试数据** - 用非敏感内容测试工作流程
2. **避免敏感信息** - 不要上传包含个人隐私的文件
3. **定期检查账户** - 在 https://datu.digilifeform.com/account 查看活动
4. **保护 API Key** - 不要在代码中硬编码 API Key，使用环境变量
5. **及时更新** - 定期检查技能更新和安全补丁

### 如何报告安全问题

如果发现安全漏洞或隐私问题：

1. **不要公开发布** - 避免在公开渠道讨论
2. **联系官方** - 发送邮件至 security@digilifeform.com
3. **提供详情** - 描述问题、影响范围和复现步骤
4. **等待回复** - 官方会在 48 小时内回应

---

## 📞 隐私和安全联系

- 📧 **隐私问题** privacy@digilifeform.com
- 🔒 **安全问题** security@digilifeform.com
- 💬 **一般支持** support@digilifeform.com
- 🌐 **官方网站** https://datu.digilifeform.com

---

## 📄 相关文档

- [完整隐私政策](https://datu.digilifeform.com/privacy)
- [服务条款](https://datu.digilifeform.com/terms)
- [API 文档](https://datu.digilifeform.com/docs)
- [GitHub 仓库](https://github.com/digilifeform/datu-skill)

---

**最后更新** 2026-04-13

如有任何疑问，欢迎联系我们。
