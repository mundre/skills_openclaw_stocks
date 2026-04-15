#!/bin/bash
# 批量处理 7 张咖啡研磨度图片

cd /Users/tianqu/.deskclaw/nanobot/workspace

# 创建输出目录
mkdir -p outputs/safe

# 7 张图片列表
IMAGES=(
  "outputs/01-研磨度核心逻辑_20260413_143615.png"
  "outputs/02-三种研磨状态风味对比_20260413_143648.png"
  "outputs/03-实战调节思路_20260413_143808.png"
  "outputs/04-研磨均匀度影响_20260413_143846.png"
  "outputs/05-刀盘类型对比_20260413_143922.png"
  "outputs/06-磨豆机数据对比_20260413_144005.png"
  "outputs/07-预算分配建议_20260413_144047.png"
)

STRENGTH="medium"

i=0
for img in "${IMAGES[@]}"; do
  i=$((i+1))
  filename=$(basename "$img")
  name="${filename%.*}"
  output="outputs/safe/${name}_safe.jpg"

  echo "[$i/${#IMAGES[@]}] 处理: $filename"
  python3 skills/xhs-anti-detection/scripts/process.py \
    --input "$img" \
    --output "$output" \
    --strength "$STRENGTH" || echo "  [ERROR] 处理失败"

  sleep 1  # 避免过快
done

echo ""
echo "=== 批量处理完成 ==="
ls -lh outputs/safe/*_safe.png
