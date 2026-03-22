#!/bin/bash
# 迁移旧知识库数据到 kb-mini skill 格式

set -e

OLD_DB="$HOME/Projects/coding-knowledge-base/data/knowledge.db"
NEW_DB="$HOME/.openclaw/agents/coding-research-partner/knowledge.db"

echo "=== 知识库数据迁移 ==="
echo "Old: $OLD_DB"
echo "New: $NEW_DB"

if [[ ! -f "$OLD_DB" ]]; then
    echo "❌ 旧数据库不存在"
    exit 1
fi

# 初始化新数据库
export KNOWLEDGE_DB="$NEW_DB"
mkdir -p "$(dirname "$NEW_DB")"
~/.openclaw/workspace/skills/kb-mini/scripts/storage.sh init

echo ""
echo "=== 统计数据 ==="
total=$(sqlite3 "$OLD_DB" "SELECT COUNT(*) FROM entries WHERE deleted_at IS NULL;")
echo "总记录数: $total"

echo ""
echo "=== 迁移数据 ==="

# 直接用 SQL 迁移
sqlite3 "$NEW_DB" "
    ATTACH DATABASE '$OLD_DB' AS old;

    -- 插入 RSS
    INSERT OR IGNORE INTO entries (id, topic_key, title, content, source, tags, access_level, status, created_at, updated_at, metadata)
    SELECT 
        id,
        topic_key,
        title,
        content,
        source,
        COALESCE(tags, ''),
        COALESCE(access_level, 2),
        'active',
        created_at,
        updated_at,
        COALESCE(metadata, '{}')
    FROM old.entries
    WHERE deleted_at IS NULL AND source='rss';

    -- 插入 HuggingFace
    INSERT OR IGNORE INTO entries (id, topic_key, title, content, source, tags, access_level, status, created_at, updated_at, metadata)
    SELECT 
        id,
        topic_key,
        title,
        content,
        source,
        COALESCE(tags, ''),
        COALESCE(access_level, 2),
        'active',
        created_at,
        updated_at,
        COALESCE(metadata, '{}')
    FROM old.entries
    WHERE deleted_at IS NULL AND source='huggingface';

    -- 插入 GitHub
    INSERT OR IGNORE INTO entries (id, topic_key, title, content, source, tags, access_level, status, created_at, updated_at, metadata)
    SELECT 
        id,
        topic_key,
        title,
        content,
        source,
        COALESCE(tags, ''),
        COALESCE(access_level, 2),
        'active',
        created_at,
        updated_at,
        COALESCE(metadata, '{}')
    FROM old.entries
    WHERE deleted_at IS NULL AND source='github';

    -- 插入 Manual
    INSERT OR IGNORE INTO entries (id, topic_key, title, content, source, tags, access_level, status, created_at, updated_at, metadata)
    SELECT 
        id,
        topic_key,
        title,
        content,
        source,
        COALESCE(tags, ''),
        COALESCE(access_level, 2),
        'active',
        created_at,
        updated_at,
        COALESCE(metadata, '{}')
    FROM old.entries
    WHERE deleted_at IS NULL AND source='manual';

    DETACH DATABASE old;
"

echo "迁移完成"

echo ""
echo "=== 验证 ==="
echo "新数据库统计:"
sqlite3 "$NEW_DB" "SELECT source, COUNT(*) FROM entries GROUP BY source ORDER BY source;"

echo ""
echo "✅ 迁移完成"
