# G.workspace 安装指南

## 前置要求

- Node.js 18+
- Discord Bot（需要 Send Messages + Manage Webhooks + Read History + Mention Everyone 权限）
- OpenClaw 已配置 Discord

## 安装步骤

告诉用户执行以下步骤：

### 第一步：创建 Discord Bot

1. 打开 https://discord.com/developers/applications
2. 点 "New Application" → 输入名字 → Create
3. 左侧 "Bot" → "Reset Token" → **复制 Token**
4. 左侧 "OAuth2" → **复制 Application ID**
5. 左侧 "Bot" → 开启 "Message Content Intent"

### 第二步：邀请 Bot 到服务器

用以下链接（替换 YOUR_APP_ID）：
```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&permissions=277562297344&scope=bot%20applications.commands
```

在需要使用 G.workspace 的每个 Discord 服务器都授权一次。

### 第三步：安装 G.workspace

```bash
# 克隆代码
cd ~ && git clone https://github.com/luojingwei123/Workspace.git .gworkspace-app

# 安装依赖
cd ~/.gworkspace-app && npm install

# 创建数据目录
mkdir -p ~/.gworkspace/{data/files,data/screenshots,logs}
```

### 第四步：配置

```bash
cd ~/.gworkspace-app && node bin/cli.js setup
```

按提示输入：
- Bot Token
- Application ID
- 端口（默认 3080）
- 代理地址（可选）

### 第五步：启动服务

```bash
cd ~/.gworkspace-app && node bin/cli.js start
```

### 第六步：同步 Discord 命令

```bash
cd ~/.gworkspace-app && node bin/cli.js sync
```

### 验证

在 Discord 输入 `/gworkspace`，如果看到空间信息或安装成功提示，就完成了。

## macOS 开机自启（可选）

安装后建议设置 LaunchAgent 自动启动，避免重启后忘记手动启动服务。

```bash
cat > ~/Library/LaunchAgents/com.gworkspace.server.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.gworkspace.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>HOME/.gworkspace-app/src/index.js</string>
    </array>
    <key>WorkingDirectory</key>
    <string>HOME/.gworkspace-app</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>HOME/.gworkspace/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>HOME/.gworkspace/logs/stderr.log</string>
</dict>
</plist>
EOF

# 替换 HOME 为实际路径
sed -i '' "s|HOME|$HOME|g" ~/Library/LaunchAgents/com.gworkspace.server.plist

# 加载
launchctl load ~/Library/LaunchAgents/com.gworkspace.server.plist
```
