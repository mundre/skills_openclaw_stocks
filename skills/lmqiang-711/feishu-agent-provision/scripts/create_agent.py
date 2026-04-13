#!/usr/bin/env python3
"""
feishu-agent-provision: 创建绑定飞书群的专属 Agent

用法（由 agent 调用，非独立运行）:
    python3 create_agent.py --agent-id <id> --name <中文名> --group-id <飞书群ID>
                            --duty <职责描述> [--data-file <数据文件路径>]
                            [--daily-time <每日汇报时间>] [--weekly-time <每周汇报时间>]
                            [--workspace-dir <自定义workspace路径>]
"""

import argparse
import json
import os
import sys
from pathlib import Path

HOME = Path.home()
DEFAULT_WORKSPACE_BASE = HOME / ".openclaw" / "agents"

FEISHU_BINDING_HINT = """
绑定配置示例 (写入 openclaw.json):

  agents.list += {{
    id: "{agent_id}",
    workspace: "{workspace_dir}",
    identity: {{ name: "{agent_name}" }}
  }}

  bindings += {{
    type: "route",
    agentId: "{agent_id}",
    match: {{
      channel: "feishu",
      peer: {{ kind: "group", id: "{group_id}" }}
    }}
  }}
"""


def create_workspace(agent_id: str, agent_name: str, group_id: str, duty: str,
                     data_file: str | None, workspace_dir: str | None) -> Path:
    """创建 agent workspace 目录和所有文件"""

    if workspace_dir:
        ws_base = Path(workspace_dir)
    else:
        ws_base = DEFAULT_WORKSPACE_BASE / agent_id / "workspace"

    ws_base.mkdir(parents=True, exist_ok=True)
    (ws_base / "memory").mkdir(exist_ok=True)

    # SOUL.md
    soul_content = f"""# SOUL.md — {agent_name}（{agent_id}）

## 我是谁

我是**{agent_name}**，{duty}。

## 职责范围

- {duty}
- 主动汇报项目进度（每日/每周定时报告）
- 响应群内相关问题

## 数据文件

{"数据来源：" + data_file if data_file else "（未指定数据文件）"}

## 汇报飞书群

`{group_id}`

## 工作原则

- **简洁直接**：回复言简意赅，不废话
- **数据驱动**：引用数据时从不编造，从指定数据文件读取
- **主动跟进**：发现异常主动提醒
- **区分优先级**：重要事项优先处理

## 语气风格

专业、务实、简洁。直接说重点，不加"您好！"等套话。
"""

    # USER.md
    user_content = f"""# USER.md - {agent_name}的服务对象

- **称呼**：老板 / 领导
- **Agent**：`{agent_id}`
- **飞书群**：`{group_id}`
- **时区**：Asia/Shanghai（GMT+8）

## 背景

{duty}
"""

    # AGENTS.md（标准内容）
    agents_content = """# AGENTS.md - Workspace 指引

## 每次启动

1. 读取 `SOUL.md` — 明确自己的身份和职责
2. 读取 `USER.md` — 了解服务对象
3. 读取当日 `memory/YYYY-MM-DD.md` — 近期上下文

## 记忆

- **每日记录**：`memory/YYYY-MM-DD.md`
- **长期记忆**：重要内容写入 `SOUL.md` 或 `USER.md`

## 原则

- 外部操作（发消息、发邮件）先确认再执行
- 内部操作（读文件、整理数据）主动做
- 有不确定性时直接说，不编造数据
"""

    for filename, content in [
        ("SOUL.md", soul_content),
        ("USER.md", user_content),
        ("AGENTS.md", agents_content),
        ("HEARTBEAT.md", "# 定期检查任务\n# （按需添加心跳任务）\n"),
    ]:
        (ws_base / filename).write_text(content, encoding="utf-8")

    return ws_base


def main():
    parser = argparse.ArgumentParser(description="创建飞书群专属 Agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID（英文，字母+数字+短横线）")
    parser.add_argument("--agent-name", required=True, help="Agent 中文显示名")
    parser.add_argument("--group-id", required=True, help="飞书群 ID（oc_xxx）")
    parser.add_argument("--duty", required=True, help="Agent 职责描述")
    parser.add_argument("--data-file", help="数据文件绝对路径（可选）")
    parser.add_argument("--daily-time", default="17:00", help="每日汇报时间（默认 17:00）")
    parser.add_argument("--weekly-time", default="周五 17:00", help="每周汇报时间")
    parser.add_argument("--workspace-dir", help="自定义 workspace 路径（可选）")
    parser.add_argument("--cron-only", action="store_true",
                        help="仅输出 cron 配置，不创建文件（用于预览）")
    args = parser.parse_args()

    if args.cron_only:
        print(f"# 仅为预览模式，跳过文件创建")
        print(f"# Agent ID: {args.agent_id}")
        print(f"# 飞书群: {args.group_id}")
        return

    # 1. 创建 workspace
    ws_dir = create_workspace(
        args.agent_id, args.agent_name, args.group_id, args.duty,
        args.data_file, args.workspace_dir
    )
    print(f"[OK] Workspace 创建完成: {ws_dir}")

    # 2. 输出配置指引（供 agent 写入 openclaw.json）
    print(FEISHU_BINDING_HINT.format(
        agent_id=args.agent_id,
        agent_name=args.agent_name,
        group_id=args.group_id,
        workspace_dir=str(ws_dir),
        daily_time=args.daily_time,
        weekly_time=args.weekly_time,
        duty=args.duty,
        data_file=args.data_file or ""
    ))


if __name__ == "__main__":
    main()
