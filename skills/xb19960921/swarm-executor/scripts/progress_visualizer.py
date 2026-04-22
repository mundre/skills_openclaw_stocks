#!/usr/bin/env python3
"""
进度可视化工具
实时展示并行执行进度，生成进度卡片
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict


class ProgressVisualizer:
    """进度可视化器"""
    
    def __init__(self, progress_file: str = "parallel-progress.json"):
        self.progress_file = Path(progress_file)
    
    def load_progress(self) -> Dict:
        """加载进度"""
        if not self.progress_file.exists():
            return None
        
        with open(self.progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def show_progress(self):
        """展示进度条"""
        progress = self.load_progress()
        if not progress:
            print("未找到进度文件")
            return
        
        total = progress["total_batches"]
        completed = len(progress["completed_batches"])
        failed = len(progress["failed_batches"])
        pending = total - completed - failed
        
        # 计算进度
        percent = (completed / total * 100) if total > 0 else 0
        
        # 进度条
        bar_length = 30
        filled = int(bar_length * completed / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # 预估剩余时间
        if progress["start_time"]:
            start = datetime.fromisoformat(progress["start_time"])
            elapsed = (datetime.now() - start).total_seconds()
            avg_time_per_batch = elapsed / completed if completed > 0 else 0
            remaining_time = avg_time_per_batch * pending
        
        print(f"\n{'='*50}")
        print(f"并行执行进度")
        print(f"{'='*50}")
        print(f"\n  [{bar}] {completed}/{total} ({percent:.1f}%)\n")
        print(f"  完成率：{percent:.1f}%")
        print(f"  成功：{completed}  失败：{failed}  待处理：{pending}")
        
        if progress["start_time"]:
            print(f"  已运行：{int(elapsed // 60)}分{int(elapsed % 60)}秒")
            if pending > 0:
                print(f"  预估剩余：{int(remaining_time // 60)}分{int(remaining_time % 60)}秒")
        
        print(f"\n{'='*50}")
    
    def generate_progress_card(self, output_path: str = "progress-card.html"):
        """生成进度卡片HTML"""
        progress = self.load_progress()
        if not progress:
            return
        
        total = progress["total_batches"]
        completed = len(progress["completed_batches"])
        failed = len(progress["failed_batches"])
        pending = total - completed - failed
        percent = (completed / total * 100) if total > 0 else 0
        
        # 计算耗时
        start = datetime.fromisoformat(progress["start_time"])
        elapsed = (datetime.now() - start).total_seconds()
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>并行执行进度</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        .card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            padding: 40px;
            text-align: center;
            max-width: 400px;
        }}
        .progress-ring {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto 30px;
        }}
        .percent {{
            font-size: 48px;
            font-weight: bold;
            color: white;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }}
        .stat {{
            padding: 15px;
            background: #f8fafc;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #334155;
        }}
        .stat-label {{
            font-size: 12px;
            color: #94a3b8;
            margin-top: 4px;
        }}
        .time {{
            margin-top: 20px;
            color: #64748b;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="progress-ring">
            <div class="percent">{int(percent)}%</div>
        </div>
        <h2>并行执行进度</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{completed}</div>
                <div class="stat-label">成功</div>
            </div>
            <div class="stat">
                <div class="stat-value">{failed}</div>
                <div class="stat-label">失败</div>
            </div>
            <div class="stat">
                <div class="stat-value">{pending}</div>
                <div class="stat-label">待处理</div>
            </div>
        </div>
        <div class="time">
            已运行：{int(elapsed // 60)}分{int(elapsed % 60)}秒
        </div>
    </div>
</body>
</html>'''
        
        Path(output_path).write_text(html, encoding='utf-8')
        print(f"进度卡片已生成：{output_path}")
    
    def clear_progress(self):
        """清理进度文件"""
        if self.progress_file.exists():
            self.progress_file.unlink()
            print("进度文件已清理")


if __name__ == '__main__':
    viz = ProgressVisualizer()
    viz.show_progress()
    viz.generate_progress_card()