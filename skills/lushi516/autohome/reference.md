# Car Master 参考文档

## 完整定时任务配置示例

### 1. 基础定时任务配置
```bash
openclaw cron add \
  --name "daily-car-news" \
  --cron "0 9 * * *" \
  --message "获取汽车之家最新10条资讯" \
  --to "user:ou_b17ab4b0acb0414e1c7844bce4111ee8" \
  --channel feishu \
  --announce \
  --description "每天上午9点获取汽车之家最新资讯"
```

### 2. 完整格式的定时任务配置
```bash
openclaw cron edit 4ad1cf2f-e9a0-4aca-892d-46949ce0a496 \
  --message "获取汽车之家最新10条资讯，按照以下格式发送给我：

**2026 年 [月] [日]汽车之家最新 10 条资讯汇总**

（1）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

（2）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

（3）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

（4）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

（5）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

（6）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

（7）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

（8）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

（9）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

（10）[标题](文章链接) | [立即询价](https://www.autohome.com.cn)


摘要：摘要内容

请确保：
1. 标题使用加粗格式：**2026 年 月 日汽车之家最新 10 条资讯汇总**
2. 包含准确的日期（年 月 日）
3. 每条资讯都要有：标题链接 + | + [立即询价](https://www.autohome.com.cn) + 简短的摘要（摘要前要加摘要：标签）
4. 格式完全按照上面的示例：加粗标题后一个空行，每条资讯的标题和摘要之间有4个空行，每条资讯之间一个空行
5. 获取最新的10条资讯"
```

## 手动获取资讯的命令

### 1. 直接获取网页内容
```bash
# 获取汽车之家新闻页面
web_fetch --url "https://www.autohome.com.cn/news/" --extractMode markdown --maxChars 4000
```

### 2. 获取具体文章内容
```bash
# 获取具体文章（示例）
web_fetch --url "https://www.autohome.com.cn/news/202603/1312959.html" --extractMode markdown --maxChars 2000
```

## 格式验证命令

### 检查当前任务配置
```bash
# 列出所有定时任务
openclaw cron list

# 查看特定任务详情
openclaw cron edit daily-car-news --json | jq '.payload.message'
```

### 测试任务执行
```bash
# 手动运行任务
openclaw cron run daily-car-news
```

## 常见问题解决方案

### 1. 资讯获取失败
**问题**：无法获取汽车之家内容
**解决**：
```bash
# 测试网络连接
curl -I https://www.autohome.com.cn

# 尝试其他新闻源
web_fetch --url "https://news.yiche.com" --extractMode markdown
```

### 2. 格式不正确
**问题**：输出格式不符合要求
**解决**：检查定时任务的消息格式，确保包含所有格式要求

### 3. 定时任务不执行
**问题**：任务已配置但不执行
**解决**：
```bash
# 检查cron服务状态
openclaw cron status

# 启用任务
openclaw cron enable daily-car-news

# 检查下次执行时间
openclaw cron list
```

## 扩展功能

### 1. 多源资讯获取
可以扩展支持多个汽车资讯网站：
- 易车网：https://news.yiche.com
- 懂车帝：https://www.dongchedi.com
- 汽车之家：https://www.autohome.com.cn

### 2. 关键词过滤
添加关键词过滤功能，只获取特定类型的资讯：
- 新能源车相关
- SUV车型相关
- 国产车相关

### 3. 个性化推送
根据用户兴趣定制推送内容：
- 品牌偏好（如：比亚迪、特斯拉、宝马等）
- 价格区间（如：10-20万元、20-30万元等）
- 车型类型（如：SUV、轿车、MPV等）

## 性能优化建议

### 1. 缓存策略
```bash
# 缓存最近获取的资讯，避免重复获取
cache_file="~/.cache/car-news-latest.txt"
if [ -f "$cache_file" ]; then
    # 使用缓存
else
    # 重新获取
fi
```

### 2. 错误重试
```bash
# 添加重试机制
max_retries=3
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if web_fetch --url "https://www.autohome.com.cn/news/"; then
        break
    fi
    retry_count=$((retry_count + 1))
    sleep 5
done
```

## 监控和维护

### 1. 日志记录
```bash
# 记录任务执行日志
log_file="~/.logs/car-master-$(date +%Y%m%d).log"
echo "$(date): 开始执行汽车资讯获取任务" >> "$log_file"
# ... 执行任务 ...
echo "$(date): 任务执行完成" >> "$log_file"
```

### 2. 性能监控
```bash
# 监控任务执行时间
start_time=$(date +%s)
# ... 执行任务 ...
end_time=$(date +%s)
duration=$((end_time - start_time))
echo "任务执行耗时: ${duration}秒"
```

## 更新和维护

### 1. 定期检查
- 每月检查汽车之家网站结构变化
- 更新解析逻辑以适应网站改版
- 测试新的资讯源

### 2. 用户反馈
- 收集用户对资讯质量的反馈
- 根据用户兴趣调整推送内容
- 优化输出格式和阅读体验