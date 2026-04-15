# Socket 故障排查

## EACCES（权限不足）
初始化脚本写入系统目录时权限不足。

处理步骤：
```bash
sudo mtop-devtools-native-host initialize
```

## 首次使用先检查
请先完成 native messaging 初始化：

```bash
npm install -g @mtop-devtools/native-host
mtop-devtools-native-host initialize
```

初始化后建议重启 AI 客户端。如仍无法连接，可打开 Chrome DevTools 的 Mtop Viewer 面板手动触发建联。

## ENOENT（找不到 Socket）
native host socket 尚未启动。

处理步骤：
1. 确认 Chrome 浏览器已打开，等待插件自动建联（约 60s 内）。
2. 如仍失败，打开 DevTools 切换到 Mtop Viewer 面板手动触发建联。
3. 如果使用本地开发版扩展，需指定扩展 ID：`mtop-devtools-native-host initialize --extension-id {EXTENSION_ID}`
4. 重新执行命令。

## ECONNREFUSED / 连接关闭
native host 可能崩溃或已断开连接。

处理步骤：
1. 插件会自动重连，稍等片刻后重试。
2. 如仍失败，打开 DevTools 切换到 Mtop Viewer 面板手动触发重连。
3. 如有需要，重新执行初始化：
   - `mtop-devtools-native-host initialize`
4. 重新执行命令。

## 请求超时
扩展未能在超时时间内返回数据。

处理步骤：
1. 增加超时参数：`--timeout 30`
2. 降低 payload 大小（如 `includeBody: false`、减小 `count`）
3. 增加过滤条件，缩小查询范围。
