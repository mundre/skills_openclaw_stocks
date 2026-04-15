#!/bin/bash
# xhs-anti-detection: batch.sh
# 批量处理目录中的所有图像

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 默认参数
INPUT_DIR=""
OUTPUT_DIR=""
STRENGTH="medium"
VERIFY=true
DRY_RUN=false

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "用法: $0 --input-dir <目录> [--output-dir <目录>] [--strength light|medium|heavy]"
    echo ""
    echo "选项:"
    echo "  --input-dir DIR     输入目录（必需）"
    echo "  --output-dir DIR    输出目录（默认：输入目录/processed）"
    echo "  --strength LEVEL    处理强度：light/medium/heavy（默认：medium）"
    echo "  --no-verify         跳过验证步骤"
    echo "  --dry-run           显示将要处理的文件但不实际执行"
    echo ""
    echo "示例:"
    echo "  $0 --input-dir ./outputs --output-dir ./safe"
    echo "  $0 --input-dir ./images --strength light --dry-run"
    exit 1
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --input-dir)
            INPUT_DIR="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --strength)
            STRENGTH="$2"
            shift 2
            ;;
        --no-verify)
            VERIFY=false
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}[ERROR] 未知参数: $1${NC}"
            usage
            ;;
    esac
done

if [ -z "$INPUT_DIR" ]; then
    echo -e "${RED}[ERROR] 必须指定 --input-dir${NC}"
    usage
fi

if [ ! -d "$INPUT_DIR" ]; then
    echo -e "${RED}[ERROR] 输入目录不存在: $INPUT_DIR${NC}"
    exit 1
fi

# 设置输出目录
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="${INPUT_DIR}/processed"
fi

mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}=== 小红书反检测批量处理 ===${NC}"
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo "处理强度: $STRENGTH"
echo "验证: $VERIFY"
echo ""

# 查找图像文件
SHAPES="*.png *.jpg *.jpeg *.webp *.gif"
FILES=()
for ext in $SHAPES; do
    while IFS= read -r -d '' file; do
        FILES+=("$file")
    done < <(find "$INPUT_DIR" -maxdepth 1 -name "$ext" -type f -print0 2>/dev/null)
done

if [ ${#FILES[@]} -eq 0 ]; then
    echo -e "${YELLOW}[WARN] 未找到图像文件${NC}"
    exit 0
fi

echo "找到 ${#FILES[@]} 个图像文件"
echo ""

# 处理顺序
# 1. 元数据清理
# 2. 文字保护
# 3. 色彩偏移
# 4. 噪声添加
# 5. 重新编码
# 6. 验证

PROCESSED=0
FAILED=0

for file in "${FILES[@]}"; do
    filename=$(basename "$file")
    name="${filename%.*}"
    ext="${filename##*.}"

    echo -e "${YELLOW}[$((PROCESSED+1))/${#FILES[@]}] 处理: $filename${NC}"

    # 中间文件名（添加点号分隔）
    temp1="$OUTPUT_DIR/${name}.step1.$ext"
    temp2="$OUTPUT_DIR/${name}.step2.$ext"
    temp3="$OUTPUT_DIR/${name}.step3.$ext"
    temp4="$OUTPUT_DIR/${name}.step4.$ext"
    final="$OUTPUT_DIR/${name}.safe.$ext"

    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] 将执行完整处理流程"
        ((PROCESSED++))
        continue
    fi

    # Step 1: 元数据清理
    echo "  [1/5] 元数据清理..."
    python3 "$SCRIPT_DIR/clean_metadata.py" \
        --input "$file" \
        --output "$temp1" \
        --strength "$STRENGTH" || {
        echo -e "  ${RED}[FAILED] 元数据清理失败${NC}"
        ((FAILED++))
        continue
    }

    # Step 2: 文字保护
    echo "  [2/5] 文字区域保护..."
    python3 "$SCRIPT_DIR/protect_text.py" \
        --input "$temp1" \
        --output "$temp2" \
        --strength "$STRENGTH" || {
        echo -e "  ${RED}[FAILED] 文字保护失败${NC}"
        ((FAILED++))
        continue
    }
    rm -f "$temp1"

    # Step 3: 色彩偏移
    echo "  [3/5] 色彩偏移..."
    python3 "$SCRIPT_DIR/color_shift.py" \
        --input "$temp2" \
        --output "$temp3" \
        --strength "$STRENGTH" || {
        echo -e "  ${RED}[FAILED] 色彩偏移失败${NC}"
        ((FAILED++))
        continue
    }
    rm -f "$temp2"

    # Step 4: 添加噪声
    echo "  [4/5] 添加噪声..."
    python3 "$SCRIPT_DIR/add_noise.py" \
        --input "$temp3" \
        --output "$temp4" \
        --strength "$STRENGTH" || {
        echo -e "  ${RED}[FAILED] 添加噪声失败${NC}"
        ((FAILED++))
        continue
    }
    rm -f "$temp3"

    # Step 5: 重新编码
    echo "  [5/5] 重新编码..."
    python3 "$SCRIPT_DIR/recompress.py" \
        --input "$temp4" \
        --output "$final" \
        --strength "$STRENGTH" || {
        echo -e "  ${RED}[FAILED] 重新编码失败${NC}"
        ((FAILED++))
        continue
    }
    rm -f "$temp4"

    # Step 6: 验证（可选）
    if [ "$VERIFY" = true ]; then
        echo "  [✓] 验证中..."
        python3 "$SCRIPT_DIR/verify.py" --input "$final" --no-report 2>/dev/null || true
    fi

    echo -e "  ${GREEN}[SUCCESS] 处理完成: $final${NC}"
    ((PROCESSED++))
done

echo ""
echo -e "${GREEN}=== 批量处理完成 ===${NC}"
echo "成功: $PROCESSED"
echo "失败: $FAILED"
echo "输出目录: $OUTPUT_DIR"

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}[WARN] 有 $FAILED 个文件处理失败，请检查日志${NC}"
    exit 1
fi

exit 0
