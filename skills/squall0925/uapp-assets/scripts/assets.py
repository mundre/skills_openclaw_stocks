#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""uapp-assets: 友盟应用资产查询工具

功能：
- 查询 App 数量 (--count)
- 查询 App 列表 (--list-apps)
- 查询小程序列表 (--list-minis)
- 同时查询 App 和小程序 (--list-all)

支持：
- 分页查询（每页最多 100 条）
- 平台过滤（支持模糊匹配）
- JSON/Table 两种输出格式
"""

import argparse
import json
import os
import sys

# -------------------------
# 工具函数：路径 & 配置加载
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
    """解析配置文件路径。

    优先级：
    1. CLI 参数 --config
    2. UMENG_CONFIG_PATH（环境变量/.env）
    3. workspace 根目录下的 umeng-config.json
    """
    if cli_config:
        return cli_config

    env_config = load_env_config_path()
    if env_config:
        return env_config

    workspace = resolve_workspace_root()
    default_path = os.path.join(workspace, "umeng-config.json")
    return default_path


def load_config(config_path: str) -> dict:
    """加载配置文件。"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_first_account(config: dict) -> dict:
    """获取第一个账号的配置（应用资产查询不需要指定具体应用）。"""
    accounts = config.get("accounts", [])
    if not accounts:
        raise ValueError("配置文件中没有账号信息")
    return accounts[0]


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
# API 调用
# -------------------------


def get_app_count() -> int:
    """获取 App 总数。"""
    from aop import api
    req = api.UmengUappGetAppCountRequest()
    resp = req.get_response()
    if isinstance(resp, dict):
        return resp.get("count", 0)
    return 0


def get_app_list(page: int = 1, per_page: int = 100) -> dict:
    """获取 App 列表。

    Returns:
        {
            "data": [...],
            "total_page": int,
            "current_page": int,
            "total_count": int (估算)
        }
    """
    from aop import api
    req = api.UmengUappGetAppListRequest()
    req.page = page
    req.perPage = per_page
    resp = req.get_response()

    if not isinstance(resp, dict):
        return {"data": [], "total_page": 0, "current_page": page, "total_count": 0}

    app_infos = resp.get("appInfos", [])
    total_page = resp.get("totalPage", 1)
    current_page = resp.get("page", page)

    # 估算总数
    total_count = (total_page - 1) * per_page + len(app_infos) if app_infos else 0

    return {
        "data": app_infos,
        "total_page": total_page,
        "current_page": current_page,
        "total_count": total_count,
    }


def get_mini_list(page: int = 1, page_size: int = 1000) -> dict:
    """获取小程序列表。

    注意：umeng.umini.getAppList 接口每页最多 1000 条记录。

    Returns:
        {
            "data": [...],
            "total_page": int,
            "current_page": int,
            "total_count": int
        }
    """
    from aop import api
    req = api.UmengUminiGetAppListRequest()
    req.pageIndex = page
    req.pageSize = page_size
    resp = req.get_response()

    if not isinstance(resp, dict):
        return {"data": [], "total_page": 0, "current_page": page, "total_count": 0}

    # 响应结构: {"data": {"totalCount": 1452, "currentPage": 9, "data": [...]}, "code": 200}
    data_wrapper = resp.get("data", {})
    mini_list = data_wrapper.get("data", [])
    total_count = data_wrapper.get("totalCount", 0)
    current_page = data_wrapper.get("currentPage", page)

    # 计算总页数
    total_page = (total_count + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "data": mini_list,
        "total_page": total_page,
        "current_page": current_page,
        "total_count": total_count,
    }


# -------------------------
# 数据转换
# -------------------------


def transform_app_data(raw_list: list[dict]) -> list[dict]:
    """转换 App 数据为统一格式。"""
    result = []
    for item in raw_list:
        result.append({
            "name": item.get("name", ""),
            "platform": item.get("platform", ""),
            "appkey": item.get("appkey", ""),
            "created_at": item.get("createdAt", ""),
            "updated_at": item.get("updatedAt", ""),
            "category": item.get("category", ""),
            "popular": item.get("popular", 0),
            "use_game_sdk": item.get("useGameSdk", False),
        })
    return result


def transform_mini_data(raw_list: list[dict]) -> list[dict]:
    """转换小程序数据为统一格式。"""
    result = []
    for item in raw_list:
        result.append({
            "name": item.get("appName", ""),
            "platform": item.get("platform", ""),
            "data_source_id": item.get("dataSourceId", ""),
            "created_at": item.get("gmtCreate", ""),
            "first_level": item.get("firstLevel", ""),
            "second_level": item.get("secondLevel", ""),
            "username": item.get("userName", ""),
        })
    return result


# -------------------------
# 平台过滤
# -------------------------

# App 平台白名单（umeng.uapp.getAppList 接口可能混入 mini_ 开头的应用）
VALID_APP_PLATFORMS = {"android", "iphone", "ipad", "harmony"}

# 小程序平台黑名单（umeng.umini.getAppList 接口会混入 App 平台数据）
INVALID_MINI_PLATFORMS = {"android", "iphone", "ipad", "harmony"}

# 平台别名映射（用于模糊匹配）
PLATFORM_ALIASES = {
    "ios": ["iphone"],
    "mini": [
        "mini_tmall_genie", "mini_bytedance", "mini_weixin",
        "mini_alipay", "mini_baidu", "mini_qq", "mini_jd",
        "mini_kuaishou", "mini_douyin", "mini_toutiao"
    ],
}


def filter_valid_app_platforms(data: list[dict]) -> list[dict]:
    """过滤 App 数据，仅保留有效平台（android/iphone/ipad/harmony）。

    用于修正 umeng.uapp.getAppList 接口可能混入 mini_ 开头平台的问题。
    """
    return [item for item in data if item.get("platform", "").lower() in VALID_APP_PLATFORMS]


def filter_valid_mini_platforms(data: list[dict]) -> list[dict]:
    """过滤小程序数据，排除 App 平台（android/iphone/ipad/harmony）。

    用于修正 umeng.umini.getAppList 接口可能混入 App 平台数据的问题。
    """
    return [item for item in data if item.get("platform", "").lower() not in INVALID_MINI_PLATFORMS]


def match_platform(platform: str, filter_value: str) -> bool:
    """检查平台是否匹配过滤条件（支持模糊匹配）。

    匹配规则：
    1. 精确匹配：filter == platform
    2. 别名匹配：platform in PLATFORM_ALIASES[filter]
    3. 前缀匹配：platform.startswith(filter)
    """
    filter_lower = filter_value.lower()
    platform_lower = platform.lower()

    # 精确匹配
    if platform_lower == filter_lower:
        return True

    # 别名匹配
    if filter_lower in PLATFORM_ALIASES:
        if platform_lower in PLATFORM_ALIASES[filter_lower]:
            return True

    # 前缀匹配（如 mini_bytedance 匹配 mini）
    if platform_lower.startswith(filter_lower):
        return True

    return False


def filter_by_platform(data: list[dict], platform_filter: str) -> list[dict]:
    """按平台过滤数据。"""
    if not platform_filter:
        return data
    return [item for item in data if match_platform(item.get("platform", ""), platform_filter)]


# -------------------------
# 输出格式化
# -------------------------


def format_table(data: list[dict], columns: list[tuple[str, str]], title: str = "") -> str:
    """格式化为表格输出。

    Args:
        data: 数据列表
        columns: 列定义 [(字段名, 显示名称), ...]
        title: 表格标题

    Returns:
        格式化后的表格字符串
    """
    if not data:
        return f"{title}\n暂无数据\n" if title else "暂无数据\n"

    lines = []
    if title:
        lines.append(title)
        lines.append("")

    # 计算每列宽度
    widths = {}
    for field, display in columns:
        max_width = len(display)
        for item in data:
            value = str(item.get(field, ""))
            max_width = max(max_width, len(value))
        widths[field] = max_width

    # 表头
    header_parts = []
    for field, display in columns:
        header_parts.append(display.ljust(widths[field]))
    lines.append("  ".join(header_parts))

    # 分隔线
    separator_parts = []
    for field, _ in columns:
        separator_parts.append("-" * widths[field])
    lines.append("  ".join(separator_parts))

    # 数据行
    for item in data:
        row_parts = []
        for field, _ in columns:
            value = str(item.get(field, ""))
            row_parts.append(value.ljust(widths[field]))
        lines.append("  ".join(row_parts))

    return "\n".join(lines) + "\n"


def format_app_table(data: list[dict], page: int, per_page: int) -> str:
    """格式化 App 列表表格。
    
    注意：由于客户端过滤，total_count 使用实际返回的数据量。
    """
    columns = [
        ("name", "名称"),
        ("platform", "平台"),
        ("appkey", "AppKey"),
        ("created_at", "创建时间"),
    ]
    
    actual_count = len(data)
    start_idx = (page - 1) * per_page + 1
    end_idx = start_idx + actual_count - 1
    
    table = format_table(data, columns, "App 列表")
    
    # 添加分页信息（使用实际记录数）
    if actual_count == 0:
        pagination = "\n暂无数据"
    else:
        pagination = f"\n本页显示 {actual_count} 个应用（第 {start_idx}-{end_idx} 条）"
        if actual_count == per_page:
            pagination += "\n提示：可能还有更多数据，输入 \"下一页\" 查看后续数据"
    
    return table + pagination


def format_mini_table(data: list[dict], page: int, per_page: int, title: str = "小程序列表") -> str:
    """格式化小程序/应用列表表格。
    
    注意：由于客户端过滤，使用实际返回的数据量。
    """
    columns = [
        ("name", "名称"),
        ("platform", "平台"),
        ("first_level", "一级分类"),
        ("second_level", "二级分类"),
        ("created_at", "创建时间"),
    ]
    
    actual_count = len(data)
    start_idx = (page - 1) * per_page + 1
    end_idx = start_idx + actual_count - 1
    
    table = format_table(data, columns, title)
    
    # 根据标题确定显示的文字
    item_name = "应用" if "全部" in title or "应用" in title else "小程序"
    
    # 添加分页信息（使用实际记录数）
    if actual_count == 0:
        pagination = "\n暂无数据"
    else:
        pagination = f"\n本页显示 {actual_count} 个{item_name}（第 {start_idx}-{end_idx} 条）"
        if actual_count == per_page:
            pagination += "\n提示：可能还有更多数据，输入 \"下一页\" 查看后续数据"
    
    return table + pagination


def format_json(data: list[dict], actual_count: int, page: int, per_page: int, data_type: str) -> str:
    """格式化为 JSON 输出。
    
    注意：actual_count 是过滤后的实际记录数。
    """
    output = {
        "type": data_type,
        "count": actual_count,
        "page": page,
        "per_page": per_page,
        "data": data,
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


# -------------------------
# CLI 参数解析
# -------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="uapp-assets: 友盟应用资产查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python assets.py --count                    # 查询 App 总数
  python assets.py --list-apps                # 列出 App 列表（第 1 页）
  python assets.py --list-apps --page 2       # 列出 App 列表（第 2 页）
  python assets.py --list-minis               # 列出小程序列表
  python assets.py --list-all                 # 同时列出 App 和小程序
  python assets.py --list-apps --platform android  # 按 Android 平台过滤
  python assets.py --list-minis --platform mini    # 列出所有小程序平台
  python assets.py --list-apps --output json       # JSON 格式输出
        """
    )
    
    parser.add_argument("--config", help="配置文件路径")
    
    # 查询命令（互斥）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--count", action="store_true", help="获取 App 总数")
    group.add_argument("--list-apps", action="store_true", help="列出 App 列表")
    group.add_argument("--list-minis", action="store_true", help="列出小程序列表")
    group.add_argument("--list-all", action="store_true", help="同时列出 App 和小程序")
    
    # 分页参数
    parser.add_argument("--page", type=int, default=1, help="页码（默认 1）")
    parser.add_argument("--per-page", type=int, default=0, help="每页记录数（App 默认 100，小程序/全部应用默认 1000，设为 0 使用默认值）")
    
    # 过滤参数
    parser.add_argument("--platform", help="平台过滤（支持模糊匹配，如 mini 匹配所有小程序平台）")
    
    # 输出格式
    parser.add_argument("--output", choices=["table", "json"], default="table", help="输出格式（默认 table）")
    
    return parser.parse_args(argv)


# -------------------------
# 主函数
# -------------------------


def do_count(args: argparse.Namespace) -> int:
    """执行 --count 命令。"""
    count = get_app_count()
    
    if args.output == "json":
        result = {"count": count}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"App 总数: {count}")
    
    return 0


def do_list_apps(args: argparse.Namespace) -> int:
    """执行 --list-apps 命令。"""
    page = args.page
    # App 列表默认 100 条/页，最大 100
    per_page = min(args.per_page, 100) if args.per_page > 0 else 100
    
    result = get_app_list(page=page, per_page=per_page)
    raw_data = result["data"]
    
    # 数据转换
    data = transform_app_data(raw_data)
    
    # 内置平台过滤：仅保留有效 App 平台（排除 mini_ 开头的混入数据）
    data = filter_valid_app_platforms(data)
    
    # 用户指定的平台过滤
    if args.platform:
        data = filter_by_platform(data, args.platform)
    
    # 输出
    if args.output == "json":
        print(format_json(data, len(data), page, per_page, "apps"))
    else:
        print(format_app_table(data, page, per_page))
    
    return 0


def do_list_minis(args: argparse.Namespace) -> int:
    """执行 --list-minis 命令。"""
    page = args.page
    # umeng.umini.getAppList 接口每页最多 1000 条，默认 1000
    per_page = min(args.per_page, 1000) if args.per_page > 0 else 1000
    
    result = get_mini_list(page=page, page_size=per_page)
    raw_data = result["data"]
    
    # 数据转换
    data = transform_mini_data(raw_data)
    
    # 内置平台过滤：排除 App 平台（android/iphone/ipad/harmony）
    data = filter_valid_mini_platforms(data)
    
    # 用户指定的平台过滤
    if args.platform:
        data = filter_by_platform(data, args.platform)
    
    # 输出
    if args.output == "json":
        print(format_json(data, len(data), page, per_page, "minis"))
    else:
        print(format_mini_table(data, page, per_page))
    
    return 0


def do_list_all(args: argparse.Namespace) -> int:
    """执行 --list-all 命令。
    
    通过 umeng.umini.getAppList 接口获取全部应用数据（包括 App 和小程序），
    不进行内置平台过滤。
    """
    page = args.page
    # umeng.umini.getAppList 接口每页最多 1000 条，默认 1000
    per_page = min(args.per_page, 1000) if args.per_page > 0 else 1000
    
    # 获取全部应用数据（umeng.umini.getAppList 接口包含所有类型）
    result = get_mini_list(page=page, page_size=per_page)
    raw_data = result["data"]
    
    # 数据转换
    data = transform_mini_data(raw_data)
    
    # 仅应用用户指定的平台过滤（不进行内置过滤）
    if args.platform:
        data = filter_by_platform(data, args.platform)
    
    # 输出
    if args.output == "json":
        print(format_json(data, len(data), page, per_page, "all"))
    else:
        print(format_mini_table(data, page, per_page, "全部应用列表"))
    
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    
    try:
        args = parse_args(argv)
        
        # 加载配置
        config_path = resolve_config_path(args.config)
        config = load_config(config_path)
        account = get_first_account(config)
        
        # 初始化 SDK
        init_sdk(account["apiKey"], account["apiSecurity"])
        
        # 执行对应命令
        if args.count:
            return do_count(args)
        elif args.list_apps:
            return do_list_apps(args)
        elif args.list_minis:
            return do_list_minis(args)
        elif args.list_all:
            return do_list_all(args)
        else:
            print("请指定操作命令，使用 --help 查看帮助", file=sys.stderr)
            return 1
    
    except ValueError as e:
        error_result = {"success": False, "error_type": "ValueError", "message": str(e)}
        if hasattr(args, 'output') and args.output == "json":
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"[错误] {e}", file=sys.stderr)
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
        if hasattr(args, 'output') and args.output == "json":
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"[配置错误] {e}", file=sys.stderr)
            print("\n可用配置方式:", file=sys.stderr)
            print("  1. --config /path/to/umeng-config.json", file=sys.stderr)
            print("  2. export UMENG_CONFIG_PATH=/path/to/umeng-config.json", file=sys.stderr)
            print("  3. 在当前目录创建 umeng-config.json", file=sys.stderr)
        return 1
    
    except Exception as e:
        error_result = {"success": False, "error_type": type(e).__name__, "message": str(e)}
        if hasattr(args, 'output') and args.output == "json":
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"[错误] {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
