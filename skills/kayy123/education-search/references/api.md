# 搜题 API 文档

## 接口信息

**接口地址**: `http://edu-openapi.baidu.com/exercise_search_online`

**请求方式**: POST

## 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | ✅ | - | 搜索内容 |
| `topK` | ❌ | 10 | 返回结果数量（最大 20） |

## 请求示例

```bash
curl --location 'http://edu-openapi.baidu.com/exercise_search_online?query=考研政治真题&topK=10' \
  --data '{}'
```

## 返回格式

返回结构：`{"data": [...], "status": 200, "errno": 0}`

### data 数组字段

| 字段 | 说明 |
|------|------|
| `id` | 习题 ID |
| `title` | 标题 |
| `answer` | 答案/描述 |
| `exerciseCategoryName` | 分类（如：考研） |
| `exerciseSubjectName` | 科目（如：数学一） |
| `materialType` | 类型（1=题目，2=答案） |
| `pdfUrl` | PDF 链接 |
| `weight` | 相关度分数 |