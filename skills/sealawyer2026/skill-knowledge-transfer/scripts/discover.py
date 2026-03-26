#!/usr/bin/env python3
"""
九章技能间知识迁移引擎 - 知识发现脚本
发现不同技能间可迁移的知识和案例
"""

import json
import os
import sys
from pathlib import Path
from difflib import SequenceMatcher
from collections import defaultdict

# 技能工作目录
SKILLS_DIR = Path(os.getenv('JIUZHANG_WORKSPACE', '~/.openclaw/workspace/skills')).expanduser()

def load_skill_cases(skill_name):
    """加载技能案例库"""
    case_file = SKILLS_DIR / skill_name / 'case-library.json'
    if not case_file.exists():
        return []
    
    with open(case_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('cases', [])

def calculate_similarity(text1, text2):
    """计算文本相似度"""
    return SequenceMatcher(None, text1, text2).ratio()

def discover_similar_cases(source_skill, target_skill, threshold=0.7):
    """发现相似案例"""
    source_cases = load_skill_cases(source_skill)
    target_cases = load_skill_cases(target_skill)
    
    similar_pairs = []
    
    for sc in source_cases:
        for tc in target_cases:
            # 计算标题相似度
            title_sim = calculate_similarity(sc.get('title', ''), tc.get('title', ''))
            # 计算案情相似度
            facts_sim = calculate_similarity(sc.get('facts', ''), tc.get('facts', ''))
            # 计算标签重叠度
            source_tags = set(sc.get('tags', []))
            target_tags = set(tc.get('tags', []))
            tag_overlap = len(source_tags & target_tags) / max(len(source_tags | target_tags), 1)
            
            # 综合相似度
            overall_sim = (title_sim * 0.3 + facts_sim * 0.5 + tag_overlap * 0.2)
            
            if overall_sim >= threshold:
                similar_pairs.append({
                    'source_case': sc['id'],
                    'source_title': sc['title'],
                    'target_case': tc['id'],
                    'target_title': tc['title'],
                    'similarity': round(overall_sim, 3),
                    'suggestion': 'consider_cross_reference' if overall_sim > 0.85 else 'review_for_transfer'
                })
    
    return sorted(similar_pairs, key=lambda x: x['similarity'], reverse=True)

def discover_common_rules(skills):
    """发现通用规则"""
    all_rules = defaultdict(list)
    
    for skill in skills:
        cases = load_skill_cases(skill)
        for case in cases:
            for insight in case.get('compliance_insights', '').split('。'):
                insight = insight.strip()
                if len(insight) > 20:
                    all_rules[insight[:50]].append({
                        'skill': skill,
                        'case_id': case['id'],
                        'full_insight': insight
                    })
    
    # 找出在多个技能中出现的规则
    common_rules = []
    for rule_prefix, occurrences in all_rules.items():
        if len(occurrences) >= 2:
            common_rules.append({
                'rule_preview': rule_prefix + '...',
                'occurrence_count': len(occurrences),
                'skills': list(set(o['skill'] for o in occurrences)),
                'cases': [o['case_id'] for o in occurrences[:3]]
            })
    
    return sorted(common_rules, key=lambda x: x['occurrence_count'], reverse=True)

def generate_transfer_plan(source_skill, target_skill):
    """生成迁移计划"""
    similar_cases = discover_similar_cases(source_skill, target_skill)
    
    plan = {
        'source_skill': source_skill,
        'target_skill': target_skill,
        'discovered_at': datetime.now().isoformat(),
        'similar_cases': similar_cases[:10],  # Top 10
        'recommendations': []
    }
    
    # 生成迁移建议
    if similar_cases:
        high_sim = [s for s in similar_cases if s['similarity'] > 0.85]
        med_sim = [s for s in similar_cases if 0.7 <= s['similarity'] <= 0.85]
        
        if high_sim:
            plan['recommendations'].append({
                'type': 'cross_reference',
                'priority': 'high',
                'description': f'发现 {len(high_sim)} 个高度相似案例，建议在目标技能中引用源案例',
                'cases': [s['source_case'] for s in high_sim]
            })
        
        if med_sim:
            plan['recommendations'].append({
                'type': 'adapt_and_transfer',
                'priority': 'medium',
                'description': f'发现 {len(med_sim)} 个中度相似案例，建议适配后迁移',
                'cases': [s['source_case'] for s in med_sim]
            })
    
    return plan

def discover_ecosystem_opportunities():
    """发现整个技能生态的迁移机会"""
    # 获取所有技能目录
    skills = [d.name for d in SKILLS_DIR.iterdir() 
              if d.is_dir() and d.name.startswith('zhang-')]
    
    opportunities = []
    
    # 两两比较
    for i, source in enumerate(skills):
        for target in skills[i+1:]:
            similar = discover_similar_cases(source, target, threshold=0.75)
            if similar:
                opportunities.append({
                    'source': source,
                    'target': target,
                    'similar_case_count': len(similar),
                    'top_similarity': similar[0]['similarity'] if similar else 0
                })
    
    return sorted(opportunities, key=lambda x: x['similar_case_count'], reverse=True)

def main():
    if len(sys.argv) < 2:
        print("用法: python discover.py [similar|common|plan|ecosystem]")
        print("  similar <source> <target>  - 发现相似案例")
        print("  common <skill1> <skill2> ... - 发现通用规则")
        print("  plan <source> <target>     - 生成迁移计划")
        print("  ecosystem                  - 发现生态迁移机会")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'similar' and len(sys.argv) >= 4:
        source, target = sys.argv[2], sys.argv[3]
        similar = discover_similar_cases(source, target)
        print(f"\n🔍 {source} → {target} 相似案例发现:")
        for s in similar[:10]:
            print(f"  相似度 {s['similarity']}: {s['source_case']} ↔ {s['target_case']}")
            print(f"    {s['source_title'][:60]}...")
    
    elif command == 'common' and len(sys.argv) >= 3:
        skills = sys.argv[2:]
        rules = discover_common_rules(skills)
        print(f"\n📋 通用规则发现 (Top 10):")
        for r in rules[:10]:
            print(f"  [{r['occurrence_count']}次] {r['rule_preview']}")
            print(f"    涉及技能: {', '.join(r['skills'])}")
    
    elif command == 'plan' and len(sys.argv) >= 4:
        source, target = sys.argv[2], sys.argv[3]
        plan = generate_transfer_plan(source, target)
        print(f"\n📋 迁移计划: {source} → {target}")
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    
    elif command == 'ecosystem':
        opportunities = discover_ecosystem_opportunities()
        print(f"\n🌐 技能生态迁移机会 (Top 10):")
        for opp in opportunities[:10]:
            print(f"  {opp['source']} ↔ {opp['target']}: {opp['similar_case_count']}个相似案例")
    
    else:
        print("用法: python discover.py [similar|common|plan|ecosystem]")

if __name__ == '__main__':
    from datetime import datetime
    main()
