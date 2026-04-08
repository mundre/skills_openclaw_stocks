# 睡眠脑波音频 API 服务

基于 Koa 的轻量 HTTP API 服务，支持**本地音频文件流媒体播放**，为小程序、APP 等第三方客户端提供睡眠脑波音频的查询、匹配和管理接口。

---

## 快速启动

```bash
cd api-server
npm install
node server.js
```

服务默认运行在 `http://0.0.0.0:3092`

---

## 本地音频配置

**当前配置（本地模式）：**
- 音频目录：`C:\Users\龚文瀚\Desktop\sleepAudio`
- 音频数量：12 个
- 模式：`LOCAL`（本地文件流）

如需修改音频目录，运行时指定环境变量：
```bash
AUDIO_BASE_DIR=/path/to/your/audio node server.js
```

---

## 部署到树莓派 / 服务器

```bash
# 1. 上传 api-server 目录到目标机器
scp -r api-server user@<server-ip>:/path/to/app/

# 2. SSH 登录后安装依赖
cd api-server && npm install

# 3. 修改 server.js 中的 AUDIO_BASE_DIR 为实际路径
#    Linux/macOS 示例: /home/pi/sleepAudio

# 4. 后台运行（推荐 pm2）
npm install -g pm2
pm2 start server.js --name sleep-brainwave-api
pm2 save && pm2 startup

# 5. 查看状态
pm2 list
pm2 logs sleep-brainwave-api
```

---

## 访问地址（本地运行）

| 接口 | 地址 |
|------|------|
| 健康检查 | `http://localhost:3092/health` |
| 流媒体播放 | `http://localhost:3092/audio-stream/{audioId}` |
| 音频列表 | `http://localhost:3092/api/audio/list` |
| 智能匹配 | `http://localhost:3092/api/audio/match?subtype=deep_sleep&severity=轻度` |

---

## 核心接口说明

### 流媒体播放（小程序直接可播放）

```
GET /audio-stream/:audioId
```

**示例：**
```
http://localhost:3092/audio-stream/bw_deep_sleep_pre_30min_mild_delta_v1
```

返回 MPEG 音频流，支持 HTTP Range（拖动播放），小程序 ` InnerAudioContext.src` 直接赋值即可播放。

---

### 获取音频清单

```
GET /api/audio/list?scene=睡前&severity=轻度
```

返回列表中每条自动附带 `streamUrl` 字段，可直接用于播放。

---

### 智能匹配

```
GET /api/audio/match?subtype=sleep_onset&severity=中度&duration=30&userId=user_001
```

返回最佳匹配音频及 `streamUrl`。

---

### 获取用户画像

```
POST /api/profile
Body: { "userId": "user_001", "disorderSubtype": "deep_sleep", "severity": "轻度" }
```

---

## 小程序调用示例

```javascript
// 查询音频列表
wx.request({
  url: 'http://localhost:3092/api/audio/list',
  data: { scene: '睡前' },
  success(res) {
    if (res.data.code === 0) {
      const audio = res.data.data.items[0];
      console.log('播放地址:', audio.streamUrl); // 直接可用于 InnerAudioContext
    }
  }
});

// 智能匹配并播放
wx.request({
  url: 'http://localhost:3092/api/audio/match',
  data: { subtype: 'deep_sleep', severity: '轻度' },
  success(res) {
    if (res.data.data) {
      const audio = res.data.data;
      const innerAudio = wx.createInnerAudioContext();
      innerAudio.src = audio.streamUrl; // 流媒体地址
      innerAudio.play();
    }
  }
});
```

---

## 注意事项

1. **音频文件**：需提前将 `.mp3` 文件放入 `C:\Users\龚文瀚\Desktop\sleepAudio` 目录
2. **小程序访问**：开发阶段勾选"不校验合法域名"；生产环境需通过 Nginx 反向代理或配置合法域名
3. **局域网访问**：本机 IP `192.168.3.18`，其他设备访问 `http://192.168.3.18:3092`
4. **CORS**：已允许所有来源，生产环境建议限制具体域名
