#!/usr/bin/env python3
"""
性能优化工具
Performance Optimization Utilities

功能:
- API 调用缓存
- 速率限制管理
- 批量数据获取
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

# 缓存目录
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)


class APICache:
    """API 响应缓存"""
    
    def __init__(self, ttl_seconds: int = 300):
        """
        初始化缓存
        
        Args:
            ttl_seconds: 缓存过期时间 (秒)，默认 5 分钟
        """
        self.ttl = ttl_seconds
        self.cache_file = os.path.join(CACHE_DIR, 'api_cache.json')
        self._load()
    
    def _load(self):
        """从文件加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except:
                self.cache = {}
        else:
            self.cache = {}
    
    def _save(self):
        """保存缓存到文件"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _generate_key(self, endpoint: str, params: dict) -> str:
        """生成缓存键"""
        key_str = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, endpoint: str, params: dict) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            endpoint: API 端点
            params: 请求参数
            
        Returns:
            缓存的数据，如果过期或不存在则返回 None
        """
        key = self._generate_key(endpoint, params)
        
        if key in self.cache:
            entry = self.cache[key]
            cached_time = datetime.fromisoformat(entry['timestamp'])
            
            # 检查是否过期
            if datetime.now() - cached_time < timedelta(seconds=self.ttl):
                print(f"✅ 缓存命中：{endpoint}")
                return entry['data']
            else:
                # 过期数据，删除
                del self.cache[key]
                self._save()
        
        return None
    
    def set(self, endpoint: str, params: dict, data: Any):
        """
        设置缓存
        
        Args:
            endpoint: API 端点
            params: 请求参数
            data: 要缓存的数据
        """
        key = self._generate_key(endpoint, params)
        
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'params': params
        }
        
        # 限制缓存大小（最多 1000 条）
        if len(self.cache) > 1000:
            # 删除最旧的 100 条
            sorted_cache = sorted(
                self.cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            for key, _ in sorted_cache[:100]:
                del self.cache[key]
        
        self._save()
        print(f"💾 缓存已保存：{endpoint}")
    
    def clear(self):
        """清空缓存"""
        self.cache = {}
        self._save()
        print("🗑️  缓存已清空")
    
    def stats(self) -> dict:
        """获取缓存统计"""
        now = datetime.now()
        valid = 0
        expired = 0
        
        for entry in self.cache.values():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if now - cached_time < timedelta(seconds=self.ttl):
                valid += 1
            else:
                expired += 1
        
        return {
            'total': len(self.cache),
            'valid': valid,
            'expired': expired,
            'size_kb': os.path.getsize(self.cache_file) / 1024 if os.path.exists(self.cache_file) else 0
        }


class RateLimiter:
    """API 速率限制器"""
    
    def __init__(self, calls_per_day: int, calls_per_minute: int = 60):
        """
        初始化速率限制器
        
        Args:
            calls_per_day: 每日调用限制
            calls_per_minute: 每分钟调用限制
        """
        self.daily_limit = calls_per_day
        self.minute_limit = calls_per_minute
        
        self.log_file = os.path.join(CACHE_DIR, 'rate_limit.json')
        self._load()
    
    def _load(self):
        """加载速率限制日志"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.log = json.load(f)
            except:
                self.log = {'calls': []}
        else:
            self.log = {'calls': []}
    
    def _save(self):
        """保存速率限制日志"""
        with open(self.log_file, 'w') as f:
            json.dump(self.log, f, indent=2)
    
    def _cleanup(self):
        """清理过期的调用记录"""
        now = time.time()
        # 保留 24 小时内的记录
        cutoff = now - 86400
        self.log['calls'] = [t for t in self.log['calls'] if t > cutoff]
        self._save()
    
    def can_call(self) -> tuple[bool, str]:
        """
        检查是否可以调用 API
        
        Returns:
            (是否可调用，等待时间或消息)
        """
        self._cleanup()
        now = time.time()
        
        # 检查每分钟限制
        minute_ago = now - 60
        calls_last_minute = sum(1 for t in self.log['calls'] if t > minute_ago)
        
        if calls_last_minute >= self.minute_limit:
            wait_time = 60 - (now - min(self.log['calls'][-self.minute_limit:]))
            return False, f"等待 {wait_time:.0f} 秒 (每分钟限制：{self.minute_limit} 次)"
        
        # 检查每日限制
        calls_today = len(self.log['calls'])
        
        if calls_today >= self.daily_limit:
            return False, f"达到每日限制 ({self.daily_limit} 次)，请明天再试"
        
        return True, "OK"
    
    def record_call(self):
        """记录一次 API 调用"""
        self.log['calls'].append(time.time())
        self._save()
    
    def stats(self) -> dict:
        """获取速率限制统计"""
        now = time.time()
        minute_ago = now - 60
        
        return {
            'calls_today': len(self.log['calls']),
            'calls_last_minute': sum(1 for t in self.log['calls'] if t > minute_ago),
            'daily_limit': self.daily_limit,
            'minute_limit': self.minute_limit,
            'remaining_today': self.daily_limit - len(self.log['calls']),
            'remaining_minute': self.minute_limit - sum(1 for t in self.log['calls'] if t > minute_ago)
        }


class DataBatcher:
    """数据批量获取器"""
    
    def __init__(self, batch_size: int = 100):
        """
        初始化批量获取器
        
        Args:
            batch_size: 每批数据量
        """
        self.batch_size = batch_size
    
    def chunk_list(self, items: list) -> list:
        """
        将列表分块
        
        Args:
            items: 要分块的列表
            
        Returns:
            分块后的列表
        """
        return [items[i:i + self.batch_size] for i in range(0, len(items), self.batch_size)]
    
    def batch_process(self, items: list, process_func, delay_seconds: float = 0.1):
        """
        批量处理数据
        
        Args:
            items: 要处理的数据
            process_func: 处理函数
            delay_seconds: 批次间延迟 (秒)
            
        Yields:
            每批处理结果
        """
        batches = self.chunk_list(items)
        
        for i, batch in enumerate(batches):
            print(f"📦 处理批次 {i+1}/{len(batches)} ({len(batch)} 项)")
            result = process_func(batch)
            yield result
            
            if i < len(batches) - 1 and delay_seconds > 0:
                time.sleep(delay_seconds)


# 全局缓存实例（5 分钟 TTL）
api_cache = APICache(ttl_seconds=300)

# 全局速率限制器实例
# Twelve Data: 800 次/天
twelve_data_limiter = RateLimiter(calls_per_day=800, calls_per_minute=60)

# Alpha Vantage: 25 次/天
alpha_vantage_limiter = RateLimiter(calls_per_day=25, calls_per_minute=5)


def get_cached_price(symbol: str, source: str = 'twelve_data') -> Optional[dict]:
    """
    获取缓存的价格数据
    
    Args:
        symbol: 股票代码
        source: 数据源
        
    Returns:
        价格数据或 None
    """
    # 检查缓存
    cached = api_cache.get('price', {'symbol': symbol, 'source': source})
    if cached:
        return cached
    
    return None


def cache_price(symbol: str, data: dict, source: str = 'twelve_data'):
    """
    缓存价格数据
    
    Args:
        symbol: 股票代码
        data: 价格数据
        source: 数据源
    """
    api_cache.set('price', {'symbol': symbol, 'source': source}, data)


def print_optimization_stats():
    """打印性能优化统计"""
    print("\n" + "=" * 50)
    print("📊 性能优化统计")
    print("=" * 50)
    
    # 缓存统计
    cache_stats = api_cache.stats()
    print(f"\n💾 缓存:")
    print(f"   总条目：{cache_stats['total']}")
    print(f"   有效：{cache_stats['valid']}")
    print(f"   过期：{cache_stats['expired']}")
    print(f"   大小：{cache_stats['size_kb']:.1f} KB")
    
    # Twelve Data 速率限制
    td_stats = twelve_data_limiter.stats()
    print(f"\n📈 Twelve Data API:")
    print(f"   今日调用：{td_stats['calls_today']}/{td_stats['daily_limit']}")
    print(f"   剩余：{td_stats['remaining_today']}")
    print(f"   最近 1 分钟：{td_stats['calls_last_minute']}/{td_stats['minute_limit']}")
    
    # Alpha Vantage 速率限制
    av_stats = alpha_vantage_limiter.stats()
    print(f"\n📉 Alpha Vantage API:")
    print(f"   今日调用：{av_stats['calls_today']}/{av_stats['daily_limit']}")
    print(f"   剩余：{av_stats['remaining_today']}")
    print(f"   最近 1 分钟：{av_stats['calls_last_minute']}/{av_stats['minute_limit']}")
    
    print("\n" + "=" * 50)


if __name__ == '__main__':
    print_optimization_stats()
