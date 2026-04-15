#!/usr/bin/env python3
"""
公众号热门数据查询脚本（最终版 - 禁用 SNI + 支持 chunked + gzip）
"""

import sys
import argparse
import json
import requests


def fetch_via_no_sni(base_url: str, params: dict, headers: dict, timeout: int = 60):
    """
    使用 requests 发起 HTTPS 请求（保持证书与主机名校验）
    """
    response = requests.get(
        base_url,
        params=params,
        headers=headers,
        timeout=timeout,
    )
    return response.status_code, response.text


def fetch_gzh_trends(keyword: str, debug: bool = False, max_retries: int = 3, start_date: str = None):
    """
    调用新接口获取公众号热门数据

    Args:
        keyword: 搜索关键词（多个关键词用逗号分隔，最多5个，总长度不超过200）
        debug: 是否打印调试信息
        max_retries: 最大重试次数
        start_date: 开始日期，格式 yyyy-MM-dd，最长为最近30天

    Returns:
        dict: 包含3类爆款数据

    Raises:
        Exception: 当API调用失败时抛出异常
    """
    base_url = "https://onetotenvip.com/skill/cozeSkill/getWxCozeSkillData"
    params = {
        "keyword": keyword,
        "source": "公众号爆款写文案-ClawHub",
    }

    # 添加开始日期参数
    if start_date:
        params["startDate"] = start_date
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            if debug:
                print(f"\n=== DEBUG: 第 {attempt + 1} 次尝试 ===", file=sys.stderr)

            status_code, body = fetch_via_no_sni(base_url, params, headers)

            if debug:
                print(f"状态码: {status_code}", file=sys.stderr)
                print(f"响应长度: {len(body)} 字节", file=sys.stderr)

            if status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {status_code}")

            data = json.loads(body)

            if "data" not in data:
                error_msg = data.get("msg", "未知错误")
                raise Exception(f"API 错误: {error_msg}")

            result_data = data.get("data", {})

            if debug:
                print("=== DEBUG: API 返回的 data 字段键 ===", file=sys.stderr)
                print(json.dumps(list(result_data.keys()), ensure_ascii=False, indent=2), file=sys.stderr)

            return {
                "keyword": keyword,
                "low_fan_explosive": result_data.get("lowPowderExplosiveArticle", []),
                "read_top": result_data.get("tenWReadingRank", []),
                "original_top": result_data.get("originalRank", [])
            }

        except Exception as e:
            last_error = str(e)
            if debug:
                print(f"  错误: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
            import time
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue

    raise Exception(f"{last_error}（已尝试 {max_retries} 次）")


def format_output(data: dict, max_items: int = None):
    """
    格式化输出热门数据（表格形式）

    Args:
        data: 原始数据
        max_items: 每类爆款数据最多展示数量，None 表示展示所有数据
    """

    def process_title(item):
        """处理标题：转义特殊字符，空标题使用summary替代，并添加作品链接"""
        title = item.get('title', '')
        # 如果标题为空，尝试使用 summary 字段
        if not title or title.strip() == '':
            summary = item.get('summary', '')
            if summary:
                # 移除 summary 中的换行符并截取前30个字符
                title = summary.replace('\n', ' ').replace('\r', ' ').strip()[:30]
                if len(summary) > 30:
                    title = title + '...'

        if not title or title.strip() == '':
            title = '无标题'

        # 转义 Markdown 表格特殊字符（|）
        title = title.replace('|', '\\|')
        # 移除换行符
        title = title.replace('\n', ' ').replace('\r', ' ')
        # 移除多余空格
        title = ' '.join(title.split())

        # 截断过长标题
        if len(title) > 30:
            title = title[:30] + "..."

        # 添加作品链接（公众号使用 oriUrl）
        ori_url = item.get('oriUrl', '')
        if ori_url:
            title = f"[{title}]({ori_url})"

        return title

    output = []

    # 按 photoId 去重（API 返回数据可能有重复）
    def dedup_items(items):
        seen = set()
        result = []
        for item in items:
            photo_id = item.get('photoId', '')
            if photo_id and photo_id not in seen:
                seen.add(photo_id)
                result.append(item)
        return result

    # 检查是否有任何数据
    low_fan_items = dedup_items(data.get("low_fan_explosive", []))
    read_top_items = dedup_items(data.get("read_top", []))
    original_top_items = dedup_items(data.get("original_top", []))

    total_count = len(low_fan_items) + len(read_top_items) + len(original_top_items)

    # 如果所有类型都没有数据，输出友好提示
    if total_count == 0:
        keyword = data.get("keyword", "")
        output.append(f"# 公众号爆款数据分析报告\n\n**关键词**：{keyword}\n\n**爆款总数**：{total_count} 条\n\n")
        output.append("---\n\n")
        output.append("## 暂无相关爆款数据\n\n")
        output.append(f"很抱歉，当前关键词 **「{keyword}」** 尚未有足够的爆款文章数据。\n\n")
        output.append("### 可能原因\n\n")
        output.append("- 该关键词相对小众或新兴，爆款内容积累较少\n")
        output.append("- 近期该赛道热度较低，暂无突出爆款文章\n")
        output.append("- 关键词表述方式可以更加具体或热门\n\n")
        output.append("### 建议操作\n\n")
        output.append("- 更换为更热门的关键词，如：**\"职场干货\"**、**\"个人成长\"**、**\"理财知识\"** 等\n")
        output.append("- 尝试更细分的长尾关键词，如：**\"副业赚钱\"**、**\"时间管理技巧\"** 等\n")
        output.append("- 输入其他感兴趣的领域或赛道进行追踪\n\n")
        output.append("---\n\n")
        output.append("*数据来源：公众号爆款雷达，每日更新最新热门内容*\n")
        return "\n".join(output)

    # 1. 低粉高阅读爆款
    items = low_fan_items
    if max_items is not None:
        items = items[:max_items]

    # 计算实际展示的总数
    display_low_fan = items
    display_read_top = read_top_items[:max_items] if max_items is not None else read_top_items
    display_original_top = original_top_items[:max_items] if max_items is not None else original_top_items
    display_total = len(display_low_fan) + len(display_read_top) + len(display_original_top)

    # 输出标题和总数量
    keyword = data.get("keyword", "")
    output.append(f"# 公众号爆款数据分析报告\n\n**关键词**：{keyword}\n\n**爆款总数**：{display_total} 条\n\n---\n")

    output.append(f"\n## 爆款文章（共 {len(items)} 条）")
    output.append(f"### - **低粉高阅读爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | **阅读数** | 在看 | 点赞 | 评论 | 分享 |")
        output.append("|------|------|------|---------|------|------|------|------|")

        for idx, item in enumerate(items, 1):
            account_id = item.get('accountId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', '0')

            # 公众号作者链接使用二维码页面
            if account_id:
                author_link = f"https://open.weixin.qq.com/qr/code?username={account_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            output.append(f"| {idx} | {title} | {author_str} | **{item.get('clicksCount', '0')}** | {item.get('watchCount', '0')} | {item.get('likeCount', '0')} | {item.get('commentCount', '0')} | {item.get('shareCount', '0')} |")

    # 2. 阅读靠前爆款
    items = read_top_items[:max_items] if max_items is not None else read_top_items

    output.append(f"\n### - **阅读靠前爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | **阅读数** | 在看 | 点赞 | 评论 | 分享 |")
        output.append("|------|------|------|---------|------|------|------|------|")

        for idx, item in enumerate(items, 1):
            account_id = item.get('accountId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', '0')

            if account_id:
                author_link = f"https://open.weixin.qq.com/qr/code?username={account_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            output.append(f"| {idx} | {title} | {author_str} | **{item.get('clicksCount', '0')}** | {item.get('watchCount', '0')} | {item.get('likeCount', '0')} | {item.get('commentCount', '0')} | {item.get('shareCount', '0')} |")

    # 3. 原创靠前爆款
    items = original_top_items[:max_items] if max_items is not None else original_top_items

    output.append(f"\n### - **原创靠前爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | **阅读数** | 在看 | 点赞 | 评论 | 分享 |")
        output.append("|------|------|---------|------|------|------|------|------|")

        for idx, item in enumerate(items, 1):
            account_id = item.get('accountId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', '0')

            if account_id:
                author_link = f"https://open.weixin.qq.com/qr/code?username={account_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            output.append(f"| {idx} | {title} | {author_str} | **{item.get('clicksCount', '0')}** | {item.get('watchCount', '0')} | {item.get('likeCount', '0')} | {item.get('commentCount', '0')} | {item.get('shareCount', '0')} |")

    return "\n".join(output)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='公众号热门数据查询工具')
    parser.add_argument('--keyword', required=True, help='搜索关键词')
    parser.add_argument('--max-items', type=int, default=10,
                       help='每类爆款内容最多展示数量（默认10条）')
    parser.add_argument('--output-format', choices=['text', 'json', 'markdown'],
                       default='markdown', help='输出格式：text（文本表格）、json（JSON格式）或 markdown（Markdown格式，默认）')
    parser.add_argument('--start-date', type=str, default=None,
                       help='开始日期，格式 yyyy-MM-dd（默认最近30天）')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='最大重试次数（默认3次）')

    args = parser.parse_args()

    try:
        data = fetch_gzh_trends(args.keyword, debug=args.debug, max_retries=args.max_retries, start_date=args.start_date)

        # 生成输出内容
        if args.output_format == 'json':
            output_content = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            output_content = format_output(data, max_items=args.max_items)

        # 直接输出到控制台
        print(output_content)

    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
