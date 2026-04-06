# Global Search API 演示文档

## 接口地址

```
POST https://clb.ciglobal.cn/web_search
```

## 请求说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| search_source | string | 否 | 搜索源：`baidu_search`、`google_search`、`baidu_search_ai`，默认 baidu_search |
| mode | string | 否 | 模式：`network`（实时爬取）、`warehouse`（ES 库），默认 network |
| page | int | 否 | 页码，从 1 开始，默认 1 |

**请求头：** 需要设置 `Content-Type` 为 `application/x-www-form-urlencoded`

## 演示示例

### 示例 1：cURL 调用

```bash
curl -X POST "https://clb.ciglobal.cn/web_search" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "keyword=人工智能" \
  -d "search_source=baidu_search" \
  -d "mode=network" \
  -d "page=1"
```

### 示例 2：Python 调用

```python
import requests

url = "https://clb.ciglobal.cn/web_search"
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "keyword": "人工智能",
    "search_source": "baidu_search",
    "mode": "network",
    "page": 1
}

response = requests.post(url, headers=headers, data=data)
result = response.json()
print(result)
```

### 示例 3：JavaScript (Fetch)

```javascript
fetch('https://clb.ciglobal.cn/web_search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    keyword: '人工智能',
    search_source: 'baidu_search',
    mode: 'network',
    page: '1'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

## 响应示例

```json
{
  "code": 200,
  "message": "success",
  "references": [
    {
      "title": "文章标题",
      "sourceAddress": "https://example.com/article",
      "origin": "来源名称",
      "publishDate": "2025-03-24 12:00:00",
      "summary": "文章摘要"
    }
  ]
}
```

## 搜索源说明

| search_source | 说明 |
|---------------|------|
| baidu_search | 百度资讯实时爬取 |
| google_search | 谷歌资讯实时爬取 |
| baidu_search_ai | 百度 AI 搜索 API |

## 模式说明

| mode | 说明 |
|------|------|
| network | 实时从搜索引擎爬取（配合 search_source 使用） |
| warehouse | 从 Elasticsearch 索引库查询（忽略 search_source） |
