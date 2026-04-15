import os
import sys
import requests
import json

SKILLBOSS_API_KEY = os.environ.get("SKILLBOSS_API_KEY")
API_BASE = "https://api.skillboss.co/v1"


def ai_picture_book_task_create(api_key: str, method: int, content: str):
    url = f"{API_BASE}/pilot"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    style = "static_picture_book" if method == 9 else "dynamic_picture_book"
    body = {
        "type": "video",
        "inputs": {
            "prompt": content,
            "style": style,
        },
        "prefer": "balanced",
    }
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    result = response.json()
    if "detail" in result:
        raise RuntimeError(result["detail"])
    return result["result"]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ai_picture_book_task_create.py <method> <content>")
        sys.exit(1)

    method = int(sys.argv[1])
    if method not in [9, 10]:
        print("Error: method must be 9 or 10.")
        sys.exit(1)
    content = sys.argv[2]

    api_key = os.getenv("SKILLBOSS_API_KEY")
    if not api_key:
        print("Error: SKILLBOSS_API_KEY must be set in environment.")
        sys.exit(1)
    try:
        results = ai_picture_book_task_create(api_key, method, content)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

