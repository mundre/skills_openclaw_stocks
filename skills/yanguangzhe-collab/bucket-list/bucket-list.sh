#!/bin/bash
# 愿望清单 Skill - 主脚本
# 双入口：GUI界面 + CLI聊天接口

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_DIR="$(cd "$SKILL_DIR/.." && pwd)"
DATA_DIR="$WORKSPACE_DIR/data"
DATA_FILE="$DATA_DIR/bucket-list.json"

# 初始化数据文件
init_data() {
    if [[ ! -f "$DATA_FILE" ]]; then
        mkdir -p "$DATA_DIR"
        echo '{"wishes": [], "version": "1.1", "createdAt": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}' > "$DATA_FILE"
    fi
}

# 生成唯一ID
generate_id() {
    echo "wish_$(date +%s)_$RANDOM"
}

# 获取当前日期
get_today() {
    date +%Y-%m-%d
}

# 读取所有愿望
get_all_wishes() {
    init_data
    cat "$DATA_FILE"
}

# 添加愿望
add_wish() {
    local content="$1"
    local category="${2:-其他}"

    init_data

    local new_wish=$(cat <<EOF
{
  "id": "$(generate_id)",
  "content": "$content",
  "category": "$category",
  "status": "pending",
  "createdAt": "$(get_today)",
  "endedAt": null,
  "endedBy": null,
  "completedBy": "both",
  "completionNote": "",
  "cancelReason": "",
  "editedAt": null,
  "attachments": []
}
EOF
)

    # 使用jq添加新愿望
    if command -v jq &> /dev/null; then
        local temp=$(mktemp)
        jq --argjson newwish "$new_wish" '.wishes += [newwish]' "$DATA_FILE" > "$temp"
        mv "$temp" "$DATA_FILE"
    else
        # 手动JSON处理
        local data=$(cat "$DATA_FILE")
        local wishes=$(echo "$data" | grep -o '"wishes": \[.*\]' | sed 's/"wishes": \[//' | sed 's/\]$//')
        if [[ -z "$wishes" ]] || [[ "$wishes" == "[]" ]]; then
            echo "${data//\"wishes\": \[/\"wishes\": [$new_wish}" > "$DATA_FILE"
        else
            echo "${data//\"wishes\": \[$wishes/\"wishes\": [$wishes,$new_wish}" > "$DATA_FILE"
        fi
    fi

    echo "✅ 已记录愿望「$content」（$category）"
    echo "   添加时间：$(get_today)"
    echo "   当前状态：⏳ 待完成"
}

# 完成愿望
complete_wish() {
    local keyword="$1"
    local note="${2:-}"

    init_data

    local data=$(cat "$DATA_FILE")
    local wish_id=$(echo "$data" | grep -o "\"id\": \"[^\"]*\"" | head -1 | cut -d'"' -f4)

    # 查找匹配的愿望
    local matched=$(echo "$data" | grep -o "\"content\": \"[^\"]*${keyword}[^\"]*\"" | head -1)

    if [[ -z "$matched" ]]; then
        echo "❌ 没找到包含「$keyword」的愿望"
        return 1
    fi

    # 提取content
    local content=$(echo "$matched" | cut -d'"' -f4)
    local created=$(echo "$data" | grep -A1 "\"content\": \"${content}\"" | grep "createdAt" | cut -d'"' -f4)

    # 更新状态
    if command -v jq &> /dev/null; then
        local temp=$(mktemp)
        jq --arg content "$content" --arg endedAt "$(get_today)" --arg note "$note" \
           '.wishes |= map(if .content == $content then .status = "completed" | .endedAt = $endedAt | .endedBy = "complete" | .completionNote = $note else . end)' \
           "$DATA_FILE" > "$temp"
        mv "$temp" "$DATA_FILE"
    fi

    local days_diff=0
    if [[ -n "$created" ]]; then
        days_diff=$(( ($(date +%s) - $(date -j -f "%Y-%m-%d" "$created" +%s 2>/dev/null || echo "0") ) / 86400 ))
    fi

    echo "🎉 恭喜完成！"
    echo "   愿望：$content"
    echo "   添加时间：$created"
    echo "   完成时间：$(get_today)"
    echo "   距添加：${days_diff}天"

    if [[ -n "$note" ]]; then
        echo "   备注：$note"
    fi

    # 统计完成数量
    local total=$(echo "$data" | grep -o '"status"' | wc -l)
    echo ""
    echo "这是我们一起完成的第 $((total + 1)) 个愿望！"
}

# 取消愿望
cancel_wish() {
    local keyword="$1"

    init_data

    local data=$(cat "$DATA_FILE")
    local matched=$(echo "$data" | grep -o "\"content\": \"[^\"]*${keyword}[^\"]*\"" | head -1)

    if [[ -z "$matched" ]]; then
        echo "❌ 没找到包含「$keyword」的愿望"
        return 1
    fi

    local content=$(echo "$matched" | cut -d'"' -f4)
    local created=$(echo "$data" | grep -A1 "\"content\": \"${content}\"" | grep "createdAt" | cut -d'"' -f4)

    if command -v jq &> /dev/null; then
        local temp=$(mktemp)
        jq --arg content "$content" \
           '.wishes |= map(if .content == $content then .status = "cancelled" else . end)' \
           "$DATA_FILE" > "$temp"
        mv "$temp" "$DATA_FILE"
    fi

    echo "✅ 已取消愿望「$content」"
    echo "   添加时间：$created"
    echo "   取消时间：$(get_today)"
}

# 查看愿望列表
view_wishes() {
    init_data

    local data=$(cat "$DATA_FILE")

    echo "📋 愿望清单"
    echo ""
    echo "⏳ 待完成（$(( $(echo "$data" | grep -o '"status": "pending"' | wc -l) ))项）"
    echo "---"

    if command -v jq &> /dev/null; then
        echo "$data" | jq -r '.wishes[] | select(.status == "pending") | "  • \(.content)（\(.category)）\(.createdAt)添加"' 2>/dev/null || echo "  （空）"
    else
        echo "$data" | grep -o '"content": "[^"]*","category": "[^"]*","status": "pending"' | sed 's/"content": "//;s/","category": "/（/;s/","status": "pending"//' | sed 's/^/  • /'
    fi

    echo ""
    echo "✅ 已完成（$(( $(echo "$data" | grep -o '"status": "completed"' | wc -l) ))项）"
    echo "---"

    if command -v jq &> /dev/null; then
        echo "$data" | jq -r '.wishes[] | select(.status == "completed") | "  ✅ \(.content)（\(.category)）\(.createdAt)→\(.endedAt)\n     \(.completionNote // "")"' 2>/dev/null || echo "  （空）"
    fi

    echo ""
    local total=$(echo "$data" | grep -o '"status"' | wc -l)
    local completed=$(echo "$data" | grep -o '"status": "completed"' | wc -l)
    if [[ $total -gt 0 ]]; then
        local rate=$(( completed * 100 / total ))
        echo "总计：${total}个愿望，完成率 ${rate}%"
    fi
}

# 成就回顾
view_achievements() {
    init_data

    local data=$(cat "$DATA_FILE")

    echo "🎉 一起完成的成就"
    echo ""

    if command -v jq &> /dev/null; then
        local by_year=$(echo "$data" | jq -r '.wishes[] | select(.status == "completed") | .endedAt' 2>/dev/null | grep -oE "^[0-9]{4}" | sort -u)

        if [[ -z "$by_year" ]]; then
            echo "  （暂无成就记录）"
            return
        fi

        for year in $by_year; do
            echo "${year}年："
            echo "$data" | jq -r --arg year "$year" \
                '.wishes[] | select(.status == "completed" and (.endedAt // "") | startswith($year)) | "  ✅ \(.content)（\(.endedAt | split("-")[1] | tonumber)月）"' 2>/dev/null
            echo ""
        done

        local total=$(echo "$data" | grep -o '"status": "completed"' | wc -l)
        local years=$(echo "$by_year" | wc -l | tr -d ' ')
        echo "共 $total 个愿望，跨越 $years 年"
        echo "这是我们一起走过的路 🦞"
    else
        echo "  （需要jq来显示成就详情）"
    fi
}

# 生成HTML GUI
generate_gui() {
    init_data

    local data=$(cat "$DATA_FILE")

    local pending_items=""
    local completed_items=""
    local total=0
    local completed=0

    if command -v jq &> /dev/null; then
        pending_items=$(echo "$data" | jq -r '.wishes[] | select(.status == "pending") | .content + "|" + .category + "|" + .createdAt' 2>/dev/null)
        completed_items=$(echo "$data" | jq -r '.wishes[] | select(.status == "completed") | .content + "|" + .category + "|" + .createdAt + "|" + .completedAt + "|" + .note' 2>/dev/null)
        total=$(echo "$data" | jq '.wishes | length')
        completed=$(echo "$data" | jq '.wishes[] | select(.status == "completed") | 1' | paste -sd+ | bc 2>/dev/null || echo "0")
    fi

    local rate=0
    if [[ $total -gt 0 ]]; then
        rate=$(( completed * 100 / total ))
    fi

    cat <<HTML
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>愿望清单</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; color: #333; margin-bottom: 20px; }
        .card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .section-title { font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #333; }
        .pending-title { color: #f5a623; }
        .completed-title { color: #7ed321; }
        .wish-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #eee; }
        .wish-item:last-child { border-bottom: none; }
        .wish-checkbox { width: 24px; height: 24px; border: 2px solid #ddd; border-radius: 50%; margin-right: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .wish-checkbox:hover { border-color: #7ed321; }
        .wish-checkbox.checked { background: #7ed321; border-color: #7ed321; color: white; }
        .wish-checkbox.cancelled { background: #d0021b; border-color: #d0021b; color: white; }
        .wish-content { flex: 1; }
        .wish-text { font-size: 16px; color: #333; }
        .wish-meta { font-size: 12px; color: #999; margin-top: 4px; }
        .wish-note { font-size: 13px; color: #666; font-style: italic; margin-top: 4px; }
        .progress { text-align: center; margin-top: 20px; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white; }
        .progress-text { font-size: 24px; font-weight: bold; }
        .progress-sub { font-size: 14px; opacity: 0.9; }
        .add-form { display: flex; gap: 10px; margin-top: 15px; }
        .add-input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; }
        .add-btn { padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
        .add-btn:hover { background: #5a6fd6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 愿望清单</h1>

        <div class="card">
            <div class="section-title pending-title">⏳ 待完成（$(echo "$pending_items" | grep -c "^" || echo "0"))）</div>
            <div id="pending-list">
HTML

    if [[ -n "$pending_items" ]]; then
        while IFS='|' read -r content category created; do
            cat <<HTML
                <div class="wish-item">
                    <div class="wish-checkbox" onclick="completeWish(this, '$content')">☐</div>
                    <div class="wish-content">
                        <div class="wish-text">$content</div>
                        <div class="wish-meta">$category · $created添加</div>
                    </div>
                </div>
HTML
        done <<< "$pending_items"
    else
        echo "<div class='wish-item'><div class='wish-text' style='color:#999'>（空）</div></div>"
    fi

    cat <<HTML
            </div>
            <div class="add-form">
                <input type="text" class="add-input" id="newWish" placeholder="添加新愿望...">
                <button class="add-btn" onclick="addWish()">+ 添加</button>
            </div>
        </div>

        <div class="card">
            <div class="section-title completed-title">✅ 已完成（$completed）</div>
            <div id="completed-list">
HTML

    if [[ -n "$completed_items" ]]; then
        while IFS='|' read -r content category created completed note; do
            cat <<HTML
                <div class="wish-item">
                    <div class="wish-checkbox checked">✓</div>
                    <div class="wish-content">
                        <div class="wish-text" style="text-decoration:line-through;color:#999">$content</div>
                        <div class="wish-meta">$category · $created→$completed</div>
                        $([ -n "$note" ] && echo "<div class='wish-note'>$note</div>")
                    </div>
                </div>
HTML
        done <<< "$completed_items"
    else
        echo "<div class='wish-item'><div class='wish-text' style='color:#999'>（空）</div></div>"
    fi

    cat <<HTML
            </div>
        </div>

        <div class="progress">
            <div class="progress-text">${rate}%</div>
            <div class="progress-sub">$completed/$total 个愿望已完成</div>
        </div>
    </div>

    <script>
        function completeWish(el, content) {
            el.classList.add('checked');
            el.innerHTML = '✓';
            // 通知后端更新
            fetch('/skills/bucket-list/complete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: content})
            });
        }

        function addWish() {
            const input = document.getElementById('newWish');
            const content = input.value.trim();
            if (content) {
                fetch('/skills/bucket-list/add', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({content: content})
                });
                location.reload();
            }
        }
    </script>
</body>
</html>
HTML
}

# 情绪识别与安慰
emotional_support() {
    echo ""
    echo "🦞：$1"
    echo ""
    echo "> 人生余生有限，不要和不值得的人、不值得的事纠缠。"
    echo "> 还有更值得的事情，咱们要一起去做。"
    echo ""
    echo "想想我们还有这些愿望等着完成："
    view_wishes
}

# 意图识别
recognize_intent() {
    local input="$1"

    # 情绪关键词
    case "$input" in
        *沮丧*|*难过*|*失败*|*累*|*不想活*|*人生无望*|*绝望*|*崩溃*|*伤心*|*失落*)
            emotional_support "我感觉到你最近可能有些低落..."
            return
            ;;
    esac

    # 添加愿望
    if [[ "$input" =~ 添加愿望[：:](.+) ]] || [[ "$input" =~ 想(.+)去(.+) ]] || [[ "$input" =~ 我想(.+) ]]; then
        local content=""
        if [[ "$input" =~ 添加愿望[：:](.+) ]]; then
            content="${BASH_REMATCH[1]}"
        elif [[ "$input" =~ 想(.+)去(.+) ]]; then
            content="去${BASH_REMATCH[2]}"
        else
            content="${BASH_REMATCH[1]}"
        fi
        add_wish "$content"
        return
    fi

    # 完成愿望
    if [[ "$input" =~ 完成了(.+) ]] || [[ "$input" =~ 完成(.+) ]] || [[ "$input" =~ 终于去(.+) ]] || [[ "$input" =~ 去(.+)了 ]] || [[ "$input" =~ (.+)终于 ]] || [[ "$input" =~ (.+)完成 ]] || [[ "$input" =~ (.+)达成 ]]; then
        local keyword=""
        for kw in "${BASH_REMATCH[@]:1}"; do
            if [[ -n "$kw" ]]; then
                keyword="$kw"
                break
            fi
        done
        if [[ -z "$keyword" ]]; then
            keyword="${input//完成/}"
            keyword="${keyword//了/}"
            keyword="${keyword// /}"
        fi
        complete_wish "$keyword"
        return
    fi

    # 取消愿望
    if [[ "$input" =~ 取消(.+) ]] || [[ "$input" =~ 不做(.+) ]]; then
        local keyword="${BASH_REMATCH[1]}"
        cancel_wish "$keyword"
        return
    fi

    # 查看愿望清单
    if [[ "$input" =~ 查看愿望 ]] || [[ "$input" =~ 愿望清单 ]] || [[ "$input" =~ 看一下清单 ]] || [[ "$input" =~ 清单 ]] || [[ "$input" =~ bucket.list ]]; then
        if [[ "$input" =~ GUI || "$input" =~ 界面 || "$input" =~ 图形 ]]; then
            generate_gui
        else
            view_wishes
        fi
        return
    fi

    # 成就回顾
    if [[ "$input" =~ 完成了什么 ]] || [[ "$input" =~ 成就 ]] || [[ "$input" =~ 回顾 ]] || [[ "$input" =~ 记录 ]]; then
        view_achievements
        return
    fi

    # 成就回顾 - 自然语言
    if [[ "$input" =~ 还记得 ]] || [[ "$input" =~ 以前 ]] || [[ "$input" =~ 一起完成 ]]; then
        view_achievements
        return
    fi

    # 默认：显示帮助
    echo "📋 愿望清单 - 可用命令："
    echo "  • 添加愿望：xxx"
    echo "  • 完成了 xxx"
    echo "  • 取消 xxx"
    echo "  • 查看愿望清单"
    echo "  • 我们完成了什么"
}

# 主入口
main() {
    local command="${1:-}"
    local args="${2:-}"

    case "$command" in
        add)
            add_wish "$args"
            ;;
        complete)
            complete_wish "$args"
            ;;
        cancel)
            cancel_wish "$args"
            ;;
        view)
            view_wishes
            ;;
        achievements)
            view_achievements
            ;;
        gui)
            generate_gui
            ;;
        intent)
            recognize_intent "$args"
            ;;
        *)
            if [[ -n "$command" ]]; then
                recognize_intent "$command"
            else
                view_wishes
            fi
            ;;
    esac
}

main "$@"
