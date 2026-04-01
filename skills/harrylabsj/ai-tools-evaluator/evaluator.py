#!/usr/bin/env python3
"""
AI Tools Evaluator - MVP
AI 工具对比评测助手 V1
帮助用户在 2~5 个候选 AI 工具之间做结构化比较，输出可直接用于决策的推荐报告。
"""

import json
import sys
from typing import List, Dict, Any

# ==================== 数据加载 ====================
def load_tools() -> Dict[str, Any]:
    """加载工具池数据"""
    with open('data/tools.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# ==================== 界面函数 ====================
def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_category_tools(tools_data: Dict[str, Any]) -> Dict[str, Any]:
    """展示分类工具池，返回用户选择的工具ID列表"""
    categories = tools_data['categories']
    
    print_header("📦 工具池 - 请选择要对比的工具（2~5个）")
    print("输入编号（用空格分隔，如: 1 3 5）\n")
    
    all_tools = []
    for cat_idx, category in enumerate(categories):
        print(f"\n{cat_idx + 1}. {category['icon']} {category['name']}")
        print("-" * 40)
        for tool_idx, tool in enumerate(category['tools']):
            global_idx = len(all_tools)
            all_tools.append(tool)
            print(f"   [{global_idx + 1}] {tool['name']} ({tool['provider']})")
            print(f"       {tool['description'][:50]}...")
    
    print("\n" + "-" * 60)
    print("请输入工具编号 (2~5个): ", end="")
    
    try:
        selected = input().strip()
        indices = [int(x.strip()) - 1 for x in selected.split() if x.strip()]
        
        # D01 fix: 去重，保持顺序
        seen = set()
        unique_indices = []
        for idx in indices:
            if idx not in seen:
                seen.add(idx)
                unique_indices.append(idx)
        indices = unique_indices
        
        if len(indices) < 2:
            print("❌ 至少需要选择2个工具")
            sys.exit(1)
        if len(indices) > 5:
            print("❌ 最多选择5个工具")
            sys.exit(1)
        
        # D01 fix: 验证每个索引都合法
        invalid_indices = [i for i in indices if i < 0 or i >= len(all_tools)]
        if invalid_indices:
            print("❌ 选择无效")
            sys.exit(1)
        
        selected_tools = [all_tools[i] for i in indices]
        if len(selected_tools) < 2:
            print("❌ 选择无效")
            sys.exit(1)
            
        return selected_tools
    except ValueError:
        print("❌ 输入格式错误")
        sys.exit(1)
    except IndexError:
        print("❌ 选择无效")
        sys.exit(1)

def select_use_case() -> str:
    """选择使用场景"""
    print_header("🎯 使用场景")
    print("1. 日常办公（文档、邮件、会议）")
    print("2. 学术研究（论文、文献、数据分析）")
    print("3. 创意创作（写作、设计、视频）")
    print("4. 程序开发（代码、调试、测试）")
    print("5. 商业应用（客服、营销、数据处理）")
    print("6. 学习教育（辅导、答疑、知识整理）")
    
    scenes = {
        "1": "日常办公",
        "2": "学术研究", 
        "3": "创意创作",
        "4": "程序开发",
        "5": "商业应用",
        "6": "学习教育"
    }
    
    print("\n请输入场景编号 (1-6): ", end="")
    choice = input().strip()
    return scenes.get(choice, "日常办公")

def select_budget() -> str:
    """选择预算区间"""
    print_header("💰 预算区间")
    print("1. 免费 / 低成本 (< $10/月)")
    print("2. 中等预算 ($10-30/月)")
    print("3. 高预算 (> $30/月)")
    print("4. 不限预算")
    
    budgets = {
        "1": "免费/低成本",
        "2": "中等预算",
        "3": "高预算",
        "4": "不限预算"
    }
    
    print("\n请输入预算编号 (1-4): ", end="")
    choice = input().strip()
    return budgets.get(choice, "中等预算")

def confirm_dimensions() -> Dict[str, float]:
    """确认评测维度权重（简化版）"""
    print_header("⚖️ 评测维度权重确认")
    print("系统将根据以下维度进行综合评分：\n")
    print("  - 能力匹配度：与您场景的匹配程度")
    print("  - 成本效益：性价比如何")
    print("  - 易用性：上手难度和体验")
    print("  - 稳定性：服务可靠性")
    print("  - 隐私安全：数据安全考量\n")
    
    print("默认权重配置（可直接回车确认）：")
    print("  能力匹配度: 40%")
    print("  成本效益:   25%")
    print("  易用性:     15%")
    print("  稳定性:     10%")
    print("  隐私安全:   10%")
    
    print("\n直接回车使用默认配置，或输入 'y' 确认: ", end="")
    choice = input().strip().lower()
    
    if choice == 'y' or choice == '':
        return {
            "能力匹配度": 0.40,
            "成本效益": 0.25,
            "易用性": 0.15,
            "稳定性": 0.10,
            "隐私安全": 0.10
        }
    else:
        # 简化处理，直接返回默认值
        return {
            "能力匹配度": 0.40,
            "成本效益": 0.25,
            "易用性": 0.15,
            "稳定性": 0.10,
            "隐私安全": 0.10
        }

# ==================== 评分引擎 ====================
def calculate_tool_score(tool: Dict, use_case: str, budget: str, weights: Dict[str, float], all_tools: List[Dict]) -> float:
    """计算工具综合评分"""
    # 能力匹配度评分
    capability_score = calculate_capability_score(tool, use_case)
    
    # 成本效益评分
    cost_score = calculate_cost_score(tool, budget)
    
    # 易用性评分
    usability_score = calculate_usability_score(tool)
    
    # 稳定性评分
    stability_score = calculate_stability_score(tool)
    
    # 隐私安全评分
    privacy_score = calculate_privacy_score(tool)
    
    # 加权求和
    total = (
        capability_score * weights["能力匹配度"] +
        cost_score * weights["成本效益"] +
        usability_score * weights["易用性"] +
        stability_score * weights["稳定性"] +
        privacy_score * weights["隐私安全"]
    )
    
    return round(total * 100, 1)

def calculate_capability_score(tool: Dict, use_case: str) -> float:
    """计算能力匹配度"""
    best_for = [x.lower() for x in tool.get('best_for', [])]
    tags = [x.lower() for x in tool.get('tags', [])]
    
    # 场景关键词映射
    scene_mapping = {
        "日常办公": ["办公", "文档", "邮件", "office", "writing", "文本", "中文"],
        "学术研究": ["研究", "学术", "论文", "分析", "research", "长文本"],
        "创意创作": ["创意", "写作", "设计", "视频", "creative", "art", "创作"],
        "程序开发": ["代码", "编程", "developer", "code", "编程", "开发"],
        "商业应用": ["商业", "企业", "business", "数据", "客服", "营销"],
        "学习教育": ["学习", "教育", "学习", "辅导", "student", "learn"]
    }
    
    scene_keywords = scene_mapping.get(use_case, [])
    
    # 基础分
    score = 0.6
    
    # 匹配加分
    for keyword in scene_keywords:
        if keyword.lower() in str(best_for).lower():
            score += 0.15
        if keyword.lower() in str(tags).lower():
            score += 0.10
    
    return min(score, 1.0)

def calculate_cost_score(tool: Dict, budget: str) -> float:
    """计算成本效益评分"""
    pricing = tool.get('pricing', '').lower()
    
    # 判断费用级别
    if '免费' in pricing or 'free' in pricing or '免费' in tool.get('pricing', ''):
        cost_level = 1.0
    elif any(x in pricing for x in ['$0', '$1', '¥0', '¥0.5']):
        cost_level = 0.85
    elif any(x in pricing for x in ['$10', '$20', '¥30']):
        cost_level = 0.65
    elif any(x in pricing for x in ['$30', '$50', '¥100']):
        cost_level = 0.45
    else:
        cost_level = 0.5  # 未知定价给中等分
    
    # 预算匹配度
    budget_mapping = {
        "免费/低成本": (1.0, 0.3),
        "中等预算": (0.6, 0.8),
        "高预算": (0.3, 1.0),
        "不限预算": (0.5, 1.0)
    }
    
    budget_min, budget_max = budget_mapping.get(budget, (0.4, 0.8))
    
    if budget_min <= cost_level <= budget_max:
        adjustment = 1.0
    elif cost_level < budget_min:
        adjustment = 1.1  # 比预算要求更便宜，加分
    else:
        adjustment = 0.8  # 超出预算，减分
    
    return min(cost_level * adjustment, 1.0)

def calculate_usability_score(tool: Dict) -> float:
    """计算易用性评分"""
    description = tool.get('description', '').lower()
    
    # 简单判断：集成生态越好越易用
    score = 0.7
    
    if any(x in description for x in ['简单', '容易', 'easy', '简单上手']):
        score = 0.9
    elif any(x in description for x in ['深度', '需要配置', 'complex']):
        score = 0.6
    
    # 开源/本地部署相对复杂
    if '开源' in tool.get('name', '') or 'stable diffusion' in tool.get('id', ''):
        score = 0.55
    
    return score

def calculate_stability_score(tool: Dict) -> float:
    """计算稳定性评分"""
    provider = tool.get('provider', '').lower()
    
    # 知名大厂稳定性好
    stable_providers = ['openai', 'anthropic', 'google', 'microsoft', '阿里', '百度']
    emerging_providers = ['deepseek', '零一', '智谱', 'cursor']
    
    if any(p in provider for p in stable_providers):
        return 0.9
    elif any(p in provider for p in emerging_providers):
        return 0.75
    else:
        return 0.7

def calculate_privacy_score(tool: Dict) -> float:
    """计算隐私安全评分"""
    tool_id = tool.get('id', '').lower()
    
    # 本地部署隐私最好
    if 'sd' in tool_id or 'stable diffusion' in tool_id:
        return 0.95
    
    # 国产服务（数据留国内）
    cn_providers = ['阿里', '百度', '智谱', '零一', '秘塔', '文心', '通义']
    if any(p in tool.get('provider', '') for p in cn_providers):
        return 0.85
    
    # 国外服务
    if any(p in tool.get('provider', '').lower() for p in ['openai', 'anthropic', 'google', 'microsoft']):
        return 0.65  # 跨境数据风险
    
    return 0.7

# ==================== 报告生成 ====================
def generate_report(selected_tools: List[Dict], use_case: str, budget: str, weights: Dict[str, float]) -> str:
    """生成对比报告"""
    
    # 计算每个工具的评分
    tool_scores = []
    for tool in selected_tools:
        score = calculate_tool_score(tool, use_case, budget, weights, selected_tools)
        tool_scores.append({
            'tool': tool,
            'score': score
        })
    
    # 按评分排序
    tool_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # 生成报告
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("       🤖 AI 工具对比评测报告")
    report_lines.append("=" * 70)
    report_lines.append(f"\n📋 评测配置")
    report_lines.append(f"   场景: {use_case}")
    report_lines.append(f"   预算: {budget}")
    report_lines.append(f"   维度权重: 能力{weights['能力匹配度']:.0%} | 成本{weights['成本效益']:.0%} | 易用{weights['易用性']:.0%} | 稳定{weights['稳定性']:.0%} | 隐私{weights['隐私安全']:.0%}")
    
    # 综合评分表
    report_lines.append("\n" + "=" * 70)
    report_lines.append("📊 综合评分对比")
    report_lines.append("=" * 70)
    report_lines.append(f"{'工具名称':<25} {'提供商':<12} {'综合评分':>8}")
    report_lines.append("-" * 50)
    
    for item in tool_scores:
        tool = item['tool']
        score = item['score']
        report_lines.append(f"{tool['name']:<25} {tool['provider']:<12} {score:>7.1f}/100")
    
    # 详细对比表
    report_lines.append("\n" + "=" * 70)
    report_lines.append("📈 维度得分详情")
    report_lines.append("=" * 70)
    report_lines.append(f"{'工具名称':<20} {'能力匹配':>8} {'成本效益':>8} {'易用性':>8} {'稳定性':>8} {'隐私安全':>8}")
    report_lines.append("-" * 70)
    
    for item in tool_scores:
        tool = item['tool']
        cap = calculate_capability_score(tool, use_case) * 100
        cost = calculate_cost_score(tool, budget) * 100
        usab = calculate_usability_score(tool) * 100
        stabi = calculate_stability_score(tool) * 100
        priv = calculate_privacy_score(tool) * 100
        
        report_lines.append(f"{tool['name'][:20]:<20} {cap:>7.1f} {cost:>7.1f} {usab:>7.1f} {stabi:>7.1f} {priv:>7.1f}")
    
    # 优劣势分析
    report_lines.append("\n" + "=" * 70)
    report_lines.append("✅ 优劣势分析")
    report_lines.append("=" * 70)
    
    for item in tool_scores:
        tool = item['tool']
        rank = tool_scores.index(item) + 1
        rank_emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        
        report_lines.append(f"\n{rank_emoji} {tool['name']} (第{rank}名)")
        report_lines.append(f"   优势: {', '.join(tool.get('strengths', [])[:3])}")
        report_lines.append(f"   劣势: {', '.join(tool.get('weaknesses', [])[:2])}")
        report_lines.append(f"   定价: {tool.get('pricing', '未知')}")
    
    # 推荐结论
    best_tool = tool_scores[0]
    report_lines.append("\n" + "=" * 70)
    report_lines.append("🎯 推荐结论")
    report_lines.append("=" * 70)
    report_lines.append(f"""
🥇 首选推荐: {best_tool['tool']['name']}

综合评分 {best_tool['score']:.1f}/100，在当前场景({use_case})和预算({budget})下表现最优。

推荐理由:
• {best_tool['tool']['strengths'][0] if best_tool['tool'].get('strengths') else '综合表现最佳'}
• 定价方案: {best_tool['tool'].get('pricing', '未知')}
• 适用场景: {', '.join(best_tool['tool'].get('best_for', [])[:3])}

目标用户: {', '.join(best_tool['tool'].get('target_users', [])[:2])}
""")
    
    # 风险提醒
    report_lines.append("=" * 70)
    report_lines.append("⚠️ 风险提醒")
    report_lines.append("=" * 70)
    report_lines.append("""
1. 评分基于公开信息整理，实际体验可能存在差异
2. 定价可能随服务商政策调整，请以官方最新为准
3. 部分工具需要科学上网，请确认使用环境
4. 涉及敏感数据时，优先考虑数据隐私合规
5. 建议先用免费额度或试用版进行实际体验
""")
    
    # 适用人群建议
    report_lines.append("=" * 70)
    report_lines.append("👥 适用人群建议")
    report_lines.append("=" * 70)
    
    for item in tool_scores:
        tool = item['tool']
        report_lines.append(f"\n• {tool['name']}: {', '.join(tool.get('target_users', ['通用用户']))}")
    
    report_lines.append("\n" + "=" * 70)
    report_lines.append("📌 使用建议")
    report_lines.append("=" * 70)
    report_lines.append("""
1. 明确核心需求：先确定最看重的1-2个维度
2. 试用验证：建议先使用免费额度实际体验
3. 关注生态：考虑与其他工具的协同效果
4. 预留灵活性：可同时使用多个工具互补
5. 定期复盘：AI工具更新快，建议定期重新评估
""")
    
    report_lines.append("\n" + "=" * 70)
    report_lines.append("报告生成时间: " + __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M"))
    report_lines.append("=" * 70)
    
    return "\n".join(report_lines)

# ==================== 主流程 ====================
def main():
    """主流程"""
    print("\n" + "=" * 60)
    print("  🚀 欢迎使用 AI Tools Evaluator")
    print("     AI 工具对比评测助手 V1")
    print("=" * 60)
    
    # 1. 加载工具池
    tools_data = load_tools()
    print(f"\n✅ 已加载 {sum(len(c['tools']) for c in tools_data['categories'])} 个AI工具")
    
    # 2. 选择工具
    selected_tools = print_category_tools(tools_data)
    if not selected_tools:
        print("\n❌ 工具选择失败，程序退出")
        sys.exit(1)
    
    print(f"\n✅ 已选择 {len(selected_tools)} 个工具:")
    for t in selected_tools:
        print(f"   - {t['name']}")
    
    # 3. 选择使用场景
    use_case = select_use_case()
    print(f"\n✅ 已选择场景: {use_case}")
    
    # 4. 选择预算
    budget = select_budget()
    print(f"\n✅ 已选择预算: {budget}")
    
    # 5. 确认评测维度
    weights = confirm_dimensions()
    print(f"\n✅ 已确认维度权重")
    
    # 6. 生成报告
    report = generate_report(selected_tools, use_case, budget, weights)
    
    # 7. 显示报告
    print_header("📄 对比报告已生成")
    print(report)
    
    # 8. 保存报告
    report_file = "ai_tools_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ 报告已保存至: {report_file}")
    
    # 9. 询问是否复制
    print("\n是否复制报告内容到剪贴板？(y/n): ", end="")
    try:
        if input().strip().lower() == 'y':
            try:
                import pyperclip
                pyperclip.copy(report)
                print("✅ 报告已复制到剪贴板")
            except ImportError:
                print("⚠️ 剪贴板功能需要安装 pyperclip: pip install pyperclip")
                print("   报告已保存到文件，可手动复制")
    except EOFError:
        print("\n   跳过复制（无终端输入）")
    
    print("\n" + "=" * 60)
    print("  👋 感谢使用 AI Tools Evaluator!")
    print("=" * 60)

if __name__ == "__main__":
    main()
