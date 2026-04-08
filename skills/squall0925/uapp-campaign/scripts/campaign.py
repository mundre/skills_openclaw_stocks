#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""uapp-campaign: 小程序推广链接管理 CLI

功能目标：
- 读取 umeng-config.json（支持 --config / UMENG_CONFIG_PATH / 当前目录）
- 解析应用（支持 --app / --account，含模糊匹配，仅支持小程序应用）
- 支持创建推广链接（--create）
- 支持查询推广活动列表（--list --type campaign）
- 支持查询推广渠道列表（--list --type channel）
- 输出：
  - 文本模式：表格/摘要
  - JSON 模式：结构化数据
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
# 应用解析（含模糊匹配）
# -------------------------


def normalize_app_name(name: str) -> str:
    """去除半角/全角空格，用于模糊匹配。"""
    return name.replace(" ", "").replace("\u3000", "")


MINI_PROGRAM_PLATFORMS = ["微信小程序", "支付宝小程序", "百度小程序", "字节跳动小程序", "QQ小程序", "H5", "小游戏"]


def is_mini_program(platform: str) -> bool:
    """判断是否为小程序/H5/小游戏平台。"""
    return platform in MINI_PROGRAM_PLATFORMS


def find_app_by_name(config: dict, app_name: str, account_id: str | None = None, mini_only: bool = True):
    """按应用名称查找应用配置，支持精确匹配 + 去空格模糊匹配。"""
    matches = []
    normalized_input = normalize_app_name(app_name)

    for account in config.get("accounts", []):
        if account_id and account.get("id") != account_id:
            continue
        for app in account.get("apps", []):
            platform = app.get("platform", "")
            if mini_only and not is_mini_program(platform):
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


def resolve_app(config: dict, app_name: str | None, account_id: str | None) -> dict:
    """解析最终使用的应用配置。"""
    if app_name:
        result = find_app_by_name(config, app_name, account_id=account_id, mini_only=True)
        if not result:
            available = []
            for account in config.get("accounts", []):
                for app in account.get("apps", []):
                    if is_mini_program(app.get("platform", "")):
                        available.append(f"{app.get('name', '')} ({app.get('platform', '')})")
            raise ValueError(f"未找到名称匹配的小程序应用: {app_name}\n可用小程序应用: {', '.join(available)}")
        if isinstance(result, list):
            raise ValueError("存在多个同名应用，请通过 --account 进一步限定")
        return result

    raise ValueError("未指定应用，请使用 --app 指定小程序应用名称")


# -------------------------
# Umeng SDK 调用
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


def create_campaign(data_source_id: str, campaign_name: str, channel_name: str, path: str | None = None) -> dict:
    """创建推广链接。"""
    from aop import api

    req = api.UmengUminiCreateCampaignRequest()
    req.dataSourceId = data_source_id
    req.campaignName = campaign_name
    req.channelName = channel_name
    if path:
        req.path = path

    resp = req.get_response()
    if isinstance(resp, str):
        import json
        resp = json.loads(resp)
    return resp if isinstance(resp, dict) else {}


def get_scene_info_list(data_source_id: str, source_type: str = "campaign") -> dict:
    """获取渠道或活动信息列表。"""
    from aop import api

    req = api.UmengUminiGetSceneInfoListRequest()
    req.dataSourceId = data_source_id
    req.sourceType = source_type

    resp = req.get_response()
    if isinstance(resp, str):
        import json
        resp = json.loads(resp)
    return resp if isinstance(resp, dict) else {}


# -------------------------
# 输出格式化
# -------------------------


def format_create_result(result: dict, campaign_name: str, channel_name: str, path: str | None = None) -> str:
    """格式化创建推广链接结果。"""
    if not result.get("success"):
        return f"创建失败: {result.get('msg', '未知错误')}"

    campaign_code = result.get("data", "")
    
    lines = []
    lines.append("推广链接创建成功")
    lines.append("-" * 50)
    lines.append(f"活动名称: {campaign_name}")
    lines.append(f"渠道名称: {channel_name}")
    lines.append(f"活动代码: {campaign_code}")
    if path:
        lines.append(f"落地页路径: {path}")
    
    return "\n".join(lines)


def format_list_result(result: dict, source_type: str) -> str:
    """格式化活动/渠道列表。"""
    data = result.get("data", [])
    
    if not data:
        type_name = "推广活动" if source_type == "campaign" else "推广渠道"
        return f"暂无{type_name}数据"

    type_name = "推广活动" if source_type == "campaign" else "推广渠道"
    lines = []
    lines.append(f"{type_name}列表（共 {len(data)} 条）")
    lines.append("-" * 80)
    lines.append(f"{'序号':<6} {'名称':<20} {'创建时间':<20} {'推广链接'}")
    lines.append("-" * 80)

    for i, item in enumerate(data):
        name = item.get("name", "")[:18]
        create_time = item.get("createDateTime", "")
        url = item.get("url", "")
        # 截断过长的 URL
        if len(url) > 40:
            url = url[:37] + "..."
        lines.append(f"{i+1:<6} {name:<20} {create_time:<20} {url}")

    return "\n".join(lines)


def build_json_output(data: dict, success: bool = True) -> str:
    """构建 JSON 输出。"""
    output = {"success": success, "data": data}
    return json.dumps(output, ensure_ascii=False, indent=2)


def build_error_json(message: str) -> str:
    """构建错误 JSON 输出。"""
    return build_json_output({"error": message}, success=False)


# -------------------------
# CLI 入口
# -------------------------


def main():
    parser = argparse.ArgumentParser(
        description="uapp-campaign: 小程序推广链接管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 创建推广链接
  python3 scripts/campaign.py --create --name "春季换新季" --channel "抖音" --app "友小盟数据官"

  # 创建推广链接（带落地页路径）
  python3 scripts/campaign.py --create --name "春季特卖" --channel "微信推广" --path "mainpage" --app "友小盟数据官"

  # 查询推广活动列表
  python3 scripts/campaign.py --list --type campaign --app "友小盟数据官"

  # 查询推广渠道列表
  python3 scripts/campaign.py --list --type channel --app "友小盟数据官"

  # JSON 输出
  python3 scripts/campaign.py --list --type campaign --app "友小盟数据官" --json
"""
    )

    # 配置与应用
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--app", required=True, help="应用名称（仅支持小程序应用）")
    parser.add_argument("--account", help="账号 ID")

    # 操作模式（互斥）
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--create", action="store_true", help="创建推广链接")
    mode_group.add_argument("--list", action="store_true", help="查询推广活动/渠道列表")

    # 创建模式参数
    parser.add_argument("--name", help="活动名称（创建模式必填）")
    parser.add_argument("--channel", help="渠道名称（创建模式必填）")
    parser.add_argument("--path", help="落地页路径（可选）")

    # 列表模式参数
    parser.add_argument("--type", choices=["campaign", "channel"], default="campaign",
                        help="列表类型：campaign(活动)/channel(渠道)，默认 campaign")

    # 输出格式
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    args = parser.parse_args()

    try:
        # 参数校验
        if args.create:
            if not args.name:
                raise ValueError("缺少必填参数: --name")
            if not args.channel:
                raise ValueError("缺少必填参数: --channel")

        # 加载配置
        config_path = resolve_config_path(args.config)
        config = load_config(config_path)

        # 解析应用
        app_info = resolve_app(config, args.app, args.account)
        data_source_id = app_info["app"]["appkey"]

        # 初始化 SDK
        init_sdk(app_info["apiKey"], app_info["apiSecurity"])

        # 执行操作
        result = None
        output = ""

        if args.create:
            result = create_campaign(data_source_id, args.name, args.channel, args.path)
            if args.json:
                output = build_json_output(result)
            else:
                output = format_create_result(result, args.name, args.channel, args.path)

        elif args.list:
            result = get_scene_info_list(data_source_id, args.type)
            if args.json:
                output = build_json_output(result)
            else:
                output = format_list_result(result, args.type)

        # 输出结果
        print(output)

    except Exception as e:
        if args.json:
            print(build_error_json(str(e)))
        else:
            print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
