---
name: wechat-read
description: Read chat history from a WeChat contact or group via macOS desktop client screenshot + agent OCR. Use when the user asks to read, view, check, or retrieve WeChat chat messages, conversation history, or recent messages from a contact or group. Requires macOS, WeChat desktop logged in, Accessibility permission, and cliclick. NOT for sending messages (use wechat-send).
metadata:
  {
    "openclaw":
      {
        "emoji": "📖",
        "os": ["darwin"],
        "requires": { "bins": ["cliclick"], "apps": ["WeChat"] },
        "install":
          [
            {
              "id": "cliclick",
              "kind": "brew",
              "formula": "cliclick",
              "bins": ["cliclick"],
              "label": "安装 cliclick（brew）",
            },
          ],
      },
  }
---

# 微信读取聊天记录（wechat-read）

在 macOS 上通过截图 + Agent 视觉识别的方式，读取微信联系人或群组的聊天记录。

## 前置条件

- macOS 微信桌面客户端已安装并登录
- 已向终端 / osascript 授予**辅助功能（Accessibility）**权限
- 已向终端授予**屏幕录制（Screen Recording）**权限（`screencapture` 需要）
- 已安装 **cliclick**（`brew install cliclick`）

## 三阶段流程

### 第一阶段：搜索并进入聊天

```bash
bash scripts/wechat_read.sh "<联系人>" --enter
```

执行以下操作：
1. 激活微信并将窗口移动到 `{50,50}`，尺寸调整为 `1200×800`
2. 打开搜索框，输入联系人名称
3. 截图保存至 `/tmp/wechat_read_search.png`

**Agent 操作**：读取截图，找到正确的联系人/群组行，记录其**屏幕坐标** `{x, y}`。

坐标换算：截图区域起始于 `(50, 50)`，因此屏幕坐标 = `(50 + 截图像素x, 50 + 截图像素y)`。

### 第二阶段：点击进入并截图捕获

```bash
bash scripts/wechat_read.sh "<联系人>" --capture <x>,<y> [--pages N]
```

点击联系人进入会话，等待聊天加载，然后逐页截图聊天记录：

- 截取**聊天内容区域**（右侧面板，不含侧边栏和输入框）
- 使用 AppleScript `key code 126`（方向键↑）向上滚动
- 每次滚动执行 **8 次方向键↑**，确保相邻两页有约 **30% 内容重叠**，防止消息遗漏
- 截图保存至 `/tmp/wechat_read_p1.png`、`/tmp/wechat_read_p2.png`……
- 默认截取 3 页；使用 `--pages N` 指定页数

**滚动终止检测**：对每张截图计算 MD5 校验值。若连续两张截图完全相同（页面未变化），则判定已到达聊天顶部，自动停止，并输出 `[REACHED_TOP]` 标记。

### 第三阶段：Agent OCR 与内容整合

**Agent 操作**：读取所有截图（`/tmp/wechat_read_p1.png` 至 `pN.png`），然后：

1. **识别消息**：从每张截图中提取发送人、时间戳、消息内容
2. **去除重叠**：相邻页面约有 30% 内容重叠，匹配重复消息并去重
3. **处理相对时间**：微信显示"昨天 14:30"、"星期三"、"3月28日"等格式，根据当前日期转换为绝对时间
4. **按时间顺序组装**：截图顺序为从新到旧（p1 最新），需反向排列为正序
5. **输出结果**：整理为清晰的对话记录格式

## 使用示例

### 读取最近消息（默认）

```bash
# 第一阶段
bash scripts/wechat_read.sh "微信联系人" --enter
# → Agent 读取 /tmp/wechat_read_search.png，找到联系人坐标 (200, 210)

# 第二阶段：截取 3 页（默认）
bash scripts/wechat_read.sh "微信联系人" --capture 200,210
```

### 读取更多历史记录

```bash
# 截取 10 页
bash scripts/wechat_read.sh "微信联系人" --capture 200,210 --pages 10
```

### 读取全部已加载历史

```bash
# 最多截取 50 页，到顶自动停止
bash scripts/wechat_read.sh "微信联系人" --capture 200,210 --pages 50
```

## 已知限制

- **截图区域固定**：聊天内容区域固定为屏幕矩形 `(370, 90, 830, 620)`，基于窗口位置 `{50,50}`、尺寸 `{1200,800}`。若微信窗口布局变化，需重新校准。
- **滚动粒度**：每页 8 次方向键↑，调整为约 30% 重叠。若重叠过多或过少，可修改脚本中的 `SCROLL_STEPS`。
- **仅捕获文字消息**：图片、表情包、语音、文件以视觉元素形式出现——Agent 可描述但无法提取内容。
- **历史深度取决于微信客户端**：仅能读取客户端已加载的消息。极旧消息可能需要先手动向上滚动加载。
- **中文 OCR 准确率**：取决于 Agent 使用的视觉模型，高分辨率截图效果更佳。
- **坐标为屏幕绝对坐标**：基于窗口固定位置 `{50,50}`，尺寸 `{1200,800}`。

## 可校准参数

以下参数为基于标准微信 macOS 布局（窗口位置 `{50,50}`，尺寸 `{1200,800}`）的固定值。若截图区域偏移，请测试并调整：

| 参数 | 当前值 | 控制内容 |
|------|--------|----------|
| `CHAT_RECT` | `370,90,830,620` | 聊天内容区截图范围（x, y, 宽, 高） |
| `SCROLL_STEPS` | `8` | 每次翻页的方向键↑次数 |
| `SCROLL_DELAY` | `0.04` | 每次方向键↑之间的等待时间（秒） |
| `POST_SCROLL_WAIT` | `0.6` | 滚动后截图前的等待时间（秒） |
| `CLICK_FOCUS_POS` | `750,400` | 截图前点击聚焦聊天区域的坐标 |
