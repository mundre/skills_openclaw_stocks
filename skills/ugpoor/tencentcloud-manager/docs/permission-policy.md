# 腾讯云子用户权限配置指南

**重要**: 为安全起见，请使用子用户凭证而非主账号密钥。

---

## 📋 权限策略模板

### 策略 1: 资源管理员（推荐）

此策略授予 CVM、Lighthouse、COS 的完整管理权限（不包括删除和财务权限）。

```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "cvm:Describe*", "cvm:RunInstances", "cvm:StartInstances",
        "cvm:StopInstances", "cvm:RestartInstances", "cvm:ModifyInstancesAttribute",
        "cvm:RenewInstances", "vpc:DescribeSecurityGroups", "vpc:CreateSecurityGroup",
        "lighthouse:Describe*", "lighthouse:CreateInstance", "lighthouse:StartInstances",
        "lighthouse:StopInstances", "lighthouse:RestartInstances",
        "lighthouse:ModifyInstancesAttribute", "lighthouse:RenewInstance",
        "name/cos:GetBucket", "name/cos:PutBucket", "name/cos:ListBucket",
        "name/cos:GetObject", "name/cos:PutObject", "name/cos:DeleteObject",
        "name/cos:PutBucketLifecycle", "name/cos:GetBucketLifecycle"
      ],
      "resource": "*"
    }
  ]
}
```

---

### 策略 2: 只读访客

仅授予查询权限，适合监控和审计用途。

```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "cvm:Describe*", "lighthouse:Describe*",
        "name/cos:GetBucket", "name/cos:ListBucket", "name/cos:GetObject"
      ],
      "resource": "*"
    }
  ]
}
```

---

### 策略 3: CVM 专员

仅管理 CVM 云服务器。

```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "cvm:Describe*", "cvm:RunInstances", "cvm:StartInstances",
        "cvm:StopInstances", "cvm:RestartInstances", "cvm:ModifyInstancesAttribute",
        "cvm:RenewInstances", "vpc:DescribeSecurityGroups"
      ],
      "resource": "*"
    }
  ]
}
```

---

### 策略 4: Lighthouse 专员

仅管理轻量应用服务器。

```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "lighthouse:Describe*", "lighthouse:CreateInstance",
        "lighthouse:StartInstances", "lighthouse:StopInstances",
        "lighthouse:RestartInstances", "lighthouse:ModifyInstancesAttribute",
        "lighthouse:RenewInstance"
      ],
      "resource": "*"
    }
  ]
}
```

---

### 策略 5: COS 专员

仅管理对象存储。

```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "name/cos:GetBucket", "name/cos:PutBucket", "name/cos:ListBucket",
        "name/cos:GetObject", "name/cos:PutObject", "name/cos:DeleteObject",
        "name/cos:PutBucketLifecycle", "name/cos:GetBucketLifecycle"
      ],
      "resource": "*"
    }
  ]
}
```

---

## 🔧 配置步骤

1. 访问 https://console.cloud.tencent.com/cam/policy
2. 点击「新建自定义策略」
3. 粘贴上述策略模板
4. 填写策略名称，点击「确定」
5. 访问 https://console.cloud.tencent.com/cam/user 创建子用户
6. 关联策略到子用户
7. 复制 SecretId 和 SecretKey 到 .env 文件

---

## 🔒 安全最佳实践

- ✅ 使用子用户密钥，不用主账号
- ✅ .env 文件加入 .gitignore
- ✅ 定期轮换密钥（90 天）
- ✅ 设置最小权限
- ❌ 不要提交密钥到 Git
- ❌ 不要授予财务权限

---

## 📚 相关文档

- [技能说明](../SKILL.md)
- [CAM 用户管理](https://cloud.tencent.com/document/product/598)
