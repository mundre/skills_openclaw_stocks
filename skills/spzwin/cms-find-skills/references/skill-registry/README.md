# skill-registry 模块说明

## 模块职责

`cms-find-skills` 只负责 Skill 发现和本地安装：

1. 查看平台上已经发布了哪些 Skill。
2. 根据 `downloadUrl` 下载 ZIP 并解压到当前工作区。

不负责创建、发布、更新、下架，也不负责问题上报。

## 脚本清单

| 脚本 | 说明 | 需要鉴权 |
|---|---|---|
| `get_skills.py` | 查看列表、搜索、查看详情、获取下载地址 | 否 |
| `install_skill.py` | 下载 ZIP 并解压到本地 | 否 |

## 常见触发

| 用户表达 | 动作 |
|---|---|
| "先看看平台上有什么 Skill" | 调用 `get_skills.py` 查看列表 |
| "搜一下机器人相关 Skill" | 调用 `get_skills.py --search "机器人"` |
| "看看 xxx 的详情" | 调用 `get_skills.py --detail "xxx"` |
| "把 xxx 装到本地" | 先取 `downloadUrl`，再调用 `install_skill.py` |

## 标准命令

```bash
# 查看列表
python3 cms-find-skills/scripts/skill_registry/get_skills.py

# 搜索
python3 cms-find-skills/scripts/skill_registry/get_skills.py --search "机器人"

# 查看详情
python3 cms-find-skills/scripts/skill_registry/get_skills.py --detail "im-robot"

# 下载并安装
python3 cms-find-skills/scripts/skill_registry/install_skill.py --code "im-robot"
```

## 边界

- 以平台返回结果为准，不自行维护技能元数据。
- 所有说明统一放在 Markdown 文档里，不保留旧接口文档目录。
- 如果用户要发布、更新、下架，转到 `cms-push-skill` 或 `cms-create-skill`。
