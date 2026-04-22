#!/usr/bin/env python3
"""
Memory Lifecycle - 记忆生命周期管理
使用 Weibull 衰减模型管理记忆重要性
"""

import os
import sys
import json
import time
import math
from typing import Dict, Any, List, Optional
import requests


class WeibullDecay:
    """Weibull 衰减模型"""
    
    # 分类衰减系数（知识类几乎不衰减）
    CATEGORY_DECAY_RATES = {
        '知识': 0.02,      # 世界观/策划案，几乎不衰减
        '人物': 0.1,       # 角色设定，很慢衰减
        '偏好': 0.3,       # 个人偏好，慢衰减
        '事件': 1.0,       # 临时事件，正常衰减
        '地点': 0.2,       # 地点信息，较慢衰减
        '时间': 0.5,       # 时间信息，中等衰减
        '其他': 0.5        # 默认中等衰减
    }
    
    def __init__(self, scale: float = 30.0, shape: float = 1.5, category: str = '其他'):
        """
        初始化 Weibull 衰减
        
        Args:
            scale: 尺度参数（天），越大衰减越慢
            shape: 形状参数
                   - >1: 先快后慢（适合记忆）
                   - =1: 指数衰减
                   - <1: 先慢后快
            category: 记忆分类（影响衰减速率）
        """
        self.scale = scale  # 默认 30 天
        self.shape = shape  # 默认 1.5
        self.category = category
        # 获取分类衰减系数
        self.decay_rate = self.CATEGORY_DECAY_RATES.get(category, 0.5)
    
    def decay(self, initial_importance: float, days_elapsed: float) -> float:
        """
        计算衰减后的重要性（考虑分类衰减系数）
        
        Args:
            initial_importance: 初始重要性 (0-1)
            days_elapsed: 经过的天数
        
        Returns:
            衰减后的重要性 (0-1)
        """
        # 知识类记忆几乎不衰减
        if self.decay_rate < 0.05:
            # 知识类：每年只衰减 2%
            yearly_decay = 0.02
            daily_decay = yearly_decay / 365
            decayed = initial_importance * (1 - daily_decay * days_elapsed)
            return max(decayed, initial_importance * 0.9)  # 最低保留 90%
        
        # 其他类型：Weibull 衰减 × 分类系数
        # Weibull 生存函数：S(t) = exp(-(t/scale)^shape)
        survival = math.exp(-math.pow(days_elapsed / self.scale, self.shape))
        
        # 应用分类衰减系数
        # decay_rate=1.0 正常衰减，0.3 慢衰减，0.02 几乎不衰减
        adjusted_survival = 1.0 - (1.0 - survival) * self.decay_rate
        
        # 衰减后的重要性 = 初始重要性 × 调整后的生存率
        # 最低保留 10% 的重要性（知识类除外）
        decayed = initial_importance * adjusted_survival
        return max(decayed, initial_importance * 0.1)
    
    def half_life(self, initial_importance: float) -> float:
        """
        计算半衰期（重要性降到一半所需时间）
        
        Args:
            initial_importance: 初始重要性
        
        Returns:
            半衰期（天）
        """
        # S(t) = 0.5 时
        # exp(-(t/scale)^shape) = 0.5
        # -(t/scale)^shape = ln(0.5)
        # t = scale * (-ln(0.5))^(1/shape)
        return self.scale * math.pow(-math.log(0.5), 1.0 / self.shape)


class MemoryLifecycle:
    """记忆生命周期管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = config.get('dbPath', '/root/.openclaw/data/memory-custom')
        
        # Weibull 参数（可按记忆类型区分）
        decay_config = config.get('decay', {})
        self.decay_models = {
            '核心': WeibullDecay(
                scale=decay_config.get('scale_core', 90.0),    # 核心记忆 90 天半衰期
                shape=decay_config.get('shape_core', 1.2)
            ),
            '工作': WeibullDecay(
                scale=decay_config.get('scale_working', 30.0),  # 工作记忆 30 天
                shape=decay_config.get('shape_working', 1.5)
            ),
            '普通': WeibullDecay(
                scale=decay_config.get('scale_peripheral', 7.0),  # 普通记忆 7 天
                shape=decay_config.get('shape_peripheral', 2.0)
            )
        }
        
        # 重要性阈值
        self.thresholds = {
            'core': decay_config.get('threshold_core', 0.7),      # ≥0.7 核心记忆
            'working': decay_config.get('threshold_working', 0.4), # 0.4-0.7 工作记忆
            'peripheral': decay_config.get('threshold_peripheral', 0.0)  # <0.4 普通记忆
        }
    
    def get_decay_model(self, category: str, importance: float) -> WeibullDecay:
        """根据分类和重要性选择衰减模型"""
        if importance >= self.thresholds['core']:
            return self.decay_models['核心']
        elif importance >= self.thresholds['working']:
            return self.decay_models['工作']
        else:
            return self.decay_models['普通']
    
    def update_importance(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新记忆的重要性（考虑使用频率增强）
        
        Args:
            memory: 记忆数据（包含 created_at, importance, recall_count）
        
        Returns:
            更新后的记忆数据
        """
        created_at = memory.get('created_at', int(time.time()))
        days_elapsed = (int(time.time()) - created_at) / 86400.0  # 转换为天
        
        initial_importance = memory.get('importance', 0.5)
        category = memory.get('category', '其他')
        recall_count = memory.get('recall_count', 0)  # 被检索次数
        
        # 获取对应的衰减模型
        decay_model = self.get_decay_model(category, initial_importance)
        
        # 计算衰减后的重要性
        decayed_importance = decay_model.decay(initial_importance, days_elapsed)
        
        # 使用频率增强：每次检索 +0.05，上限 1.0
        usage_bonus = min(0.5, recall_count * 0.05)  # 最多 +0.5
        new_importance = min(1.0, decayed_importance + usage_bonus)
        
        # 更新记忆
        memory['importance'] = new_importance
        memory['days_elapsed'] = round(days_elapsed, 2)
        memory['decay_model'] = self._get_model_name(decay_model)
        memory['usage_bonus'] = round(usage_bonus, 3)
        
        return memory
    
    def _get_model_name(self, model: WeibullDecay) -> str:
        """获取衰减模型名称"""
        if model == self.decay_models['核心']:
            return '核心'
        elif model == self.decay_models['工作']:
            return '工作'
        else:
            return '普通'
    
    def cleanup_old_memories(self, min_importance: float = 0.05) -> List[str]:
        """
        清理重要性过低的记忆
        
        Args:
            min_importance: 最低重要性阈值
        
        Returns:
            被清理的记忆 ID 列表
        """
        # 获取所有记忆
        all_memories = self._list_all_memories()
        
        to_delete = []
        for mem in all_memories:
            updated = self.update_importance(mem)
            if updated['importance'] < min_importance:
                to_delete.append(updated['id'])
        
        # 批量删除
        for mem_id in to_delete:
            self._delete_memory(mem_id)
        
        return to_delete
    
    def _list_all_memories(self) -> List[Dict[str, Any]]:
        """获取所有记忆（调用 memory_core）"""
        import subprocess
        result = subprocess.run(
            ['python3', os.path.join(os.path.dirname(__file__), 'memory_core.py'), 'list', '1000'],
            capture_output=True, text=True
        )
        try:
            return json.loads(result.stdout)
        except:
            return []
    
    def _delete_memory(self, memory_id: str):
        """删除记忆（调用 memory_core）"""
        import subprocess
        subprocess.run(
            ['python3', os.path.join(os.path.dirname(__file__), 'memory_core.py'), 'delete', memory_id],
            capture_output=True
        )


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python lifecycle.py <command> [args]")
        print("Commands:")
        print("  update <memory_id>  - 更新指定记忆的重要性")
        print("  update-all          - 更新所有记忆的重要性")
        print("  cleanup             - 清理重要性过低的记忆")
        print("  stats               - 查看生命周期统计")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # 加载配置
    config_file = os.path.expanduser('~/.openclaw/data/memory-custom-config.json')
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    lifecycle = MemoryLifecycle(config)
    
    if command == 'update':
        # 更新单个记忆（需要获取记忆详情，简化处理）
        print("请使用 update-all 更新所有记忆")
    
    elif command == 'update-all':
        print("正在更新所有记忆的重要性...")
        memories = lifecycle._list_all_memories()
        updated = []
        for mem in memories:
            updated_mem = lifecycle.update_importance(mem)
            updated.append(updated_mem)
            print(f"  {mem.get('text', 'N/A')[:30]}...")
            print(f"    重要性：{mem.get('importance', 0):.3f} → {updated_mem['importance']:.3f}")
            print(f"    经过：{updated_mem['days_elapsed']:.1f} 天，衰减模型：{updated_mem['decay_model']}")
        print(f"\n共更新 {len(updated)} 条记忆")
    
    elif command == 'cleanup':
        print("正在清理重要性过低的记忆...")
        deleted = lifecycle.cleanup_old_memories()
        print(f"清理了 {len(deleted)} 条记忆")
        for mem_id in deleted:
            print(f"  - {mem_id}")
    
    elif command == 'stats':
        print("\n=== 记忆生命周期统计 ===\n")
        memories = lifecycle._list_all_memories()
        
        # 分类统计
        categories = {'核心': 0, '工作': 0, '普通': 0}
        for mem in memories:
            updated = lifecycle.update_importance(mem.copy())
            if updated['importance'] >= 0.7:
                categories['核心'] += 1
            elif updated['importance'] >= 0.4:
                categories['工作'] += 1
            else:
                categories['普通'] += 1
        
        print(f"总记忆数：{len(memories)}")
        print(f"  核心记忆：{categories['核心']} 条 (重要性≥0.7)")
        print(f"  工作记忆：{categories['工作']} 条 (0.4≤重要性<0.7)")
        print(f"  普通记忆：{categories['普通']} 条 (重要性<0.4)")
        print(f"\nWeibull 参数:")
        print(f"  核心记忆：scale={lifecycle.decay_models['核心'].scale}天，shape={lifecycle.decay_models['核心'].shape}")
        print(f"  工作记忆：scale={lifecycle.decay_models['工作'].scale}天，shape={lifecycle.decay_models['工作'].shape}")
        print(f"  普通记忆：scale={lifecycle.decay_models['普通'].scale}天，shape={lifecycle.decay_models['普通'].shape}")
        print(f"\n半衰期:")
        print(f"  核心记忆：{lifecycle.decay_models['核心'].half_life(0.8):.1f} 天")
        print(f"  工作记忆：{lifecycle.decay_models['工作'].half_life(0.5):.1f} 天")
        print(f"  普通记忆：{lifecycle.decay_models['普通'].half_life(0.3):.1f} 天")
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
