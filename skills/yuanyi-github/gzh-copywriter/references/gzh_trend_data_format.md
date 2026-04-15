# 公众号热门数据格式说明

## 概览

本文档定义了公众号热门数据查询脚本 `fetch_gzh_trends.py` 的输入输出格式规范。

## 输入格式

### 脚本参数

```bash
python scripts/fetch_gzh_trends.py --keyword <关键词> [选项]
```

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `--keyword` | 是 | 搜索关键词（支持多个关键词，逗号分隔，最多5个，总长度不超过200字符） | - |
| `--start-date` | 否 | 开始日期，格式 yyyy-MM-dd | 最近30天 |
| `--max-items` | 否 | 每类内容最多展示数量 | 10 |
| `--output-format` | 否 | 输出格式：text、json 或 markdown | markdown |
| `--debug` | 否 | 调试模式，打印原始API响应 | False |

## 输出格式

### 三类爆款内容

脚本返回**近30天**的公众号热门数据，包含以下三类爆款内容：

| 内容类型 | 适用场景 |
|---------|---------|
| **低粉高阅读爆款** | 适合模仿学习，发现低粉丝高阅读的优质内容 |
| **阅读靠前爆款** | 了解当前阅读量最高的热门内容 |
| **原创靠前爆款** | 发现高质量原创内容 |

### 作品数据字段（完整）

每个作品包含以下字段：

#### 作品基本信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `photoId` | string | 作品ID（唯一标识） |
| `title` | string | 作品标题 |
| `summary` | string | 作品摘要/描述 |
| `oriUrl` | string | 作品链接（公众号文章地址） |
| `publicTime` | string | 发布时间（格式：YYYY-MM-DD HH:MM:SS） |
| `type` | string | 文章类型（如：文摘、原创等） |
| `originalFlag` | int | 是否原创（1=原创，0=非原创） |
| `orderNum` | int | 文章位置（0=头条，1=次条） |

#### 作者信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `accountId` | string | 公众号账号ID |
| `userName` | string | 公众号名称 |
| `userHeadUrl` | string | 作者头像URL（需拼接：https://open.weixin.qq.com/qr/code?username={accountId}） |
| `fans` | string | 粉丝数（如："100w+"、"48w+"） |

**作者主页链接拼接规则**：
```
https://open.weixin.qq.com/qr/code?username={accountId}
```

#### 互动数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `clicksCount` | string | 阅读数（如："10w+"、"8w+"） |
| `likeCount` | int | 点赞数 |
| `commentCount` | int | 评论数 |
| `shareCount` | int | 分享数 |
| `watchCount` | int | 在看数 |
| `interactiveCount` | int | 互动总数 |

#### 图片链接

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `coverUrl` | string | 封面图URL |
| `thumbnail` | string | 缩略图URL |

### JSON 输出示例

```json
{
  "keyword": "职场",
  "low_fan_explosive": [
    {
      "photoId": "ACF0E1227424ABAA91722B8CB9A61596",
      "title": "我找老板加薪。老板把全公司1万人的薪资表摊给我看，我排第10...",
      "summary": "哈马斯呼吁伊朗避免袭击邻国...",
      "oriUrl": "https://mp.weixin.qq.com/s?__biz=Mzg2Njc1MjkwMA==&mid=2247508072&idx=1&sn=46aadeb917574b98c38e1d70c068d1f5#rd",
      "publicTime": "2026-03-15 07:26:13",
      "type": "文摘",
      "originalFlag": 0,
      "orderNum": 0,
      "accountId": "RiixDesign",
      "userName": "大熊聊设计",
      "fans": "100w+",
      "clicksCount": "10w+",
      "likeCount": 234,
      "commentCount": 29,
      "shareCount": 381,
      "watchCount": 67,
      "interactiveCount": 711,
      "coverUrl": "https://mmbiz.qpic.cn/sz_mmbiz_jpg/...",
      "thumbnail": "https://mmbiz.qpic.cn/sz_mmbiz_jpg/..."
    }
  ],
  "read_top": [...],
  "original_top": [...]
}
```

### 文本输出格式（表格形式）

文本输出采用 Markdown 表格格式，结构清晰，便于阅读：

```markdown
## 爆款文章（共 3 条）
### - **低粉高阅读爆款**（共 3 条）
统计时间：近30天

| 序号 | 标题 | 作者 | **阅读数** | 在看 | 点赞 | 评论 | 分享 |
|------|------|------|---------|------|------|------|------|
| 1 | [我找老板加薪。老板把全公司1万人的薪资表摊给我看，我排第10...](https://mp.weixin.qq.com/s?__biz=...) | [大熊聊设计](https://open.weixin.qq.com/qr/code?username=RiixDesign)（粉丝：100w+） | **10w+** | 67 | 234 | 29 | 381 |
| 2 | [张雪峰走后才懂：北京户口，真的值得拿命换吗？](https://mp.weixin.qq.com/s?__biz=...) | [记录生活边角](https://open.weixin.qq.com/qr/code?username=gh_620c50aa531c)（粉丝：100w+） | **8w+** | 112 | 236 | 182 | 1247 |
| 3 | ... | ... | ... | ... | ... | ... | ... |

### - **阅读靠前爆款**（共 3 条）
统计时间：近30天

| 序号 | 标题 | 作者 | **阅读数** | 在看 | 点赞 | 评论 | 分享 |
|------|------|------|---------|------|------|------|------|
| 1 | [上班的意义是什么](https://mp.weixin.qq.com/s?__biz=...) | [日常感集铺](https://open.weixin.qq.com/qr/code?username=itinghyy)（粉丝：100w+） | **10w+** | 86 | 254 | 109 | 1018 |
| 2 | ... | ... | ... | ... | ... | ... | ... |

### - **原创靠前爆款**（共 3 条）
统计时间：近30天

| 序号 | 标题 | 作者 | **阅读数** | 在看 | 点赞 | 评论 | 分享 |
|------|------|---------|------|------|------|------|------|
| 1 | [我一年抄底了8套老破小 \| 谷雨](https://mp.weixin.qq.com/s?__biz=...) | [谷雨实验室](https://open.weixin.qq.com/qr/code?username=guyulab)（粉丝：48w+） | **10w+** | 448 | 1453 | 44 | 1w+ |
| 2 | ... | ... | ... | ... | ... | ... | ... |
```

### 表格字段说明

| 列名 | 说明 |
|------|------|
| 序号 | 排名 |
| 标题 | 作品标题（可点击跳转到文章） |
| 作者 | 作者名称（可点击跳转到公众号二维码页面）+ 粉丝数 |
| 阅读数 | 阅读数（加粗显示） |
| 在看 | 在看数 |
| 点赞 | 点赞数 |
| 评论 | 评论数 |
| 分享 | 分享数 |

## 使用注意事项

### 数据获取原则

1. **必须调用脚本查询**：不能使用其他方式查询或直接搜索网络资讯
2. **必须等待脚本执行完成**：获取返回结果后才能进行后续步骤
3. **必须展示完整数据列表**：不能跳过或询问用户

### 数据展示原则

1. **展示所有字段**：每个作品展示完整信息，包括标题链接、作者链接、互动数据等
2. **三类爆款内容全部展示**：低粉高阅读、阅读靠前、原创靠前

### 字段说明

1. **阅读数格式**：API 返回的阅读数可能是字符串（如："10w+"、"8w+"），不是纯数字
2. **粉丝数格式**：粉丝数也可能是字符串（如："100w+"、"48w+"）
3. **封面图和缩略图**：通常相同，但有时缩略图分辨率更低
