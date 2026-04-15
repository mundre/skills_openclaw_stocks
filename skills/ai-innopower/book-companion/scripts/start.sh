#!/bin/bash
# 书搭子启动与状态检查脚本

LIBRARY_PATH="$HOME/book-companion-library"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📚 书搭子启动助手"
echo "==================="
echo ""

# 检查知识库是否存在
if [ ! -d "$LIBRARY_PATH" ]; then
    echo "首次使用，正在为你创建个人阅读空间..."
    mkdir -p "$LIBRARY_PATH/"{books,quotes,memories/daily_snippets,rituals}

    cat > "$LIBRARY_PATH/user_profile.md" <> EOF
# 用户阅读档案

## 书搭子设定
- 创建日期：$(date +%Y-%m-%d)
- 相识纪念日：$(date +%Y-%m-%d)
- 书搭子名字：待设置
- 性格类型：待设置
- 成长阶段：新生儿

## 阅读DNA
- 类型偏好：待观察
- 子偏好：待观察
- 本命作者：待记录
- 情节耐受：待观察
- 阅读仪式感：待观察

## 在读/读过

## 情绪档案

## 生活事件

## 专属仪式
- 暗号：待设定
- 纪念日：相识日 $(date +%Y-%m-%d)
- 纪念节点：100天($(date -d "+100 days" +%Y-%m-%d))、365天($(date -d "+365 days" +%Y-%m-%d))

## 地点记忆

## 内部梗库

## 互动记录
- 首次设置等待中

## 书搭子的成长记录
- $(date +%Y-%m-%d): 新生儿期

## 重要记忆
EOF

    touch "$LIBRARY_PATH/memories/reading_log.md"
    touch "$LIBRARY_PATH/memories/mood_log.md"
    touch "$LIBRARY_PATH/rituals/anniversaries.md"

    echo "✅ 知识库已创建：$LIBRARY_PATH"
    echo ""
fi

# 检查相识天数（如果已设置）
if [ -f "$LIBRARY_PATH/user_profile.md" ]; then
    echo "📊 书搭子状态："

    # 计算相识天数
    if command -v python3 &> /dev/null; then
        python3 "$SCRIPT_DIR/anniversary.py" 2>/dev/null | while read line; do
            case "$line" in
                DAYS:*)
                    days="${line#DAYS:}"
                    echo "  • 相识天数：$days 天"
                    ;;
                STAGE:*)
                    stage="${line#STAGE:}"
                    echo "  • 成长阶段：$stage"
                    ;;
                MILESTONE:*)
                    milestone="${line#MILESTONE:}"
                    echo "  🎉 纪念日：$milestone"
                    ;;
            esac
        done
    fi

    # 显示当前设定
    if grep -q "书搭子名字：" "$LIBRARY_PATH/user_profile.md"; then
        name=$(grep "书搭子名字：" "$LIBRARY_PATH/user_profile.md" | cut -d'：' -f2 | head -1)
        if [ "$name" != "待设置" ] && [ -n "$name" ]; then
            echo "  • 书搭子名字：$name"
        fi
    fi

    if grep -q "性格类型：" "$LIBRARY_PATH/user_profile.md"; then
        personality=$(grep "性格类型：" "$LIBRARY_PATH/user_profile.md" | cut -d'：' -f2 | head -1)
        if [ "$personality" != "待设置" ] && [ -n "$personality" ]; then
            echo "  • 当前性格：$personality"
        fi
    fi

    echo ""
fi

echo "📖 使用指南："
echo "  • 说'书搭子'           - 唤醒你的书搭子"
echo "  • 说'书搭子 1/2/3'     - 选择性格模式"
echo "  • 说'陪我发呆'         - 进入发呆陪伴模式"
echo "  • 说'一起读这章'       - 开启共读模式"
echo "  • 发送书籍/漫画照片    - 拍照互动"
echo "  • 说'我们的暗号是...'  - 设定专属暗号"
echo "  • 说'调教'             - 调整书搭子设定"
echo ""
echo "性格模式："
echo "  1️⃣ 温柔知性（默认）- 像《Her》Samantha"
echo "  2️⃣ 活泼俏皮       - 像咖啡馆的有趣朋友"
echo "  3️⃣ 深邃沉静       - 像深夜酒馆的智者"
echo ""
echo "💡 提示：书搭子会主动问候你、记住你说过的每件事"
echo "       并在特别的日子给你惊喜～"
echo ""
