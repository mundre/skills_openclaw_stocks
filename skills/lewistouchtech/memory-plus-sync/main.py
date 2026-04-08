#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Plus - 跨渠道记忆同步工具

主入口脚本

作者：伊娃 (Eva)
版本：1.0
创建：2026-04-07
"""

import sys
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from memory_plus import MemoryPlus
from collector import MultiChannelCollector
from monitor import MemoryMonitor


def cmd_sync(args):
    """同步命令"""
    print(f"🔄 开始同步渠道：{args.channels}")
    
    # 创建采集器
    collector = MultiChannelCollector()
    
    # 解析时间范围
    end_time = datetime.now()
    if args.hours:
        start_time = end_time - timedelta(hours=args.hours)
    else:
        start_time = end_time - timedelta(days=1)
    
    print(f"⏰ 时间范围：{start_time} ~ {end_time}")
    
    # 采集消息
    channels = args.channels.split(',') if args.channels else None
    messages = collector.collect_and_merge(
        channels=channels,
        start_time=start_time,
        end_time=end_time
    )
    
    print(f"📥 采集到 {len(messages)} 条消息")
    
    # 同步到数据库
    mp = MemoryPlus()
    if not mp.connect():
        print("❌ 无法连接数据库")
        return 1
    
    try:
        # 按渠道分组同步
        by_channel = {}
        for msg in messages:
            channel = msg.get('channel', 'unknown')
            if channel not in by_channel:
                by_channel[channel] = []
            by_channel[channel].append(msg)
        
        # 逐个渠道同步
        for channel, channel_messages in by_channel.items():
            print(f"\n同步渠道：{channel} ({len(channel_messages)} 条)")
            mp.sync_from_channel(channel, channel_messages)
        
        # 输出统计
        print("\n📊 同步统计:")
        stats = mp.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    finally:
        mp.close()
    
    print("\n✅ 同步完成！")
    return 0


def cmd_monitor(args):
    """监控命令"""
    print("👁️  启动监控模式")
    
    mp = MemoryPlus()
    if not mp.connect():
        print("❌ 无法连接数据库")
        return 1
    
    try:
        if args.once:
            # 单次检查
            result = mp.monitor_official_system()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 持续监控
            monitor = MemoryMonitor()
            monitor.memory_plus = mp
            monitor.start()
    
    finally:
        mp.close()
    
    return 0


def cmd_health(args):
    """健康检查命令"""
    print("🏥 执行健康检查")
    
    mp = MemoryPlus()
    if not mp.connect():
        print("❌ 无法连接数据库")
        return 1
    
    try:
        is_healthy = mp.health_check()
        
        if is_healthy:
            print("✅ 记忆系统健康")
            return 0
        else:
            print("❌ 记忆系统不健康，请检查日志")
            return 1
    
    finally:
        mp.close()


def cmd_demo(args):
    """演示命令"""
    from memory_plus import demo
    demo()


def main():
    parser = argparse.ArgumentParser(
        description='Memory Plus - 跨渠道记忆同步工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s sync --channels feishu,voice --hours 2
  %(prog)s monitor --once
  %(prog)s health
  %(prog)s demo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # sync 命令
    sync_parser = subparsers.add_parser('sync', help='同步渠道消息到记忆库')
    sync_parser.add_argument('--channels', type=str, help='渠道列表，逗号分隔 (feishu,wechat,telegram,voice)')
    sync_parser.add_argument('--hours', type=int, help='同步最近 N 小时的消息')
    sync_parser.set_defaults(func=cmd_sync)
    
    # monitor 命令
    monitor_parser = subparsers.add_parser('monitor', help='监控记忆系统状态')
    monitor_parser.add_argument('--once', action='store_true', help='只执行一次检查')
    monitor_parser.set_defaults(func=cmd_monitor)
    
    # health 命令
    health_parser = subparsers.add_parser('health', help='健康检查')
    health_parser.set_defaults(func=cmd_health)
    
    # demo 命令
    demo_parser = subparsers.add_parser('demo', help='运行演示')
    demo_parser.set_defaults(func=cmd_demo)
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 执行命令
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
