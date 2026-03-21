# 企业年金智能查询技能 Pro

🏦 企业年金/职业年金智能查询技能 - 专业版

## 快速开始

```bash
# 基本搜索
./scripts/search.sh "腾讯公司"

# 指定结果数量
./scripts/search.sh "深圳市道桥维修中心" 15

# 完整调查（所有渠道）
./scripts/search.sh "华为技术有限公司" --full

# 仅查询单位性质
./scripts/search.sh "阿里巴巴" --nature-only
```

## 功能特性

- ✅ **18 种调查渠道**：政府采购网、银行官网、招聘信息、员工分享等
- ✅ **多搜索引擎**：Tavily + 百度/Bing/360/搜狗 4 引擎
- ✅ **单位性质智能识别**：自动判断事业单位/企业/民营企业
- ✅ **年金类型精确判断**：企业年金 vs 职业年金
- ✅ **标准化报告输出**：带来源链接、置信度、错误检查清单

## 安装依赖

```bash
# Ubuntu/Debian
sudo apt-get install curl jq

# macOS
brew install curl jq

# Python PDF 解析（可选）
pip install pypdf
```

## 环境变量

```bash
# Tavily API Key（推荐）
export TAVILY_API_KEY="your_api_key"

# SearXNG 本地实例（可选）
export SEARXNG_URL="http://localhost:8080"
```

## 工具使用顺序

1. **Tavily API** - 8 个关键词组合全部搜索
2. **Multi Search Engine** - 百度/Bing/360/搜狗 4 引擎必须全部执行

## 输出示例

```markdown
# 腾讯公司 - 企业年金/职业年金调查报告

## 核心结论
| 项目 | 结论 | 置信度 | 来源 |
|------|------|--------|------|
| 单位性质 | 民营企业（上市公司） | ⭐⭐⭐⭐⭐ | 百度百科 |
| 企业年金 | ❌ 无 | ⭐⭐⭐⭐⭐ | 知乎分析 |
| 替代方案 | ✅ 股权激励 + 退休福利 | ⭐⭐⭐⭐⭐ | 腾讯新闻 |
```

## License

MIT
