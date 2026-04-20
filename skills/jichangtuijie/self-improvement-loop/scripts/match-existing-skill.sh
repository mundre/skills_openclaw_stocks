#!/bin/bash
# match-existing-skill.sh
# v4.0 — 纯机械：匹配技能目录，返回 candidates 列表
# action 判断由 Cron AI 完成，本脚本不输出 action 结论
#
# Usage: ./match-existing-skill.sh "<pattern_name>"
# Output: {"candidates": [...]}

PATTERN="$1"

if [ -z "$PATTERN" ]; then
    printf "%s\n" "{\"candidates\": []}"
    exit 0
fi

SKILLS_DIR="${HOME}/.openclaw/workspace/skills"

# 提取匹配关键词：pattern 的最后一段 + 全部（去点）
KEYWORD=$(echo "$PATTERN" | rev | cut -d. -f1 | rev)
PATTERN_DASHED=$(echo "$PATTERN" | tr '.' '-')

# 收集所有匹配技能（大小写不敏感 substring 匹配目录名）
MATCHES=""
for skill_dir in "$SKILLS_DIR"/*/; do
    [ ! -d "$skill_dir" ] && continue
    [ ! -f "$skill_dir/SKILL.md" ] && continue

    skill_name=$(basename "$skill_dir")

    # 大小写不敏感：匹配目录名
    if echo "$skill_name" | grep -qi "$KEYWORD" || \
       echo "$skill_name" | grep -qi "$PATTERN_DASHED"; then
        # JSON-escape skill_name（处理特殊字符）
        skill_json=$(printf '%s' "$skill_name" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')
        dir_json=$(printf '%s' "$skill_dir" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')
        MATCHES="${MATCHES}{\"skill_name\": ${skill_json}, \"path\": ${dir_json}},"
    fi
done

# 组装 JSON
if [ -n "$MATCHES" ]; then
    # 去掉末尾逗号
    MATCHES=${MATCHES%,}
    printf "%s\n" "{\"candidates\": [${MATCHES}]}"
else
    printf "%s\n" "{\"candidates\": []}"
fi
