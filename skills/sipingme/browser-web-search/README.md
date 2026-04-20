# Browser Web Search Skill

把任何网站变成命令行 API，专为 OpenClaw 设计。

## 安装

```bash
npm install -g browser-web-search
```

## 使用

```bash
bws site list                      # 查看所有命令
bws zhihu/hot                      # 知乎热榜
bws xiaohongshu/search "旅行"       # 小红书搜索
bws bilibili/popular               # B站热门
```

## 内置平台

13 平台，41 个命令：

- **搜索**：Google, Baidu, Bing
- **社交**：小红书, 知乎
- **新闻**：36kr, 今日头条
- **开发**：GitHub, CSDN, 博客园
- **视频**：Bilibili
- **娱乐**：豆瓣
- **招聘**：BOSS直聘

## 文档

详细使用说明请查看 [SKILL.md](./SKILL.md)

## 相关链接

- [browser-web-search](https://github.com/sipingme/browser-web-search) - 核心库
- [npm](https://www.npmjs.com/package/browser-web-search)

## License

MIT
