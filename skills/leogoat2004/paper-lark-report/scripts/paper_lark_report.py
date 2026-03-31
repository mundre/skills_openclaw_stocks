#!/usr/bin/env python3
"""
paper-lark-report - 科研论文日报/周报生成
支持 --weekly 参数生成周报
"""
import json
import yaml
import ssl
import urllib.request
import re
import os
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import time

# ========== 配置路径 ==========
SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "config.yaml"
PROCESSED_IDS_PATH = SKILL_DIR / "data" / "processed_ids.json"
DOC_REGISTRY_PATH = SKILL_DIR / "data" / "doc_registry.json"
PROCESSED_LOG_DIR = SKILL_DIR / "processed_log"
PAPER_ROOT = Path("/mnt/hgfs/OpenClaw-v/paper")

# ========== 数据类 ==========
@dataclass
class Paper:
    title: str
    authors: List[str]
    venue: str
    year: int
    paper_id: str
    url: str
    abstract: str  # RSS short abstract
    full_abstract: str = ""  # arXiv API full abstract
    posted_date: Optional[str] = None
    relevance_score: int = 0  # LLM 语义相关性评分

# ========== 工具函数 ==========
def load_config() -> dict:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_processed_ids() -> dict:
    if not PROCESSED_IDS_PATH.exists():
        return {"processed": [], "last_updated": ""}
    with open(PROCESSED_IDS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_processed_ids(data: dict):
    PROCESSED_IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_IDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_processed(paper_id: str, processed_data: dict) -> bool:
    return paper_id in processed_data.get("processed", [])

def add_processed(paper_id: str, processed_data: dict):
    processed_data.setdefault("processed", []).append(paper_id)
    processed_data["last_updated"] = datetime.now().isoformat()

def save_daily_log(date: str, papers: List[dict]):
    """保存当日日报日志，供周报聚合"""
    PROCESSED_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = PROCESSED_LOG_DIR / f"{date}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            "date": date,
            "papers": papers,
            "generated_at": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

def load_doc_registry() -> dict:
    """加载文档注册表 {date: {url, title, doc_id}}"""
    if not DOC_REGISTRY_PATH.exists():
        return {}
    with open(DOC_REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_doc_registry(registry: dict):
    """保存文档注册表"""
    with open(DOC_REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

def get_today_doc_info() -> Optional[dict]:
    """获取今天的文档信息（如果已生成），返回 None 表示今天还没生成"""
    today = datetime.now().strftime('%Y-%m-%d')
    registry = load_doc_registry()
    return registry.get(today)

def register_today_doc(doc_url: str, doc_id: str, title: str = ""):
    """注册今天生成的文档"""
    today = datetime.now().strftime('%Y-%m-%d')
    registry = load_doc_registry()
    registry[today] = {
        "url": doc_url,
        "doc_id": doc_id,
        "title": title,
        "registered_at": datetime.now().isoformat()
    }
    save_doc_registry(registry)

# ========== RSS 抓取 ==========
def fetch_rss_feed(url: str, venue_name: str) -> List[Paper]:
    papers = []
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            raw = response.read()
        
        # arXiv RSS 是 RSS 1.0 格式，item 在 channel 下
        root = ET.fromstring(raw)
        channel = root.find('channel')
        entries = channel.findall('item') if channel is not None else root.findall('item')
        
        if not entries:
            # 尝试 Atom 格式
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
        
        for entry in entries[:100]:
            try:
                def get_text(el, tag):
                    found = el.find(tag)
                    return found.text.strip() if found is not None and found.text else ''
                
                title = get_text(entry, 'title') or 'Unknown'
                link = get_text(entry, 'link')
                
                # link 可能没有子标签而是属性
                if not link:
                    link_el = entry.find('link')
                    if link_el is not None:
                        link = link_el.get('href', '')
                
                summary = get_text(entry, 'description') or get_text(entry, 'summary') or ''
                summary = re.sub('<[^<]+?>', '', summary).strip()
                
                # 提取 arXiv ID
                paper_id = ""
                for link_src in [link, get_text(entry, 'guid')]:
                    if not link_src:
                        continue
                    m = re.search(r'arxiv\.org/(?:abs|pdf)/([0-9.]+)', link_src)
                    if m:
                        paper_id = m.group(1)
                        break
                
                if not paper_id:
                    continue
                
                # 提取日期
                posted_date = None
                date_str = get_text(entry, 'date') or get_text(entry, 'pubDate')
                if date_str:
                    try:
                        from email.utils import parsedate_to_datetime
                        posted_date = parsedate_to_datetime(date_str).strftime('%Y-%m-%d')
                    except:
                        posted_date = date_str[:10]
                
                # 提取作者（RSS 1.0 用 dc:creator）
                authors = []
                creator = get_text(entry, '{http://purl.org/dc/elements/1.1/}creator')
                if creator:
                    authors = [creator]
                
                paper = Paper(
                    title=title.strip(),
                    authors=authors,
                    venue=venue_name,
                    year=datetime.now().year,
                    paper_id=paper_id,
                    url=link,
                    abstract=summary[:800],
                    posted_date=posted_date
                )
                papers.append(paper)
            except Exception:
                continue
    except Exception as e:
        print(f"  ❌ {venue_name}: {e}")
    return papers

def fetch_all_rss(venue_rss: List[dict]) -> List[Paper]:
    all_papers = []
    print(f"📡 抓取 {len(venue_rss)} 个 RSS 源...")
    
    for rss in venue_rss:
        papers = fetch_rss_feed(rss['url'], rss['name'])
        print(f"  ✅ {rss['name']}: {len(papers)} 篇")
        all_papers.extend(papers)
        time.sleep(0.5)  # 避免过快
    
    print(f"📚 总计获取 {len(all_papers)} 篇")
    return all_papers

# ========== arXiv API 获取完整摘要 ==========
def fetch_arxiv_details(papers: List[Paper]) -> List[Paper]:
    """通过 arXiv API 获取每篇论文的完整摘要"""
    if not papers:
        return papers
    
    # 批量获取，每批最多 5 个 ID（arXiv API 限制）
    batch_size = 5
    paper_map = {p.paper_id: p for p in papers}
    
    print(f"📡 通过 arXiv API 获取完整摘要（{len(papers)} 篇）...")
    
    ATOM_NS = '{http://www.w3.org/2005/Atom}'
    
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i+batch_size]
        ids = '+'.join([p.paper_id for p in batch])
        
        try:
            url = f"https://export.arxiv.org/api/query?id_list={ids}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as response:
                raw = response.read().decode('utf-8')
            
            root = ET.fromstring(raw)
            
            # arXiv API 返回的 entry 直接在 root 下
            for entry in root:
                if entry.tag != f'{ATOM_NS}entry':
                    continue
                
                # 提取 paper ID
                paper_id_elem = entry.find(f'{ATOM_NS}id')
                if paper_id_elem is None or not paper_id_elem.text:
                    continue
                
                full_id = paper_id_elem.text.strip()
                pid = full_id.split('/')[-1] if '/' in full_id else full_id
                
                if pid in paper_map:
                    # 获取完整摘要
                    summary_elem = entry.find(f'{ATOM_NS}summary')
                    if summary_elem is not None and summary_elem.text:
                        paper_map[pid].full_abstract = summary_elem.text.strip()
                    
                    # 更新作者列表（API 返回完整列表）
                    authors = []
                    for author in entry.findall(f'{ATOM_NS}author'):
                        name_elem = author.find(f'{ATOM_NS}name')
                        if name_elem is not None and name_elem.text:
                            authors.append(name_elem.text)
                    if authors:
                        paper_map[pid].authors = authors
                    
                    # 更新发布日期
                    published_elem = entry.find(f'{ATOM_NS}published')
                    if published_elem is not None and published_elem.text:
                        paper_map[pid].posted_date = published_elem.text[:10]
            
            print(f"  ✅ 批次 {i//batch_size + 1}: 获取 {len(batch)} 篇完整摘要")
            time.sleep(0.5)  # 避免过快
            
        except Exception as e:
            print(f"  ⚠️ 批次 {i//batch_size + 1} 获取失败: {e}")
            continue
    
    # 返回更新后的论文列表
    return list(paper_map.values())

# ========== 日期过滤 + 去重 ==========
def filter_papers(papers: List[Paper], config: dict, processed_data: dict) -> List[Paper]:
    max_days = config.get('arxiv_paper_max_days', 30)
    now = datetime.now()
    
    filtered = []
    for paper in papers:
        if is_processed(paper.paper_id, processed_data):
            continue
        
        if paper.posted_date:
            try:
                paper_date = datetime.strptime(paper.posted_date, '%Y-%m-%d')
                days_ago = (now - paper_date).days
                if days_ago > max_days:
                    continue
            except:
                pass
        
        filtered.append(paper)
    
    print(f"🔍 过滤后剩余 {len(filtered)} 篇")
    return filtered

# ========== 日报模式 ==========
def run_daily():
    print("=" * 60)
    print("📰 paper-lark-report 日报生成")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    config = load_config()
    processed_data = load_processed_ids()
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # 检查配置
    if not config.get('feishu_root'):
        print("❌ 错误: 未配置 feishu_root")
        return
    if not config.get('research_direction'):
        print("❌ 错误: 未配置 research_direction")
        return
    
    # 0. 检查今天是否已生成过文档（去重）
    existing_doc = get_today_doc_info()
    
    # 1. 抓取 RSS
    venue_rss = config.get('venue_rss', [])
    all_papers = fetch_all_rss(venue_rss)
    
    # 2. 过滤（按日期去重）
    filtered = filter_papers(all_papers, config, processed_data)
    
    # 3. 获取完整摘要（先筛选，后精读）
    #    每篇论文通过 arXiv API 获取完整 abstract，避免 LLM 基于残缺信息产生幻觉
    filtered_with_details = fetch_arxiv_details(filtered[:20])  # 最多处理 20 篇候选
    
    # 4. 输出 JSON 供 LLM 使用
    # 如果没有论文，设置 skip 并告知原因
    has_papers = len(filtered) > 0
    no_paper_reason = None
    
    if not has_papers:
        no_paper_reason = "今日 arXiv 无新论文（或周末停更）"
        skip = True
    elif existing_doc is not None:
        skip = True
    else:
        skip = False
    
    output = {
        "date": today_str,
        "research_direction": config['research_direction'],
        "venues": [r['name'] for r in venue_rss],
        "papers": [asdict(p) for p in filtered_with_details],  # 包含 full_abstract
        "max_daily_papers": config.get('max_daily_papers', 5),
        "skip": skip,
        "no_paper_reason": no_paper_reason,
        "existing_doc": existing_doc,
        "config": {
            "feishu_root": config['feishu_root']
        }
    }
    
    # 保存输出
    output_path = SKILL_DIR / "data" / "daily_papers.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    if no_paper_reason:
        print(f"\n⏭️ {no_paper_reason}，跳过生成")
        print(f"   LLM 将收到通知，无需创建文档")
    elif existing_doc:
        print(f"\n⏭️ 今日文档已存在，跳过创建:")
        print(f"   标题: {existing_doc.get('title', 'N/A')}")
        print(f"   链接: {existing_doc.get('url', 'N/A')}")
        print(f"\n📄 信息已保存到: {output_path}")
    else:
        print(f"\n📄 论文列表已保存到: {output_path}")
        print(f"📋 共 {len(filtered)} 篇论文待筛选")
        print("\n✅ 下一步：LLM 读取论文列表，进行相关性评分，生成报告")
    
    return output

# ========== 周报模式 ==========
def run_weekly():
    print("=" * 60)
    print("📊 paper-lark-report 周报生成")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    config = load_config()
    
    # 读取过去7天的日报日志
    today = datetime.now()
    week_papers = []
    dates_included = []
    
    # 计算本周一到周五
    today_weekday = today.weekday()  # 0=周一, 5=周六
    # 如果是周六(5)，往前取周一到周五
    if today_weekday == 5:  # 周六
        for i in range(1, 6):  # 周一到周五
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            log_file = PROCESSED_LOG_DIR / f"{date}.json"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    day_data = json.load(f)
                    week_papers.extend(day_data.get('papers', []))
                    dates_included.append(date)
    else:
        # 其他情况取过去7天
        for i in range(1, 8):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            log_file = PROCESSED_LOG_DIR / f"{date}.json"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    day_data = json.load(f)
                    week_papers.extend(day_data.get('papers', []))
                    dates_included.append(date)
    
    # 没有论文则跳过，不报错
    skip = True
    no_paper_reason = None
    
    if not week_papers:
        no_paper_reason = "本周（周一至周五）无日报数据，跳过周报生成"
        skip = True
        output = {
            "week": f"{today.year}-W{today.isocalendar()[1]:02d}",
            "start_date": "",
            "end_date": "",
            "research_direction": config['research_direction'],
            "total_papers": 0,
            "dates_included": [],
            "papers": [],
            "skip": True,
            "no_paper_reason": no_paper_reason,
            "config": {
                "feishu_root": config['feishu_root']
            }
        }
    else:
        skip = False
        output = {
            "week": f"{today.year}-W{today.isocalendar()[1]:02d}",
            "start_date": dates_included[0] if dates_included else "",
            "end_date": dates_included[-1] if dates_included else "",
            "research_direction": config['research_direction'],
            "total_papers": len(week_papers),
            "dates_included": dates_included,
            "papers": week_papers,
            "skip": False,
            "no_paper_reason": None,
            "config": {
                "feishu_root": config['feishu_root']
            }
        }
    
    # 保存输出
    output_path = SKILL_DIR / "data" / "weekly_papers.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    if no_paper_reason:
        print(f"\n⏭️ {no_paper_reason}")
        print(f"   LLM 将收到通知，无需创建文档")
    else:
        print(f"📅 覆盖日期: {', '.join(dates_included)}")
        print(f"📚 共收集 {len(week_papers)} 篇论文")
        print(f"\n📄 周报数据已保存到: {output_path}")
        print("\n✅ 下一步：LLM 读取周报数据，进行横向比较，生成周报")
    
    return output

# ========== 文档注册（供 LLM 创建文档后调用）==========
def register_daily_doc(doc_id: str, doc_url: str, title: str = ""):
    """记录今日已创建的文档，供去重检查使用"""
    today = datetime.now().strftime('%Y-%m-%d')
    registry = load_doc_registry()
    registry[today] = {
        "doc_id": doc_id,
        "url": doc_url,
        "title": title or f"科研日报 {today}",
        "registered_at": datetime.now().isoformat()
    }
    save_doc_registry(registry)
    print(f"✅ 文档已注册: {today} -> {doc_url}")

# ========== 日报日志保存（供周报聚合用）==========
def save_daily_selected_papers(date: str, papers: List[dict]):
    """保存当日精选论文，供周报聚合使用，同时更新去重列表"""
    save_daily_log(date, papers)
    
    # 更新 processed_ids（防止明日重复推荐）
    processed_data = load_processed_ids()
    for paper in papers:
        add_processed(paper.get('paper_id', ''), processed_data)
    save_processed_ids(processed_data)
    
    print(f"✅ 日报日志已保存: {date} - {len(papers)} 篇论文")

# ========== 主入口 ==========
def main():
    parser = argparse.ArgumentParser(description='paper-lark-report 日报/周报生成')
    parser.add_argument('--weekly', action='store_true', help='生成周报（默认生成日报）')
    parser.add_argument('--register-daily-doc', nargs=3, metavar=('DOC_ID', 'DOC_URL', 'TITLE'),
                        help='注册今日已创建的文档 (DOC_ID DOC_URL TITLE)')
    parser.add_argument('--save-daily', nargs=2, metavar=('DATE', 'PAPERS_JSON'),
                        help='保存当日精选论文到日志 (DATE PAPERS_JSON_FILE)')
    args = parser.parse_args()
    
    if args.save_daily:
        date_str, papers_json_file = args.save_daily
        with open(papers_json_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        save_daily_selected_papers(date_str, papers)
    elif args.register_daily_doc:
        doc_id, doc_url, title = args.register_daily_doc
        register_daily_doc(doc_id, doc_url, title)
    elif args.weekly:
        run_weekly()
    else:
        run_daily()

if __name__ == "__main__":
    main()
