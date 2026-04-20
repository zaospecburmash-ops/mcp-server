import os
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Meeting Operations", json_response=True)

MAKE_WEBHOOK = os.getenv("MAKE_WEBHOOK", "")

def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not url:
        return {
            "ok": False,
            "error": "Webhook URL is empty. Set env var first."
        }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        return {
            "ok": resp.ok,
            "status_code": resp.status_code,
            "response_text": resp.text[:4000],
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
        }


@mcp.tool()
def create_bitrix_tasks(
    meeting_date: str,
    meeting_title: str,
    tasks: list[dict[str, Any]]
) -> dict[str, Any]:
    payload = {
        "meeting_date": meeting_date,
        "meeting_title": meeting_title,
        "tasks": tasks,
        "unassigned_tasks": []
    }
    return post_json(MAKE_WEBHOOK, payload)


@mcp.tool()
def send_unassigned_to_maxim(
    meeting_date: str,
    meeting_title: str,
    unassigned_tasks: list[dict[str, Any]]
) -> dict[str, Any]:
    payload = {
        "meeting_date": meeting_date,
        "meeting_title": meeting_title,
        "tasks": [],
        "unassigned_tasks": unassigned_tasks
    }
    return post_json(MAKE_WEBHOOK, payload)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")