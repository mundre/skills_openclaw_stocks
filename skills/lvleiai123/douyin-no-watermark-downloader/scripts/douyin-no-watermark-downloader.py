import sys
import requests
import time
import logging
import os
from datetime import datetime
import re

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def get_douyin_real_video_urls(douyin_share_url: str, max_retries: int = 3) -> list[str]:
    """
    解析抖音分享链接，返回真实视频播放地址列表（按清晰度降序，最高清在前）。
    """
    base_url = "https://lvhomeproxy2.dpdns.org/api/hybrid/video_data"
    params = {
        "url": douyin_share_url,
        "minimal": False
    }

    retry_delay = 1

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"正在请求抖音视频解析接口... (第 {attempt}/{max_retries} 次尝试)")
            response = requests.get(base_url, params=params, timeout=20)

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ 解析成功！")

                bit_rate_list = data.get('data', {}).get('video', {}).get('bit_rate', [])
                if bit_rate_list:
                    url_list = bit_rate_list[0].get('play_addr', {}).get('url_list', [])
                else:
                    url_list = (
                        data
                        .get('data', {})
                        .get('video', {})
                        .get('download_addr', {})
                        .get('url_list', [])
                    )

                video_urls = [str(url) for url in url_list] if url_list else []
                return video_urls

            else:
                logger.warning(f"第 {attempt} 次请求失败，状态码: {response.status_code}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"❌ 所有 {max_retries} 次尝试均失败，最终状态码: {response.status_code}")
                    return []

        except Exception as e:
            logger.warning(f"第 {attempt} 次请求异常: {e}")
            if attempt < max_retries:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"❌ 所有 {max_retries} 次尝试均失败，最终错误: {e}")
                return []


def download_video_from_url(video_url: str, save_dir: str = None) -> str:
    if save_dir is None:
        home = os.path.expanduser("~")
        save_dir = os.path.join(home, "Desktop") if os.name != "nt" else os.path.join(home, "Desktop")

    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"douyin_video_{timestamp}.mp4"
    filepath = os.path.join(save_dir, filename)

    logger.info(f"正在下载视频到: {filepath}")

    # === 关键：添加防盗链所需的 headers ===
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    }

    try:
        response = requests.get(
            video_url,
            headers=headers,
            stream=True,
            timeout=600
        )
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info("✅ 视频下载完成！")
        return filepath

    except Exception as e:
        logger.error(f"❌ 视频下载失败: {e}")
        raise





def url_info_extra(url_info: str) -> str:
    """
    从抖音分享文本中提取短链接 https://v.douyin.com/xxxxx
    Args:
        url_info (str): 包含抖音分享链接的原始文本
    Returns:
        str: 提取到的完整短链接
    Raises:
        ValueError: 如果未找到有效链接
    """
    match = re.search(r'https://v\.douyin\.com/[^\s]+', url_info)
    if match:
        # print( match.group(0))
        return match.group(0)
    else:
        raise ValueError("未在输入文本中找到抖音短链接")



# ===== 命令行参数入口（直接解析+直接下载）=====
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
抖音无水印视频下载器
====================

用法:
  python douyin-no-watermark-downloader.py "抖音分享链接/分享文本"

示例:
  python douyin-no-watermark-downloader.py "https://v.douyin.com/XIkH2hGDHnw/"
  python douyin-no-watermark-downloader.py "复制打开抖音，看看【xxx】https://v.douyin.com/1A4yExNduOU/"
""")
        sys.exit(1)

    user_input = sys.argv[1]


    try:
        # 1. 提取链接
        share_url = url_info_extra(user_input)
        print(f"🔍 解析到有效链接: {share_url}")

        # 2. 获取真实视频地址
        urls = get_douyin_real_video_urls(share_url)
        if not urls:
            raise ValueError("未能解析出视频下载链接")

        print("\n✅ 获取到无水印视频地址")

        # 3. 直接下载（最高清）
        print("\n⬇️  开始下载视频...")
        saved_path = download_video_from_url(urls[0])
        print(f"\n🎉 下载完成！已保存到: {saved_path}")

    except Exception as e:
        print(f"\n❌ 失败: {str(e)}")
        sys.exit(1)