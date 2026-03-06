# 八爪鱼 RPA Webhook 调用工具

通过 Webhook 触发八爪鱼 RPA 任务运行，支持自定义参数传递。

---

## 📦 安装

### 方式一：直接复制

```bash
# 复制整个 skill 目录
cp -r /path/to/bazhuayu-webhook ~/your/path/

# 进入目录
cd ~/your/path/bazhuayu-webhook
```

### 方式二：从 ClawHub 安装（待发布）

```bash
clawhub install bazhuayu-webhook
```

---

## ⚙️ 首次配置

运行初始化命令：

```bash
python3 bazhuayu-webhook.py init
```

按提示输入以下信息：

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| **Webhook URL** | 八爪鱼 Webhook 接口地址 | 从八爪鱼 RPA 触发器页面复制 |
| **签名密钥 (Key)** | Webhook 的签名密钥 | 从八爪鱼 RPA 触发器页面复制 |
| **参数名称** | RPA 应用的输入变量名 | 如：A, B 或 参数 1, 参数 2 |
| **默认参数值** | 每个参数的默认值 | 可选，方便快速运行 |

---

## 🚀 使用方法

### 运行任务（使用默认参数）

```bash
python3 bazhuayu-webhook.py run
```

### 运行任务（指定参数值）

```bash
python3 bazhuayu-webhook.py run --A=值 1 --B=值 2
```

**参数名根据实际配置而定**，例如：
```bash
# 如果参数名是 参数 1 和 参数 2
python3 bazhuayu-webhook.py run --参数 1=李飞 --参数 2=来了

# 如果参数名是 A 和 B
python3 bazhuayu-webhook.py run --A=aa --B=bb
```

### 测试模式（不实际发送）

```bash
python3 bazhuayu-webhook.py test
```

查看将要发送的请求内容，用于调试。

### 查看当前配置

```bash
python3 bazhuayu-webhook.py config
```

---

## 📁 文件结构

```
bazhuayu-webhook/
├── README.md              # 使用说明（本文件）
├── SKILL.md               # Skill 元数据
├── bazhuayu-webhook.py    # 主程序
├── bazhuayu-webhook       # Shell 快捷命令
├── config.json            # 配置文件（需自行填写）
└── config.example.json    # 配置模板
```

---

## 📝 配置文件说明

`config.json` 格式：

```json
{
  "url": "https://api-rpa.bazhuayu.com/api/v1/bots/webhooks/xxx/invoke",
  "key": "你的签名密钥",
  "paramNames": ["A", "B"],
  "defaultParams": {
    "A": "默认值 A",
    "B": "默认值 B"
  }
}
```

| 字段 | 说明 |
|------|------|
| `url` | Webhook 接口地址 |
| `key` | 签名密钥（用于计算请求签名） |
| `paramNames` | 参数名称列表 |
| `defaultParams` | 参数默认值（键值对） |

---

## 🔐 签名算法

根据八爪鱼文档，签名计算方式：

```
string_to_sign = timestamp + "\n" + key
sign = Base64(HmacSHA256(string_to_sign, message=""))
```

本工具已自动处理签名计算，无需手动操作。

---

## 📤 返回结果

### 成功响应（HTTP 200）

```json
{
  "enterpriseId": "企业 ID",
  "flowId": "应用 ID",
  "flowProcessNo": "运行批次号"
}
```

### 失败响应（HTTP 400）

```json
{
  "code": "错误码",
  "description": "错误描述"
}
```

常见错误：
- `SignatureVerificationFailureOrTimestampExpired` - 签名错误或时间戳过期
- 检查系统时间是否准确
- 检查 Key 是否正确

---

## 🛠️ 常见问题

### Q: 参数未设置值？
**A**: 检查 `config.json` 中的参数名是否与 RPA 应用中的变量名**完全一致**（包括空格）。

### Q: 签名验证失败？
**A**: 
1. 检查系统时间是否准确
2. 检查 Key 是否正确复制（无多余空格）

### Q: 如何修改默认参数？
**A**: 直接编辑 `config.json` 中的 `defaultParams` 部分。

---

## 📞 技术支持

如有问题，请联系技能作者或参考八爪鱼官方文档：
- [Webhook 触发任务](https://rpa.bazhuayu.com/helpcenter/docs/skmvua)
- [API 接口文档](https://rpa.bazhuayu.com/helpcenter/docs/rpaapi)
