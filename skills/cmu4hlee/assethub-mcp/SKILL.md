---
name: "assethub-mcp"
description: "资产管理系统AI助手(openclaw技能)。提供资产查询、维修报修等工具 via MCP 协议"
version: "1.0.2"
metadata: { "openclaw": { "emoji": "🔧", "requires": { "bins": ["python3"] } } }
---

# AssetHub MCP Server

资产管理系统 MCP 服务器，将资产管理的 API 功能暴露为 MCP 工具。

## 功能

| 工具 | 说明 |
|------|------|
| list_assets | 查询资产列表 |
| get_asset | 获取单个资产详情 |
| create_repair_request | 创建维修申请 |
| list_repair_requests | 查询维修申请 |

## 使用方法

### 方式一：使用 mcporter

```bash
# 列出资产
mcporter call assethub.list_assets keyword:CT pageSize:10

# 创建报修
mcporter call assethub.create_repair_request asset_code:000001053 fault_description:"设备故障" fault_level:"一般"
```

### 方式二：直接运行

```bash
# 启动 MCP 服务器
python3 server/server.py
```

## 配置

服务器地址已在代码中配置：
- Base URL: http://160ttth72797.vicp.fun:59745/api
- 租户 ID: 2
- 用户名: su
- 密码: 123456

如需修改，请编辑 `server/server.py` 中的配置。

## 安全提示

- 凭据硬编码在代码中，生产环境请使用环境变量
- 建议添加访问控制

---

**版本**: 1.0.0
