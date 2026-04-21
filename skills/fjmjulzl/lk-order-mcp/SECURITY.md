# 🔐 lk-order-mcp 安全说明

## 敏感信息保护

### ⚠️ 切勿提交到版本控制

以下文件包含敏感信息，**绝对不要**提交到 Git 仓库：

- `.env` - 环境变量文件（含 Token）
- `.env.local` - 本地环境配置
- `*.token` - Token 文件
- `*.secret` - 密钥文件

### ✅ 已配置的保护

项目已包含 `.gitignore` 文件，自动忽略上述敏感文件。

---

## Token 配置方式

### 方式 1：环境变量（推荐）

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export LK_ORDER_TOKEN="your_token_here"

# 或临时使用
export LK_ORDER_TOKEN="your_token_here"
node lk-order.cjs quick 美式
```

**优点**：
- Token 不存储在文件中
- 不同环境使用不同 Token
- 符合 12-Factor App 原则

---

### 方式 2：.env 文件（开发环境）

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env，填入 Token
LK_ORDER_TOKEN="your_token_here"
```

**⚠️ 注意**：
- `.env` 已被 `.gitignore` 忽略
- 不要手动添加 `.env` 到 Git
- 仅用于本地开发

---

### 方式 3：openclaw.json（生产环境）

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "mcpServers": {
    "lk-order": {
      "url": "https://inpre.lkcoffee.com/app/proxymcp",
      "transportType": "streamable-http",
      "headers": {
        "Authorization": "Bearer your_token_here"
      }
    }
  }
}
```

**优点**：
- 集中管理所有 MCP 配置
- OpenClaw 自动加载
- 适合生产环境

---

## 获取 Token

Token 存储在 OpenClaw 配置中：

```bash
# 查看当前 Token（注意保密）
grep -A2 '"lk-order"' ~/.openclaw/openclaw.json
```

**⚠️ 安全提醒**：
- Token 等同于密码，不要分享给他人
- 不要提交到代码仓库
- 不要发布到公开论坛
- 如泄露，立即联系管理员重置

---

## 安装安全

### ✅ 安全的安装方式

```bash
# 方式 1：从 ClawHub 安装（推荐）
openclaw skills install lk-order-mcp

# 方式 2：本地安装
bash install.sh /path/to/lk-order-mcp
```

### ❌ 不安全的安装方式

```bash
# 不要使用 curl|bash（有中间人攻击风险）
curl -sSL https://example.com/install.sh | bash  # ❌ 危险！
```

---

## 权限说明

lk-order-mcp 的 Token 有以下权限：

| 权限 | 说明 | 风险等级 |
|------|------|----------|
| 创建订单 | 可以创建新订单 | 🟡 中 |
| 支付订单 | 可以发起支付 | 🔴 高 |
| 查看订单 | 可以查看订单历史 | 🟢 低 |
| 查看菜单 | 可以获取门店菜单 | 🟢 低 |
| 管理购物车 | 可以添加/删除商品 | 🟡 中 |

**建议**：
- 仅在自己信任的设备上使用
- 定期检查订单记录
- 发现异常立即重置 Token

---

## 泄露应急

如果 Token 泄露：

1. **立即联系管理员**重置 Token
2. **检查订单记录**是否有异常
3. **更新所有配置**中的 Token
4. **重新安装技能**（如必要）

---

## 审计日志

定期检查订单记录：

```bash
# 查看最近的订单
/home/node/.openclaw/scripts/lkorder-mcp.sh call get_order_list '{"pageNo":1}'
```

---

## 联系支持

如有安全问题，请联系：
- 安全团队：security@lkcoffee.com
- 技术支持：tech-support@lkcoffee.com

---

**最后更新**: 2026-04-16  
**版本**: 1.0.0
