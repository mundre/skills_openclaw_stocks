#!/bin/bash
# 增量索引：只在新文件存在时才全量扫描
PAPERS_DIR="/data/disk/papers"
DB_PATH="/data/disk/papers/index.db"
LOG="/data/disk/papers/auto_index.log"

cd "$PAPERS_DIR"

# 用inotifywait如果可用，否则直接跑
NEW_COUNT=$(python3 -c "
import sqlite3, hashlib, os, glob
conn = sqlite3.connect('$DB_PATH')
indexed = set(r[0] for r in conn.execute('SELECT file_hash FROM papers').fetchall())
new = 0
for f in glob.glob('$PAPERS_DIR/*.pdf'):
    try:
        h = hashlib.md5(open(f,'rb').read()).hexdigest()
        if h not in indexed:
            new += 1
    except:
        pass
conn.close()
print(new)
")

if [ "$NEW_COUNT" -gt 0 ]; then
    echo "[$(date)] 发现 $NEW_COUNT 个新文件，开始索引..." >> "$LOG"
    python3 "$PAPERS_DIR/paper_manager.py" index >> "$LOG" 2>&1
    python3 "$PAPERS_DIR/paper_manager.py" rename >> "$LOG" 2>&1

    # 补提取新文件全文（跳过已有 full_text 的记录）
    NEW_EXTRACT=$(python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cnt = conn.execute(\"SELECT COUNT(*) FROM papers WHERE full_text IS NULL OR full_text = ''\").fetchone()[0]
conn.close()
print(cnt)
")
    if [ "$NEW_EXTRACT" -gt 0 ]; then
        echo "[$(date)] $NEW_EXTRACT 篇缺少全文，开始提取..." >> "$LOG"
        python3 "$PAPERS_DIR/extract_fulltext.py" >> "$LOG" 2>&1
    fi

    # AI智能提炼（新增）
    echo "[$(date)] 开始AI智能提炼..." >> "$LOG"
    python3 "$PAPERS_DIR/ai_summarize.py" >> "$LOG" 2>&1

    echo "[$(date)] 索引+全文+AI提炼完成" >> "$LOG"
else
    echo "[$(date)] 没有新文件" >> "$LOG"
fi
