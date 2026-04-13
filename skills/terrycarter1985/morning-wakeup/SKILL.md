---
name: morning-wakeup
description: 晨间唤醒自动化流程，每天早上获取当天天气后自动匹配对应的Sonos播放预设播放音乐。使用场景：设置每日晨间唤醒、天气自适应音乐播放、家庭自动化晨间例程。
tags: ['automation', 'weather', 'sonos', 'home-automation', 'morning-routine']
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["sonos", "clawhub"] },
        "install":
          [
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/steipete/sonoscli/cmd/sonos@latest",
              "bins": ["sonos"],
              "label": "Install sonoscli (go)",
            },
            {
              "id": "node",
              "kind": "node",
              "package": "clawhub",
              "bins": ["clawhub"],
              "label": "Install ClawHub CLI (npm)",
            },
          ],
      },
  }
---

# Morning Wakeup Automation

晨间唤醒自动化流程，根据当日天气自动选择并播放匹配的Sonos音乐预设。

## 功能特点

- 自动获取当日天气（温度、天气状况、降水概率）
- 根据天气条件智能匹配音乐风格
- 自动播放到指定的Sonos设备
- 支持自定义天气-音乐映射规则
- 可通过cron设置每日定时执行

## 快速开始

### 1. 立即执行唤醒流程

```bash
# 使用默认位置（北京）
node scripts/wakeup.js

# 指定位置
node scripts/wakeup.js --location "Shanghai"
```

### 2. 设置每日定时唤醒

使用OpenClaw cron设置晨间唤醒：

```javascript
// 每天早上7:00执行（Asia/Shanghai时区）
const cron = require('openclaw/cron');
cron.add({
  name: 'morning-wakeup-daily',
  schedule: { kind: 'cron', expr: '0 7 * * *', tz: 'Asia/Shanghai' },
  payload: {
    kind: 'agentTurn',
    message: '执行晨间唤醒流程，使用北京天气'
  }
});
```

## 天气-音乐映射规则

| 天气状况 | 温度范围 | 推荐音乐风格 | Sonos预设 |
|----------|----------|-------------|-----------|
| ☀️ 晴天 | > 25°C | 轻快流行、电子音乐 | "Summer Vibes" |
| ☀️ 晴天 | 15-25°C | 轻音乐、爵士 | "Morning Coffee" |
| 🌤️ 多云 | 任意 | 独立音乐、民谣 | "Chill Morning" |
| ☁️ 阴天 | 任意 | 古典音乐、氛围音乐 | "Cloudy Day" |
| 🌧️ 雨天 | 任意 | Lo-Fi、蓝调 | "Rainy Mood" |
| ❄️ 雪天 | < 0°C | 温暖爵士、圣诞音乐 | "Cozy Winter" |

## 使用方式

### 基本使用

```javascript
// scripts/main.js 核心调用
const WakeupAutomation = require('./wakeup');

const automation = new WakeupAutomation({
  location: 'Beijing',
  sonosSpeaker: 'Living Room',
  volume: 25
});

await automation.run();
```

### 自定义配置

```javascript
const automation = new WakeupAutomation({
  location: 'Tokyo',
  units: 'celsius',
  sonosSpeaker: 'Bedroom',
  volume: 30,
  customMappings: {
    sunny: { hot: 'Beach Party', mild: 'Sunny Jazz' },
    rainy: 'Deep Focus'
  }
});
```

## 集成的技能

### Weather 技能

使用 Open-Meteo API 获取天气数据，无需API密钥：

- 当前温度、体感温度
- 天气状况描述
- 降水概率
- 风速、湿度

### Sonos CLI 技能

使用 sonoscli 控制音箱：

- 发现设备：`sonos discover`
- 播放预设：`sonos favorites open "Preset Name"`
- 设置音量：`sonos volume set 25`
- 状态查询：`sonos status`

## 脚本说明

### scripts/wakeup.js

核心自动化脚本，执行以下流程：

1. **获取天气** - 调用 Weather API 获取当日天气数据
2. **匹配预设** - 根据天气规则选择最合适的Sonos预设
3. **播放音乐** - 连接Sonos并播放匹配的预设
4. **输出报告** - 生成执行报告包含天气和播放信息

## Cron 调度配置

使用 OpenClaw cron 工具进行调度：

```bash
# 查看现有cron任务
openclaw cron list

# 添加每日唤醒任务
openclaw cron add \
  --name "morning-wakeup" \
  --schedule "0 7 * * *" \
  --timezone "Asia/Shanghai" \
  --command "node ~/.openclaw/skills/morning-wakeup/scripts/wakeup.js"
```

## 故障排查

### Sonos 设备发现失败

1. 确保设备和网关在同一局域网
2. 尝试直接指定IP：`sonos --ip 192.168.1.100 status`
3. 检查本地网络权限设置（macOS隐私设置）

### 天气获取失败

1. 检查网络连接
2. 验证位置名称格式是否正确
3. 尝试使用经纬度坐标：`--location "39.9042,116.4074"`

### 预设播放失败

1. 列出可用预设：`sonos favorites list`
2. 确认预设名称拼写正确
3. 检查Spotify/Apple Music等服务账号是否正常登录

## 输出示例

```
🌅 晨间唤醒流程已执行
📍 位置: 北京
🌡️ 天气: 晴天，22°C
💧 降水概率: 5%
🎵 匹配预设: Morning Coffee
🔊 设备: Living Room
🔊 音量: 25%
✅ 状态: 播放中
```
