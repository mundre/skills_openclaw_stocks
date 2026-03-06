# 八爪鱼 RPA Webhook 调用技能

通过 Webhook 触发八爪鱼 RPA 任务运行，支持自定义参数传递。

## 目录

`~/.openclaw/workspace/skills/bazhuayu-webhook/`

## 安装

```bash
# 复制 skill 目录
cp -r ~/.openclaw/workspace/skills/bazhuayu-webhook /你的路径/

# 进入目录并初始化
cd /你的路径/bazhuayu-webhook
python3 bazhuayu-webhook.py init
```

## 配置文件

`config.json` - 存储 Webhook URL、签名密钥、参数配置

```json
{
  "url": "Webhook 地址",
  "key": "签名密钥",
  "paramNames": ["A", "B"],
  "defaultParams": {"A": "默认值 A", "B": "默认值 B"}
}
```

## 使用方法

### 运行任务（使用默认参数）

```bash
python3 bazhuayu-webhook.py run
```

### 运行任务（指定参数值）

```bash
python3 bazhuayu-webhook.py run --A=新值 --B=新值
```

### 测试模式（不实际发送）

```bash
python3 bazhuayu-webhook.py test
```

### 查看配置

```bash
python3 bazhuayu-webhook.py config
```

## 签名算法

```
string_to_sign = timestamp + "\n" + key
sign = Base64(HmacSHA256(string_to_sign, message=""))
```

## 返回结果

- 成功：返回 `flowId`、`flowProcessNo`、`enterpriseId`
- 失败：返回错误码和错误描述

## 文件结构

```
bazhuayu-webhook/
├── README.md              # 完整使用说明
├── SKILL.md               # 本文件
├── bazhuayu-webhook.py    # 主程序
├── bazhuayu-webhook       # Shell 快捷命令
├── config.json            # 配置文件
└── config.example.json    # 配置模板
```
