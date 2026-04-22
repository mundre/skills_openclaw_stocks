# movie-resource-search

影视资源搜索工具，支持百度、夸克、天翼、雷电四大网盘。

## 搜索

```
/movie-resource-search <关键词>
```

## 新增功能

### 扩展信息字段
每条资源包含：
- 📖 简介 - 剧情简介
- 🖼️ 海报 - 海报图片链接
- 💬 评论 - 影视评论摘要
- 📝 备注 - 自定义备注
- 🎬 TMDB数据 - 电影元数据（标题/年份/类型/评分/导演/演员/剧情/国家/受欢迎程度等）

### TMDB 字段详情
| 字段 | 说明 | 示例 |
|------|------|------|
| title | 电影标题 | 阿凡达：火与烬 |
| year | 上映年份 | 2025 |
| genres | 电影类型（/分隔） | 科幻/惊悚/奇幻/冒险 |
| rating | 评分 | 7.6 |
| votes | 评分人数 | 266038 |
| countries | 制片国家 | 美国/中国大陆 |
| director | 导演 | 詹姆斯·卡梅隆 |
| actors | 主演（/分隔） | 萨姆·沃辛顿/佐伊·索尔达娜 |
| overview | 剧情概要 | 影片聚焦杰克·萨利与... |
| popularity | 受欢迎程度 | 🔥Top 100 |
| poster_url | 海报URL | https://... |
| url | TMDB详情页 | https://douban.com/... |

### 智能 TMDB 模糊搜索
搜索支持从 TMDB 字段模糊匹配：
- 搜索 `Avatar` → 可命中资源名含"阿凡达"但 TMDB 标题为 "Avatar" 的条目
- 搜索 `Cameron` → 只匹配导演含 Cameron 的条目，不会误匹配 Decameron
- 搜索中文关键词 → 子串包含匹配

### 智能信息补充
当搜索结果缺少信息时，会提示用户补充：
```
📝 信息补充提示：
「阿凡达3」缺少以下信息：简介, 海报, TMDB数据

回复格式：电影名|简介|海报URL|评论|备注
或：电影名|tmdb标题|year|genres|rating|votes|countries|director|actors|overview|popularity|poster_url|url
```

### TMDB 反馈示例
```
python search.py --feedback "阿凡达|阿凡达：火与烬|2025|科幻/惊悚|7.6|266038|美国|詹姆斯·卡梅隆|萨姆沃辛顿|剧情概要|TOP100|海报URL|TMDB链接"
```

### 用户积分和等级系统

| 操作 | 积分 |
|------|------|
| 搜索资源 | +1 |
| 反馈补充 | +5 |
| 数据改进 | +10 |

**等级：**
- 🌟 入门新手 (0-10)
- 🎓 进阶用户 (11-50)
- 🎮 高级玩家 (51-200)
- 👑 大神 (201-500)
- 🏆 传奇 (501+)

**成就：**
- 🎯 百次搜索达人 (100次搜索)
- 📝 反馈达人 (10次反馈)
- 📊 数据贡献者 (5次改进)
- 🏆 传奇王者 (500积分)

## 命令

```
python search.py "阿凡达3"           # 搜索（含TMDB显示）
python search.py "Avatar"            # 用英文名搜索（TMDB字段匹配）
python search.py --profile           # 查看个人等级和积分
python search.py --reflect           # 自我诊断报告
python search.py --learn-alias 沙丘3 沙丘  # 学习别名
python search.py --feedback "阿凡达|tmdb标题|2025|类型|7.6|票数|国家|导演|演员|概要|热度|海报|url"  # 补充TMDB
python search.py --block <链接>       # 屏蔽失效链接
python search.py --correct 阿凡达3 <old> <new>  # 记录纠正
```

## 依赖

```
pip install cryptography
```
