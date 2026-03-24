# 错敏检测 Skill

## 简介

这是一个用于检测文本敏感信息的 Skill，通过调用 UCAP 平台的安全防护接口，快速识别文本内容中的敏感数据，适用于内容审核、数据合规等场景。

## 功能特性

- 支持多种敏感类型检测（可自定义检测类型列表）
- 标准化的 JSON 格式输入输出
- 完善的错误处理和超时机制
- 兼容 OpenClaw 对话式调用

## 使用方法

### 对话式调用

```
请帮我检测这段文本是否包含敏感信息：{待检测文本内容}
```

### 参数说明

| 参数名 | 类型 | 必传 | 说明 |
|--------|------|------|------|
| content | string | 是 | 待检测的文本内容 |
| userKey | string | 是 | UCAP 平台用户密钥 |
| sensitive_code_list | array | 否 | 检测类型列表，不传则检测所有类型 |

### 返回格式

```json
{
  "code": 0,
  "message": "检测成功",
  "data": {
    // UCAP 接口返回的检测结果
  },
  "request_params": {
    // 请求参数，方便调试
  }
}
```

### 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 检测成功 |
| -1 | 待检测文本不能为空 |
| -2 | userKey 不能为空 |
| -3 | 接口调用超时（15秒） |
| -4 | 接口返回错误 |
| -5 | 接口调用失败 |
| -6 | 接口返回非 JSON 格式数据 |

## 依赖环境

- Python 3.6+
- requests 库

## 安装依赖

```bash
pip install requests
```

## 示例代码

```python
from main import check_sensitive

# 基础检测
result = check_sensitive(
    content="这是一段待检测的文本内容",
    userKey="your_user_key_here"
)

# 指定检测类型
result = check_sensitive(
    content="这是一段待检测的文本内容",
    userKey="your_user_key_here",
    sensitive_code_list=["TYPE_1", "TYPE_2"]
)

print(result)
```

## 注意事项

1. 使用前需要获取有效的 UCAP 平台 userKey
2. 接口调用超时时间为 15 秒
3. 启用了 TLS 验证确保通信安全
