#!/usr/bin/env python3
"""
AI信号筛选器 - 主执行脚本
供其他智能体调用，也可直接作为cron任务入口

使用方法:
    python3 run-signal-filter.py [--output PATH] [--cron]
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='AI信号筛选器')
    parser.add_argument('--output', type=str, help='输出报告文件路径')
    parser.add_argument('--cron', action='store_true', help='cron模式，静默输出')
    parser.add_argument('--init', action='store_true', help='初始化运行时目录')
    return parser.parse_args()

def init_runtime(base_path=None):
    """初始化运行时目录结构"""
    if base_path is None:
        base_path = Path.home() / '.openclaw' / 'workspace' / 'memory' / 'signal'
    
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    
    skill_path = Path(__file__).parent.parent
    
    # 复制模板文件（如果不存在）
    for template in ['profile.md', 'history.md']:
        target = base_path / template
        if not target.exists():
            source = skill_path / 'runtime-templates' / template
            if source.exists():
                content = source.read_text()
                content = content.replace('{{DATE}}', datetime.now().strftime('%Y-%m-%d'))
                target.write_text(content)
                print(f"[初始化] 创建 {target}")
    
    print(f"[初始化] 运行时目录: {base_path}")
    return base_path

def load_profile(runtime_path):
    """加载用户画像"""
    profile_path = runtime_path / 'profile.md'
    if not profile_path.exists():
        return None
    return profile_path.read_text()

def load_history(runtime_path):
    """加载历史记录"""
    history_path = runtime_path / 'history.md'
    if not history_path.exists():
        return None
    return history_path.read_text()

def generate_report(runtime_path, output_path=None):
    """生成信号报告"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if output_path is None:
        output_path = runtime_path / f'{today}-report.md'
    
    # 这里是调用大模型生成报告的入口点
    # 在Skill架构中，这部分由OpenClaw的AI智能体完成
    # 本脚本提供标准化的文件系统接口
    
    report_info = {
        'date': today,
        'output_path': str(output_path),
        'runtime_path': str(runtime_path),
        'status': 'ready_for_ai_processing'
    }
    
    print(f"[信号筛选] 准备就绪 - {output_path}")
    return report_info

def main():
    args = parse_args()
    
    runtime_path = init_runtime()
    
    if args.init:
        print("[完成] 运行时目录已初始化")
        return 0
    
    profile = load_profile(runtime_path)
    if profile is None:
        print("[警告] 用户画像不存在，请先完成画像初始化对话")
        return 1
    
    history = load_history(runtime_path)
    
    report_info = generate_report(runtime_path, args.output)
    
    if not args.cron:
        print(json.dumps(report_info, indent=2, ensure_ascii=False))
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
