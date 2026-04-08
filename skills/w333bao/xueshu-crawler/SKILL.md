---
name: xueshu-crawler
description: |
  学术创新网（xueshuchuangxin.com）理论详情页批量爬取。当用户要求采集、爬取、下载学术创新网的文章、理论详情、theoryDetail 页面时使用此 skill。
  支持按guid范围采集，输出Markdown格式，断点续爬，浏览器自动重连。
  Keywords: 学术创新网, xueshuchuangxin, theoryDetail, 理论详情, 网站爬虫, 批量下载, 学术文章采集
---

# 学术创新网理论详情爬虫

## 依赖

- Python 3.8+
- DrissionPage：`pip install DrissionPage`
- Chrome 浏览器（无头模式运行）

## 用法

### 基本命令

```powershell
python scripts\crawl_theory.py --start 318 --end 2000 --output "C:\AIDOW\lunwen\pdf01"
```

### 完整参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--start` | 是 | — | 起始guid |
| `--end` | 是 | — | 结束guid |
| `--output` | 是 | — | 输出目录（本地或UNC路径） |
| `--delay` | 否 | 2.0 | 请求间隔秒数 |
| `--no-images` | 否 | false | 不加载图片加速爬取 |
| `--max-reconnect` | 否 | 5 | 最大浏览器重连次数 |

### 典型场景

```powershell
# 从guid 1开始全量采集到500
python scripts\crawl_theory.py --start 1 --end 500 --output "D:\output\theories"

# 快速模式（不加载图片，间隔3秒）
python scripts\crawl_theory.py --start 100 --end 1000 --output "D:\out" --delay 3 --no-images

# 保存到NAS（注意验证网络连通性）
python scripts\crawl_theory.py --start 318 --end 2000 --output "\\192.168.110.182\e\AIDOW\lunwen\pdf01"
```

## 执行流程

1. **验证输出目录**：自动创建目录并测试写入权限
2. **启动无头Chrome**：DrissionPage驱动，失败自动重连
3. **逐页采集**：guid递增，每页提取标题+正文
4. **断点续爬**：自动跳过 `guid_*.md` 已存在文件
5. **保存校验**：写入后验证文件存在性
6. **输出格式**：`{guid}_{title}.md`（Markdown，含元数据）

## 已知问题

- 部分guid无有效内容（标题为undefined或内容过短），会标记为 `Fail: Invalid title`
- NAS网络路径可能不稳定导致文件写入失败，建议先保存到本地再手动复制
- 浏览器长时间运行可能被系统SIGKILL，重启后利用断点续爬继续

## Markdown输出格式

```markdown
# 文章标题

正文内容...

---
*GUID: 318*
*Crawled: 2026-04-07 23:13:45*
```
