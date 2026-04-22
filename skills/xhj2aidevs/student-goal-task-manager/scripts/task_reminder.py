#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
助学星 - 任务临期/超期提醒 & 学习调整建议生成器

读取助学星导出的 JSON 备份文件，分析所有任务的临期和超期情况，
结合目标进度和任务分布，生成个性化的学习调整建议报告。

用法:
  python task_reminder.py <备份文件.json>
  python task_reminder.py <备份文件.json> --output report.md
  python task_reminder.py <备份文件.json> --days 3   # 自定义临期阈值天数

数据来源: 助学星「设置→数据备份」导出的 .json 文件
"""

import json
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict


def load_backup(filepath: str) -> dict:
    """加载助学星备份 JSON 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 校验是否为助学星备份
    app_name = data.get('_appName', '')
    if '助学星' not in app_name and '好学帮' not in app_name:
        print(f"⚠️ 警告：该文件可能不是助学星的备份文件（_appName={app_name}）")
    return data


def get_tasks(data: dict) -> list:
    """提取任务列表，兼容新旧备份 key"""
    tasks = data.get('stu_tasks_v4') or data.get('tasks') or []
    return [t for t in tasks if isinstance(t, dict)]


def get_goals(data: dict) -> list:
    """提取目标列表"""
    goals = data.get('stu_goals_v1') or data.get('taskGoals') or []
    return [g for g in goals if isinstance(g, dict)]


def get_memos(data: dict) -> list:
    """提取备忘录列表"""
    return data.get('stu_memos_v1') or data.get('memos') or []


def today_str():
    return datetime.now().strftime('%Y-%m-%d')


def now_dt():
    return datetime.now()


def parse_deadline(task: dict) -> datetime:
    """解析任务截止时间"""
    date_str = task.get('date', '')
    time_str = task.get('time', '')
    if not date_str:
        return None
    try:
        if time_str:
            return datetime.strptime(f"{date_str}T{time_str}", '%Y-%m-%dT%H:%M')
        return datetime.strptime(f"{date_str}T23:59:59", '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return None


def classify_task(task: dict, urgent_days: int = 3) -> str:
    """分类任务状态：overdue / urgent / soon / normal / done / nodate"""
    if task.get('done'):
        return 'done'
    deadline = parse_deadline(task)
    if not deadline:
        return 'nodate'
    now = now_dt()
    if deadline < now:
        return 'overdue'
    diff = (deadline - now).total_seconds() / 86400
    if diff <= 1:
        return 'urgent'   # < 24h
    if diff <= urgent_days:
        return 'soon'     # <= urgent_days
    return 'normal'


def calc_deviation(goal: dict) -> float:
    """计算目标偏离度（与助学星逻辑一致）"""
    if goal.get('status') == 'done':
        return 0.0
    deadline = goal.get('deadline', '')
    if not deadline:
        return 0.0
    created = goal.get('createdAt', '')
    if not created:
        return 0.0

    try:
        d_deadline = datetime.strptime(deadline[:10], '%Y-%m-%d')
        # createdAt 可能是时间戳(毫秒)或日期字符串
        if isinstance(created, (int, float)):
            if created > 1e12:
                created = created / 1000
            d_created = datetime.fromtimestamp(created)
        else:
            d_created = datetime.strptime(str(created)[:10], '%Y-%m-%d')
    except (ValueError, OSError):
        return 0.0

    total_days = max(1, (d_deadline - d_created).days)
    elapsed_days = max(0, (now_dt() - d_created).days)
    expected_pct = min(100, round(elapsed_days / total_days * 100))
    actual_pct = goal.get('progress', 0)
    return actual_pct - expected_pct


# ==================== 报告生成 ====================

def build_report(data: dict, urgent_days: int = 3) -> str:
    """生成完整的学习提醒报告"""
    tasks = get_tasks(data)
    goals = get_goals(data)
    memos = get_memos(data)
    today = today_str()

    # ---------- 分类任务 ----------
    categories = defaultdict(list)
    for t in tasks:
        cat = classify_task(t, urgent_days)
        categories[cat].append(t)

    overdue = categories['overdue']
    urgent = categories['urgent']
    soon = categories['soon']
    normal = categories['normal']
    done = categories['done']
    nodate = categories['nodate']

    total = len(tasks)
    total_done = len(done)
    total_pending = total - total_done
    done_rate = round(total_done / total * 100) if total else 0

    # ---------- 目标偏离分析 ----------
    deviated_goals = []
    for g in goals:
        if g.get('status') in ('progress', 'in_progress', 'deviated'):
            dev = calc_deviation(g)
            if dev < -15:
                deviated_goals.append((g, dev))

    # ---------- 今日任务 ----------
    today_tasks = [t for t in tasks if t.get('date') == today and not t.get('done')]
    today_done = [t for t in tasks if t.get('date') == today and t.get('done')]

    # ---------- 按标签统计 ----------
    tag_stats = defaultdict(lambda: {'total': 0, 'done': 0, 'overdue': 0})
    for t in tasks:
        tag = t.get('tag') or '未分类'
        tag_stats[tag]['total'] += 1
        if t.get('done'):
            tag_stats[tag]['done'] += 1
        if classify_task(t, urgent_days) in ('overdue',):
            tag_stats[tag]['overdue'] += 1

    # ========== 组装报告 ==========
    lines = []
    lines.append(f"# 📊 助学星 · 学习提醒报告")
    lines.append(f"")
    lines.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**分析数据：** {total} 个任务 · {len(goals)} 个目标 · {len(memos)} 个备忘录")
    lines.append(f"")

    # ===== 一、总览 =====
    lines.append("---")
    lines.append("")
    lines.append("## 📈 任务总览")
    lines.append("")
    lines.append(f"| 指标 | 数量 |")
    lines.append(f"|------|------|")
    lines.append(f"| 📋 总任务数 | {total} |")
    lines.append(f"| ✅ 已完成 | {total_done} |")
    lines.append(f"| 🔄 进行中 | {total_pending} |")
    lines.append(f"| 📊 完成率 | {done_rate}% |")
    lines.append(f"| 🔴 已逾期 | {len(overdue)} |")
    lines.append(f"| ⚡ 临期（24h内） | {len(urgent)} |")
    lines.append(f"| 🟡 近期（{urgent_days}天内） | {len(soon)} |")
    lines.append(f"| 📝 今日任务 | {len(today_tasks)}/{len(today_tasks)+len(today_done)} 完成 |")
    lines.append("")

    # ===== 二、逾期任务（紧急） =====
    if overdue:
        lines.append("---")
        lines.append("")
        lines.append(f"## 🔴 逾期任务（{len(overdue)}个）— 需立即处理")
        lines.append("")
        for i, t in enumerate(sorted(overdue, key=lambda x: parse_deadline(x) or datetime.min), 1):
            deadline = parse_deadline(t)
            days_late = ""
            if deadline:
                late = (now_dt() - deadline).days
                days_late = f"（已逾期 {late} 天）"
            priority_icon = {'high': '🔴', 'med': '🟡', 'low': '🟢'}.get(t.get('priority', ''), '⚪')
            tag = f"`{t.get('tag', '')}`" if t.get('tag') else ''
            lines.append(f"### {i}. {priority_icon} {t.get('title', '无标题')} {tag} {days_late}")
            desc = t.get('desc', '')
            if desc:
                lines.append(f"> {desc}")
            if deadline:
                lines.append(f"- ⏰ 截止：{deadline.strftime('%Y-%m-%d %H:%M')}")
            lines.append("")

        lines.append(f"> 💡 **处理建议**：{generate_overdue_advice(overdue)}")
        lines.append("")
    else:
        lines.append("---")
        lines.append("")
        lines.append("## ✅ 无逾期任务")
        lines.append("")
        lines.append("> 太棒了！没有逾期任务，继续保持 👍")
        lines.append("")

    # ===== 三、临期任务 =====
    if urgent or soon:
        urgent_and_soon = urgent + soon
        lines.append("---")
        lines.append("")
        lines.append(f"## ⚡ 临期任务（{len(urgent_and_soon)}个）— 24h ~ {urgent_days}天内到期")
        lines.append("")
        for i, t in enumerate(sorted(urgent_and_soon, key=lambda x: parse_deadline(x) or datetime.max), 1):
            deadline = parse_deadline(t)
            remain = ""
            if deadline:
                hours = (deadline - now_dt()).total_seconds() / 3600
                if hours < 24:
                    remain = f"（剩余 {round(hours, 1)} 小时）"
                else:
                    remain = f"（剩余 {round(hours/24, 1)} 天）"
            cat_icon = '⚡' if t in urgent else '🟡'
            tag = f"`{t.get('tag', '')}`" if t.get('tag') else ''
            lines.append(f"### {i}. {cat_icon} {t.get('title', '无标题')} {tag} {remain}")
            desc = t.get('desc', '')
            if desc:
                lines.append(f"> {desc}")
            if deadline:
                lines.append(f"- ⏰ 截止：{deadline.strftime('%Y-%m-%d %H:%M')}")
            lines.append("")
    else:
        lines.append("---")
        lines.append("")
        lines.append("## 📅 无临期任务")
        lines.append("")

    # ===== 四、今日任务 =====
    lines.append("---")
    lines.append("")
    lines.append(f"## 📋 今日任务（{len(today_tasks)} 未完成）")
    lines.append("")
    if today_tasks:
        for i, t in enumerate(today_tasks, 1):
            status = "⬜" if not t.get('done') else "✅"
            time_str = f" `{t.get('time', '')}`" if t.get('time') else ''
            tag = f" `{t.get('tag', '')}`" if t.get('tag') else ''
            lines.append(f"{i}. {status} **{t.get('title', '')}**{time_str}{tag}")
            if t.get('desc'):
                lines.append(f"   - {t.get('desc')}")
        lines.append("")
        if not today_done and today_tasks:
            lines.append("> ⚠️ 今天还没有完成任何任务，现在开始吧！")
            lines.append("")
    else:
        if today_done:
            lines.append(f"> 🎉 今日 {len(today_done)} 个任务全部完成！")
            lines.append("")
        else:
            lines.append("> 📝 今天暂无安排任务。可以：")
            lines.append("> - 使用「📐 任务模板」快速生成计划")
            lines.append("> - 复习一下备忘录里的知识点")
            lines.append("> - 提前准备明天的任务")
            lines.append("")

    # ===== 五、目标偏离分析 =====
    if deviated_goals:
        lines.append("---")
        lines.append("")
        lines.append(f"## ⚠️ 目标偏离预警（{len(deviated_goals)}个目标落后）")
        lines.append("")
        for g, dev in sorted(deviated_goals, key=lambda x: x[1]):
            gtitle = g.get('title', '未命名目标')
            progress = g.get('progress', 0)
            deadline = g.get('deadline', '未设置')
            lines.append(f"### 🚨 {gtitle}")
            lines.append(f"- 📊 进度：{progress}%")
            lines.append(f"- 📉 偏离度：**{dev}%**（落后预期 {abs(dev)}%）")
            lines.append(f"- ⏰ 截止：{deadline}")
            advice = generate_goal_catchup_advice(g, dev)
            lines.append(f"- 💡 {advice}")
            lines.append("")
    elif goals:
        lines.append("---")
        lines.append("")
        lines.append("## 🎯 目标状态正常")
        lines.append("")
        doing = [g for g in goals if g.get('status') in ('progress', 'in_progress')]
        if doing:
            lines.append(f"当前有 **{len(doing)}** 个目标正在进行中，暂无严重偏离。")
        else:
            lines.append("当前没有进行中的目标。建议选择一个目标开始推进。")
        lines.append("")

    # ===== 六、分类统计 =====
    if tag_stats:
        lines.append("---")
        lines.append("")
        lines.append("## 🏷️ 分类任务统计")
        lines.append("")
        lines.append("| 分类 | 总数 | 完成 | 逾期 | 完成率 |")
        lines.append("|------|------|------|------|--------|")
        for tag, st in sorted(tag_stats.items(), key=lambda x: x[1]['total'], reverse=True):
            rate = round(st['done'] / st['total'] * 100) if st['total'] else 0
            over_mark = f" ⚠️" if st['overdue'] > 0 else ""
            lines.append(f"| {tag} | {st['total']} | {st['done']} | {st['overdue']}{over_mark} | {rate}% |")
        lines.append("")

        # 分类失衡检查
        if len(tag_stats) >= 2:
            sorted_tags = sorted(tag_stats.values(), key=lambda x: x['total'], reverse=True)
            if sorted_tags[0]['total'] > sorted_tags[1]['total'] * 4:
                max_tag = [k for k, v in tag_stats.items() if v['total'] == sorted_tags[0]['total']][0]
                lines.append(f"> ⚖️ **分类失衡提醒**：「{max_tag}」类任务占比过高，建议适当平衡其他方向的学习时间。")
                lines.append("")

    # ===== 七、综合学习调整建议 =====
    lines.append("---")
    lines.append("")
    lines.append("## 🤖 综合学习调整建议")
    lines.append("")
    suggestions = generate_comprehensive_advice(
        overdue, urgent, soon, today_tasks, today_done,
        goals, deviated_goals, tag_stats, done_rate, total
    )
    for i, s in enumerate(suggestions, 1):
        icon, title, content = s
        lines.append(f"### {i}. {icon} {title}")
        lines.append("")
        lines.append(content)
        lines.append("")

    # ===== 八、本周建议计划 =====
    lines.append("---")
    lines.append("")
    lines.append("## 📅 本周行动建议")
    lines.append("")
    week_plan = generate_week_plan(overdue, urgent, soon, deviated_goals, tag_stats)
    for day_name, items in week_plan.items():
        lines.append(f"### {day_name}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


# ==================== 建议生成引擎 ====================

def generate_overdue_advice(overdue_tasks: list) -> str:
    """生成逾期任务处理建议"""
    count = len(overdue_tasks)
    high = [t for t in overdue_tasks if t.get('priority') == 'high']

    if count >= 5:
        advice = (
            f"你有 {count} 个逾期任务（其中 {len(high)} 个高优先），数量较多。"
            "建议：\n"
            "1. **立即清理**：删除已不再需要的任务，将合理任务延期\n"
            "2. **三三法则**：今天集中处理 3 个最重要的逾期任务\n"
            "3. **根本原因**：检查是否每日任务量过大，建议控制在 5-7 个\n"
            "4. **时间审计**：回顾本周时间分配，找出任务积压的原因"
        )
    elif count >= 3:
        advice = (
            f"有 {count} 个逾期任务需要处理。建议按优先级逐个击破，"
            "先处理高优先级任务。每完成一个逾期任务就划掉，积少成多。"
        )
    else:
        advice = (
            f"有 {count} 个逾期任务。少量逾期是正常的，关键是及时处理，"
            "不要让它们继续累积。建议今天就完成其中最重要的一个。"
        )
    return advice


def generate_goal_catchup_advice(goal: dict, deviation: float) -> str:
    """生成目标追赶建议"""
    progress = goal.get('progress', 0)
    deadline = goal.get('deadline', '')
    title = goal.get('title', '')

    try:
        d_deadline = datetime.strptime(str(deadline)[:10], '%Y-%m-%d')
        remain_days = max(0, (d_deadline - now_dt()).days)
    except (ValueError, TypeError):
        return "建议重新评估目标可行性，设定合理的截止日期。"

    if remain_days == 0:
        return "目标今天到期！集中所有精力完成剩余子目标。"

    need_per_day = round((100 - progress) / remain_days)
    sub_goals = goal.get('subGoals', [])
    undone_subs = [s for s in sub_goals if not s.get('done')]

    if need_per_day > 10:
        return (
            f"剩余 {remain_days} 天，每天需完成约 {need_per_day}% 进度，"
            f"压力较大。建议：重新评估是否可以延长截止日期，或将目标拆分为更小的短期目标。"
            f"当前还有 {len(undone_subs)} 个子目标未完成。"
        )
    else:
        return (
            f"剩余 {remain_days} 天，每天需完成约 {need_per_day}% 进度，完全可以追上。"
            f"建议将 {len(undone_subs)} 个未完成子目标分配到每天，"
            f"每天完成 {max(1, round(len(undone_subs)/remain_days))} 个。"
        )


def generate_comprehensive_advice(overdue, urgent, soon, today_tasks, today_done,
                                   goals, deviated_goals, tag_stats, done_rate, total) -> list:
    """生成综合学习调整建议（7类场景）"""
    suggestions = []

    # 1. 逾期预警
    if len(overdue) >= 3:
        suggestions.append((
            "🔴", "逾期任务紧急清理",
            "大量任务逾期会引发焦虑，形成恶性循环。\n\n"
            "**立即行动：**\n"
            "- 从逾期任务中选出 3 个最重要的，今天必须完成\n"
            "- 其他逾期任务：要么删除（不需要了），要么重设截止日期\n"
            "- 设置每日任务上限 5-7 个，防止再次积压"
        ))
    elif len(overdue) > 0:
        suggestions.append((
            "📋", f"处理 {len(overdue)} 个逾期任务",
            "少量逾期是正常的，关键是不让它们继续累积。\n\n"
            "- 优先处理高优先级逾期任务\n"
            "- 如果反复逾期同一类任务，可能是难度评估有误，考虑拆分"
        ))

    # 2. 今日进度
    if not today_done and today_tasks:
        hour = now_dt().hour
        if hour < 12:
            time_tip = "上午是精力最好的时段，现在开始效率最高！"
        elif hour < 18:
            time_tip = "下午容易犯困，建议先做一个简单任务热身。"
        else:
            time_tip = "晚上适合复习和回顾，但注意不要熬夜太晚。"
        suggestions.append((
            "💪", "今天还没有完成任务",
            f"今天有 {len(today_tasks)} 个任务等待完成。{time_tip}\n\n"
            "- **先做最简单的**：完成一个 5 分钟就能搞定的任务，建立动力\n"
            "- **再啃硬骨头**：趁热打铁处理高优先级任务\n"
            "- **番茄钟**：25 分钟专注 + 5 分钟休息，保持节奏"
        ))
    elif today_done and today_tasks:
        pct = len(today_done) / (len(today_tasks) + len(today_done)) * 100
        suggestions.append((
            "🏃", f"今日完成 {pct:.0f}%，继续加油",
            f"已完成 {len(today_done)} 个，还剩 {len(today_tasks)} 个。\n\n"
            "- 距离今日全部完成只差一步，冲刺一下！\n"
            "- 如果剩余任务太难，可以拆分为更小的步骤"
        ))

    # 3. 目标偏离
    if deviated_goals:
        worst = min(deviated_goals, key=lambda x: x[1])
        g, dev = worst
        suggestions.append((
            "🚨", f"「{g.get('title', '')[:15]}」严重偏离",
            f"当前落后预期 {abs(dev)}%，需要紧急调整。\n\n"
            "- 重新评估剩余子目标的可行性\n"
            "- 将大任务拆分为每日可完成的小目标\n"
            "- 增加每天的有效学习时间（利用碎片时间）\n"
            "- 每周日晚复盘，及时调整下周计划"
        ))

    # 4. 无进行中目标
    doing_goals = [g for g in goals if g.get('status') in ('progress', 'in_progress')]
    if not doing_goals and goals:
        suggestions.append((
            "🎯", "当前无进行中的目标",
            "有目标但没有正在推进的。\n\n"
            "- 选择一个未开始的目标，设置具体的启动日期\n"
            "- 使用「📐 任务模板」一键生成周计划\n"
            "- 设置每日最小行动量（如「每天背 10 个单词」）"
        ))

    # 5. 高优先级完成率
    high_tasks = [t for t in (overdue + urgent + soon) if t.get('priority') == 'high']
    all_high = [t for t in get_tasks_from_backup() if t.get('priority') == 'high']
    if len(all_high) > 3:
        all_high_done = [t for t in all_high if t.get('done')]
        h_rate = round(len(all_high_done) / len(all_high) * 100)
        if h_rate < 40:
            suggestions.append((
                "❗", f"高优先级完成率偏低（{h_rate}%）",
                "重要的事情没做完，可能是计划安排有问题。\n\n"
                "- 高优先级任务每天不超过 3 个\n"
                "- 任务是否过于笼统？拆分为具体可执行的步骤\n"
                "- 是否在回避困难任务？试试「先啃硬骨头」策略"
            ))

    # 6. 分类失衡
    if len(tag_stats) >= 2:
        sorted_tags = sorted(tag_stats.values(), key=lambda x: x['total'], reverse=True)
        if sorted_tags[0]['total'] > sorted_tags[1]['total'] * 4:
            max_tag = [k for k, v in tag_stats.items() if v['total'] == sorted_tags[0]['total']][0]
            suggestions.append((
                "⚖️", "任务分类可能失衡",
                f"「{max_tag}」类任务占比过高。\n\n"
                "- 检查是否需要平衡不同方向的学习时间\n"
                "- 适当的多样性有助于保持学习动力\n"
                "- 建议按目标方向均匀分配每周任务"
            ))

    # 7. 正向激励
    if not suggestions:
        suggestions.append((
            "🌟", "整体状况良好！",
            f"当前没有明显问题，已完成 {round(done_rate)}% 的任务。\n\n"
            "- 保持当前的学习节奏\n"
            "- 可以适当挑战更高难度的目标\n"
            "- 每周回顾一次统计页，持续优化"
        ))

    # 8. 补考专项建议
    bukao_tags = ['补考', '高代', '数分', '高等代数', '数学分析']
    bukao_tasks = [t for t in (overdue + urgent + soon) if any(bt in str(t.get('tag', '')) or bt in str(t.get('title', '')) for bt in bukao_tags)]
    if bukao_tasks:
        suggestions.append((
            "📚", "补考科目专项建议",
            f"检测到 {len(bukao_tasks)} 个补考相关任务需要关注。\n\n"
            "**补考复习策略：**\n"
            "- **高代 I**：重点突破多项式→行列式→矩阵→线性方程组四条主线\n"
            "- **数分 I**：重点掌握 ε-N/ε-δ 证明模板 + 中值定理应用\n"
            "- **每天交叉复习**：高代 1h + 数分 1h，比单科连续复习效率高\n"
            "- **真题优先**：考前 3 天至少做 2 套完整模拟\n"
            "- **错题本**：整理每次练习的错题，考前重点回顾"
        ))

    return suggestions


def generate_week_plan(overdue, urgent, soon, deviated_goals, tag_stats) -> dict:
    """生成本周行动建议计划"""
    plan = {}

    # 周一：清理逾期
    if overdue:
        plan["📅 周一 · 逾期清理日"] = [
            f"集中处理 {min(len(overdue), 3)} 个最重要的逾期任务",
            "删除不再需要的过期任务，减少心理负担",
            "为剩余逾期任务重新设置合理的截止日期",
        ]

    # 周二：紧急任务日
    if urgent or soon:
        count = len(urgent) + len(soon)
        plan["⚡ 周二 · 临期攻坚日"] = [
            f"完成 {min(count, 4)} 个临期任务（优先高优先级）",
            "使用番茄钟提高专注度（25min 工作 + 5min 休息）",
            "每完成一个任务打勾，保持成就感",
        ]

    # 周三：目标调整
    if deviated_goals:
        plan["🎯 周三 · 目标校准日"] = [
            f"审查 {len(deviated_goals)} 个偏离目标的进展",
            "重新评估剩余子目标，删除不可行的，拆分太大的",
            "为每个偏离目标制定本周追赶计划",
        ]

    # 周四：短板突破
    plan["📚 周四 · 薄弱突破日"] = [
        "找出最近错误率最高的知识点/题型",
        "针对性练习 2 小时，整理错题笔记",
        "如果涉及补考，集中攻克最薄弱的章节",
    ]

    # 周五：综合巩固
    plan["🔄 周五 · 综合巩固日"] = [
        "回顾本周所有已完成任务，总结方法论",
        "做 1 套综合模拟/自测题",
        "整理本周学习笔记，归档到备忘录",
    ]

    # 周六：模拟测试
    plan["📝 周六 · 模拟测试日"] = [
        "做 1-2 套完整真题/模拟题（限时）",
        "对照答案评分，标记薄弱环节",
        "根据测试结果调整下周学习重点",
    ]

    # 周日：复盘规划
    plan["🗓️ 周日 · 复盘规划日"] = [
        "复盘本周：完成了多少任务？哪些没完成？为什么？",
        "规划下周：列出下周必须完成的 5-7 个核心任务",
        "更新目标进度，检查是否需要调整策略",
        "适当休息，保持学习与生活的平衡",
    ]

    return plan


# ==================== 全局缓存（供建议引擎调用） ====================
_backup_data_cache = None

def get_tasks_from_backup() -> list:
    """获取全局缓存的完整任务列表（供建议引擎使用）"""
    global _backup_data_cache
    if _backup_data_cache:
        return get_tasks(_backup_data_cache)
    return []


# ==================== 入口 ====================

def main():
    # 修复 Windows 控制台编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print("用法: python task_reminder.py <备份文件.json> [--output report.md] [--days 3]")
        print("")
        print("说明:")
        print("  备份文件  助学星「设置→数据备份」导出的 .json 文件")
        print("  --output  输出报告路径（默认输出到控制台）")
        print("  --days    临期阈值天数（默认 3 天）")
        sys.exit(1)

    filepath = sys.argv[1]
    output_path = None
    urgent_days = 3

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--days' and i + 1 < len(sys.argv):
            urgent_days = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    if not os.path.exists(filepath):
        print(f"❌ 文件不存在：{filepath}")
        sys.exit(1)

    # 加载数据
    data = load_backup(filepath)
    global _backup_data_cache
    _backup_data_cache = data

    # 生成报告
    report = build_report(data, urgent_days)

    # 输出
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 报告已保存到：{output_path}")
    else:
        print(report)


if __name__ == '__main__':
    main()
