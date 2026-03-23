#!/usr/bin/env python3
"""
Ask Stocki a financial question (instant mode).

Usage:
    python3 stocki-instant.py <question> [--timezone Asia/Shanghai]

Stdout: markdown answer
Stderr: error messages
Exit:   0 success, 1 auth error, 2 service error
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


STOCKI_URL = "https://instant-agent-test.miti.chat/"
ASSISTANT_ID = "InstantModeAgent"


async def query(question: str, timezone: str) -> str:
    from langgraph_sdk import get_client
    from langgraph.pregel.remote import RemoteGraph

    api_key = os.environ.get("STOCKI_USER_API_KEY", "")

    # Build time_prompt from timezone
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        print(f"Unknown timezone '{timezone}', falling back to Asia/Shanghai", file=sys.stderr)
        tz = ZoneInfo("Asia/Shanghai")
    time_prompt = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    client = get_client(url=STOCKI_URL)
    graph = RemoteGraph(ASSISTANT_ID, client=client)

    thread = await client.threads.create()
    thread_id = thread["thread_id"]

    response = await graph.ainvoke(
        input={
            "query": question,
            "time_prompt": time_prompt,
            "agent_type": "instant",
        },
        config={"configurable": {"thread_id": thread_id}},
    )

    return response.get("answer", "")


def main():
    parser = argparse.ArgumentParser(description="Ask Stocki a financial question.")
    parser.add_argument("question", help="The question to ask")
    parser.add_argument(
        "--timezone", default="Asia/Shanghai",
        help="IANA timezone for interpreting relative dates (default: Asia/Shanghai)",
    )
    args = parser.parse_args()

    try:
        answer = asyncio.run(query(args.question, args.timezone))
    except Exception as e:
        print(f"Stocki unavailable: {e}", file=sys.stderr)
        sys.exit(2)

    if answer is None:
        sys.exit(1)

    print(answer)


if __name__ == "__main__":
    main()
