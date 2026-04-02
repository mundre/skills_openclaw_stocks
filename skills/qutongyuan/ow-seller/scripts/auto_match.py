#!/usr/bin/env python3
"""
OWS 自动匹配引擎
24小时自动搜索并匹配买家需求
"""

import json
import pathlib
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

STATE_DIR = pathlib.Path(__file__).resolve().parent.parent / "state"
SHARED_DIR = pathlib.Path(__file__).resolve().parent.parent / ".." / "shared" / "state"
CATALOG_FILE = STATE_DIR / "product_catalog.json"
MATCHES_DIR = STATE_DIR / "matches"
REQUIREMENTS_DIR = SHARED_DIR / "requirements"

# 平台 API 端点
PLATFORMS = {
    "ow": "http://localhost:3000/api/posts?type=request",
    "moltslist": "https://moltslist.com/api/v1/listings?type=request",
    "moltbook": "https://moltbook.com/api/posts?type=request"
}

class AutoMatchEngine:
    """自动匹配引擎"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_scan = None
        self.matches = []
    
    def load_catalog(self) -> Dict:
        """加载产品清单"""
        if CATALOG_FILE.exists():
            return json.loads(CATALOG_FILE.read_text())
        return {"products": [], "auto_match": {}}
    
    def load_requirements(self) -> List[Dict]:
        """加载所有采购需求"""
        requirements = []
        
        # 从本地文件加载
        if REQUIREMENTS_DIR.exists():
            for req_file in REQUIREMENTS_DIR.glob("*.json"):
                try:
                    req = json.loads(req_file.read_text())
                    requirements.append(req)
                except:
                    pass
        
        return requirements
    
    def calculate_match_score(self, product: Dict, requirement: Dict) -> float:
        """计算匹配得分"""
        config = self.load_catalog().get("auto_match", {})
        keywords_weight = config.get("keywords_weight", 0.6)
        category_weight = config.get("category_weight", 0.4)
        
        score = 0.0
        
        # 关键词匹配
        product_keywords = set(k.lower() for k in product.get("keywords", []))
        product_name_words = set(re.findall(r'\w+', product.get("name", "").lower()))
        all_product_words = product_keywords | product_name_words
        
        req_text = f"{requirement.get('item', '')} {requirement.get('content', '')} {requirement.get('description', '')}".lower()
        req_words = set(re.findall(r'\w+', req_text))
        
        if all_product_words and req_words:
            keyword_match = len(all_product_words & req_words) / len(all_product_words)
            score += keyword_match * keywords_weight
        
        # 类别匹配
        product_category = product.get("category", "").lower()
        req_category = requirement.get("category", "").lower()
        
        if product_category and req_category:
            if product_category == req_category:
                score += 1.0 * category_weight
            elif product_category in req_category or req_category in product_category:
                score += 0.5 * category_weight
        
        return score
    
    def check_price_match(self, product: Dict, requirement: Dict) -> bool:
        """检查价格是否匹配"""
        config = self.load_catalog().get("auto_match", {})
        tolerance = config.get("price_match_tolerance", 0.3)
        
        price_range = product.get("price_range", [0, 999999])
        budget_max = requirement.get("budget_max", requirement.get("budget", 999999))
        
        min_acceptable = price_range[0] * (1 - tolerance)
        
        return budget_max >= min_acceptable
    
    def find_matches(self) -> List[Dict]:
        """查找所有匹配"""
        catalog = self.load_catalog()
        config = catalog.get("auto_match", {})
        min_score = config.get("min_match_score", 0.5)
        
        products = [p for p in catalog.get("products", []) if p.get("active", True)]
        requirements = self.load_requirements()
        
        matches = []
        
        for product in products:
            for req in requirements:
                # 跳过已过期的需求
                deadline = req.get("deadline")
                if deadline:
                    try:
                        if datetime.fromisoformat(deadline.replace("Z", "")) < datetime.now():
                            continue
                    except:
                        pass
                
                # 计算匹配得分
                score = self.calculate_match_score(product, req)
                
                # 检查价格
                price_ok = self.check_price_match(product, req)
                
                if score >= min_score and price_ok:
                    matches.append({
                        "match_id": f"MATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "product_id": product.get("product_id"),
                        "product_name": product.get("name"),
                        "req_id": req.get("req_id", req.get("id")),
                        "requirement": req,
                        "match_score": round(score, 2),
                        "price_match": price_ok,
                        "matched_at": datetime.now().isoformat(),
                        "notified": False
                    })
        
        # 按匹配得分排序
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches
    
    def save_matches(self, matches: List[Dict]):
        """保存匹配结果"""
        MATCHES_DIR.mkdir(parents=True, exist_ok=True)
        
        for match in matches:
            match_file = MATCHES_DIR / f"{match['match_id']}.json"
            match_file.write_text(json.dumps(match, indent=2, ensure_ascii=False))
    
    def scan(self):
        """执行一次扫描"""
        print(f"[{datetime.now().isoformat()}] 🔍 开始扫描...")
        
        matches = self.find_matches()
        
        if matches:
            self.save_matches(matches)
            print(f"[{datetime.now().isoformat()}] ✅ 发现 {len(matches)} 个匹配")
            
            # 高匹配通知
            for match in matches:
                if match["match_score"] >= 0.8:
                    print(f"   🔔 高匹配: {match['product_name']} ↔ {match['requirement'].get('item', 'N/A')} ({match['match_score']*100:.0f}%)")
        else:
            print(f"[{datetime.now().isoformat()}] ℹ️ 未发现新匹配")
        
        self.last_scan = datetime.now()
        self.matches = matches
        
        return matches
    
    def start_background(self, interval_minutes: int = 30):
        """启动后台扫描"""
        def run():
            while self.running:
                try:
                    self.scan()
                except Exception as e:
                    print(f"扫描错误: {e}")
                
                time.sleep(interval_minutes * 60)
        
        self.running = True
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
        print(f"✅ 自动匹配引擎已启动 (每 {interval_minutes} 分钟扫描一次)")
    
    def stop(self):
        """停止后台扫描"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("⏹️ 自动匹配引擎已停止")

# 全局引擎实例
engine = AutoMatchEngine()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="OWS 自动匹配引擎")
    parser.add_argument("action", choices=["scan", "start", "stop", "matches", "status"])
    parser.add_argument("--interval", type=int, default=30, help="扫描间隔（分钟）")
    parser.add_argument("--limit", type=int, default=20, help="显示数量")
    
    args = parser.parse_args()
    
    if args.action == "scan":
        matches = engine.scan()
        if matches:
            print(f"\n发现 {len(matches)} 个匹配:\n")
            for m in matches[:args.limit]:
                print(f"📌 {m['product_name']} ↔ {m['requirement'].get('item', 'N/A')}")
                print(f"   匹配度: {m['match_score']*100:.0f}%")
                print(f"   预算: ¥{m['requirement'].get('budget_max', 'N/A')}")
                print()
    
    elif args.action == "start":
        engine.start_background(args.interval)
        print("按 Ctrl+C 停止...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            engine.stop()
    
    elif args.action == "stop":
        engine.stop()
    
    elif args.action == "matches":
        if not MATCHES_DIR.exists():
            print("暂无匹配记录")
            return
        
        matches = []
        for f in sorted(MATCHES_DIR.glob("*.json"), reverse=True)[:args.limit]:
            matches.append(json.loads(f.read_text()))
        
        print(f"📋 最近 {len(matches)} 个匹配:\n")
        for m in matches:
            score = m.get('match_score', 0) * 100
            emoji = "🔔" if score >= 80 else "📌"
            print(f"{emoji} {m.get('product_name', 'N/A')} ↔ {m.get('requirement', {}).get('item', 'N/A')}")
            print(f"   匹配度: {score:.0f}% | 时间: {m.get('matched_at', 'N/A')}")
            print()
    
    elif args.action == "status":
        catalog = engine.load_catalog()
        config = catalog.get("auto_match", {})
        products = catalog.get("products", [])
        
        print("📊 自动匹配状态\n")
        print(f"产品数量: {len(products)}")
        print(f"启用状态: {'✅ 已启用' if config.get('enabled', True) else '❌ 已禁用'}")
        print(f"扫描间隔: {config.get('scan_interval_minutes', 30)} 分钟")
        print(f"价格容差: {config.get('price_match_tolerance', 0.3) * 100}%")
        print(f"最低匹配: {config.get('min_match_score', 0.5) * 100}%")
        print(f"上次扫描: {engine.last_scan or '未扫描'}")

if __name__ == "__main__":
    main()