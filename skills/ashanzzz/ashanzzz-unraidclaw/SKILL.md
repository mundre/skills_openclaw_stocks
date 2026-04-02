---
name: unraidclaw
description: |
  通过 UnraidCLaW API 管理 Unraid 服务器的全套操作。
  用于：
  - Docker 容器管理（创建/启动/停止/删除/查看日志）
  - VM 管理（启动/停止/重启/暂停）
  - 阵列管理（启动/停止/奇偶校验）
  - 硬盘/共享/用户/网络/通知查询
  - 系统重启/关机
  - 完整权限矩阵与 API Key 管理

  前置条件：已在 Unraid 安装 UnraidCLaW 插件，插件已启用 HTTPS + API Key。
  API Base URL：https://<UNRAID_IP>:9876
  认证：Header `x-api-key: <API_KEY>`

  重要：UnraidCLaW API 通过 docker CLI 操作容器，因此镜像必须能从 Unraid 主机访问到（注意国内网络访问 ghcr.io 可能需要代理）。
---

# UnraidCLaW 全套操作指南

## API 基础

- **Base URL**: `https://<UNRAID_IP>:9876`
- **认证**: `x-api-key: <API_KEY>` (Header)
- **返回格式**: 统一包络 `{ "ok": true, "data": {...} }` 或 `{ "ok": false, "error": {...} }`
- **TLS**: 默认自签名证书，请求时加 `-k` 或在业务系统中关闭证书验证

## API 端点总表

| 分类 | 方法 | 端点 | 权限 |
|------|------|------|------|
| Health | GET | `/api/health` | 无 |
| Docker | GET | `/api/docker/containers` | docker:read |
| Docker | GET | `/api/docker/containers/:id` | docker:read |
| Docker | GET | `/api/docker/containers/:id/logs` | docker:read |
| Docker | POST | `/api/docker/containers` | docker:create |
| Docker | POST | `/api/docker/containers/:id/:action` | docker:update |
| Docker | DELETE | `/api/docker/containers/:id` | docker:delete |
| VMs | GET | `/api/vms` | vms:read |
| VMs | GET | `/api/vms/:id` | vms:read |
| VMs | POST | `/api/vms/:id/:action` | vms:update |
| VMs | DELETE | `/api/vms/:id` | vms:delete |
| Array | GET | `/api/array/status` | array:read |
| Array | GET | `/api/array/parity/status` | array:read |
| Array | POST | `/api/array/start` | array:update |
| Array | POST | `/api/array/stop` | array:update |
| Array | POST | `/api/array/parity/start` | array:update |
| Array | POST | `/api/array/parity/pause` | array:update |
| Array | POST | `/api/array/parity/resume` | array:update |
| Array | POST | `/api/array/parity/cancel` | array:update |
| Disks | GET | `/api/disks` | disk:read |
| Disks | GET | `/api/disks/:id` | disk:read |
| Shares | GET | `/api/shares` | share:read |
| Shares | GET | `/api/shares/:name` | share:read |
| Shares | PATCH | `/api/shares/:name` | share:update |
| System | GET | `/api/system/info` | info:read |
| System | GET | `/api/system/metrics` | info:read |
| System | GET | `/api/system/services` | services:read |
| System | POST | `/api/system/reboot` | os:update |
| System | POST | `/api/system/shutdown` | os:update |
| Notifications | GET | `/api/notifications` | notification:read |
| Notifications | GET | `/api/notifications/overview` | notification:read |
| Notifications | POST | `/api/notifications` | notification:create |
| Notifications | POST | `/api/notifications/:id/archive` | notification:update |
| Notifications | DELETE | `/api/notifications/:id` | notification:delete |
| Network | GET | `/api/network` | network:read |
| Users | GET | `/api/users/me` | me:read |
| Logs | GET | `/api/logs/syslog` | logs:read |

## 权限矩阵

| 分类 | 权限 |
|------|------|
| Docker | docker:read, docker:create, docker:update, docker:delete |
| VMs | vms:read, vms:update, vms:delete |
| 阵列/存储 | array:read, array:update, disk:read, share:read, share:update |
| 系统 | info:read, os:update, services:read |
| 通知 | notification:read, notification:create, notification:update, notification:delete |
| 网络 | network:read |
| 用户 | me:read |
| 日志 | logs:read |

预设角色：Read Only、Docker Manager、VM Manager、Full Admin、None

## 核心操作详解

### 1. 容器列表

```bash
curl -s -k -H "x-api-key: $UNRAIDCLAW_TOKEN" \
  https://192.168.8.11:9876/api/docker/containers | python3 -m json.tool
```

### 2. 创建容器（POST /api/docker/containers）

Body 参数（仅 `image` 必填）：

```json
{
  "image": "ghcr.io/anomalyco/opencode:latest",
  "name": "opencode",
  "ports": ["4096:4096", "4097:4097"],
  "volumes": [
    "/mnt/user/appdata/opencode/config:/home/opencode/.config/opencode",
    "/mnt/user/appdata/opencode/data:/home/opencode/.local/share/opencode"
  ],
  "env": [
    "HTTP_PROXY=http://192.168.8.30:7893",
    "HTTPS_PROXY=http://192.168.8.30:7893",
    "NO_PROXY=localhost,127.0.0.1",
    "ENABLE_WEB_UI=true",
    "PUID=99",
    "PGID=100"
  ],
  "restart": "unless-stopped",
  "network": "bridge",
  "icon": "https://example.com/icon.png",
  "webui": "http://[IP]:4097/"
}
```

**注意**：
- 容器创建后会自动生成 DockerMan XML 模板，出现在 Unraid Docker 页面
- `volumes` 格式：`宿主机路径:容器内路径`
- `env` 格式：`KEY=value`
- `ports` 格式：`宿主机端口:容器端口`

### 3. 容器操作（POST /api/docker/containers/:id/:action）

```bash
# 启动
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  https://HOST/api/docker/containers/opencode/start

# 停止
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  https://HOST/api/docker/containers/opencode/stop

# 重启
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  https://HOST/api/docker/containers/opencode/restart

# 暂停
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  https://HOST/api/docker/containers/opencode/pause

# 取消暂停
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  https://HOST/api/docker/containers/opencode/unpause
```

### 4. 查看容器日志

```bash
curl -s -k -H "x-api-key: $TOKEN" \
  "https://HOST/api/docker/containers/opencode/logs?stdout=1&stderr=1&tail=50"
```

### 5. 删除容器

```bash
curl -s -k -X DELETE -H "x-api-key: $TOKEN" \
  https://HOST/api/docker/containers/opencode
```

### 6. 阵列操作

```bash
# 查看阵列状态
curl -s -k -H "x-api-key: $TOKEN" \
  https://HOST/api/array/status

# 启动阵列
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  https://HOST/api/array/start

# 停止阵列
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  https://HOST/api/array/stop
```

### 7. 系统操作

```bash
# 重启 Unraid 宿主机
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  https://HOST/api/system/reboot

# 关机
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  https://HOST/api/system/shutdown
```

### 8. VM 操作

```bash
# 列表
curl -s -k -H "x-api-key: $TOKEN" \
  https://HOST/api/vms

# 启动/停止/重启/强制停止
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  "https://HOST/api/vms/<vm_id>/start"

curl -s -k -X POST -H "x-api-key: $TOKEN" \
  "https://HOST/api/vms/<vm_id>/stop"
```

### 9. 创建通知

```bash
curl -s -k -X POST -H "x-api-key: $TOKEN" \
  -H "Content-Type: application/json" \
  https://HOST/api/notifications \
  -d '{
    "title": "容器已停止",
    "body": "OpenCode 容器在 19:55 异常停止",
    "severity": "warning"
  }'
```

## 镜像访问代理配置（国内必读）

国内服务器访问 `ghcr.io`（GitHub Container Registry）通常需要代理。在创建容器时通过 `env` 传入：

```json
"env": [
  "HTTP_PROXY=http://192.168.8.30:7893",
  "HTTPS_PROXY=http://192.168.8.30:7893",
  "NO_PROXY=localhost,127.0.0.1,192.168.0.0/16"
]
```

但注意：
- 代理环境变量作用于容器内进程，如果镜像拉取在 Docker daemon 层发生（如使用代理registry），需要在 Unraid Docker 设置里配置 registry mirror
- 容器运行时的 HTTP_PROXY/HTTPS_PROXY 影响容器内所有出站请求

## 常见错误处理

| 错误码 | 含义 | 解决方案 |
|--------|------|---------|
| `GRAPHQL_ERROR` / Invalid CSRF token | API Key 权限不足或格式错误 | 检查 Key 是否有对应操作权限 |
| `DOCKER_CREATE_FAILED` / Conflict | 容器名已占用 | 先删除同名容器 |
| `DOCKER_CREATE_FAILED` / No such image | 镜像在主机上不存在 | 手动 `docker pull` 或配置代理 |
| `DOCKER_CREATE_FAILED` / network not found | 网络不存在 | 检查 `network` 字段，用 `bridge` |
| `NOT_FOUND` | 端点或资源不存在 | 检查 URL 和容器/VM ID |

## 脚本工具

配套脚本在 `scripts/` 目录：

- `unraid_docker.sh` — Docker 容器常用操作（创建/启动/停止/删除/日志）
- `unraid_common.sh` — 公共函数（API 调用/凭据读取）
- `opencode_install.sh` — OpenCode Docker 容器一键安装（带代理）

使用前先设置环境变量或在 `.env` 文件中配置：

```bash
export UNRAIDCLAW_TOKEN="your-api-key-here"
export UNRAID_HOST="192.168.8.11"
```

## 参考文档

- UnraidCLaW GitHub: <https://github.com/emaspa/unraidclaw>
- API 完整源码: `packages/unraid-plugin/server`
- OpenClaw Plugin: `packages/openclaw-plugin`（以 npm 包 `unraidclaw` 发布）