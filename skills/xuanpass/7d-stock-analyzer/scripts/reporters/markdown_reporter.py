"""
Markdown 报告生成器
"""

from typing import Dict, Any
from datetime import datetime


class MarkdownReporter:
    """Markdown 报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def generate(self, symbol: str, results: Dict[str, Any], full: bool = False) -> str:
        """
        生成 Markdown 格式报告

        Args:
            symbol: 股票代码
            results: 分析结果字典
            full: 是否生成完整报告

        Returns:
            Markdown 格式报告
        """
        lines = []

        # 标题
        lines.append(f"# 📊 股票分析报告 - {symbol}")
        lines.append("")
        lines.append(f"**生成时间**: {self.timestamp}")
        lines.append("")

        # 如果有结论，先显示结论
        if 'conclusion' in results:
            lines.extend(self._render_conclusion(results['conclusion']))
            lines.append("")

        # 各维度分析结果
        dimension_names = {
            'data': '数据收集与验证',
            'fundamental': '基本面分析',
            'valuation': '估值分析',
            'industry': '行业与竞争分析',
            'technical': '技术面分析',
            'risk': '风险识别'
        }

        for key, name in dimension_names.items():
            if key in results and results[key]:
                lines.extend(self._render_dimension(name, results[key]))
                lines.append("")

        # 免责声明
        lines.append("---")
        lines.append("")
        lines.append("## ⚠️ 风险提示")
        lines.append("")
        lines.append("- 本分析仅供参考，不构成投资建议")
        lines.append("- 投资有风险，入市需谨慎")
        lines.append("- 请结合市场情况和自身判断做出决策")
        lines.append("- 数据可能存在延迟，请以实时数据为准")

        return "\n".join(lines)

    def _render_conclusion(self, conclusion: Dict[str, Any]) -> list:
        """渲染结论部分"""
        lines = []

        lines.append("## 🎯 综合评价")
        lines.append("")

        # 评级
        rating = conclusion.get('rating', '⭐⭐⭐ 中性')
        score = conclusion.get('overall_score', 50)
        lines.append(f"**综合评分**: {score}/100")
        lines.append(f"**投资评级**: {rating}")
        lines.append("")

        # 投资建议
        recommendation = conclusion.get('recommendation', '')
        if recommendation:
            lines.append(f"**投资建议**: {recommendation}")
            lines.append("")

        # 投资论点
        thesis = conclusion.get('investment_thesis', '')
        if thesis:
            lines.append("### 💡 投资论点")
            lines.append("")
            lines.append(thesis)
            lines.append("")

        # 行动计划
        action_plan = conclusion.get('action_plan', [])
        if action_plan:
            lines.append("### 📋 行动计划")
            lines.append("")
            for i, action in enumerate(action_plan, 1):
                lines.append(f"{i}. {action}")
            lines.append("")

        # 监控要点
        monitoring_points = conclusion.get('monitoring_points', [])
        if monitoring_points:
            lines.append("### 🔍 监控要点")
            lines.append("")
            for point in monitoring_points:
                lines.append(f"- {point}")
            lines.append("")

        return lines

    def _render_dimension(self, name: str, result: Dict[str, Any]) -> list:
        """渲染单个维度"""
        lines = []

        lines.append(f"## {name}")
        lines.append("")

        # 显示评分
        if 'score' in result:
            score = result['score']
            lines.append(f"**评分**: {score}/100")
            lines.append("")

        # 显示详情
        if 'details' in result:
            details = result['details']
            for section_name, section_data in details.items():
                lines.append(f"### {section_name.replace('_', ' ').title()}")
                lines.append("")
                lines.append(f"```json")
                lines.append(self._format_json(section_data))
                lines.append(f"```")
                lines.append("")

        # 显示错误
        if result.get('errors'):
            lines.append("### ⚠️ 错误提示")
            lines.append("")
            for error in result['errors']:
                lines.append(f"- {error}")
            lines.append("")

        return lines

    def _format_json(self, data: Any, indent: int = 2) -> str:
        """格式化 JSON 数据"""
        import json
        return json.dumps(data, ensure_ascii=False, indent=indent)
