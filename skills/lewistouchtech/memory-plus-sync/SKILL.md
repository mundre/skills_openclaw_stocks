# Memory Plus - 跨渠道记忆同步技能

**版本**: 1.0  
**创建**: 2026-04-07  
**作者**: 伊娃 (Eva)  
**状态**: ✅ 已完成

---

## 背景

- mem0 已删除，官方无跨渠道同步
- 需要实现多渠道记忆同步（飞书、微信、Telegram 等）
- 使用官方 SQLite 数据库，不另起炉灶

---

## 功能清单

### 1. 跨渠道记忆同步 ✅
- ✅ 飞书消息采集与同步
- ✅ 微信消息采集（框架已就绪，待集成）
- ✅ Telegram 消息采集（框架已就绪，待集成）
- ✅ 语音对话记录采集
- ✅ 统一存储到官方 SQLite 数据库

### 2. 实时监控官方系统 ✅
- ✅ 数据库连通性监控
- ✅ 记忆写入新鲜度检测
- ✅ FTS 索引一致性检查
- ✅ 数据库完整性检查
- ✅ 数据库大小监控

### 3. 异常告警 ✅
- ✅ 停滞检测（>1 小时未写入）
- ✅ 严重停滞检测（>2 小时未写入）
- ✅ 数据库损坏检测
- ✅ 索引不一致告警
- ✅ 告警冷却机制（5 分钟）
- ✅ 告警日志记录（JSONL 格式）

### 4. 自动恢复机制 ✅
- ✅ 数据库自动备份
- ✅ VACUUM 修复尝试
- ✅ FTS 索引重建（框架）

---

## 文件结构

```
~/.openclaw/workspace/skills/memory-plus/
├── SKILL.md              # 技能文档（本文件）
├── main.py               # 主入口脚本
├── memory_plus.py        # 核心功能模块
├── monitor.py            # 监控守护进程
├── collector.py          # 多渠道采集器
└── README.md             # 使用说明
```

---

## 使用方法

### 1. 同步渠道消息

```bash
# 同步最近 24 小时的所有渠道消息
cd ~/.openclaw/workspace/skills/memory-plus
python3 main.py sync

# 同步最近 2 小时的飞书和语音消息
python3 main.py sync --channels feishu,voice --hours 2

# 只同步飞书消息
python3 main.py sync --channels feishu --hours 1
```

### 2. 监控记忆系统

```bash
# 单次检查
python3 main.py monitor --once

# 持续监控（守护进程模式）
python3 main.py monitor
```

### 3. 健康检查

```bash
# 执行健康检查
python3 main.py health
```

### 4. 演示模式

```bash
# 运行演示
python3 main.py demo
```

---

## 核心 API

### MemoryPlus 类

```python
from memory_plus import MemoryPlus

# 创建实例
mp = MemoryPlus()

# 连接数据库
mp.connect()

# 插入记忆块
mp.insert_chunk(
    path='memory/feishu/2026-04-07.md',
    text='记忆内容',
    source='memory',
    channel='feishu',
    metadata={'sender': '老板', 'timestamp': '2026-04-07 14:30:00'}
)

# 监控官方系统
result = mp.monitor_official_system()
print(result['status'])  # normal/warning/critical

# 健康检查
is_healthy = mp.health_check()

# 获取统计
stats = mp.get_stats()

# 关闭连接
mp.close()
```

### MultiChannelCollector 类

```python
from collector import MultiChannelCollector

# 创建采集器
mcc = MultiChannelCollector()

# 采集所有渠道
from datetime import datetime, timedelta
end_time = datetime.now()
start_time = end_time - timedelta(hours=2)

messages = mcc.collect_and_merge(
    channels=['feishu', 'voice'],
    start_time=start_time,
    end_time=end_time
)

# 按渠道分组采集
results = mcc.collect_all(
    channels=['feishu', 'wechat'],
    start_time=start_time,
    end_time=end_time
)
```

---

## 数据库表结构

### chunks 表（核心）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 主键，SHA256 哈希 |
| path | TEXT | 记忆文件路径 |
| source | TEXT | 来源（memory/channel） |
| start_line | INTEGER | 起始行号 |
| end_line | INTEGER | 结束行号 |
| hash | TEXT | 内容哈希 |
| model | TEXT | Embedding 模型 |
| text | TEXT | 记忆文本 |
| embedding | TEXT | 向量（JSON 数组） |
| updated_at | INTEGER | 更新时间戳（毫秒） |

### validated_memories 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| content | TEXT | 记忆内容 |
| user_id | TEXT | 用户 ID |
| memory_type | TEXT | 记忆类型 |
| importance | TEXT | 重要程度 |
| tags | TEXT | 标签（JSON 数组） |
| metadata | TEXT | 元数据（JSON 对象） |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

---

## 监控指标

### 正常状态
- ✅ 记忆块数 > 50
- ✅ 文件数 > 20
- ✅ 最新记忆 < 2 小时前
- ✅ FTS 一致性 100%
- ✅ 数据库完整性 ok
- ✅ 数据库大小 < 50MB

### 警戒状态
- ⚠️ 记忆块数 20-50
- ⚠️ 文件数 10-20
- ⚠️ 最新记忆 2-4 小时前
- ⚠️ FTS 一致性 90-99%
- ⚠️ 数据库大小 50-100MB

### 危险状态
- ❌ 记忆块数 < 20
- ❌ 文件数 < 10
- ❌ 最新记忆 > 4 小时前
- ❌ FTS 一致性 < 90%
- ❌ 数据库完整性失败
- ❌ 数据库大小 > 100MB

---

## 告警日志

告警记录在：`~/.openclaw/workspace/logs/memory_plus_alerts.jsonl`

格式：
```json
{
  "timestamp": "2026-04-07T01:30:00",
  "level": "warning",
  "message": "⚠️  记忆系统停滞：65 分钟未写入",
  "uptime_seconds": 3600
}
```

---

## 统计日志

统计记录在：`~/.openclaw/workspace/logs/memory_plus_stats.json`

格式：
```json
{
  "last_check": "2026-04-07T01:30:00",
  "status": "normal",
  "total_chunks": 3000,
  "total_files": 50,
  "db_size_mb": 273.85,
  "uptime_hours": 1.5
}
```

---

## 监控日志

监控日志：`~/.openclaw/workspace/logs/memory_plus_monitor.log`

---

## 集成示例

### 1. 集成到 OpenClaw 主循环

```python
# 在 OpenClaw 主循环中定期调用
from memory_plus import MemoryPlus

mp = MemoryPlus()
if mp.connect():
    result = mp.monitor_official_system()
    if result['status'] == 'critical':
        # 发送告警
        send_alert(result['issues'])
    mp.close()
```

### 2. 集成到飞书消息处理

```python
# 在飞书消息处理后同步
from memory_plus import MemoryPlus

mp = MemoryPlus()
if mp.connect():
    mp.sync_from_channel('feishu', [message])
    mp.close()
```

### 3. 定时任务（Cron）

```bash
# 每小时健康检查
0 * * * * cd ~/.openclaw/workspace/skills/memory-plus && python3 main.py health >> logs/health_cron.log 2>&1

# 每 5 分钟监控
*/5 * * * * cd ~/.openclaw/workspace/skills/memory-plus && python3 main.py monitor --once >> logs/monitor_cron.log 2>&1

# 每天同步所有渠道
0 2 * * * cd ~/.openclaw/workspace/skills/memory-plus && python3 main.py sync --hours 24 >> logs/sync_cron.log 2>&1
```

---

## 测试验证

### 测试 1：数据库连接

```bash
cd ~/.openclaw/workspace/skills/memory-plus
python3 -c "from memory_plus import MemoryPlus; mp = MemoryPlus(); print('✅ 连接成功' if mp.connect() else '❌ 连接失败'); mp.close()"
```

### 测试 2：监控功能

```bash
python3 main.py monitor --once
```

期望输出：
```json
{
  "timestamp": "2026-04-07T01:30:00",
  "status": "normal",
  "total_chunks": 3000,
  "total_files": 50,
  "db_size_mb": 273.85,
  "integrity": "ok"
}
```

### 测试 3：同步功能

```bash
python3 main.py demo
```

期望输出：
```
============================================================
Memory Plus - 跨渠道记忆同步工具演示
============================================================
1️⃣  监控官方记忆系统状态...
   状态：normal
   总记忆块：3000
   总文件数：50
   数据库大小：273.85 MB
...
✅ 同步完成！
```

### 测试 4：健康检查

```bash
python3 main.py health
```

期望输出：
```
🏥 执行健康检查
✅ 记忆系统健康
```

---

## 已知限制

1. **微信集成**：框架已就绪，需要集成 WeChatFerry 或其他微信 API
2. **Telegram 集成**：框架已就绪，需要集成 python-telegram-bot 或 Telethon
3. **Embedding**：当前使用占位向量，实际部署应调用真实 Embedding API
4. **去重逻辑**：基于 hash 去重，可能需要更智能的语义去重

---

## 后续优化

### 短期（1 周内）
- [ ] 集成真实 Embedding API（Qwen/GLM）
- [ ] 完善微信消息采集
- [ ] 完善 Telegram 消息采集
- [ ] 添加语义去重功能

### 中期（1 个月内）
- [ ] 添加记忆检索 API
- [ ] 集成到 OpenClaw 主循环
- [ ] 添加 Web 管理界面
- [ ] 支持更多渠道（Discord、Email 等）

### 长期（3 个月内）
- [ ] 记忆重要性自动评估
- [ ] 记忆关联图谱
- [ ] 跨渠道记忆关联分析
- [ ] 记忆压缩与归档

---

## 教训与改进

### 2026-04-07 经验
**问题**: mem0 删除后无跨渠道同步机制
**根因**: 
- 依赖单一记忆系统
- 无多渠道采集
- 无监控告警

**防范机制**:
1. ✅ 使用官方数据库，不另起炉灶
2. ✅ 实现多渠道采集框架
3. ✅ 实时监控官方系统状态
4. ✅ 异常告警机制
5. ✅ 自动恢复机制

---

## 参考文档

- OpenClaw Memory Core: `/opt/homebrew/lib/node_modules/openclaw/dist/extensions/memory-core/`
- 记忆数据库：`~/.openclaw/memory/main.sqlite`
- 记忆文件：`~/.openclaw/memory/*.md`
- 日志目录：`~/.openclaw/workspace/logs/`

---

*此技能文档将作为 OpenClaw 跨渠道记忆同步的标准操作程序*
*定期审查和更新以适应新的需求*
