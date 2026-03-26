---
name: dknowc-search
description: "深知可信搜索 - 政策法规权威搜索引擎。触发条件：(1) 用户搜索政策、法规、条例、规章、规范性文件，(2) 用户查询政务办事流程、办事材料、办理条件，(3) 用户说'搜索政策'、'查一下法规'、'深知搜索'、'可信搜索'，(4) 公文写作需要搜索政策依据，(5) 任何需要查找政府、法律、行业标准、公共服务相关资料的场景。"
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["python3"], "env": ["DKNOWC_SEARCH_API_KEY", "DKNOWC_SEARCH_ENDPOINT"] }, "primaryEnv": "DKNOWC_SEARCH_API_KEY" } }
---

# 深知可信搜索

基于深知智能 1.7 亿公开文件和 16 亿知识切片的政策法规搜索引擎，所有结果可溯源到官方权威网站。

## 配置

通过环境变量注入（OpenClaw 自动管理）：

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `DKNOWC_SEARCH_API_KEY` | API 密钥 | `sk-xxxxx` |
| `DKNOWC_SEARCH_ENDPOINT` | 搜索接口地址 | `https://open.dknowc.cn/dependable/search/{appid}` |

首次触发时，如检测到环境变量未配置：

1. 告知用户：「请提供深知可信搜索的 API Key 和调用地址。可在 https://platform.dknowc.cn 注册并实名认证（送 100 元）后获取。获取指南见 `references/apikey-guide.md`。」
2. 用户提供了 API Key 和调用地址后，AI 自动调用 `gateway config.patch` 写入配置：

```json
{
  "skills": {
    "entries": {
      "dknowc-search": {
        "env": {
          "DKNOWC_SEARCH_API_KEY": "{用户提供的key}",
          "DKNOWC_SEARCH_ENDPOINT": "{用户提供的地址}"
        }
      }
    }
  }
}
```

3. 配置完成后 OpenClaw 会自动重启，重启后即可使用。

## 接口调用

**使用脚本调用**：

```bash
python3 {baseDir}/scripts/search.py "搜索内容"
```

**请求参数**：

| 参数 | 命令行参数 | 说明 | 示例 |
|------|-----------|------|------|
| query | 位置参数 | 搜索内容（必填） | `"高新技术企业认定"` |
| service_area | `--area` | 办理地域 | `--area 北京` |
| eff_time | `--time` | 生效日期 | `--time 2025年` |
| knowBase | 默认开启 | 知识专库链接 | `--no-knowbase` 关闭 |
| policy | `--policy` | 规范性文件清单 | `--policy` |
| item | `--item` | 在线办理清单 | `--item` |

**调用示例**：

```bash
# 最简搜索
python3 {baseDir}/scripts/search.py "高新技术企业认定"

# 有地域
python3 {baseDir}/scripts/search.py "社保政策" --area 北京

# 有地域 + 时间 + 知识专库
python3 {baseDir}/scripts/search.py "社保卡" --area 北京 --time 2025年

# 需要规范性文件清单
python3 {baseDir}/scripts/search.py "数据安全管理办法" --policy
```

## 返回结构

脚本自动输出格式化结果，包含：
- 召回文章数
- 每篇文章的标题、来源、日期、链接、关键段落
- 知识专库链接（如有）
- 规范性文件清单（如有）
- 在线办理清单（如有）
- 原始 JSON（`RAW_JSON_START` / `RAW_JSON_END` 之间，供程序化使用）

**错误码**：401 密钥无效、403 权限不足、429 余额不足、500 服务异常

## 使用流程

1. 从用户问题中提取搜索关键词和地域
2. 根据场景选择参数组合（地域 → `--area`，时间 → `--time`）
3. 调用脚本，整理呈现结果
4. 如有知识专库链接，立即发给用户
5. 如有规范性文件清单或在线办理清单，单独列出

## 使用建议

- 控制搜索词在核心业务关键词，去掉"帮我搜""查一下"等无关词
- 地域信息同时出现在搜索词和 `--area` 参数中，提高召回精度
- 结果中的源网址均可溯源到官方权威网站
- 如需引用具体政策条款，使用 `--policy` 获取完整文件清单
