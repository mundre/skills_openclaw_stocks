#!/usr/bin/env bash
# Solvea Chat Skill - 一键安装脚本

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
OPENCLAW_DIR="$(cd "$WORKSPACE_DIR/../.." && pwd)"
OPENCLAW_JSON="$OPENCLAW_DIR/openclaw.json"
TEMPLATES_DIR="$SKILL_DIR/templates"

# ── 前置校验：必须在合法的 OpenClaw workspace 里 ──────────────────────────────
if [ ! -f "$OPENCLAW_JSON" ]; then
    echo ""
    echo "✖ 错误：未找到 OpenClaw 配置文件"
    echo ""
    echo "  此 skill 必须安装在 OpenClaw 的 workspace 目录下才能运行。"
    echo "  请先 cd 到一个已有的 workspace，再安装 skill："
    echo ""
    echo "    cd ~/.openclaw/workspaces/main/"
    echo "    npx clawhub@latest install Airoucat233/solvea-chat"
    echo "    bash skills/solvea-chat/setup.sh"
    echo ""
    exit 1
fi

# ── 辅助：渲染模板（替换占位符）────────────────────────────────────────────────
render_template() {
    local src="$1" dst="$2"
    sed \
        -e "s|{{AGENT_NAME}}|$AGENT_NAME|g" \
        -e "s|{{CHANNEL}}|$SELECTED_CHANNEL|g" \
        -e "s|{{BUSINESS_DESC}}|$BUSINESS_DESC|g" \
        "$src" > "$dst"
}

# ── 1. Python 环境 ────────────────────────────────────────────────────────────

echo "→ 创建 Python 虚拟环境..."
python3 -m venv "$SKILL_DIR/.venv"

echo "→ 安装依赖..."
"$SKILL_DIR/.venv/bin/pip" install -q -r "$SKILL_DIR/scripts/requirements.txt"

echo ""

# ── 2. Solvea API 配置 ────────────────────────────────────────────────────────

if [ -f "$SKILL_DIR/.env" ]; then
    echo "✓ .env 已存在，跳过 API 配置"
else
    echo "请填写 Solvea API 配置（直接回车跳过，稍后手动编辑 .env）："
    echo ""
    read -p "  SOLVEA_API_KEY    (X-Token): " api_key
    read -p "  SOLVEA_AGENT_ID (Agent ID, 如 1291): " agent_id

    cat > "$SKILL_DIR/.env" <<EOF
SOLVEA_API_KEY=${api_key}
SOLVEA_AGENT_ID=${agent_id}
EOF

    missing=()
    [ -z "$api_key" ]    && missing+=("SOLVEA_API_KEY")
    [ -z "$agent_id" ] && missing+=("SOLVEA_AGENT_ID")

    if [ ${#missing[@]} -gt 0 ]; then
        echo ""
        echo "⚠ 以下字段未填写，请手动补全："
        for key in "${missing[@]}"; do echo "    $key"; done
        echo "  配置文件：$SKILL_DIR/.env"
    else
        echo "✓ 已写入 .env"
    fi
fi

echo ""

# ── 3. OpenClaw 渠道绑定 ──────────────────────────────────────────────────────


# 读取已启用渠道 & 已有 agent
read -r CHANNELS EXISTING_AGENTS <<< "$("$SKILL_DIR/.venv/bin/python3" - "$OPENCLAW_JSON" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    cfg = json.load(f)
channels = [k for k, v in cfg.get("channels", {}).items() if v.get("enabled", False)]
agents   = [a["id"] for a in cfg.get("agents", {}).get("list", [])]
print(" ".join(channels), "|||", " ".join(agents))
PYEOF
)"

IFS="|||" read -r raw_channels raw_agents <<< "$CHANNELS $EXISTING_AGENTS"
# 重新解析（避免 bash 嵌套复杂）
mapfile -t CHANNEL_LIST < <("$SKILL_DIR/.venv/bin/python3" - "$OPENCLAW_JSON" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    cfg = json.load(f)
for k, v in cfg.get("channels", {}).items():
    if v.get("enabled", False):
        print(k)
PYEOF
)

mapfile -t AGENT_LIST < <("$SKILL_DIR/.venv/bin/python3" - "$OPENCLAW_JSON" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    cfg = json.load(f)
for a in cfg.get("agents", {}).get("list", []):
    print(a["id"])
PYEOF
)

if [ ${#CHANNEL_LIST[@]} -eq 0 ]; then
    echo "⚠ openclaw.json 中没有已启用的渠道，跳过绑定"
    echo "  请先在 OpenClaw 中接入渠道，然后手动添加 binding"
    echo ""
    echo "✓ 安装完成"
    exit 0
fi

# 选择渠道
echo "已启用的渠道："
for i in "${!CHANNEL_LIST[@]}"; do
    echo "  $((i+1))) ${CHANNEL_LIST[$i]}"
done
echo ""
read -p "选择要接入 Solvea 客服的渠道编号（直接回车跳过）: " ch_pick

if [ -z "$ch_pick" ]; then
    echo "跳过渠道绑定，稍后可手动配置"
    echo ""
    echo "✓ 安装完成"
    exit 0
fi

ch_idx=$((ch_pick - 1))
if [ $ch_idx -lt 0 ] || [ $ch_idx -ge ${#CHANNEL_LIST[@]} ]; then
    echo "⚠ 无效编号，跳过绑定"
    echo ""
    echo "✓ 安装完成"
    exit 0
fi
SELECTED_CHANNEL="${CHANNEL_LIST[$ch_idx]}"

# 检查渠道是否已被其他 agent 绑定
EXISTING_BINDING=$("$SKILL_DIR/.venv/bin/python3" - "$OPENCLAW_JSON" "$SELECTED_CHANNEL" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    cfg = json.load(f)
channel = sys.argv[2]
for b in cfg.get("bindings", []):
    if b.get("match", {}).get("channel") == channel:
        print(b.get("agentId", ""))
        break
PYEOF
)

OVERWRITE=true
if [ -n "$EXISTING_BINDING" ]; then
    echo ""
    echo "⚠ 渠道 $SELECTED_CHANNEL 已绑定到 agent: $EXISTING_BINDING"
    read -p "  是否覆盖？原有绑定将被移除 [y/N]: " confirm
    case "$confirm" in
        [yY]|[yY][eE][sS]) OVERWRITE=true ;;
        *)
            echo "已取消，跳过渠道绑定"
            echo ""
            echo "✓ 安装完成"
            exit 0
            ;;
    esac
fi

echo ""

# 选择或新建 agent
echo "选择 Agent："
for i in "${!AGENT_LIST[@]}"; do
    echo "  $((i+1))) ${AGENT_LIST[$i]}"
done
NEW_IDX=$((${#AGENT_LIST[@]} + 1))
echo "  $NEW_IDX) 新建 Agent（推荐）"
echo ""
read -p "请选择编号（默认 $NEW_IDX）: " agent_pick
agent_pick="${agent_pick:-$NEW_IDX}"

CREATE_NEW=false
if [ "$agent_pick" = "$NEW_IDX" ]; then
    CREATE_NEW=true
    echo ""
    read -p "  Agent ID（英文，如 my-cs-bot）: " AGENT_ID
    read -p "  Agent 名称（如 小悦）: " AGENT_NAME
    read -p "  业务描述（如 蔬菜菜摊，用于 USER.md）: " BUSINESS_DESC
    AGENT_ID="${AGENT_ID:-solvea}"
    AGENT_NAME="${AGENT_NAME:-$AGENT_ID}"
    BUSINESS_DESC="${BUSINESS_DESC:-客服}"
else
    agent_idx=$((agent_pick - 1))
    if [ $agent_idx -lt 0 ] || [ $agent_idx -ge ${#AGENT_LIST[@]} ]; then
        echo "⚠ 无效编号，跳过"
        echo ""
        echo "✓ 安装完成"
        exit 0
    fi
    AGENT_ID="${AGENT_LIST[$agent_idx]}"
    AGENT_NAME="$AGENT_ID"
    BUSINESS_DESC=""
fi

# 新建 agent：创建 workspace + 渲染模板
if [ "$CREATE_NEW" = true ]; then
    DEFAULT_WORKSPACE="$OPENCLAW_DIR/workspaces/$AGENT_ID"
    read -p "  Workspace 路径（默认 $DEFAULT_WORKSPACE）: " custom_workspace
    NEW_WORKSPACE="${custom_workspace:-$DEFAULT_WORKSPACE}"
    if [ -d "$NEW_WORKSPACE" ]; then
        echo "⚠ workspace $NEW_WORKSPACE 已存在，跳过初始化"
    else
        echo ""
        echo "→ 初始化 workspace: $NEW_WORKSPACE"
        mkdir -p "$NEW_WORKSPACE/memory" "$NEW_WORKSPACE/skills"

        # 将 skill 安装到新 workspace（从 clawhub 重新下载，避免软链依赖）
        ORIGIN_JSON="$SKILL_DIR/.clawhub/origin.json"
        if [ -f "$ORIGIN_JSON" ]; then
            SKILL_SLUG=$("$SKILL_DIR/.venv/bin/python3" -c \
                "import json; d=json.load(open('$ORIGIN_JSON')); print(d['slug'])")
            SKILL_REGISTRY=$("$SKILL_DIR/.venv/bin/python3" -c \
                "import json; d=json.load(open('$ORIGIN_JSON')); print(d.get('registry','https://clawhub.ai'))")
            echo "→ 从 clawhub 安装 skill 到新 workspace..."
            npx clawhub@latest install "$SKILL_SLUG" \
                --workdir "$NEW_WORKSPACE" \
                --registry "$SKILL_REGISTRY" 2>/dev/null \
            && echo "✓ skill 已安装到 $NEW_WORKSPACE/skills/solvea-chat" \
            || {
                echo "⚠ 网络安装失败，退回复制模式"
                cp -r "$SKILL_DIR" "$NEW_WORKSPACE/skills/solvea-chat"
                # 复制时去掉 .venv（新 workspace 的 setup.sh 运行时会再建）
                rm -rf "$NEW_WORKSPACE/skills/solvea-chat/.venv"
            }
        else
            # 非 clawhub 安装（手动放置），直接复制源文件
            cp -r "$SKILL_DIR" "$NEW_WORKSPACE/skills/solvea-chat"
            rm -rf "$NEW_WORKSPACE/skills/solvea-chat/.venv"
            echo "✓ skill 已复制到 $NEW_WORKSPACE/skills/solvea-chat"
        fi

        render_template "$TEMPLATES_DIR/IDENTITY.md" "$NEW_WORKSPACE/IDENTITY.md"
        render_template "$TEMPLATES_DIR/AGENTS.md"   "$NEW_WORKSPACE/AGENTS.md"
        render_template "$TEMPLATES_DIR/SOUL.md"     "$NEW_WORKSPACE/SOUL.md"
        render_template "$TEMPLATES_DIR/USER.md"     "$NEW_WORKSPACE/USER.md"
        echo "✓ workspace 初始化完成：$NEW_WORKSPACE"
    fi
    AGENT_WORKSPACE="$NEW_WORKSPACE"
else
    AGENT_WORKSPACE="$WORKSPACE_DIR"
fi

# 写入 openclaw.json（agent + binding）
"$SKILL_DIR/.venv/bin/python3" - <<PYEOF
import json

openclaw_json  = "$OPENCLAW_JSON"
agent_id       = "$AGENT_ID"
agent_workspace = "$AGENT_WORKSPACE"
channel        = "$SELECTED_CHANNEL"

with open(openclaw_json) as f:
    cfg = json.load(f)

# agent
existing_ids = [a["id"] for a in cfg.get("agents", {}).get("list", [])]
if agent_id not in existing_ids:
    openclaw_dir = openclaw_json.rsplit("openclaw.json", 1)[0]
    cfg.setdefault("agents", {}).setdefault("list", []).append({
        "id": agent_id,
        "name": agent_id,
        "workspace": agent_workspace,
        "agentDir": f"{openclaw_dir}agents/{agent_id}/agent",
        "model": cfg.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "openai/gpt-5.2")
    })
    print(f"✓ 已添加 agent: {agent_id}")
else:
    print(f"✓ agent {agent_id} 已存在，跳过")

# binding：先移除该渠道的旧绑定，再写入新的
old_bindings = cfg.get("bindings", [])
new_bindings = [b for b in old_bindings if b.get("match", {}).get("channel") != channel]
already_correct = any(
    b.get("agentId") == agent_id and b.get("match", {}).get("channel") == channel
    for b in old_bindings
)
if already_correct:
    print(f"✓ 渠道 {channel} 已绑定到 {agent_id}，无需变更")
else:
    new_bindings.append({"agentId": agent_id, "match": {"channel": channel}})
    cfg["bindings"] = new_bindings
    print(f"✓ 已绑定渠道: {channel} → {agent_id}")

with open(openclaw_json, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write("\n")
PYEOF

echo ""
echo "✓ 安装完成"
echo ""
echo "请重启 OpenClaw 使渠道绑定生效。"
