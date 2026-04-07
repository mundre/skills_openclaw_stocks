# Swarm Control Feishu

一键配置飞书智能体集群，支持多项目并行、语音服务、全权限控制。

## 🚀 快速开始

### 1. 安装 Skill

```bash
# 克隆或解压到 ~/.openclaw/skills/swarm-control-feishu/
mkdir -p ~/.openclaw/skills
cp -r swarm-control-feishu ~/.openclaw/skills/
```

### 2. 配置

编辑 `~/.openclaw/skills/swarm-control-feishu/files/openclaw-config.json`，填入：

- 飞书 App ID 和 App Secret
- LLM API Key

### 3. 部署

```bash
bash ~/.openclaw/skills/swarm-control-feishu/scripts/deploy.sh
```

### 4. 启动语音服务

```bash
bash ~/.openclaw/skills/swarm-control-feishu/files/start-voice-service.sh
```

### 5. 完成！

在飞书中测试机器人！

## 📋 功能特性

- ✅ **多 Agent 集群** - main, xg, xc, xd 四个独立 agent
- ✅ **全权限控制** - webchat 和飞书都有最大权限
- ✅ **语音服务** - 自动检测和转录语音
- ✅ **子 Agent 支持** - 支持 10 个并发子 agent
- ✅ **Agent 间通信** - 可以互相发送消息
- ✅ **sudo 免密** - 自动配置系统权限

## 📖 文档

查看 `SKILL.md` 获取完整文档。

## 🛠️ 脚本说明

| 脚本 | 说明 |
|------|------|
| `deploy.sh` | 一键部署，创建工作空间、复制配置 |
| `setup-workspaces.sh` | 仅创建工作空间 |
| `sync-config.sh` | 同步 AGENTS.md 到所有 agent |
| `check-status.sh` | 检查所有服务状态 |
| `start-voice-service.sh` | 启动语音服务 |

## 🔧 配置示例

### 最小配置

在 `openclaw-config.json` 中修改：

```json
{
  "channels": {
    "feishu": {
      "accounts": {
        "default": {
          "appId": "cli_xxxxx",  // 修改这里
          "appSecret": "xxxxx"    // 修改这里
        }
      }
    }
  },
  "models": {
    "providers": {
      "jmrzw": {
        "apiKey": "sk-xxxxx"  // 修改这里
      }
    }
  }
}
```

## 🤝 贡献

欢迎 Issue 和 PR！

## 📄 许可证

MIT License
