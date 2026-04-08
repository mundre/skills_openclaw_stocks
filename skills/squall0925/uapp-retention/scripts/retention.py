#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""uapp-retention: 友盟 App 留存率查询与对比分析脚本

阶段一实现：
- 基础留存查询（--retention-type, --retention-day, --period, --range）
- 支持新增/活跃用户留存
- 支持按日/周/月周期
- 输出：自然语言摘要 + JSON 趋势数据
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

# -------------------------
# 常量定义
# -------------------------

# 留存天数到数组索引的映射（统一标准）
RETENTION_DAY_INDEX = {
    1: 0,   # 次日留存
    3: 1,   # 3日留存
    7: 2,   # 7日留存
    14: 3,  # 14日留存
    30: 4,  # 30日留存
}

RETENTION_DAY_LABEL = {
    1: "次日留存",
    3: "3日留存",
    7: "7日留存",
    14: "14日留存",
    30: "30日留存",
}

RETENTION_TYPE_LABEL = {
    "new": "新增用户",
    "active": "活跃用户",
}

PERIOD_LABEL = {
    "day": "按日",
    "week": "按周",
    "month": "按月",
}

# -------------------------
# 工具函数：路径 & 配置加载（从 uapp-core-index 复制）
# -------------------------


def resolve_workspace_root() -> str:
    """解析 workspace 根目录。"""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workspace = os.path.dirname(skill_dir)
    return workspace


def load_env_config_path() -> str | None:
    """从环境变量或 .env 中加载 UMENG_CONFIG_PATH。"""
    env_path = os.environ.get("UMENG_CONFIG_PATH")
    if env_path:
        return env_path

    workspace = resolve_workspace_root()
    env_file = os.path.join(workspace, ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("UMENG_CONFIG_PATH="):
                        return line.split("UMENG_CONFIG_PATH=", 1)[1].strip()
        except Exception:
            pass
    return None


def resolve_config_path(cli_config: str | None) -> str:
    """解析配置文件路径。"""
    if cli_config:
        return cli_config

    env_config = load_env_config_path()
    if env_config:
        return env_config

    workspace = resolve_workspace_root()
    default_path = os.path.join(workspace, "umeng-config.json")
    return default_path


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------
# 应用解析（从 uapp-core-index 复制）
# -------------------------


def normalize_app_name(name: str) -> str:
    """去除半角/全角空格，用于模糊匹配。"""
    return name.replace(" ", "").replace("\u3000", "")


def find_app_by_name(config: dict, app_name: str, account_id: str | None = None, platform: str | None = None):
    """按应用名称查找应用配置，支持精确匹配 + 去空格模糊匹配。"""
    matches = []
    normalized_input = normalize_app_name(app_name)

    for account in config.get("accounts", []):
        if account_id and account.get("id") != account_id:
            continue
        for app in account.get("apps", []):
            if platform and app.get("platform") != platform:
                continue
            name = app.get("name", "")
            if name == app_name or normalize_app_name(name) == normalized_input:
                matches.append({
                    "account_id": account.get("id"),
                    "apiKey": account.get("apiKey"),
                    "apiSecurity": account.get("apiSecurity"),
                    "app": app,
                })

    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    return matches


def resolve_app(config: dict, app_name: str | None, account_id: str | None, platform: str | None) -> dict:
    """解析最终使用的应用配置。"""
    if app_name:
        result = find_app_by_name(config, app_name, account_id=account_id, platform=platform)
        if not result:
            available = []
            for account in config.get("accounts", []):
                for app in account.get("apps", []):
                    available.append(app.get("name", ""))
            raise ValueError(f"未找到名称匹配的应用: {app_name}，可用应用: {', '.join(available)}")
        if isinstance(result, list):
            raise ValueError("存在多个同名应用，请通过 --account / --platform 进一步限定")
        return result

    default_app = config.get("defaultApp")
    if default_app:
        return {
            "account_id": default_app.get("account_id"),
            "apiKey": default_app.get("apiKey"),
            "apiSecurity": default_app.get("apiSecurity"),
            "app": {
                "name": default_app.get("name"),
                "appkey": default_app.get("appkey"),
                "platform": default_app.get("platform"),
            },
        }

    raise ValueError("未指定应用且配置中未设置 defaultApp，请使用 --app 指定应用名称")


# -------------------------
# 时间范围解析
# -------------------------


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def resolve_time_range(range_name: str, today: date | None = None) -> tuple[date, date]:
    """解析时间范围名称到起止日期（含）。"""
    if today is None:
        today = date.today()

    if range_name == "yesterday":
        d = today - timedelta(days=1)
        return d, d
    if range_name == "last_7_days":
        end = today - timedelta(days=1)
        start = end - timedelta(days=6)
        return start, end
    if range_name == "last_30_days":
        end = today - timedelta(days=1)
        start = end - timedelta(days=29)
        return start, end
    if range_name == "last_90_days":
        end = today - timedelta(days=1)
        start = end - timedelta(days=89)
        return start, end

    try:
        d = parse_date(range_name)
        return d, d
    except Exception as exc:  # noqa: F841
        raise ValueError(f"不支持的时间范围: {range_name}")


# -------------------------
# SDK 初始化
# -------------------------


def get_sdk_root() -> str:
    """获取当前 skill 内部 SDK 根目录。"""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(skill_dir, "友盟_openapi_python_SDK")


def init_sdk(api_key: str, api_security: str) -> None:
    """初始化 SDK 路径和默认服务器配置。"""
    sdk_root = get_sdk_root()
    if sdk_root not in sys.path:
        sys.path.insert(0, sdk_root)

    import aop
    aop.set_default_server('gateway.open.umeng.com')
    aop.set_default_appinfo(int(api_key), api_security)


# -------------------------
# 留存查询核心逻辑
# -------------------------


def extract_retention_rate(retention_info: dict, day: int) -> float | None:
    """从 retentionInfo 中提取指定天数的留存率。"""
    rates = retention_info.get("retentionRate", [])
    idx = RETENTION_DAY_INDEX.get(day)
    if idx is None or idx >= len(rates):
        return None
    return rates[idx]


def query_retention(
    app_cfg: dict,
    retention_type: str,
    period: str,
    start: date,
    end: date,
    version: str | None = None,
    channel: str | None = None,
) -> list[dict]:
    """查询留存数据。"""
    from aop import api

    appkey = app_cfg["app"].get("appkey")
    if not appkey:
        raise ValueError("应用配置缺少 appkey")

    req = api.UmengUappGetRetentionsRequest()
    req.appkey = appkey
    req.startDate = start.strftime("%Y-%m-%d")
    req.endDate = end.strftime("%Y-%m-%d")
    req.type = retention_type
    req.periodType = period
    if version:
        req.version = version
    if channel:
        req.channel = channel

    resp = req.get_response()
    if not isinstance(resp, dict):
        raise ValueError("API 响应格式错误")

    return resp.get("retentionInfo", [])


def query_version_list(app_cfg: dict, query_date: date) -> list[dict]:
    """查询版本列表。"""
    from aop import api

    appkey = app_cfg["app"].get("appkey")
    if not appkey:
        raise ValueError("应用配置缺少 appkey")

    req = api.UmengUappGetVersionDataRequest()
    req.appkey = appkey
    req.date = query_date.strftime("%Y-%m-%d")

    resp = req.get_response()
    if not isinstance(resp, dict):
        raise ValueError("API 响应格式错误")

    return resp.get("versionInfos", [])


def query_channel_list(app_cfg: dict, start: date, end: date) -> list[str]:
    """查询渠道列表（通过留存数据反推）。"""
    from aop import api

    appkey = app_cfg["app"].get("appkey")
    if not appkey:
        raise ValueError("应用配置缺少 appkey")

    # 尝试通过 getRetentions 获取渠道列表
    # 由于 API 没有直接提供渠道列表接口，我们尝试查询一个日期范围
    # 并检查返回数据中是否包含渠道信息
    # 实际上 getRetentions 不支持返回渠道列表，这里需要其他方式
    # 暂时返回空列表，后续可以通过 getChannelData 或其他 API 获取
    return []


# -------------------------
# 输出格式化
# -------------------------


def build_retention_summary(
    app_info: dict,
    retention_type: str,
    retention_day: int,
    period: str,
    start: date,
    end: date,
    series: list[dict],
    version: str | None = None,
    channel: str | None = None,
) -> str:
    """构造留存率查询的中文摘要文案。"""
    app_name = app_info["app"].get("name")
    type_label = RETENTION_TYPE_LABEL.get(retention_type, retention_type)
    day_label = RETENTION_DAY_LABEL.get(retention_day, f"{retention_day}日留存")
    period_label = PERIOD_LABEL.get(period, period)

    # 提取有效留存率
    rates = [item.get("retention_rate") for item in series if item.get("retention_rate") is not None]
    # 提取新增用户数作为参考
    install_users = [item.get("total_install_user", 0) for item in series]

    # 构建维度描述
    dimension_desc = ""
    if version and channel:
        dimension_desc = f"版本 {version}（{channel}渠道）"
    elif version:
        dimension_desc = f"版本 {version}"
    elif channel:
        dimension_desc = f"{channel}渠道"

    if not rates:
        if dimension_desc:
            return f"应用 {app_name} {dimension_desc} 在 {start} 至 {end} 的 {day_label}（{type_label}）暂无可用数据。"
        return f"应用 {app_name} 在 {start} 至 {end} 的 {day_label}（{type_label}）暂无可用数据。"

    first_rate = rates[0]
    last_rate = rates[-1]
    avg_rate = sum(rates) / len(rates)
    avg_install = sum(install_users) / len(install_users) if install_users else 0

    # 趋势判断
    if first_rate == 0:
        trend = "变化情况不明显"
    else:
        change_rate = (last_rate - first_rate) / float(first_rate)
        if change_rate > 0.05:
            trend = f"整体呈上升趋势，末期较初期上升 {change_rate*100:.1f}%"
        elif change_rate < -0.05:
            trend = f"整体呈下降趋势，末期较初期下降 {abs(change_rate)*100:.1f}%"
        else:
            trend = "整体基本持平"

    # 构建输出
    base_desc = f"应用 {app_name}"
    if dimension_desc:
        base_desc += f" {dimension_desc}"

    return (
        f"{base_desc} 在 {start} 至 {end} 的 {day_label}（{type_label}，{period_label}）"
        f"日均 {avg_rate:.2f}%，从 {first_rate:.2f}% 变化到 {last_rate:.2f}%，{trend}。"
        f"新增用户基数：日均 {int(avg_install)} 人。"
    )


def build_json_output(
    app_info: dict,
    retention_type: str,
    retention_day: int,
    period: str,
    start: date,
    end: date,
    series: list[dict],
    version: str | None = None,
    channel: str | None = None,
) -> dict:
    """构造留存率查询的 JSON 输出。"""
    return {
        "app": {
            "name": app_info["app"].get("name"),
            "appkey": app_info["app"].get("appkey"),
            "platform": app_info["app"].get("platform"),
        },
        "retention_type": retention_type,
        "retention_day": retention_day,
        "period": period,
        "version": version,
        "channel": channel,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "series": series,
    }


def build_version_list_output(app_info: dict, versions: list[dict]) -> str:
    """构造版本列表的文本输出。"""
    app_name = app_info["app"].get("name")
    lines = [f"应用 {app_name} 的版本列表：", ""]

    if not versions:
        lines.append("暂无版本数据。")
        return "\n".join(lines)

    lines.append(f"{'版本号':<20} {'活跃用户':<10} {'新增用户':<10} {'总用户':<10}")
    lines.append("-" * 60)

    for v in versions[:20]:  # 最多显示 20 个版本
        version = v.get("version", "N/A")
        active = v.get("activeUser", 0)
        new = v.get("newUser", 0)
        total = v.get("totalUser", 0)
        lines.append(f"{version:<20} {active:<10} {new:<10} {total:<10}")

    if len(versions) > 20:
        lines.append(f"... 还有 {len(versions) - 20} 个版本")

    return "\n".join(lines)


def build_version_list_json(app_info: dict, versions: list[dict]) -> dict:
    """构造版本列表的 JSON 输出。"""
    return {
        "app": {
            "name": app_info["app"].get("name"),
            "appkey": app_info["app"].get("appkey"),
            "platform": app_info["app"].get("platform"),
        },
        "versions": versions,
        "count": len(versions),
    }


def build_comparison_summary(
    app_info: dict,
    retention_type: str,
    retention_day: int,
    comparison_type: str,  # 'version' or 'channel'
    comparison_data: dict,  # {name: series}
) -> str:
    """构造对比结果的文本摘要。"""
    app_name = app_info["app"].get("name")
    type_label = RETENTION_TYPE_LABEL.get(retention_type, retention_type)
    day_label = RETENTION_DAY_LABEL.get(retention_day, f"{retention_day}日留存")
    dim_label = "版本" if comparison_type == "version" else "渠道"

    lines = [f"应用 {app_name} 的 {day_label}（{type_label}）对比：", ""]

    # 计算每个维度的平均留存率
    avg_rates = {}
    for name, series in comparison_data.items():
        rates = [item.get("retention_rate") for item in series if item.get("retention_rate") is not None]
        avg_rates[name] = sum(rates) / len(rates) if rates else 0

    # 按留存率排序
    sorted_items = sorted(avg_rates.items(), key=lambda x: x[1], reverse=True)

    for name, avg_rate in sorted_items:
        lines.append(f"- {dim_label} {name}: {avg_rate:.2f}%")

    # 如果有两个以上，显示最高和最低的差异
    if len(sorted_items) >= 2:
        highest = sorted_items[0]
        lowest = sorted_items[-1]
        diff = highest[1] - lowest[1]
        lines.append("")
        lines.append(f"{dim_label} {highest[0]} 比 {lowest[0]} 高 {diff:.2f} 个百分点。")

    return "\n".join(lines)


def build_comparison_json(
    app_info: dict,
    retention_type: str,
    retention_day: int,
    comparison_type: str,
    comparison_data: dict,
) -> dict:
    """构造对比结果的 JSON 输出。"""
    return {
        "app": {
            "name": app_info["app"].get("name"),
            "appkey": app_info["app"].get("appkey"),
            "platform": app_info["app"].get("platform"),
        },
        "retention_type": retention_type,
        "retention_day": retention_day,
        "comparison_type": comparison_type,
        "data": comparison_data,
    }


# -------------------------
# CLI 入口
# -------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="uapp-retention: 友盟 App 留存率查询与对比分析")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--app", help="应用名称（支持模糊匹配）")
    parser.add_argument("--account", help="账号 ID")
    parser.add_argument("--platform", help="平台标识")

    parser.add_argument(
        "--retention-type",
        choices=["new", "active"],
        default="new",
        help="留存类型：new（新增用户，默认）/ active（活跃用户）",
    )
    parser.add_argument(
        "--retention-day",
        type=int,
        choices=[1, 3, 7, 14, 30],
        default=1,
        help="留存天数：1（次日，默认）/ 3 / 7 / 14 / 30",
    )
    parser.add_argument(
        "--period",
        choices=["day", "week", "month"],
        default="day",
        help="周期类型：day（按日，默认）/ week / month",
    )
    parser.add_argument("--range", dest="time_range", help="时间范围：yesterday/last_7_days/last_30_days/last_90_days 或 yyyy-mm-dd")

    # 维度筛选（阶段二实现）
    parser.add_argument("--version", help="版本筛选（可选）")
    parser.add_argument("--channel", help="渠道筛选（可选）")

    # 列表查询（阶段三）
    parser.add_argument("--list-versions", action="store_true", help="列出所有版本")
    parser.add_argument("--list-channels", action="store_true", help="列出所有渠道")

    # 对比功能（阶段三）
    parser.add_argument("--compare-versions", help="版本对比，逗号分隔（如：3.2,3.1）")
    parser.add_argument("--compare-channels", help="渠道对比，逗号分隔（如：GooglePlay,AppStore）")

    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    try:
        args = parse_args(argv)

        config_path = resolve_config_path(args.config)
        config = load_config(config_path)

        app_info = resolve_app(config, app_name=args.app, account_id=args.account, platform=args.platform)

        init_sdk(app_info["apiKey"], app_info["apiSecurity"])

        # 阶段三：列表查询 - 版本列表
        if args.list_versions:
            # 使用昨天作为查询日期（版本数据通常较新）
            query_date = date.today() - timedelta(days=1)
            versions = query_version_list(app_info, query_date)
            if args.json:
                output = build_version_list_json(app_info, versions)
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                text = build_version_list_output(app_info, versions)
                print(text)
            return 0

        # 阶段三：列表查询 - 渠道列表
        if args.list_channels:
            # 渠道列表需要特殊处理，暂时返回提示
            if args.json:
                print(json.dumps({
                    "app": {
                        "name": app_info["app"].get("name"),
                        "appkey": app_info["app"].get("appkey"),
                    },
                    "channels": [],
                    "note": "渠道列表功能需要额外 API 支持，建议通过 --channel 参数直接指定已知渠道"
                }, ensure_ascii=False, indent=2))
            else:
                print(f"应用 {app_info['app'].get('name')} 的渠道列表：")
                print("")
                print("渠道列表功能需要额外 API 支持。")
                print("建议通过 --channel 参数直接指定已知渠道（如：GooglePlay、AppStore 等）")
            return 0

        # 检查是否需要时间范围参数
        if not args.time_range:
            raise ValueError("必须使用 --range 指定时间范围，或使用 --list-versions/--list-channels 查询列表")

        start, end = resolve_time_range(args.time_range)

        # 阶段三：版本对比
        if args.compare_versions:
            versions = [v.strip() for v in args.compare_versions.split(",")]
            if len(versions) < 2:
                raise ValueError("版本对比需要至少两个版本，用逗号分隔")

            comparison_data = {}
            for version in versions:
                retention_info_list = query_retention(
                    app_info,
                    retention_type=args.retention_type,
                    period=args.period,
                    start=start,
                    end=end,
                    version=version,
                    channel=args.channel,  # 可以配合渠道筛选
                )
                series = []
                for info in retention_info_list:
                    series.append({
                        "date": info.get("date"),
                        "retention_rate": extract_retention_rate(info, args.retention_day),
                        "total_install_user": info.get("totalInstallUser"),
                        "raw": info,
                    })
                comparison_data[version] = series

            if args.json:
                output = build_comparison_json(
                    app_info,
                    args.retention_type,
                    args.retention_day,
                    "version",
                    comparison_data,
                )
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                text = build_comparison_summary(
                    app_info,
                    args.retention_type,
                    args.retention_day,
                    "version",
                    comparison_data,
                )
                print(text)
            return 0

        # 阶段三：渠道对比
        if args.compare_channels:
            channels = [c.strip() for c in args.compare_channels.split(",")]
            if len(channels) < 2:
                raise ValueError("渠道对比需要至少两个渠道，用逗号分隔")

            comparison_data = {}
            for channel in channels:
                retention_info_list = query_retention(
                    app_info,
                    retention_type=args.retention_type,
                    period=args.period,
                    start=start,
                    end=end,
                    version=args.version,  # 可以配合版本筛选
                    channel=channel,
                )
                series = []
                for info in retention_info_list:
                    series.append({
                        "date": info.get("date"),
                        "retention_rate": extract_retention_rate(info, args.retention_day),
                        "total_install_user": info.get("totalInstallUser"),
                        "raw": info,
                    })
                comparison_data[channel] = series

            if args.json:
                output = build_comparison_json(
                    app_info,
                    args.retention_type,
                    args.retention_day,
                    "channel",
                    comparison_data,
                )
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                text = build_comparison_summary(
                    app_info,
                    args.retention_type,
                    args.retention_day,
                    "channel",
                    comparison_data,
                )
                print(text)
            return 0

        # 普通留存查询（阶段一/二）
        retention_info_list = query_retention(
            app_info,
            retention_type=args.retention_type,
            period=args.period,
            start=start,
            end=end,
            version=args.version,
            channel=args.channel,
        )

        # 转换为统一格式的 series
        series = []
        for info in retention_info_list:
            series.append({
                "date": info.get("date"),
                "retention_rate": extract_retention_rate(info, args.retention_day),
                "total_install_user": info.get("totalInstallUser"),
                "raw": info,
            })

        if args.json:
            output = build_json_output(
                app_info,
                args.retention_type,
                args.retention_day,
                args.period,
                start,
                end,
                series,
                version=args.version,
                channel=args.channel,
            )
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            text = build_retention_summary(
                app_info,
                args.retention_type,
                args.retention_day,
                args.period,
                start,
                end,
                series,
                version=args.version,
                channel=args.channel,
            )
            print(text)

        return 0

    except ValueError as e:
        error_result = {
            "success": False,
            "error_type": "ValueError",
            "message": str(e),
        }
        if hasattr(args, 'json') and args.json:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"[错误] {e}", file=sys.stderr)
            print("\n提示：使用 --help 查看可用选项", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        error_result = {
            "success": False,
            "error_type": "FileNotFoundError",
            "message": str(e),
            "help": "配置方式:\n"
                    "1. --config /path/to/umeng-config.json\n"
                    "2. export UMENG_CONFIG_PATH=/path/to/umeng-config.json\n"
                    "3. 在当前目录创建 umeng-config.json",
        }
        if hasattr(args, 'json') and args.json:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"[配置错误] {e}", file=sys.stderr)
            print("\n可用配置方式:", file=sys.stderr)
            print("  1. --config /path/to/umeng-config.json", file=sys.stderr)
            print("  2. export UMENG_CONFIG_PATH=/path/to/umeng-config.json", file=sys.stderr)
            print("  3. 在当前目录创建 umeng-config.json", file=sys.stderr)
        return 1
    except Exception as e:
        error_result = {
            "success": False,
            "error_type": type(e).__name__,
            "message": str(e),
        }
        if hasattr(args, 'json') and args.json:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"[错误] {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
