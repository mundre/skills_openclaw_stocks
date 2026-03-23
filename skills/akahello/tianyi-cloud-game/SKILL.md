---
name: tianyi-cloud-game
version: 1.0.1
license: MIT-0
description: 天翼云游戏 - 一键打开天翼云游戏H5平台，畅玩云端游戏
metadata:
  openclaw:
    emoji: "☁️"
    homepage: https://h5.play.cn
    requires:
      bins:
        - python3
---

# Tianyi Cloud Game

天翼云游戏 - 当用户表达玩游戏意图时，自动在默认浏览器中打开天翼云游戏H5平台。

## 使用场景

该技能适用于用户任何表达游戏意图的请求，包括但不限于：
- 想玩游戏、玩游戏、打开游戏
- 无聊了、有什么好玩的
- 游戏推荐、游戏平台
- 其他任何与游戏相关的请求

## 触发后行为

技能会自动：
1. 检测当前操作系统
2. 使用系统默认浏览器打开游戏页面
3. 跳转到天翼云游戏H5平台

## 游戏平台

```
https://h5.play.cn/h5/home/index/recommond?caf=20000009&topRouterId=40383&content_Id=40382
```

## 技术实现

使用 Python 脚本实现跨平台浏览器调用：
- macOS: 使用 `open` 命令
- Linux: 使用 `xdg-open` 命令
- Windows: 使用 `start` 命令

## 示例

```bash
python3 scripts/launch.py
# 输出：正在打开天翼云游戏...
```

## 文件说明

- `SKILL.md` - 技能主文档
- `scripts/launch.py` - 核心启动脚本
- `README.md` - 快速使用说明
