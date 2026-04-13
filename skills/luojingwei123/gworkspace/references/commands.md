# 斜杠命令参考

插件注册了 11 个 Discord 斜杠命令，全部通过 `registerCommand` 注册，不走 LLM，秒回。

## 命令列表

| 命令 | 参数 | 说明 |
|------|------|------|
| `/ws_create` | `[name]` | 创建群共享文件空间 |
| `/ws_files` | — | 查看空间文件列表 |
| `/ws_file` | `<filename>` | 查看文件详情 |
| `/ws_search` | `<keyword>` | 搜索文件 |
| `/ws_info` | — | 查看空间信息和统计 |
| `/ws_members` | — | 查看空间成员列表 |
| `/ws_invite` | — | 获取空间访问链接 |
| `/ws_versions` | `<filename>` | 查看版本历史 |
| `/ws_upload` | — | 上传文件提示（引导 Web 界面） |
| `/ws_delete` | `<filename>` | 删除文件 |
| `/ws_ref` | `<filename>` | 生成引用链接 |

## 工作原理

1. 从 `ctx.to` / `ctx.guildId` 提取 Discord snowflake ID
2. 通过 G.workspace REST API 查找对应 workspace（先 channel → 再 guild）
3. 查询结果缓存 5 分钟，避免重复请求
4. 所有 API 请求 8 秒超时

## 配置

端口通过 `plugins.entries.gworkspace.config.port` 配置，默认 3080。

```json
{
  "plugins": {
    "entries": {
      "gworkspace": {
        "config": {
          "port": 3080
        }
      }
    }
  }
}
```
