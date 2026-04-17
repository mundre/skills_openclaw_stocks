#!/bin/bash
set -e

SCRAPE_DIR="${SCRAPE_DIR:-$HOME/scrapes}"
mkdir -p "$SCRAPE_DIR"

echo "从STDIN读取ASIN列表..."
ASINS=$(cat)

COUNT=0
for ASIN in $ASINS; do
    ASIN=$(echo "$ASIN" | tr -d '[:space:]')
    [[ -z "$ASIN" ]] && continue

    TS=$(date +%s)
    OUTFILE="${TS}.json"

    echo "[$(date +%H:%M:%S)] 爬取: $ASIN -> $SCRAPE_DIR/$OUTFILE"

    docker run --rm \
        -v "$SCRAPE_DIR:/data" \
        --name="scrape_${ASIN}_${TS}" \
        clawd-crawlee \
        sh -c "node assets/amazon_handler.js 'https://www.amazon.com/dp/$ASIN' > /data/$OUTFILE" 2>&1 || true

    if grep -q '^{' "$SCRAPE_DIR/$OUTFILE" 2>/dev/null; then
        echo "  -> 成功"
    else
        echo "  -> 文件异常或为空"
    fi

    COUNT=$((COUNT + 1))
done

echo ""
echo "完成！共 $COUNT 个文件"
echo "输出目录: $SCRAPE_DIR"