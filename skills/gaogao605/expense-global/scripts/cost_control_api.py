#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能费控技能 - 核心API
"""

import json
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class CostControlError(Exception):
    """费控异常"""
    pass


class BudgetType(Enum):
    """预算类型"""
    DEPARTMENT = "department"
    PROJECT = "project"
    COMPANY = "company"


class BudgetPeriod(Enum):
    """预算周期"""
    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"


class StandardType(Enum):
    """标准类型"""
    TRAVEL = "travel"
    DAILY = "daily"
    SPECIAL = "special"


class AlertType(Enum):
    """预警类型"""
    BUDGET_DEPLETION = "budget_depletion"
    OVERRUN = "overrun"
    ANOMALY = "anomaly"
    APPROVAL_TIMEOUT = "approval_timeout"


# 城市等级
CITY_TIERS = {
    "tier1": ["北京", "上海", "广州", "深圳"],
    "tier2": ["杭州", "南京", "成都", "武汉", "西安", "重庆", "天津", "苏州", "青岛", "长沙"]
}

# 费用标准配置
EXPENSE_STANDARDS = {
    "travel": {
        "flight": {
            "executive": {"class": "商务舱/头等舱", "limit": None},
            "manager": {"class": "经济舱", "limit": None},
            "staff": {"class": "经济舱", "limit": None}
        },
        "train": {
            "executive": {"class": "一等座/软卧", "limit": None},
            "manager": {"class": "一等座/软卧", "limit": None},
            "staff": {"class": "二等座/硬卧", "limit": None}
        },
        "hotel": {
            "executive": {"tier1": 1000, "tier2": 800, "other": 600},
            "manager": {"tier1": 800, "tier2": 600, "other": 450},
            "staff": {"tier1": 500, "tier2": 400, "other": 350}
        },
        "meal": {
            "executive": {"tier1": 300, "tier2": 250, "other": 200},
            "manager": {"tier1": 200, "tier2": 180, "other": 150},
            "staff": {"tier1": 150, "tier2": 130, "other": 100}
        },
        "transport": {
            "executive": {"limit": None, "type": "实报实销"},
            "manager": {"limit": 200, "type": "限额"},
            "staff": {"limit": 100, "type": "限额"}
        }
    },
    "daily": {
        "communication": {
            "executive": 500,
            "manager": 300,
            "staff": 200
        },
        "office": {
            "executive": 200,
            "manager": 150,
            "staff": 100
        },
        "entertainment": {
            "executive": 2000,
            "manager": 1000,
            "staff": 500
        },
        "training": {
            "executive": 10000,
            "manager": 5000,
            "staff": 2000
        }
    }
}


@dataclass
class BudgetCategory:
    """预算分类"""
    category: str
    category_name: str
    budget: float
    used: float
    remaining: float


@dataclass
class Budget:
    """预算"""
    budget_id: str
    budget_name: str
    budget_type: str
    budget_period: str
    start_date: str
    end_date: str
    total_amount: float
    used_amount: float
    remaining_amount: float
    usage_rate: float
    owner_id: str
    owner_name: str
    owner_type: str
    categories: List[BudgetCategory]
    monthly_breakdown: List[Dict]
    status: str
    create_time: str

    def to_dict(self) -> Dict:
        return {
            "budget_id": self.budget_id,
            "budget_name": self.budget_name,
            "budget_type": self.budget_type,
            "budget_period": self.budget_period,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_amount": self.total_amount,
            "used_amount": self.used_amount,
            "remaining_amount": self.remaining_amount,
            "usage_rate": self.usage_rate,
            "owner": {
                "type": self.owner_type,
                "id": self.owner_id,
                "name": self.owner_name
            },
            "category_breakdown": {
                cat.category: {
                    "budget": cat.budget,
                    "used": cat.used,
                    "remaining": cat.remaining
                } for cat in self.categories
            },
            "monthly_breakdown": self.monthly_breakdown,
            "status": self.status,
            "create_time": self.create_time
        }


@dataclass
class ExpenseStandard:
    """费用标准"""
    standard_id: str
    standard_type: str
    expense_category: str
    level: str
    city_tier: Optional[str]
    limit_amount: Optional[float]
    limit_type: str
    currency: str
    effective_date: str
    expiry_date: str
    description: str

    def to_dict(self) -> Dict:
        result = {
            "standard_id": self.standard_id,
            "standard_type": self.standard_type,
            "expense_category": self.expense_category,
            "level": self.level,
            "limit_type": self.limit_type,
            "currency": self.currency,
            "effective_date": self.effective_date,
            "expiry_date": self.expiry_date,
            "description": self.description
        }
        if self.city_tier:
            result["city_tier"] = self.city_tier
        if self.limit_amount:
            result["limit_amount"] = self.limit_amount
        return result


@dataclass
class Alert:
    """预警"""
    alert_id: str
    alert_type: str
    alert_type_name: str
    title: str
    description: str
    severity: str
    related_budget: Optional[str]
    related_department: Optional[str]
    threshold: float
    current_value: float
    status: str
    create_time: str
    notify_users: List[str]

    def to_dict(self) -> Dict:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "alert_type_name": self.alert_type_name,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "related_budget": self.related_budget,
            "related_department": self.related_department,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "status": self.status,
            "create_time": self.create_time,
            "notify_users": self.notify_users
        }


class CostControlApi:
    """费控API"""
    
    def __init__(self):
        self.city_tiers = CITY_TIERS
        self.expense_standards = EXPENSE_STANDARDS
        self.budgets = {}
        self.standards = {}
        self.alerts = {}
    
    def create_budget(
        self,
        budget_type: str,
        budget_name: str,
        budget_period: str,
        start_date: str,
        end_date: str,
        total_amount: float,
        owner_id: str,
        owner_name: str,
        owner_type: str,
        category_breakdown: Dict = None
    ) -> Dict:
        """
        创建预算
        """
        # 验证预算类型
        if budget_type not in ["department", "project", "company"]:
            return {
                "code": 400,
                "msg": f"不支持的预算类型: {budget_type}",
                "data": None
            }
        
        # 验证预算周期
        if budget_period not in ["year", "quarter", "month"]:
            return {
                "code": 400,
                "msg": f"不支持的预算周期: {budget_period}",
                "data": None
            }
        
        # 生成预算ID
        budget_id = f"BUD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建分类明细
        categories = []
        default_categories = {
            "travel": {"name": "差旅费", "ratio": 0.4},
            "entertainment": {"name": "招待费", "ratio": 0.2},
            "office": {"name": "办公费", "ratio": 0.1},
            "communication": {"name": "通讯费", "ratio": 0.06},
            "training": {"name": "培训费", "ratio": 0.1},
            "other": {"name": "其他", "ratio": 0.14}
        }
        
        for cat_key, cat_info in default_categories.items():
            cat_budget = category_breakdown.get(cat_key, total_amount * cat_info["ratio"]) if category_breakdown else total_amount * cat_info["ratio"]
            categories.append(BudgetCategory(
                category=cat_key,
                category_name=cat_info["name"],
                budget=cat_budget,
                used=0,
                remaining=cat_budget
            ))
        
        # 创建月度分解
        monthly_breakdown = []
        if budget_period == "year":
            monthly_budget = total_amount / 12
            for i in range(1, 13):
                month = f"{start_date[:4]}-{i:02d}"
                monthly_breakdown.append({
                    "month": month,
                    "budget": round(monthly_budget, 2),
                    "used": 0,
                    "variance": round(monthly_budget, 2)
                })
        
        # 创建预算
        budget = Budget(
            budget_id=budget_id,
            budget_name=budget_name,
            budget_type=budget_type,
            budget_period=budget_period,
            start_date=start_date,
            end_date=end_date,
            total_amount=total_amount,
            used_amount=0,
            remaining_amount=total_amount,
            usage_rate=0.0,
            owner_id=owner_id,
            owner_name=owner_name,
            owner_type=owner_type,
            categories=categories,
            monthly_breakdown=monthly_breakdown,
            status="active",
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 保存预算
        self.budgets[budget_id] = budget
        
        return {
            "code": 0,
            "msg": "success",
            "data": budget.to_dict()
        }
    
    def get_budget_detail(self, budget_id: str) -> Dict:
        """
        获取预算详情
        """
        budget = self.budgets.get(budget_id)
        if not budget:
            return {
                "code": 404,
                "msg": f"预算不存在: {budget_id}",
                "data": None
            }
        
        return {
            "code": 0,
            "msg": "success",
            "data": budget.to_dict()
        }
    
    def get_budget_list(
        self,
        budget_type: str = None,
        status: str = None,
        period: str = None
    ) -> Dict:
        """
        获取预算列表
        """
        filtered_budgets = []
        
        for budget in self.budgets.values():
            if budget_type and budget.budget_type != budget_type:
                continue
            if status and budget.status != status:
                continue
            if period and budget.budget_period != period:
                continue
            filtered_budgets.append(budget.to_dict())
        
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "total": len(filtered_budgets),
                "budgets": filtered_budgets
            }
        }
    
    def get_expense_standard(
        self,
        standard_type: str,
        expense_category: str,
        level: str,
        city_tier: str = None
    ) -> Dict:
        """
        获取费用标准
        """
        standards_data = []
        
        if standard_type == "travel":
            if expense_category == "hotel":
                # 住宿标准
                for lvl in ["executive", "manager", "staff"]:
                    if level and level != lvl:
                        continue
                    for tier in ["tier1", "tier2", "other"]:
                        if city_tier and city_tier != tier:
                            continue
                        limit = self.expense_standards["travel"]["hotel"][lvl][tier]
                        standards_data.append({
                            "level": lvl,
                            "city_tier": tier,
                            "limit_amount": limit,
                            "limit_type": "per_day"
                        })
            elif expense_category == "meal":
                # 餐饮标准
                for lvl in ["executive", "manager", "staff"]:
                    if level and level != lvl:
                        continue
                    for tier in ["tier1", "tier2", "other"]:
                        if city_tier and city_tier != tier:
                            continue
                        limit = self.expense_standards["travel"]["meal"][lvl][tier]
                        standards_data.append({
                            "level": lvl,
                            "city_tier": tier,
                            "limit_amount": limit,
                            "limit_type": "per_day"
                        })
            elif expense_category == "flight":
                # 飞机标准
                for lvl in ["executive", "manager", "staff"]:
                    if level and level != lvl:
                        continue
                    config = self.expense_standards["travel"]["flight"][lvl]
                    standards_data.append({
                        "level": lvl,
                        "class": config["class"],
                        "limit_amount": config["limit"]
                    })
            elif expense_category == "transport":
                # 市内交通
                for lvl in ["executive", "manager", "staff"]:
                    if level and level != lvl:
                        continue
                    config = self.expense_standards["travel"]["transport"][lvl]
                    standards_data.append({
                        "level": lvl,
                        "limit_amount": config["limit"],
                        "limit_type": "per_day",
                        "type": config["type"]
                    })
        
        elif standard_type == "daily":
            # 日常费用标准
            if expense_category in self.expense_standards["daily"]:
                for lvl in ["executive", "manager", "staff"]:
                    if level and level != lvl:
                        continue
                    limit = self.expense_standards["daily"][expense_category][lvl]
                    standards_data.append({
                        "level": lvl,
                        "limit_amount": limit,
                        "limit_type": "per_month"
                    })
        
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "standard_type": standard_type,
                "expense_category": expense_category,
                "standards": standards_data
            }
        }
    
    def check_compliance(
        self,
        expense_type: str,
        amount: float,
        level: str,
        city_tier: str = None,
        budget_id: str = None
    ) -> Dict:
        """
        合规检查
        """
        result = {
            "compliant": True,
            "within_standard": True,
            "within_budget": True,
            "warnings": [],
            "violations": []
        }
        
        # 检查费用标准
        if expense_type == "hotel" and city_tier:
            standard_limit = self.expense_standards["travel"]["hotel"][level][city_tier]
            if amount > standard_limit:
                result["within_standard"] = False
                result["compliant"] = False
                result["violations"].append({
                    "type": "standard_exceeded",
                    "message": f"住宿费¥{amount}超出标准¥{standard_limit}",
                    "standard": standard_limit,
                    "actual": amount
                })
        
        # 检查预算
        if budget_id and budget_id in self.budgets:
            budget = self.budgets[budget_id]
            if budget.remaining_amount < amount:
                result["within_budget"] = False
                result["warnings"].append({
                    "type": "budget_insufficient",
                    "message": f"预算余额不足，剩余¥{budget.remaining_amount}"
                })
        
        return {
            "code": 0,
            "msg": "success",
            "data": result
        }
    
    def create_alert(
        self,
        alert_type: str,
        title: str,
        description: str,
        severity: str,
        threshold: float,
        current_value: float,
        related_budget: str = None,
        related_department: str = None,
        notify_users: List[str] = None
    ) -> Dict:
        """
        创建预警
        """
        alert_id = f"ALT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        alert_type_names = {
            "budget_depletion": "预算耗尽预警",
            "overrun": "超标预警",
            "anomaly": "异常预警",
            "approval_timeout": "审批超时预警"
        }
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            alert_type_name=alert_type_names.get(alert_type, alert_type),
            title=title,
            description=description,
            severity=severity,
            related_budget=related_budget,
            related_department=related_department,
            threshold=threshold,
            current_value=current_value,
            status="active",
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            notify_users=notify_users or []
        )
        
        self.alerts[alert_id] = alert
        
        return {
            "code": 0,
            "msg": "success",
            "data": alert.to_dict()
        }
    
    def get_alerts(
        self,
        status: str = None,
        alert_type: str = None,
        severity: str = None
    ) -> Dict:
        """
        获取预警列表
        """
        filtered_alerts = []
        
        for alert in self.alerts.values():
            if status and alert.status != status:
                continue
            if alert_type and alert.alert_type != alert_type:
                continue
            if severity and alert.severity != severity:
                continue
            filtered_alerts.append(alert.to_dict())
        
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "total": len(filtered_alerts),
                "alerts": filtered_alerts
            }
        }
    
    def generate_analysis_report(
        self,
        start_date: str,
        end_date: str,
        dimensions: List[str] = None
    ) -> Dict:
        """
        生成分析报告
        """
        # 模拟数据
        total_expense = 1250000.00
        total_budget = 1500000.00
        
        report = {
            "report_id": f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "report_name": f"{start_date}至{end_date}费用分析报告",
            "report_period": {
                "start": start_date,
                "end": end_date
            },
            "summary": {
                "total_expense": total_expense,
                "total_budget": total_budget,
                "budget_usage": round(total_expense / total_budget * 100, 2),
                "yoy_growth": 15.2,
                "mom_growth": 5.8
            },
            "by_department": [
                {
                    "department": "销售部",
                    "expense": 450000.00,
                    "budget": 500000.00,
                    "usage_rate": 90.0,
                    "rank": 1
                },
                {
                    "department": "技术部",
                    "expense": 380000.00,
                    "budget": 500000.00,
                    "usage_rate": 76.0,
                    "rank": 2
                },
                {
                    "department": "市场部",
                    "expense": 280000.00,
                    "budget": 400000.00,
                    "usage_rate": 70.0,
                    "rank": 3
                },
                {
                    "department": "行政部",
                    "expense": 140000.00,
                    "budget": 250000.00,
                    "usage_rate": 56.0,
                    "rank": 4
                }
            ],
            "by_category": [
                {
                    "category": "差旅费",
                    "amount": 500000.00,
                    "percentage": 40.0,
                    "yoy_change": 20.5
                },
                {
                    "category": "招待费",
                    "amount": 300000.00,
                    "percentage": 24.0,
                    "yoy_change": 8.2
                },
                {
                    "category": "办公费",
                    "amount": 200000.00,
                    "percentage": 16.0,
                    "yoy_change": -5.3
                },
                {
                    "category": "通讯费",
                    "amount": 150000.00,
                    "percentage": 12.0,
                    "yoy_change": 2.1
                },
                {
                    "category": "培训费",
                    "amount": 100000.00,
                    "percentage": 8.0,
                    "yoy_change": 15.0
                }
            ],
            "overrun_analysis": {
                "overrun_count": 3,
                "overrun_amount": 25000.00,
                "top_overruns": [
                    {
                        "department": "销售部",
                        "category": "招待费",
                        "overrun_amount": 15000.00
                    }
                ]
            },
            "anomalies": [
                {
                    "type": "sudden_increase",
                    "description": "3月招待费较上月增长200%",
                    "severity": "high"
                }
            ],
            "recommendations": [
                {
                    "type": "cost_optimization",
                    "title": "优化差旅预订",
                    "description": "建议提前7天预订机票，可节省约15%费用",
                    "potential_saving": 75000.00
                },
                {
                    "type": "cost_optimization",
                    "title": "控制招待费用",
                    "description": "3月招待费异常增长，建议制定更严格的审批流程",
                    "potential_saving": 50000.00
                }
            ]
        }
        
        return {
            "code": 0,
            "msg": "success",
            "data": report
        }
    
    def format_budget(self, result: Dict) -> str:
        """格式化预算信息"""
        data = result.get("data", {})
        
        if not data:
            return "预算信息获取失败"
        
        lines = []
        lines.append(f"📊 {data.get('budget_name', '预算概览')}")
        lines.append("")
        lines.append("=" * 40)
        lines.append("")
        
        # 预算总览
        lines.append("💰 预算总览")
        lines.append("━" * 40)
        total = data.get('total_amount', 0)
        used = data.get('used_amount', 0)
        remaining = data.get('remaining_amount', 0)
        usage_rate = data.get('usage_rate', 0)
        
        lines.append(f"预算总额：        ¥{total:,.2f}")
        lines.append(f"已使用：          ¥{used:,.2f}  {'█' * int(usage_rate/10)}{'░' * (10-int(usage_rate/10))}  {usage_rate:.0f}%")
        lines.append(f"剩余预算：        ¥{remaining:,.2f}")
        lines.append("")
        
        status = data.get('status', '')
        status_icon = "🟢" if status == "active" else "⚪"
        lines.append(f"状态：{status_icon} 执行正常")
        lines.append("")
        
        # 分类预算
        categories = data.get('category_breakdown', {})
        if categories:
            lines.append("📈 分类预算执行情况")
            lines.append("━" * 40)
            
            category_icons = {
                "travel": "🚗",
                "entertainment": "🍽️",
                "office": "📝",
                "communication": "📱",
                "training": "🎓",
                "other": "📦"
            }
            
            for cat_key, cat_data in categories.items():
                icon = category_icons.get(cat_key, "📋")
                cat_name = cat_key
                budget = cat_data.get('budget', 0)
                used = cat_data.get('used', 0)
                cat_usage = used / budget * 100 if budget > 0 else 0
                
                status = "🟢"
                if cat_usage > 90:
                    status = "🔴"
                elif cat_usage > 75:
                    status = "🟡"
                
                lines.append(f"{icon} {cat_name:8}  ¥{budget:>8,.0f}  ¥{used:>8,.0f}  {'█' * int(cat_usage/10):10}  {cat_usage:>5.0f}%  {status}")
            
            lines.append("")
        
        # 月度趋势
        monthly = data.get('monthly_breakdown', [])
        if monthly:
            lines.append("📅 月度执行趋势")
            lines.append("━" * 40)
            
            for month_data in monthly[:6]:  # 只显示前6个月
                month = month_data.get('month', '')
                budget = month_data.get('budget', 0)
                used = month_data.get('used', 0)
                usage = used / budget * 100 if budget > 0 else 0
                
                status = "🟢"
                if usage > 100:
                    status = "🔴 超标"
                elif usage > 90:
                    status = "🟡 接近"
                
                lines.append(f"{month}  ¥{used:>8,.0f}  {'█' * int(usage/10):10}  {usage:>5.0f}%  {status}")
            
            lines.append("")
        
        lines.append("=" * 40)
        
        return "\n".join(lines)
    
    def format_standard(self, result: Dict) -> str:
        """格式化费用标准"""
        data = result.get("data", {})
        
        if not data:
            return "费用标准获取失败"
        
        standard_type = data.get('standard_type', '')
        category = data.get('expense_category', '')
        standards = data.get('standards', [])
        
        lines = []
        
        if category == "hotel":
            lines.append("📋 住宿费用标准")
        elif category == "meal":
            lines.append("📋 餐饮补贴标准")
        elif category == "flight":
            lines.append("📋 飞机舱位标准")
        elif category == "transport":
            lines.append("📋 市内交通标准")
        else:
            lines.append(f"📋 {category}费用标准")
        
        lines.append("")
        lines.append("=" * 40)
        lines.append("")
        
        level_names = {
            "executive": "高管",
            "manager": "中层",
            "staff": "普通员工"
        }
        
        tier_names = {
            "tier1": "一线城市",
            "tier2": "新一线城市",
            "other": "其他城市"
        }
        
        if category == "flight":
            lines.append("✈️ 交通标准")
            lines.append("━" * 40)
            for std in standards:
                level = level_names.get(std.get('level'), std.get('level'))
                class_type = std.get('class', '')
                lines.append(f"{level}：{class_type}")
        
        elif category in ["hotel", "meal"]:
            if category == "hotel":
                lines.append("🏨 住宿标准")
            else:
                lines.append("🍽️ 餐饮补贴")
            
            lines.append("━" * 40)
            
            for std in standards:
                level = level_names.get(std.get('level'), std.get('level'))
                tier = tier_names.get(std.get('city_tier'), std.get('city_tier'))
                limit = std.get('limit_amount', 0)
                lines.append(f"{level} - {tier}：¥{limit}/晚" if category == "hotel" else f"{level} - {tier}：¥{limit}/天")
        
        elif category == "transport":
            lines.append("🚕 市内交通标准")
            lines.append("━" * 40)
            for std in standards:
                level = level_names.get(std.get('level'), std.get('level'))
                limit = std.get('limit_amount')
                type_desc = std.get('type', '')
                if limit:
                    lines.append(f"{level}：¥{limit}/天")
                else:
                    lines.append(f"{level}：实报实销")
        
        lines.append("")
        lines.append("=" * 40)
        
        return "\n".join(lines)
    
    def format_analysis_report(self, result: Dict) -> str:
        """格式化分析报告"""
        data = result.get("data", {})
        
        if not data:
            return "分析报告获取失败"
        
        lines = []
        lines.append(f"📈 {data.get('report_name', '费用分析报告')}")
        lines.append("")
        lines.append("=" * 40)
        lines.append("")
        
        # 总体概况
        summary = data.get('summary', {})
        lines.append("💰 总体概况")
        lines.append("━" * 40)
        lines.append(f"总费用：    ¥{summary.get('total_expense', 0):,.2f}")
        lines.append(f"预算：      ¥{summary.get('total_budget', 0):,.2f}")
        lines.append(f"执行率：    {summary.get('budget_usage', 0):.2f}%")
        lines.append("")
        lines.append(f"同比：      {summary.get('yoy_growth', 0):+.1f}% {'↑' if summary.get('yoy_growth', 0) > 0 else '↓'}")
        lines.append(f"环比：      {summary.get('mom_growth', 0):+.1f}% {'↑' if summary.get('mom_growth', 0) > 0 else '↓'}")
        lines.append("")
        
        # 部门排行
        departments = data.get('by_department', [])
        if departments:
            lines.append("🏢 部门费用排行")
            lines.append("━" * 40)
            
            for dept in departments:
                name = dept.get('department', '')
                expense = dept.get('expense', 0)
                budget = dept.get('budget', 0)
                usage = dept.get('usage_rate', 0)
                rank = dept.get('rank', 0)
                
                status = "🟢"
                if usage > 90:
                    status = "🔴"
                elif usage > 75:
                    status = "🟡"
                
                lines.append(f"{rank}. {name:8}  ¥{expense:>10,.0f}  {'█' * int(usage/10):12}  {usage:>5.0f}%  {status}")
            
            lines.append("")
        
        # 费用结构
        categories = data.get('by_category', [])
        if categories:
            lines.append("📊 费用结构分析")
            lines.append("━" * 40)
            
            category_icons = {
                "差旅费": "🚗",
                "招待费": "🍽️",
                "办公费": "💻",
                "通讯费": "📱",
                "培训费": "🎓"
            }
            
            for cat in categories:
                name = cat.get('category', '')
                amount = cat.get('amount', 0)
                pct = cat.get('percentage', 0)
                change = cat.get('yoy_change', 0)
                icon = category_icons.get(name, "📋")
                
                lines.append(f"{icon} {name:8}  ¥{amount:>10,.0f}  {'█' * int(pct/2):10}  {pct:>5.0f}%  {change:>+6.1f}%")
            
            lines.append("")
        
        # 异常检测
        anomalies = data.get('anomalies', [])
        if anomalies:
            lines.append("⚠️ 异常检测")
            lines.append("━" * 40)
            
            for anomaly in anomalies:
                severity = anomaly.get('severity', '')
                desc = anomaly.get('description', '')
                
                icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                lines.append(f"{icon} {desc}")
            
            lines.append("")
        
        # 优化建议
        recommendations = data.get('recommendations', [])
        if recommendations:
            lines.append("💡 优化建议")
            lines.append("━" * 40)
            
            for i, rec in enumerate(recommendations, 1):
                title = rec.get('title', '')
                desc = rec.get('description', '')
                saving = rec.get('potential_saving', 0)
                
                lines.append(f"{i}. {title}")
                lines.append(f"   {desc}")
                if saving:
                    lines.append(f"   预计可节省：¥{saving:,.2f}")
                lines.append("")
        
        lines.append("=" * 40)
        
        return "\n".join(lines)


# 测试
if __name__ == "__main__":
    api = CostControlApi()
    
    # 测试创建预算
    print("=" * 60)
    print("测试创建预算")
    print("=" * 60)
    result = api.create_budget(
        budget_type="department",
        budget_name="2026年销售部预算",
        budget_period="year",
        start_date="2026-01-01",
        end_date="2026-12-31",
        total_amount=500000,
        owner_id="DEPT001",
        owner_name="销售部",
        owner_type="department"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 格式化展示
    print("\n" + "=" * 60)
    print("格式化预算：")
    print("=" * 60)
    print(api.format_budget(result))
    
    # 测试获取费用标准
    print("\n" + "=" * 60)
    print("测试获取费用标准")
    print("=" * 60)
    result = api.get_expense_standard(
        standard_type="travel",
        expense_category="hotel",
        level="manager"
    )
    print(api.format_standard(result))
    
    # 测试生成分析报告
    print("\n" + "=" * 60)
    print("测试生成分析报告")
    print("=" * 60)
    result = api.generate_analysis_report(
        start_date="2026-01-01",
        end_date="2026-03-31"
    )
    print(api.format_analysis_report(result))
