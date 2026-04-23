#!/usr/bin/env python3
"""
药品价格监控数据库存储模块
数据库路径：~/.openclaw/skills/pharmacy-price-monitor/price_monitor.db
"""

import sqlite3
import os
from datetime import datetime

DB_DIR = os.path.expanduser("~/.openclaw/skills/pharmacy-price-monitor")
DB_PATH = os.path.join(DB_DIR, "price_monitor.db")


def get_db_path():
    return DB_PATH


def init_db():
    """初始化数据库，创建表结构"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS drugs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        spec TEXT,
        standard_price REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS crawl_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drug_id INTEGER NOT NULL,
        platform TEXT NOT NULL,
        total_items INTEGER,
        min_price REAL,
        max_price REAL,
        avg_price REAL,
        crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (drug_id) REFERENCES drugs(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crawl_record_id INTEGER NOT NULL,
        drug_id INTEGER NOT NULL,
        platform TEXT NOT NULL,
        title TEXT,
        price REAL NOT NULL,
        shop TEXT,
        deals TEXT,
        url TEXT,
        is_low_price BOOLEAN DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (crawl_record_id) REFERENCES crawl_records(id),
        FOREIGN KEY (drug_id) REFERENCES drugs(id))''')

    conn.commit()
    return conn


def parse_price(price_str):
    """解析价格字符串为浮点数"""
    if not price_str:
        return 0.0
    return float(str(price_str).replace('¥', '').replace(',', '').replace(' ', ''))


def save_crawl(drug_name, spec, standard_price, platform, products, conn=None):
    """
    保存一次抓取数据到数据库

    参数:
        drug_name: 药品名称
        spec: 规格
        standard_price: 标准价格
        platform: 平台（京东/淘宝/拼多多）
        products: 商品列表，每项包含 title, price, shop, deals, url
        conn: 可选的数据库连接（用于批量操作）
    """
    should_close = False
    if conn is None:
        conn = init_db()
        should_close = True

    c = conn.cursor()

    # 插入或获取药品ID
    c.execute('''INSERT OR IGNORE INTO drugs (name, spec, standard_price)
                 VALUES (?, ?, ?)''', (drug_name, spec, standard_price))
    c.execute('SELECT id FROM drugs WHERE name = ?', (drug_name,))
    row = c.fetchone()
    drug_id = row[0] if row else None

    if drug_id is None:
        print("错误：无法获取药品ID")
        return None

    # 计算价格统计
    prices = [parse_price(p.get('price', '0')) for p in products if p.get('price')]
    if prices:
        min_p, max_p, avg_p = min(prices), max(prices), sum(prices) / len(prices)
    else:
        min_p, max_p, avg_p = 0, 0, 0

    # 插入抓取记录
    c.execute('''INSERT INTO crawl_records
                 (drug_id, platform, total_items, min_price, max_price, avg_price)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (drug_id, platform, len(products), min_p, max_p, avg_p))
    crawl_record_id = c.lastrowid

    # 插入商品
    for p in products:
        price_val = parse_price(p.get('price', '0'))
        is_low = 1 if (standard_price and price_val < standard_price) else 0
        c.execute('''INSERT INTO products
                     (crawl_record_id, drug_id, platform, title, price, shop, deals, url, is_low_price)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (crawl_record_id, drug_id, platform,
                   p.get('title', ''), price_val, p.get('shop', ''),
                   p.get('deals', ''), p.get('url', ''), is_low))

    conn.commit()
    print(f"[{platform}] 已存储 {len(products)} 条商品数据到数据库 (记录ID: {crawl_record_id})")

    if should_close:
        conn.close()

    return crawl_record_id


def query_history(drug_name, platform=None, limit=10):
    """查询历史抓取记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if platform:
        c.execute('''SELECT cr.id, cr.crawl_time, cr.platform, cr.total_items,
                            cr.min_price, cr.max_price, cr.avg_price
                     FROM crawl_records cr
                     JOIN drugs d ON cr.drug_id = d.id
                     WHERE d.name = ? AND cr.platform = ?
                     ORDER BY cr.crawl_time DESC LIMIT ?''',
                  (drug_name, platform, limit))
    else:
        c.execute('''SELECT cr.id, cr.crawl_time, cr.platform, cr.total_items,
                            cr.min_price, cr.max_price, cr.avg_price
                     FROM crawl_records cr
                     JOIN drugs d ON cr.drug_id = d.id
                     WHERE d.name = ?
                     ORDER BY cr.crawl_time DESC LIMIT ?''',
                  (drug_name, limit))

    results = c.fetchall()
    conn.close()
    return results


def query_low_price_products(drug_name, platform=None, standard_price=None):
    """查询低于标准价的商品"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if platform:
        c.execute('''SELECT p.platform, p.shop, p.price, p.title, p.deals, p.is_low_price
                     FROM products p
                     JOIN drugs d ON p.drug_id = d.id
                     WHERE d.name = ? AND p.platform = ? AND p.is_low_price = 1
                     ORDER BY p.price ASC''',
                  (drug_name, platform))
    else:
        c.execute('''SELECT p.platform, p.shop, p.price, p.title, p.deals, p.is_low_price
                     FROM products p
                     JOIN drugs d ON p.drug_id = d.id
                     WHERE d.name = ? AND p.is_low_price = 1
                     ORDER BY p.price ASC''',
                  (drug_name,))

    results = c.fetchall()
    conn.close()
    return results


def get_latest_crawl_id(drug_name, platform):
    """获取最新一次抓取记录ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT cr.id
                 FROM crawl_records cr
                 JOIN drugs d ON cr.drug_id = d.id
                 WHERE d.name = ? AND cr.platform = ?
                 ORDER BY cr.crawl_time DESC LIMIT 1''',
              (drug_name, platform))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def get_products_by_crawl(crawl_record_id):
    """获取某次抓取记录的所有商品"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT title, price, shop, deals, url, is_low_price
                 FROM products WHERE crawl_record_id = ? ORDER BY price ASC''',
              (crawl_record_id,))
    results = c.fetchall()
    conn.close()
    return results


def print_history_table(drug_name, platform=None):
    """格式化打印历史记录"""
    rows = query_history(drug_name, platform)
    if not rows:
        print(f"暂无 '{drug_name}' 的历史抓取记录")
        return

    print(f"\n{'='*80}")
    print(f"药品: {drug_name}")
    if platform:
        print(f"平台: {platform}")
    print(f"{'='*80}")
    print(f"{'时间':<20} {'平台':<6} {'商品数':<6} {'最低价':<8} {'最高价':<8} {'均价':<8}")
    print("-"*80)

    for row in rows:
        crawl_id, crawl_time, plat, total, min_p, max_p, avg_p = row
        print(f"{crawl_time:<20} {plat:<6} {total:<6} ¥{min_p:<7.2f} ¥{max_p:<7.2f} ¥{avg_p:<7.2f}")


if __name__ == "__main__":
    # 初始化数据库
    init_db()
    print(f"数据库已初始化: {DB_PATH}")
