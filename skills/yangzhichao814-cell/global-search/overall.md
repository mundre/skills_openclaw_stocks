
# Global Search
# 注意：此脚本专门用于执行全面搜索（即同时搜索所有可用来源），当用户要求进行全面搜索时必须使用此脚本。
from aiohttp import FormData

# 定义四种请求配置
SEARCH_CONFIGS = [
    {
        "id":3,
        "name": "百度搜索",
        "mode": "network",
        "search_source": "baidu_search"
    },
    {   "id":2,
        "name": "谷歌搜索",
        "mode": "network",
        "search_source": "google_search"
    },
    {
        "id":1,
        "name": "百度AI搜索",
        "mode": "network",
        "search_source": "baidu_search_ai"
    },
    {
        "id":4,
        "name": "全库搜",
        "mode": "warehouse",
        "search_source": None  # 全库搜模式下不需要search_source
    }
]


import aiohttp
import asyncio
import json
API_URL = "https://clb.ciglobal.cn/web_search"  # 根据你的文档填写完整 URL
headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
keyword # 关键词
page  # 页数
async def fetch_data(semaphore, i):
    async with semaphore:  # 控制并发数
        print(f"开始请求 {i}")

        async with aiohttp.ClientSession() as session:
            result_data = None
            for item in SEARCH_CONFIGS:
                if item['id'] == i:
                    result_data = item
                    break
            data = {
                "keyword": keyword,
                "page": page,
                "mode": result_data['mode'],
                "search_source": result_data['search_source']
            }
            async with session.post(API_URL, headers=headers,data=data) as response:
                # 重要：必须 await response.json()
                try:
                    result = await response.json()
                except Exception as e:
                    print(e)
                    result = {}
                references = result.get('references')
                return references

async def main():
    semaphore = asyncio.Semaphore(5)  # 最多同时5个请求
    tasks = [fetch_data(semaphore, i) for i in range(1,5)]
    results = await asyncio.gather(*tasks)
    result = []
    for item in results:
        result += item
    print(result)
    return result

asyncio.run(main())
