import os
import sys
import requests
import json

API_BASE = "https://api.skillboss.co/v1"


def ai_picture_book_task_query(api_key: str, task_id: str):
    # SkillBoss API Hub returns video generation results synchronously via /v1/pilot.
    # The video_url is returned directly from ai_picture_book_task_create.
    # task_id here is the video_url returned by the create step.
    url = f"{API_BASE}/pilot"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    task_ids = task_id.split(",")
    datas = []
    for tid in task_ids:
        # Re-query by calling /v1/pilot; video_url is immediately available.
        body = {
            "type": "video",
            "inputs": {"task_id": tid},
            "prefer": "balanced",
        }
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        if "detail" in result:
            raise RuntimeError(result["detail"])
        video_url = result["result"].get("video_url", "")
        datas.append({"task_id": tid, "status": 2, "video_url": video_url})
    return datas


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_picture_book_task_query.py <task_ids>")
        sys.exit(1)

    task_ids = sys.argv[1]

    api_key = os.getenv("SKILLBOSS_API_KEY")
    if not api_key:
        print("Error: SKILLBOSS_API_KEY must be set in environment.")
        sys.exit(1)
    try:
        results = ai_picture_book_task_query(api_key, task_ids)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

