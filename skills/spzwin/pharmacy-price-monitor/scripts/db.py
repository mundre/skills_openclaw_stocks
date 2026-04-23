#!/usr/bin/env python3
"""
药品价格监控数据库管理脚本
SQLite 数据库，支持按平台、按时间存储数据
"""

import sqlite3
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pharmacy_monitor.db')


def get_db_path() -> str:
    """获取数据库路径"""
    return os.path.abspath(DB_PATH)


def init_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    """初始化数据库，创建表结构"""
    if db_path is None:
        db_path = get_db_path()

    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建商品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            crawl_date TEXT NOT NULL,
            drug_name TEXT NOT NULL,
            drug_spec TEXT,
            title TEXT NOT NULL,
            shop TEXT,
            price REAL,
            url TEXT,
            is_violation INTEGER DEFAULT 0,
            is_unauthorized INTEGER DEFAULT 0,
            unauthorized_reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(platform, crawl_date, url)
        )
    ''')

    # 创建汇总表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crawl_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            crawl_date TEXT NOT NULL,
            drug_name TEXT NOT NULL,
            drug_spec TEXT,
            total_products INTEGER DEFAULT 0,
            total_violations INTEGER DEFAULT 0,
            total_unauthorized INTEGER DEFAULT 0,
            standard_price REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(platform, crawl_date, drug_name, drug_spec)
        )
    ''')

    # 创建索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_platform_date
        ON products(platform, crawl_date)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_drug_name
        ON products(drug_name)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_crawl_date
        ON products(crawl_date)
    ''')

    conn.commit()
    return conn


def save_products(products: List[Dict], platform: str, drug_name: str,
                  drug_spec: str, standard_price: float,
                  db_path: Optional[str] = None) -> int:
    """
    保存商品数据到数据库

    Args:
        products: 商品列表
        platform: 平台名称
        drug_name: 药品名称
        drug_spec: 药品规格
        standard_price: 标准价格
        db_path: 数据库路径

    Returns:
        保存的商品数量
    """
    conn = init_db(db_path)
    cursor = conn.cursor()

    crawl_date = datetime.now().strftime('%Y-%m-%d')
    saved_count = 0
    violation_count = 0
    unauthorized_count = 0

    for product in products:
        try:
            price = float(product.get('price', 0))
            is_violation = 1 if price < standard_price else 0
            is_unauthorized = product.get('is_unauthorized', 0)
            unauthorized_reason = product.get('unauthorized_reason', '')

            if is_violation:
                violation_count += 1
            if is_unauthorized:
                unauthorized_count += 1

            cursor.execute('''
                INSERT OR REPLACE INTO products
                (platform, crawl_date, drug_name, drug_spec, title, shop,
                 price, url, is_violation, is_unauthorized, unauthorized_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                platform,
                crawl_date,
                drug_name,
                drug_spec or '',
                product.get('title', ''),
                product.get('shop', ''),
                price,
                product.get('url', ''),
                is_violation,
                is_unauthorized,
                unauthorized_reason
            ))
            saved_count += 1
        except Exception as e:
            print(f"保存商品失败: {e}")
            continue

    # 保存汇总
    cursor.execute('''
        INSERT OR REPLACE INTO crawl_summary
        (platform, crawl_date, drug_name, drug_spec, total_products,
         total_violations, total_unauthorized, standard_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        platform,
        crawl_date,
        drug_name,
        drug_spec or '',
        saved_count,
        violation_count,
        unauthorized_count,
        standard_price
    ))

    conn.commit()
    conn.close()

    return saved_count


def get_history(platform: str, drug_name: str,
                days: int = 30,
                db_path: Optional[str] = None) -> List[Dict]:
    """
    获取历史数据

    Args:
        platform: 平台名称
        drug_name: 药品名称
        days: 查询最近天数
        db_path: 数据库路径

    Returns:
        历史数据列表
    """
    conn = init_db(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM crawl_summary
        WHERE platform = ?
          AND drug_name = ?
          AND crawl_date >= date('now', '-' || ? || ' days')
        ORDER BY crawl_date DESC
    ''', (platform, drug_name, days))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_trend(drug_name: str, db_path: Optional[str] = None) -> Dict:
    """
    获取趋势分析数据

    Args:
        drug_name: 药品名称
        db_path: 数据库路径

    Returns:
        趋势分析数据
    """
    conn = init_db(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 获取最近7天的汇总
    cursor.execute('''
        SELECT
            crawl_date,
            platform,
            SUM(total_products) as total_products,
            SUM(total_violations) as total_violations,
            SUM(total_unauthorized) as total_unauthorized
        FROM crawl_summary
        WHERE drug_name = ?
          AND crawl_date >= date('now', '-7 days')
        GROUP BY crawl_date, platform
        ORDER BY crawl_date DESC
    ''', (drug_name,))

    daily_data = [dict(row) for row in cursor.fetchall()]

    # 获取上期数据对比
    cursor.execute('''
        SELECT
            platform,
            SUM(total_products) as total_products,
            SUM(total_violations) as total_violations,
            SUM(total_unauthorized) as total_unauthorized
        FROM crawl_summary
        WHERE drug_name = ?
          AND crawl_date >= date('now', '-14 days')
          AND crawl_date < date('now', '-7 days')
        GROUP BY platform
    ''', (drug_name,))

    prev_week = {row['platform']: dict(row) for row in cursor.fetchall()}

    conn.close()

    return {
        'daily_data': daily_data,
        'prev_week': prev_week
    }


def get_violations(platform: str, drug_name: str,
                   days: int = 7,
                   db_path: Optional[str] = None) -> List[Dict]:
    """
    获取违规商品列表

    Args:
        platform: 平台名称
        drug_name: 药品名称
        days: 查询最近天数
        db_path: 数据库路径

    Returns:
        违规商品列表
    """
    conn = init_db(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM products
        WHERE platform = ?
          AND drug_name = ?
          AND crawl_date >= date('now', '-' || ? || ' days')
          AND is_violation = 1
        ORDER BY price ASC
    ''', (platform, drug_name, days))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_unauthorized(platform: str, drug_name: str,
                      days: int = 7,
                      db_path: Optional[str] = None) -> List[Dict]:
    """
    获取非授权商品列表

    Args:
        platform: 平台名称
        drug_name: 药品名称
        days: 查询最近天数
        db_path: 数据库路径

    Returns:
        非授权商品列表
    """
    conn = init_db(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM products
        WHERE platform = ?
          AND drug_name = ?
          AND crawl_date >= date('now', '-' || ? || ' days')
          AND is_unauthorized = 1
        ORDER BY crawl_date DESC
    ''', (platform, drug_name, days))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def export_to_json(platform: str, drug_name: str,
                   output_path: str,
                   days: int = 7,
                   db_path: Optional[str] = None):
    """
    导出数据到 JSON 文件

    Args:
        platform: 平台名称
        drug_name: 药品名称
        output_path: 输出文件路径
        days: 查询最近天数
        db_path: 数据库路径
    """
    conn = init_db(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 获取商品数据
    cursor.execute('''
        SELECT * FROM products
        WHERE platform = ?
          AND drug_name = ?
          AND crawl_date >= date('now', '-' || ? || ' days')
        ORDER BY crawl_date DESC, price ASC
    ''', (platform, drug_name, days))

    products = [dict(row) for row in cursor.fetchall()]

    # 获取汇总数据
    cursor.execute('''
        SELECT * FROM crawl_summary
        WHERE platform = ?
          AND drug_name = ?
          AND crawl_date >= date('now', '-' || ? || ' days')
        ORDER BY crawl_date DESC
    ''', (platform, drug_name, days))

    summary = [dict(row) for row in cursor.fetchall()]

    conn.close()

    data = {
        'platform': platform,
        'drug_name': drug_name,
        'export_time': datetime.now().isoformat(),
        'products': products,
        'summary': summary
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 导出完成: {output_path}")
    print(f"   商品数量: {len(products)}")
    print(f"   汇总记录: {len(summary)}")


def main():
    parser = argparse.ArgumentParser(description='药品价格监控数据库管理')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # init 命令
    subparsers.add_parser('init', help='初始化数据库')

    # save 命令
    save_parser = subparsers.add_parser('save', help='保存商品数据')
    save_parser.add_argument('--platform', required=True, help='平台名称')
    save_parser.add_argument('--drug-name', required=True, help='药品名称')
    save_parser.add_argument('--spec', help='药品规格')
    save_parser.add_argument('--price', type=float, required=True, help='标准价格')
    save_parser.add_argument('--data', required=True, help='商品数据文件 (JSON)')

    # history 命令
    history_parser = subparsers.add_parser('history', help='查询历史数据')
    history_parser.add_argument('--platform', required=True, help='平台名称')
    history_parser.add_argument('--drug-name', required=True, help='药品名称')
    history_parser.add_argument('--days', type=int, default=30, help='查询天数')

    # trend 命令
    trend_parser = subparsers.add_parser('trend', help='趋势分析')
    trend_parser.add_argument('--drug-name', required=True, help='药品名称')

    # violations 命令
    violations_parser = subparsers.add_parser('violations', help='查询违规商品')
    violations_parser.add_argument('--platform', required=True, help='平台名称')
    violations_parser.add_argument('--drug-name', required=True, help='药品名称')
    violations_parser.add_argument('--days', type=int, default=7, help='查询天数')

    # export 命令
    export_parser = subparsers.add_parser('export', help='导出数据')
    export_parser.add_argument('--platform', required=True, help='平台名称')
    export_parser.add_argument('--drug-name', required=True, help='药品名称')
    export_parser.add_argument('--output', required=True, help='输出文件路径')
    export_parser.add_argument('--days', type=int, default=7, help='查询天数')

    args = parser.parse_args()

    if args.command == 'init':
        conn = init_db()
        conn.close()
        print(f"✅ 数据库初始化完成: {get_db_path()}")

    elif args.command == 'save':
        with open(args.data, 'r', encoding='utf-8') as f:
            products = json.load(f)
        count = save_products(products, args.platform, args.drug_name,
                            args.spec, args.price)
        print(f"✅ 保存完成: {count} 件商品")

    elif args.command == 'history':
        results = get_history(args.platform, args.drug_name, args.days)
        print(f"历史数据 ({args.days} 天):")
        for row in results:
            print(f"  {row['crawl_date']}: {row['total_products']} 件商品, "
                  f"{row['total_violations']} 违规, {row['total_unauthorized']} 非授权")

    elif args.command == 'trend':
        results = get_trend(args.drug_name)
        print(f"趋势分析 (最近7天):")
        for day in results['daily_data']:
            print(f"  {day['crawl_date']} [{day['platform']}]: "
                  f"{day['total_products']} 件, {day['total_violations']} 违规")

    elif args.command == 'violations':
        results = get_violations(args.platform, args.drug_name, args.days)
        print(f"违规商品 ({args.days} 天):")
        for row in results:
            print(f"  [{row['shop']}] {row['title']}: ¥{row['price']}")

    elif args.command == 'export':
        export_to_json(args.platform, args.drug_name, args.output, args.days)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
