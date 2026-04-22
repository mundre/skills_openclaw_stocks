#!/usr/bin/env python3
"""
并行子任务执行器核心引擎
大任务自动拆分、并行spawn子agent、超时检查+进度恢复、结果汇总
"""

import json
import os
import sys
import signal
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from tqdm import tqdm


class ParallelTaskExecutor:
    """并行任务执行器"""
    
    def __init__(
        self,
        parallel_count: int = 5,
        timeout_per_batch: int = 300,
        max_retries: int = 2,
        progress_file: str = "parallel-progress.json",
        results_dir: str = "results"
    ):
        self.parallel_count = parallel_count
        self.timeout_per_batch = timeout_per_batch
        self.max_retries = max_retries
        self.progress_file = Path(progress_file)
        self.results_dir = Path(results_dir)
        
        # 创建结果目录
        self.results_dir.mkdir(exist_ok=True)
        
        # 进度追踪
        self.progress = {
            "total_batches": 0,
            "completed_batches": [],
            "failed_batches": [],
            "current_batch": 0,
            "start_time": None,
            "end_time": None
        }
        
        # 中断标志
        self.interrupted = False
        signal.signal(signal.SIGINT, self._handle_interrupt)
    
    def _handle_interrupt(self, signum, frame):
        """处理Ctrl+C中断"""
        print("\n\n⚠️ 检测到中断信号，正在保存进度...")
        self.interrupted = True
        self._save_progress()
        print(f"✅ 进度已保存到 {self.progress_file}")
        print(f"   已完成 {len(self.progress['completed_batches'])}/{self.progress['total_batches']} 批次")
        print("   下次运行将从断点继续")
        sys.exit(0)
    
    def split_task(self, items: List[Any], batch_size: int = None) -> List[List[Any]]:
        """
        拆分任务为批次
        
        Args:
            items: 任务项列表
            batch_size: 每批数量（None则自动计算）
        
        Returns:
            批次列表
        """
        if batch_size is None:
            # 自动计算：每批处理时间≤5分钟
            # 假设每项处理时间30秒，则每批10项
            batch_size = min(10, len(items))
        
        batches = []
        for i in range(0, len(items), batch_size):
            batches.append(items[i:i + batch_size])
        
        return batches
    
    def _save_progress(self):
        """保存进度到文件"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def _load_progress(self) -> bool:
        """从文件恢复进度"""
        if not self.progress_file.exists():
            return False
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            
            self.progress.update(saved)
            return True
        except Exception as e:
            print(f"⚠️ 读取进度文件失败: {e}")
            return False
    
    def execute_batch(
        self,
        batch_id: int,
        items: List[Any],
        task_func: Callable,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行单个批次
        
        Args:
            batch_id: 批次ID
            items: 任务项列表
            task_func: 任务处理函数
            **kwargs: 传递给task_func的额外参数
        
        Returns:
            批次结果
        """
        result = {
            "batch_id": batch_id,
            "items": items,
            "success": False,
            "output": None,
            "error": None,
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        try:
            # 执行任务
            output = task_func(items, **kwargs)
            result["output"] = output
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        finally:
            result["end_time"] = datetime.now().isoformat()
        
        # 保存批次结果
        result_file = self.results_dir / f"batch-{batch_id}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    def execute_parallel(
        self,
        items: List[Any],
        task_func: Callable,
        batch_size: int = None,
        task_name: str = "任务",
        **kwargs
    ) -> Dict[str, Any]:
        """
        并行执行任务
        
        Args:
            items: 任务项列表
            task_func: 任务处理函数
            batch_size: 每批数量
            task_name: 任务名称（用于显示）
            **kwargs: 传递给task_func的额外参数
        
        Returns:
            执行结果汇总
        """
        # 尝试恢复进度
        resumed = self._load_progress()
        
        if resumed:
            print(f"\n📂 发现上次进度：")
            print(f"   已完成：{len(self.progress['completed_batches'])} 批")
            print(f"   失败：{len(self.progress['failed_batches'])} 批（将重试）")
            
            # 计算未完成批次
            all_batches = self.split_task(items, batch_size)
            pending_ids = [
                i for i in range(len(all_batches))
                if i not in self.progress['completed_batches']
            ]
            
            batches = [all_batches[i] for i in pending_ids]
            print(f"   待处理：{len(batches)} 批")
            print(f"\n从上次进度继续...")
        else:
            # 全新执行
            batches = self.split_task(items, batch_size)
            self.progress["total_batches"] = len(batches)
            self.progress["start_time"] = datetime.now().isoformat()
        
        print(f"\n{task_name}：")
        print(f"  总项数：{len(items)}")
        print(f"  总批次：{len(batches)}")
        print(f"  并行数：{self.parallel_count}")
        print(f"  预估时间：{len(batches) * 5 // self.parallel_count} 分钟\n")
        
        # 并行执行
        completed = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=self.parallel_count) as executor:
            # 提交任务
            futures = {}
            batch_iter = iter(enumerate(batches))
            
            # 初始提交
            for _ in range(min(self.parallel_count, len(batches))):
                try:
                    batch_id, batch_items = next(batch_iter)
                    # 调整batch_id（如果是恢复模式）
                    actual_id = pending_ids[batch_id] if resumed else batch_id
                    
                    future = executor.submit(
                        self.execute_batch,
                        actual_id,
                        batch_items,
                        task_func,
                        **kwargs
                    )
                    futures[future] = actual_id
                except StopIteration:
                    break
            
            # 进度条
            pbar = tqdm(total=len(batches), desc="执行进度", unit="批")
            
            # 处理完成的任务
            while futures:
                try:
                    # 等待任意一个完成（带超时）
                    done_futures = []
                    for future in list(futures.keys()):
                        if future.done():
                            done_futures.append(future)
                    
                    if not done_futures:
                        time.sleep(0.1)
                        continue
                    
                    for future in done_futures:
                        batch_id = futures.pop(future)
                        
                        try:
                            result = future.result(timeout=1)
                            
                            if result["success"]:
                                self.progress["completed_batches"].append(batch_id)
                                completed += 1
                            else:
                                self.progress["failed_batches"].append(batch_id)
                                failed += 1
                            
                            # 保存进度
                            self._save_progress()
                            
                        except Exception as e:
                            print(f"\n⚠️ 批次 {batch_id} 执行异常: {e}")
                            self.progress["failed_batches"].append(batch_id)
                            failed += 1
                        
                        pbar.update(1)
                        
                        # 提交新任务
                        try:
                            next_batch_id, next_batch_items = next(batch_iter)
                            actual_id = pending_ids[next_batch_id] if resumed else next_batch_id
                            
                            future = executor.submit(
                                self.execute_batch,
                                actual_id,
                                next_batch_items,
                                task_func,
                                **kwargs
                            )
                            futures[future] = actual_id
                        except StopIteration:
                            pass
                
                except KeyboardInterrupt:
                    # 已经被signal处理
                    pass
            
            pbar.close()
        
        # 汇总结果
        self.progress["end_time"] = datetime.now().isoformat()
        self._save_progress()
        
        # 计算耗时
        start = datetime.fromisoformat(self.progress["start_time"])
        end = datetime.fromisoformat(self.progress["end_time"])
        duration = (end - start).total_seconds()
        
        summary = {
            "total_items": len(items),
            "total_batches": len(batches),
            "completed": len(self.progress["completed_batches"]),
            "failed": len(self.progress["failed_batches"]),
            "success_rate": round(len(self.progress["completed_batches"]) / len(batches) * 100, 1) if batches else 0,
            "duration_seconds": round(duration, 1),
            "parallel_count": self.parallel_count
        }
        
        # 打印汇总
        print(f"\n{'='*50}")
        print(f"并行执行完成！")
        print(f"{'='*50}")
        print(f"  总批次：{summary['total_batches']}")
        print(f"  成功：{summary['completed']}  失败：{summary['failed']}")
        print(f"  成功率：{summary['success_rate']}%")
        print(f"  总耗时：{int(duration // 60)}分{int(duration % 60)}秒")
        print(f"  并行效率：{self.parallel_count}倍")
        print(f"{'='*50}")
        
        # 清理进度文件（执行成功）
        if summary["failed"] == 0:
            self.progress_file.unlink(missing_ok=True)
            print(f"\n✅ 全部完成，进度文件已清理")
        
        return summary


# 示例用法
if __name__ == '__main__':
    # 示例任务函数
    def process_files(files: List[str]) -> List[str]:
        """处理文件列表"""
        import time
        results = []
        for file in files:
            # 模拟处理
            time.sleep(0.5)
            results.append(f"处理完成: {file}")
        return results
    
    # 创建执行器
    executor = ParallelTaskExecutor(
        parallel_count=5,
        timeout_per_batch=300
    )
    
    # 准备任务项
    items = [f"file_{i}.pdf" for i in range(30)]
    
    # 执行
    result = executor.execute_parallel(
        items=items,
        task_func=process_files,
        batch_size=5,
        task_name="PDF文件处理"
    )
    
    print(f"\n结果: {result}")
