#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能费控技能 - OpenAI适配器
"""

import json
import sys
from typing import Dict, Any

sys.path.append('.')
from cost_control_api import CostControlApi, CostControlError

# 初始化API实例
cost_control_api = CostControlApi()

# OpenAI函数描述
COST_CONTROL_FUNCTIONS = [
    {
        "name": "create_budget",
        "description": "创建预算",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_type": {
                    "type": "string",
                    "description": "预算类型：department/project/company"
                },
                "budget_name": {
                    "type": "string",
                    "description": "预算名称"
                },
                "budget_period": {
                    "type": "string",
                    "description": "预算周期：year/quarter/month"
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式yyyy-MM-dd"
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式yyyy-MM-dd"
                },
                "total_amount": {
                    "type": "number",
                    "description": "预算总额"
                },
                "owner_id": {
                    "type": "string",
                    "description": "负责人ID"
                },
                "owner_name": {
                    "type": "string",
                    "description": "负责人名称"
                },
                "owner_type": {
                    "type": "string",
                    "description": "负责人类型：department/user"
                }
            },
            "required": ["budget_type", "budget_name", "budget_period", "start_date", "end_date", "total_amount", "owner_id", "owner_name", "owner_type"]
        }
    },
    {
        "name": "get_budget_detail",
        "description": "查询预算详情",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_id": {
                    "type": "string",
                    "description": "预算ID"
                }
            },
            "required": ["budget_id"]
        }
    },
    {
        "name": "get_budget_list",
        "description": "查询预算列表",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_type": {
                    "type": "string",
                    "description": "预算类型过滤"
                },
                "status": {
                    "type": "string",
                    "description": "状态过滤"
                },
                "period": {
                    "type": "string",
                    "description": "周期过滤"
                }
            }
        }
    },
    {
        "name": "get_expense_standard",
        "description": "查询费用标准",
        "parameters": {
            "type": "object",
            "properties": {
                "standard_type": {
                    "type": "string",
                    "description": "标准类型：travel/daily"
                },
                "expense_category": {
                    "type": "string",
                    "description": "费用类别：hotel/meal/flight/transport"
                },
                "level": {
                    "type": "string",
                    "description": "职级：executive/manager/staff"
                },
                "city_tier": {
                    "type": "string",
                    "description": "城市等级：tier1/tier2/other"
                }
            },
            "required": ["standard_type", "expense_category"]
        }
    },
    {
        "name": "check_compliance",
        "description": "合规检查",
        "parameters": {
            "type": "object",
            "properties": {
                "expense_type": {
                    "type": "string",
                    "description": "费用类型"
                },
                "amount": {
                    "type": "number",
                    "description": "金额"
                },
                "level": {
                    "type": "string",
                    "description": "职级"
                },
                "city_tier": {
                    "type": "string",
                    "description": "城市等级"
                },
                "budget_id": {
                    "type": "string",
                    "description": "预算ID"
                }
            },
            "required": ["expense_type", "amount", "level"]
        }
    },
    {
        "name": "create_alert",
        "description": "创建预警",
        "parameters": {
            "type": "object",
            "properties": {
                "alert_type": {
                    "type": "string",
                    "description": "预警类型：budget_depletion/overrun/anomaly"
                },
                "title": {
                    "type": "string",
                    "description": "预警标题"
                },
                "description": {
                    "type": "string",
                    "description": "预警描述"
                },
                "severity": {
                    "type": "string",
                    "description": "严重程度：high/medium/low"
                },
                "threshold": {
                    "type": "number",
                    "description": "预警阈值"
                },
                "current_value": {
                    "type": "number",
                    "description": "当前值"
                },
                "related_budget": {
                    "type": "string",
                    "description": "关联预算ID"
                },
                "related_department": {
                    "type": "string",
                    "description": "关联部门"
                },
                "notify_users": {
                    "type": "array",
                    "description": "通知用户列表",
                    "items": {"type": "string"}
                }
            },
            "required": ["alert_type", "title", "description", "severity", "threshold", "current_value"]
        }
    },
    {
        "name": "get_alerts",
        "description": "查询预警列表",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "状态过滤"
                },
                "alert_type": {
                    "type": "string",
                    "description": "类型过滤"
                },
                "severity": {
                    "type": "string",
                    "description": "严重程度过滤"
                }
            }
        }
    },
    {
        "name": "generate_analysis_report",
        "description": "生成费用分析报告",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "开始日期"
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期"
                },
                "dimensions": {
                    "type": "array",
                    "description": "分析维度",
                    "items": {"type": "string"}
                }
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "format_budget",
        "description": "格式化预算信息",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "description": "预算查询结果"
                }
            },
            "required": ["result"]
        }
    },
    {
        "name": "format_standard",
        "description": "格式化费用标准",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "description": "费用标准查询结果"
                }
            },
            "required": ["result"]
        }
    },
    {
        "name": "format_analysis_report",
        "description": "格式化分析报告",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "description": "分析报告结果"
                }
            },
            "required": ["result"]
        }
    }
]


class OpenaiCostControlAdapter:
    """OpenAI费控适配器"""
    
    @staticmethod
    def call_function(function_name: str, function_arguments: str) -> Dict:
        """
        调用费控函数
        
        :param function_name: 函数名称
        :param function_arguments: 函数参数（JSON字符串）
        :return: 调用结果
        """
        try:
            args = json.loads(function_arguments)
            
            function_map = {
                "create_budget": lambda **kwargs: cost_control_api.create_budget(
                    budget_type=kwargs["budget_type"],
                    budget_name=kwargs["budget_name"],
                    budget_period=kwargs["budget_period"],
                    start_date=kwargs["start_date"],
                    end_date=kwargs["end_date"],
                    total_amount=kwargs["total_amount"],
                    owner_id=kwargs["owner_id"],
                    owner_name=kwargs["owner_name"],
                    owner_type=kwargs["owner_type"]
                ),
                "get_budget_detail": lambda **kwargs: cost_control_api.get_budget_detail(
                    budget_id=kwargs["budget_id"]
                ),
                "get_budget_list": lambda **kwargs: cost_control_api.get_budget_list(
                    budget_type=kwargs.get("budget_type"),
                    status=kwargs.get("status"),
                    period=kwargs.get("period")
                ),
                "get_expense_standard": lambda **kwargs: cost_control_api.get_expense_standard(
                    standard_type=kwargs["standard_type"],
                    expense_category=kwargs["expense_category"],
                    level=kwargs.get("level"),
                    city_tier=kwargs.get("city_tier")
                ),
                "check_compliance": lambda **kwargs: cost_control_api.check_compliance(
                    expense_type=kwargs["expense_type"],
                    amount=kwargs["amount"],
                    level=kwargs["level"],
                    city_tier=kwargs.get("city_tier"),
                    budget_id=kwargs.get("budget_id")
                ),
                "create_alert": lambda **kwargs: cost_control_api.create_alert(
                    alert_type=kwargs["alert_type"],
                    title=kwargs["title"],
                    description=kwargs["description"],
                    severity=kwargs["severity"],
                    threshold=kwargs["threshold"],
                    current_value=kwargs["current_value"],
                    related_budget=kwargs.get("related_budget"),
                    related_department=kwargs.get("related_department"),
                    notify_users=kwargs.get("notify_users")
                ),
                "get_alerts": lambda **kwargs: cost_control_api.get_alerts(
                    status=kwargs.get("status"),
                    alert_type=kwargs.get("alert_type"),
                    severity=kwargs.get("severity")
                ),
                "generate_analysis_report": lambda **kwargs: cost_control_api.generate_analysis_report(
                    start_date=kwargs["start_date"],
                    end_date=kwargs["end_date"],
                    dimensions=kwargs.get("dimensions")
                ),
                "format_budget": lambda **kwargs: {
                    "formatted_text": cost_control_api.format_budget(kwargs["result"])
                },
                "format_standard": lambda **kwargs: {
                    "formatted_text": cost_control_api.format_standard(kwargs["result"])
                },
                "format_analysis_report": lambda **kwargs: {
                    "formatted_text": cost_control_api.format_analysis_report(kwargs["result"])
                }
            }
            
            if function_name not in function_map:
                return {
                    "code": 404,
                    "msg": f"函数{function_name}不存在",
                    "data": None
                }
            
            result = function_map[function_name](**args)
            return result
            
        except json.JSONDecodeError as e:
            return {
                "code": 400,
                "msg": f"参数格式错误: {str(e)}",
                "data": None
            }
        except CostControlError as e:
            return {
                "code": 500,
                "msg": str(e),
                "data": None
            }
        except Exception as e:
            return {
                "code": 500,
                "msg": f"未知错误: {str(e)}",
                "data": None
            }
    
    @staticmethod
    def get_functions() -> list:
        """获取所有可用函数描述"""
        return COST_CONTROL_FUNCTIONS


if __name__ == "__main__":
    adapter = OpenaiCostControlAdapter()
    
    # 测试创建预算
    print("=" * 60)
    print("测试创建预算")
    print("=" * 60)
    func_args = json.dumps({
        "budget_type": "department",
        "budget_name": "2026年销售部预算",
        "budget_period": "year",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "total_amount": 500000,
        "owner_id": "DEPT001",
        "owner_name": "销售部",
        "owner_type": "department"
    })
    result = adapter.call_function("create_budget", func_args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试格式化
    print("\n" + "=" * 60)
    print("测试格式化预算")
    print("=" * 60)
    func_args = json.dumps({"result": result})
    formatted = adapter.call_function("format_budget", func_args)
    print(formatted.get("data", {}).get("formatted_text", ""))
