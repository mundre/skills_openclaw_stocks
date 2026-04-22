---
name: silas_clash
description: Clash/Mihomo 代理管理。安装配置、查看状态、切换模式/节点、测速、外网失败时自动代理。
metadata:
  openclaw:
    os: linux
---

# Silas-Clash 代理管理

通过 Clash RESTful API 管理本地代理（Mihomo/Clash Meta）。

## 首次安装配置

### 1. 安装 Mihomo（Clash Meta 内核）

```bash
# 检查架构
uname -m

# 下载对应版本（以 amd64 为例）
curl -Lo /tmp/mihomo.gz https://github.com/MetaCubeX/mihomo/releases/download/v1.19.21/mihomo-linux-amd64-v1.19.21.gz
gunzip /tmp/mihomo.gz
chmod +x /tmp/mihomo
sudo mv /tmp/mihomo /usr/local/bin/mihomo
```

### 2. 获取配置

**询问用户订阅地址**，然后下载配置：

```bash
# 方式一：订阅链接直接下载
curl -Lo ~/.config/mihomo/config.yaml "用户提供的订阅地址"

# 方式二：Clash 仪表盘配置（推荐）
# 访问 https://yacd.haishan.me 或 https://metacubexd.github.io/metacubexd
# 在仪表盘中粘贴订阅地址，自动生成 config.yaml
```

### 3. 确保配置开启 API

检查 `~/.config/mihomo/config.yaml` 中有：
```yaml
external-controller: 127.0.0.1:9090
# secret: "你的密码"  # 可选，建议空
```

### 4. 启动

```bash
mihomo -d ~/.config/mihomo
```

### 5. 验证

```bash
curl -s http://127.0.0.1:9090/version
# 应返回 {"meta":true,"version":"v1.x.x"}
```

### 6. 写入本地配置

将连接信息保存到 `memory/clash-config.json`：
```json
{
  "api_url": "http://127.0.0.1:9090",
  "api_secret": "",
  "proxy_http": "http://127.0.0.1:7890",
  "proxy_socks5": "socks5://127.0.0.1:7891",
  "proxy_all": "socks5://127.0.0.1:7891",
  "install_path": "/usr/local/bin/mihomo",
  "config_path": "~/.config/mihomo/config.yaml"
}
```

> ⚠️ 代理端口（7890/7891）以实际 config.yaml 中的 mixed-port / port 为准。

## 常用操作

### 查看状态
```bash
curl -s http://127.0.0.1:9090/version
curl -s http://127.0.0.1:9090/configs | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"模式: {d.get('mode')}\")"
```

### 查看当前节点
```bash
curl -s http://127.0.0.1:9090/proxies/%F0%9F%9A%80%20%E8%8A%82%E7%82%B9%E9%80%89%E6%8B%A9 | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f\"当前节点: {d.get('now','?')}\")
"
```

### 切换模式
```bash
# rule（规则分流，推荐日常）
curl -X PATCH http://127.0.0.1:9090/configs -H "Content-Type: application/json" -d '{"mode":"rule"}'

# global（全局代理）
curl -X PATCH http://127.0.0.1:9090/configs -H "Content-Type: application/json" -d '{"mode":"global"}'

# direct（直连）
curl -X PATCH http://127.0.0.1:9090/configs -H "Content-Type: application/json" -d '{"mode":"direct"}'
```

### 切换节点
```bash
# 先列出节点名
curl -s http://127.0.0.1:9090/proxies/%F0%9F%9A%80%20%E8%8A%82%E7%82%B9%E9%80%89%E6%8B%A9 | python3 -c "
import json,sys
d=json.load(sys.stdin)
for n in d.get('all',[]): print(n)
"

# 切换到指定节点
curl -X PUT "http://127.0.0.1:9090/proxies/%F0%9F%9A%80%20%E8%8A%82%E7%82%B9%E9%80%89%E6%8B%A9" \
  -H "Content-Type: application/json" \
  -d '{"name":"节点名称"}'
```

### 测速
```bash
# 测所有节点
curl -X GET "http://127.0.0.1:9090/group/%F0%9F%9A%80%20%E8%8A%82%E7%82%B9%E9%80%89%E6%8B%A9/delay?timeout=5000&url=https://www.google.com/generate_204"

# 测当前节点
curl -X GET "http://127.0.0.1:9090/proxies/%F0%9F%9A%80%20%E8%8A%82%E7%82%B9%E9%80%89%E6%8B%A9/delay?timeout=5000&url=https://www.google.com/generate_204"
```

## 外网访问代理策略

当 web_search / web_fetch / Serper / Tavily 等外网工具失败时：

1. **第一次重试**：设置环境变量走代理
   ```bash
   export http_proxy=http://127.0.0.1:7890
   export https_proxy=http://127.0.0.1:7890
   export all_proxy=socks5://127.0.0.1:7891
   ```
2. **第二次重试**：如果还失败，切换 Clash 为 global 模式重试
3. **恢复**：成功后切回 rule 模式

## 订阅更新（手动操作）

⚠️ 订阅更新**不要通过技能自动执行**，手动操作更安全：

```bash
# 备份当前配置
cp ~/.config/mihomo/config.yaml ~/.config/mihomo/config.yaml.bak

# 下载最新订阅
curl -Lo ~/.config/mihomo/config.yaml "订阅地址"

# 重启
pkill mihomo && mihomo -d ~/.config/mihomo
```

## 踩坑指南

- **节点名称含特殊字符**：URL encode 处理，或先列出节点再选
- **API 无响应**：检查 mihomo 是否运行（`pgrep mihomo`），端口是否正确
- **测速超时**：timeout 设 5000ms，太短会误判
- **切节点后不生效**：部分应用有 DNS 缓存，等几秒或重启应用
- **订阅更新搞挂网络**：先备份再更新，挂了用 bak 恢复
- **rule 模式足够**：日常用 rule，只在需要全局代理时临时切 global
- **代理端口**：以 config.yaml 中 mixed-port / port 配置为准，不要硬编码
- **macOS 兼容**：安装路径改为 `/opt/homebrew/bin/mihomo`，其余操作相同
