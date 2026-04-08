#!/usr/bin/env python3
"""后台全量提取PDF全文，写入index.db的full_text字段"""
import fitz, sqlite3, hashlib, os, sys, glob, json, time

DB_PATH = "/data/disk/papers/index.db"
PAPERS_DIR = "/data/disk/papers"
LOG_FILE = "/data/disk/papers/extract_fulltext.log"
FAILED_FILE = "/data/disk/papers/extract_failed.json"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def extract_fulltext(pdf_path, max_pages=0):
    """提取PDF全部页面文本，max_pages=0表示全部"""
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        if max_pages > 0:
            pages = range(min(max_pages, total_pages))
        else:
            pages = range(total_pages)
        
        texts = []
        for i in pages:
            text = doc[i].get_text()
            if text and text.strip():
                texts.append(text.strip())
        
        doc.close()
        full = '\n\n'.join(texts)
        
        # 过滤掉明显是扫描件/纯图片PDF的情况
        if len(full.strip()) < 50:
            return None, f"文本不足50字符(共{total_pages}页)，可能是扫描件"
        
        return full, None
    except Exception as e:
        return None, str(e)

def main():
    conn = get_db()
    
    # 统计
    rows = conn.execute("SELECT id, filepath, title FROM papers WHERE full_text IS NULL").fetchall()
    total = len(rows)
    success = 0
    failed = []
    skipped = 0
    
    log_lines = [f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始全文提取，共 {total} 篇待处理"]
    
    for idx, row in enumerate(rows):
        pid = row['id']
        fpath = row['filepath']
        title = (row['title'] or os.path.basename(fpath))[:60]
        
        if not os.path.exists(fpath):
            failed.append({"id": pid, "file": fpath, "title": title, "error": "文件不存在"})
            skipped += 1
            continue
        
        # 检查是否已提取过（别的同名文件）
        # 跳过已知的小文件/测试文件
        fsize = os.path.getsize(fpath)
        if fsize < 1024:  # <1KB
            failed.append({"id": pid, "file": fpath, "title": title, "error": f"文件过小({fsize}B)"})
            skipped += 1
            continue
        
        text, error = extract_fulltext(fpath)
        
        if text:
            conn.execute("UPDATE papers SET full_text = ? WHERE id = ?", (text, pid))
            success += 1
            if (idx + 1) % 20 == 0:
                conn.commit()
                log_lines.append(f"  进度: {idx+1}/{total}，成功: {success}，失败: {len(failed)}")
                print(f"  进度: {idx+1}/{total}，成功: {success}，失败: {len(failed)}", flush=True)
        else:
            failed.append({"id": pid, "file": fpath, "title": title, "error": error})
    
    conn.commit()
    
    log_lines.append(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 提取完成: 成功 {success}, 失败 {len(failed)}, 跳过 {skipped}")
    
    # 写日志
    with open(LOG_FILE, 'w') as f:
        f.write('\n'.join(log_lines) + '\n')
    
    # 写失败列表
    with open(FAILED_FILE, 'w') as f:
        json.dump(failed, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"成功: {success}")
    print(f"失败/跳过: {len(failed)}")
    print(f"日志: {LOG_FILE}")
    print(f"失败列表: {FAILED_FILE}")

if __name__ == '__main__':
    main()
