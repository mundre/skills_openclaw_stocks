***

name: claw-plugin-yixiaoer
description: 对外发布入口技能，覆盖登录、团队选择、账号查询、素材上传与发布提交，并负责组装文章/图文/视频三类发布表单参数。用于端到端发布与相关账号/内容查询。
---------------------------------------------------------------------------------------

# 蚁小二发布技能

## ⚠️ 前置条件（必读）

> **使用本技能前必须先完成以下操作：**
>
> 1. **注册蚁小二账号** - 访问 [蚁小二官网](https://www.yixiaoer.cn) 注册账号
> 2. **绑定自媒体账号** - 在蚁小二后台绑定需要发布的自媒体平台账号（抖音、小红书、B站等）
> 3. **登录获取凭证** - 使用 `login` 命令登录蚁小二账号

**注意**：本技能依赖蚁小二平台的服务，需要用户自行注册蚁小二账号并完成自媒体账号绑定后才能正常使用。

## 技能介绍

该技能是唯一对外发布入口，负责流程编排与表单组装。支持文章、图文、视频三类内容的多平台一键分发。AI Agent 在执行任何发布任务时必须调用此技能。

## 使用场景

当用户出现以下意图时必须使用该技能：

- 发布文章
- 发布图文
- 发布视频
- 自媒体内容分发
- 发布到抖音 / 小红书 / 视频号
- 多平台内容发布
- 一键分发内容
- 将内容发布到多个平台
- 上传视频素材
- 查询发布记录

## 支持平台

明确允许的 platform 值（AI 只能从以下枚举中选择），并标注各平台支持的内容类型：

### 支持视频发布

| 平台      | platform 值 |
| ------- | ---------- |
| 抖音      | 抖音         |
| 快手      | 快手         |
| 小红书     | 小红书        |
| 微信视频号   | 微信视频号      |
| 新浪微博    | 新浪微博       |
| 腾讯微视    | 腾讯微视       |
| 知乎      | 知乎         |
| 企鹅号     | 企鹅号        |
| 搜狐号     | 搜狐号        |
| 一点号     | 一点号        |
| 网易号     | 网易号        |
| 爱奇艺     | 爱奇艺        |
| 哔哩哔哩    | 哔哩哔哩       |
| 百家号     | 百家号        |
| 头条号     | 头条号        |
| 大鱼号     | 大鱼号        |
| 搜狐视频    | 搜狐视频       |
| 皮皮虾     | 皮皮虾        |
| 腾讯视频    | 腾讯视频       |
| 多多视频    | 多多视频       |
| 美拍视频    | 美拍视频       |
| ACFun视频 | ACFun视频    |
| 小红书商家号  | 小红书商家号     |
| 车家号视频   | 车家号视频      |
| 易车号视频   | 易车号视频      |
| 蜂网视频    | 蜂网视频       |
| 得物      | 得物         |
| 美柚视频    | 美柚视频       |

### 支持图文发布

| 平台    | platform 值 |
| ----- | ---------- |
| 抖音    | 抖音         |
| 快手    | 快手         |
| 新浪微博  | 新浪微博       |
| 小红书   | 小红书        |
| 微信视频号 | 微信视频号      |
| 百家号   | 百家号        |
| 知乎    | 知乎         |
| 头条    | 头条         |

### 支持文章发布

| 平台       | platform 值 |
| -------- | ---------- |
| 爱奇艺      | 爱奇艺        |
| 百家号      | 百家号        |
| 头条号      | 头条号        |
| 新浪微博     | 新浪微博       |
| 知乎       | 知乎         |
| 企鹅号      | 企鹅号        |
| 搜狐号      | 搜狐号        |
| 一点号      | 一点号        |
| 网易号      | 网易号        |
| 大鱼号      | 大鱼号        |
| 快传号      | 快传号        |
| 雪球号      | 雪球号        |
| 哔哩哔哩     | 哔哩哔哩       |
| 微信公众号    | 微信公众号      |
| 豆瓣       | 豆瓣         |
| CSDN     | CSDN       |
| AcFun    | AcFun      |
| 简书       | 简书         |
| wifi万能钥匙 | wifi万能钥匙   |
| 车家号      | 车家号        |
| 易车号文章    | 易车号文章      |

## 支持操作

| 操作                    | 说明                                                                             | 调用优先级      |
| --------------------- | ------------------------------------------------------------------------------ | ---------- |
| `login`               | 用户名密码登录                                                                        | 自动触发       |
| `logout`              | 退出登录                                                                           | 按需         |
| `list-accounts`       | 获取已绑定自媒体账号列表                                                                   | 必须         |
| `get-teams`           | 获取团队列表                                                                         | 必须         |
| `account-overviews`   | 获取账号概览数据（新版）；参数 `platform` 必填（平台中文名如"抖音""小红书"），可选 `page`、`size`、`name`、`group` | 按需         |
| `content-overviews`   | 获取作品数据列表；参数 `page`、`size` 与筛选条件                                                | 按需         |
| `publish-flow`        | 一键发布流程（自动登录、选团队、发布）                                                            | **唯一推荐入口** |
| `get-publish-records` | 获取发布记录                                                                         | 按需         |
| `upload-url`          | 获取文件上传到 OSS 的 URL                                                              | 按需         |

> **内部接口**（不对外暴露）：`publish`

## AI调用规则

当用户表达以下需求时必须调用本技能：

- 发布内容
- 发布文章
- 发布视频
- 发布到抖音
- 发布到小红书
- 多平台分发
- 自媒体分发
- 一键分发

**调用优先级：`publish-flow`** **>** **`publish`**

> **重要**：AI 发布内容时**必须优先调用** **`publish-flow`**，该接口自动完成登录、选团队、发布全流程。`publish` 为内部接口，不推荐直接调用。

## 发布流程

标准 workflow 如下（AI 必须严格遵循）：

1. **检查登录状态**
   - 检查是否存在有效登录会话
   - 如无会话或会话过期，自动调用 `login` 进行登录
2. **获取团队列表（如需）**
   - 调用 `get-teams` 获取用户所属团队
   - 如有多团队，自动选择或提示用户选择
3. **获取账号列表**
   - 调用 `list-accounts` 获取已绑定的自媒体账号
4. **匹配平台账号**
   - 根据用户指定的 `platform` 从账号列表中匹配对应的 `platformAccountId`
   - 如未找到对应账号，返回错误提示用户先绑定账号
5. **处理素材**
   - 远程素材：直接使用素材 URL 和尺寸信息
   - 本地素材：先调用 `upload-url` 获取 key，再使用 key 发布
   - 视频素材必须包含 `duration` 字段
6. **组装发布表单**
   - 根据内容类型（article/imageText/video）组装对应参数
7. **调用发布接口**
   - **必须使用** **`publish-flow`** 自动完成登录、选团队、发布全流程

## 发布参数规则

所有发布请求必须包含以下字段：

| 字段                | 说明         | 必填 | 规则                                    |
| ----------------- | ---------- | -- | ------------------------------------- |
| title             | 标题         | 是  | 最大 50 字                               |
| description       | 描述         | 是  | 最大 2000 字                             |
| platforms         | 发布平台数组     | 是  | 必须是数组，如 `["抖音", "小红书"]`               |
| platformAccountId | 平台账号ID     | 是  | 通过 list-accounts 获取                   |
| publishType       | 内容类型       | 是  | 固定值：`article` / `imageText` / `video` |
| clientId          | 设备号/客户端ID  | 是  | 发布必填                                  |
| publishChannel    | 发布渠道       | 否  | cloud-云发布（默认）, local-本机发布            |
| coverKey          | 封面 OSS Key | 否  | 本地封面上传后获取的 OSS key                    |

## 素材处理规则

### 远程素材

```json
{
  "path": "https://example.com/image.jpg",
  "width": 1920,
  "height": 1080,
  "size": 1024000
}
```

### 本地素材

1. 先调用 `upload-url` 获取上传凭证和 key
2. 获取 key 后使用 key 进行发布

```json
{
  "key": "upload/key/path.jpg",
  "width": 1920,
  "height": 1080,
  "size": 1024000
}
```

### 视频素材特殊规则

视频素材**必须**包含 `duration` 字段，且封面**需要从视频上截图**获取：

```json
{
  "path": "https://example.com/video.mp4",
  "width": 1920,
  "height": 1080,
  "size": 10240000,
  "duration": 30
}
```

> **注意**：视频发布时，封面不能使用任意图片，必须从视频中截取一帧作为封面。可通过视频处理工具提取关键帧。

## 内容类型规则

### 文章（article）

- `publishType` 固定为 `article`
- 必填字段：`title`、`description`、`platforms`、`platformAccountId`、`clientId`
- 可选字段：`createType`、`pubType`、`publishContentId`
- 封面字段：远端使用 `{ path, width, height, size }`；本地路径先上传后使用 `key`
- 竖版封面字段 `verticalCoverPath` / `verticalCoverKey` 同上规则

### 图文（imageText）

- `publishType` 固定为 `imageText`
- 必填字段：`title`、`description`、`imagePaths`、`platforms`、`platformAccountId`、`clientId`
- 图片字段：远端使用 `{ path, width, height, size }`；本地路径先上传后使用 `key`
- 未提供封面时，默认使用第一张图作为封面

### 视频（video）

- `publishType` 固定为 `video`
- 必填字段：`title`、`description`、`videoPath`、`platforms`、`platformAccountId`、`clientId`
- 可选字段：`videoDuration`、`videoWidth`、`videoHeight`、`coverPath`
- 视频字段：远端使用 `{ path, width, height, size, duration }`；本地路径先上传后使用 `key`
- 封面字段：远端使用 `{ path, width, height, size }`；本地路径先上传后使用 `key`

## 登录逻辑

### 自动登录策略

1. 如果没有登录会话，自动调用 `login`
2. 如果会话过期，重新登录
3. 登录成功后缓存凭证，避免重复登录

### 前置条件

- 已完成 `login`，具备有效会话，并保存登录凭证
- 已通过 `get-teams` 选定团队
- 后续所有接口调用必须携带登录凭证
- 如未满足，AI 应自动补全后继续流程

## 示例

### 发布视频示例

```json
{
  "publishType": "video",
  "title": "AI创业的三个机会",
  "description": "分享AI创业趋势",
  "platforms": ["抖音", "小红书"],
  "videoPath": {
    "path": "https://example.com/video.mp4",
    "duration": 30,
    "width": 1920,
    "height": 1080,
    "size": 15360000
  },
  "coverPath": {
    "path": "https://example.com/cover.jpg",
    "width": 1920,
    "height": 1080,
    "size": 512000
  }
}
```

### 发布图文示例

```json
{
  "publishType": "imageText",
  "title": "今日热点分析",
  "description": "深度解读今日热点事件",
  "platforms": ["小红书", "视频号"],
  "imagePaths": [
    {
      "path": "https://example.com/image1.jpg",
      "width": 1920,
      "height": 1080,
      "size": 1024000
    },
    {
      "path": "https://example.com/image2.jpg",
      "width": 1920,
      "height": 1080,
      "size": 921600
    }
  ]
}
```

### 发布文章示例

```json
{
  "publishType": "article",
  "title": "2024年AI发展趋势",
  "description": "本文分析了2024年AI领域的主要发展趋势...",
  "platforms": ["头条号", "百家号"],
  "coverPath": {
    "path": "https://example.com/article_cover.jpg",
    "width": 1920,
    "height": 1080,
    "size": 768000
  }
}
```

### 使用 publish-flow 完整流程示例

```json
{
  "username": "your_username",
  "password": "your_password",
  "teamId": 12345,
  "content": {
    "publishType": "video",
    "title": "AI创业的三个机会",
    "description": "分享AI创业趋势",
    "platforms": ["抖音", "小红书"],
    "platformAccountId": "account_123",
    "videoPath": {
      "path": "https://example.com/video.mp4",
      "duration": 30,
      "width": 1920,
      "height": 1080,
      "size": 15360000
    }
  }
}
```

