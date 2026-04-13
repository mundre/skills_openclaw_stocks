#!/usr/bin/env python3
"""
DMP人群洞察分析脚本 v7.0 - 标准特征识别版

集成了特征识别标准规范 v7.0，确保每次分析都按照完整的算法流程进行：
- 三步法特征筛选（TGI ≥ 1.0 → 占比排序 → 取前40%）
- 并列核心特征识别
- 互斥关系处理
- 无区分度特征排除

作者：OpenClaw AI Assistant
版本：7.0
日期：2026-03-30
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# 导入特征识别标准模块
sys.path.insert(0, os.path.dirname(__file__))
from feature_extraction import FeatureExtractor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PersonaInsightAnalyzerV7:
    """v7.0 规范化人群洞察分析器（集成 v7.0 特征识别算法）"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        初始化分析器
        
        Args:
            output_dir: 输出报告目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化特征提取器（v7.0 标准）
        self.feature_extractor = FeatureExtractor()
        
        logger.info(f"初始化 PersonaInsightAnalyzerV7（特征识别 v7.0）")
        logger.info(f"输出目录：{self.output_dir}")
    
    def load_data(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        加载 Excel 或 CSV 数据
        
        Args:
            file_path: 数据文件路径
            
        Returns:
            sheet 名称 → DataFrame 的字典
        """
        file_path = str(file_path)
        logger.info(f"开始加载数据：{file_path}")
        
        if file_path.endswith(('.xlsx', '.xls')):
            excel_file = pd.ExcelFile(file_path)
            sheets = {}
            for sheet_name in excel_file.sheet_names:
                sheets[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"Excel 加载完成，共 {len(sheets)} 个 sheet")
            return sheets
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            logger.info(f"CSV 加载完成，共 {len(df)} 行")
            return {'data': df}
        else:
            raise ValueError("仅支持 .xlsx、.xls 和 .csv 格式")
    
    def analyze_dimension_with_v7(self, dimension_name: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        使用 v7.0 算法分析单个维度
        
        完整流程：
        1. 自动列名识别
        2. 三步法特征筛选（特征提取器）
        3. 并列特征识别（特征提取器）
        4. 互斥关系处理（特征提取器）
        5. 无区分度排除（特征提取器）
        
        Args:
            dimension_name: 维度名称
            df: 维度数据 DataFrame
            
        Returns:
            分析结果字典
        """
        logger.info(f"\n=== 开始分析维度：{dimension_name} ===")
        
        result = {
            'dimension': dimension_name,
            'total_items': len(df),
            'columns': list(df.columns),
            'features': [],
            'core_count': 0,
            'avg_tgi': 0,
            'max_tgi': 0,
        }
        
        # 步骤 1：自动列名识别
        tgi_col = self._find_column(df, ['tgi', 'TGI', 'index', '指数'])
        label_col = self._find_column(df, ['二级标签', '标签', '特征', '名称', '一级标签', 'name', 'label'])
        coverage_col = self._find_column(df, ['占比', 'coverage', '比例', 'percentage', '百分比'])
        
        result['tgi_column'] = tgi_col
        result['label_column'] = label_col
        result['coverage_column'] = coverage_col
        
        # 检查 TGI 列
        if not tgi_col or tgi_col not in df.columns:
            logger.warning(f"维度 {dimension_name}：未找到 TGI 列，跳过")
            return result
        
        # 步骤 2：准备特征列表
        features_list = []
        for idx, (_, row) in enumerate(df.iterrows()):
            feature_name = str(row[label_col]) if label_col and label_col in df.columns else f"特征{idx}"
            tgi_val = row[tgi_col]
            
            # 跳过非数值 TGI
            if not isinstance(tgi_val, (int, float)) or pd.isna(tgi_val):
                continue
            
            coverage_val = 0
            if coverage_col and coverage_col in df.columns:
                cov = row[coverage_col]
                if isinstance(cov, (int, float)) and not pd.isna(cov):
                    coverage_val = float(cov)
            
            features_list.append({
                'name': feature_name,
                'tgi': float(tgi_val),
                'coverage': coverage_val,
            })
        
        if not features_list:
            logger.warning(f"维度 {dimension_name}：无有效特征")
            return result
        
        # 步骤 3：使用 v7.0 特征提取器进行完整分析
        logger.info(f"调用 FeatureExtractor v7.0 进行特征识别...")
        core_features, stats = self.feature_extractor.extract_dimension_features(
            dimension_name, features_list
        )
        
        # 步骤 4：整理结果
        result['features'] = core_features
        result['core_count'] = len(core_features)
        result['total_valid'] = stats.get('valid', 0)
        result['avg_tgi'] = stats.get('avg_tgi', 0)
        result['max_tgi'] = stats.get('max_tgi', 0)
        result['parallel_groups'] = stats.get('parallel_groups', 0)
        
        logger.info(f"分析完成：{len(core_features)} 条核心特征")
        
        return result
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """
        在 DataFrame 中查找列
        
        Args:
            df: DataFrame
            possible_names: 可能的列名列表
            
        Returns:
            找到的列名，或 None
        """
        for name in possible_names:
            if name in df.columns:
                return name
            # 尝试不区分大小写
            for col in df.columns:
                if col.lower() == name.lower():
                    return col
        return None
    
    def analyze_all_dimensions(self, data: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict]]:
        """
        分析所有维度
        
        Args:
            data: sheet 名称 → DataFrame 字典
            
        Returns:
            维度分析结果
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"开始全维度分析（使用 v7.0 特征识别标准）")
        logger.info(f"{'='*60}\n")
        
        all_dimensions = {}
        
        for sheet_name, df in data.items():
            logger.info(f"\n处理 sheet：{sheet_name}")
            
            # 分析该 sheet 作为一个维度
            result = self.analyze_dimension_with_v7(sheet_name, df)
            all_dimensions[sheet_name] = result
        
        return all_dimensions
    
    def generate_markdown_report(self, dimensions: Dict[str, Any], persona_name: str = "") -> str:
        """
        生成 Markdown 分析报告
        
        Args:
            dimensions: 维度分析结果
            persona_name: 人群名称
            
        Returns:
            Markdown 报告文本
        """
        logger.info("\n开始生成 Markdown 报告...")
        
        if not persona_name:
            persona_name = "人群"
        
        report = f"""# 📊 {persona_name}洞察分析报告 v7.0

> 本报告使用标准特征识别算法 v7.0 生成，采用三步法 + 四检查规范

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 一、用户画像（待补充）

*注：此部分需结合维度分析结果手动提炼*

### 一句话核心特征
基于以下维度的 Top 特征组合生成

### 核心定位标签
（向上提炼一层）

## 二、各维度分析

"""
        
        # 按 TGI 从高到低排序维度
        sorted_dims = sorted(
            dimensions.items(),
            key=lambda x: x[1].get('max_tgi', 0),
            reverse=True
        )
        
        for dim_name, dim_result in sorted_dims:
            if not dim_result['features']:
                continue
            
            report += f"### {dim_name}维度\n\n"
            
            # 核心特征列表
            report += "**核心特征列表（Top 10）** (v7.0 标准筛选)\n"
            for i, feat in enumerate(dim_result['features'][:10], 1):
                tgi = feat.get('tgi', 0)
                coverage = feat.get('coverage', 0)
                if coverage:
                    report += f"  {i}. {feat['name']}（TGI {tgi:.2f}, 占比 {coverage:.2%}）\n"
                else:
                    report += f"  {i}. {feat['name']}（TGI {tgi:.2f}）\n"
            
            report += "\n"
            
            # 维度统计
            report += "**维度统计**\n\n"
            report += f"- 总特征数：{dim_result['total_items']}\n"
            report += f"- 有效特征：{dim_result['total_valid']} (TGI ≥ 1.0)\n"
            report += f"- 核心特征：{dim_result['core_count']} (前40%)\n"
            report += f"- 平均 TGI：{dim_result['avg_tgi']:.2f}\n"
            report += f"- 最高 TGI：{dim_result['max_tgi']:.2f}\n"
            
            if dim_result.get('parallel_groups', 0) > 0:
                report += f"- 并列特征组：{dim_result['parallel_groups']}\n"
            
            report += "\n**判断理由**\n\n"
            
            # 自动判断特征类型
            if dim_result['max_tgi'] > 0 and dim_result['avg_tgi'] > 0:
                ratio = dim_result['max_tgi'] / dim_result['avg_tgi']
                if ratio > 1.5:
                    feature_type = "聚焦型"
                    reason = f"该维度特征聚焦度高（最高TGI {dim_result['max_tgi']:.2f} 是平均值 {dim_result['avg_tgi']:.2f} 的 {ratio:.1f} 倍），用户在此维度有明显的特征集中。"
                else:
                    feature_type = "均衡型"
                    reason = f"该维度特征分布相对均衡（最高TGI {dim_result['max_tgi']:.2f}，平均值 {dim_result['avg_tgi']:.2f}），用户呈现多元化特征。"
            else:
                feature_type = "待评"
                reason = "无有效TGI数据，无法判断。"
            
            report += f"🎯 **特征类型**：{feature_type}\n\n"
            report += f"🎯 **分析**：{reason}\n\n"
            
            report += "**数据分布说明**\n\n"
            report += f"📊 该维度共包含 {dim_result['total_items']} 条标签数据，其中 {dim_result['total_valid']} 条有效特征（TGI ≥ 1.0），"
            report += f"筛选后保留 {dim_result['core_count']} 条核心特征（前40%），最高TGI {dim_result['max_tgi']:.2f}，"
            report += f"平均TGI {dim_result['avg_tgi']:.2f}。\n\n"
        
        # 三、综合建议
        report += """## 三、综合分析建议

> 注：此部分需结合各维度核心特征组合手动生成

### 产品定位
（基于核心特征推导）

### 渠道布局
（基于维度热点推导）

### 内容营销
（基于兴趣维度推导）

## 四、深度分析建议

> 注：此部分需基于维度间的关联性手动生成

### 单维度深度分析
（按优先级 - 高/中/低）

### 交叉维度分析
（高价值组合）

---

## 附录：特征识别算法说明

本报告使用标准特征识别算法 v7.0，包含以下规范：

### 三步法特征筛选
1. **筛选 TGI ≥ 1.0** - 排除无效特征
2. **按占比降序排名** - 维度内相对排序
3. **取前40%** - 动态阈值（大维度最多20条）

### 四大检查规则
1. **并列特征识别** - TGI差 ≤ 0.2 + 占比比 < 1:1.5 + 均超平均
2. **互斥关系处理** - 选择TGI更高的标签
3. **无区分度排除** - TGI比和占比比都在 0.9-1.1 范围内
4. **自动验证** - 所有操作都有日志记录

**更多信息参见**: 
- `FEATURE_EXTRACTION_STANDARD.md` - 完整算法规范
- `feature_extraction.py` - Python实现

---

*报告生成器：PersonaInsightAnalyzerV7 (v7.0)*
"""
        
        logger.info("Markdown 报告生成完成")
        return report
    
    def save_report(self, report_content: str, filename: str) -> Path:
        """
        保存报告到文件
        
        Args:
            report_content: 报告内容
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        filepath = self.output_dir / filename
        filepath.write_text(report_content, encoding='utf-8')
        logger.info(f"报告已保存：{filepath}")
        return filepath
    
    def process(self, file_path: str, persona_name: str = "") -> Path:
        """
        完整分析流程：加载 → 分析 → 生成报告
        
        Args:
            file_path: 数据文件路径
            persona_name: 人群名称（可选）
            
        Returns:
            生成的报告文件路径
        """
        # 加载数据
        data = self.load_data(file_path)
        
        # 分析所有维度（使用 v7.0 标准）
        dimensions = self.analyze_all_dimensions(data)
        
        # 生成 Markdown 报告
        report_content = self.generate_markdown_report(dimensions, persona_name)
        
        # 保存报告
        if not persona_name:
            persona_name = Path(file_path).stem
        
        filename = f"{persona_name}_分析报告_v7.0.md"
        report_path = self.save_report(report_content, filename)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ 分析完成！")
        logger.info(f"{'='*60}")
        logger.info(f"报告已保存到：{report_path}")
        
        return report_path


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="DMP 人群洞察分析（v7.0 标准特征识别）"
    )
    parser.add_argument("file", help="数据文件路径（Excel/CSV）")
    parser.add_argument("--name", "-n", help="人群名称", default="")
    parser.add_argument("--output", "-o", help="输出目录", default="reports")
    
    args = parser.parse_args()
    
    # 创建分析器并处理
    analyzer = PersonaInsightAnalyzerV7(output_dir=args.output)
    analyzer.process(args.file, args.name)


if __name__ == '__main__':
    main()
