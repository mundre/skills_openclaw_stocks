---
name: wechat-send
description: Send a message to a contact or group via macOS WeChat desktop client. Use when the user asks to send a WeChat message, message someone on WeChat, or reply to a WeChat contact/group. Requires macOS, WeChat desktop logged in, Accessibility permission, and cliclick. NOT for reading messages, sending files/images.
metadata:
  {
    "openclaw":
      {
        "emoji": "💬",
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

# 微信发送消息（wechat-send）

在 macOS 上通过微信桌面客户端向联系人或群组发送文本消息。

## 前置条件

- macOS 微信桌面客户端已安装并登录
- 已向终端 / osascript 授予**辅助功能（Accessibility）**权限
- 已安装 **cliclick**（`brew install cliclick`）

## 两阶段流程

### 第一阶段：搜索联系人

```bash
bash scripts/wechat_send.sh "<联系人>" --search-only
```

执行以下操作：
1. 激活微信并将窗口移动到 `{50,50}`，尺寸调整为 `1200×800`
2. 打开 Cmd+F 搜索框，输入联系人名称
3. 等待下拉结果出现
4. 截图保存至 `/tmp/wechat_search_dropdown.png`

**Agent 操作**：读取截图，找到正确的联系人/群组行（带头像和绿色高亮的行），记录其**屏幕坐标** `{x, y}`。

坐标换算：截图区域起始于 `(50, 50)`，因此屏幕坐标 = `(50 + 截图像素x, 50 + 截图像素y)`。

### 第二阶段：点击并发送

```bash
bash scripts/wechat_send.sh "<联系人>" "<消息内容>" --send-only <x>,<y>
```

通过 `cliclick` 点击目标坐标，粘贴消息内容，按回车发送。

## 示例

```bash
# 第一阶段：搜索
bash scripts/wechat_send.sh "微信联系人" --search-only
# → 读取 /tmp/wechat_search_dropdown.png，找到"微信联系人"位于屏幕坐标 (200, 210)

# 第二阶段：发送
bash scripts/wechat_send.sh "微信联系人" "你好" --send-only 200,210
```

## 为什么需要两个阶段

微信搜索下拉框会混合显示"搜索网络结果"、分区标题和联系人/群组条目，顺序不固定。直接按回车或方向键往往会选中错误条目。由 Agent 视觉识别是唯一可靠的方式。

## 为什么使用 cliclick

AppleScript 的 `click at` 无法点击微信搜索下拉弹窗（非标准 UI 层）。`cliclick` 发送系统级鼠标事件，可以可靠地点击该弹窗。

## 已知限制

- **中文输入**：消息内容写入临时文件，通过 `osascript read POSIX file` 方式粘贴。**禁止**对中文使用 `keystroke`。
- **坐标为屏幕绝对坐标**：基于窗口固定位置 `{50,50}`，尺寸 `{1200,800}`。
- **消息输入框**：粘贴位置固定在 `{700, 650}`。
- **发送键**：默认使用回车（Enter）发送，不是 Ctrl+Enter。
- **多行消息**：支持——剪贴板粘贴会保留换行符。
- **禁止在搜索结果中按方向键↓**：会误选"搜索网络结果"。
