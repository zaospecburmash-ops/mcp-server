import os
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "8080"))
MAKE_WEBHOOK = os.getenv("MAKE_WEBHOOK", "")

mcp = FastMCP(
    "Meeting Operations",
    json_response=True,
    host=HOST,
    port=PORT,
)


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not url:
        return {
            "ok": False,
            "error": "MAKE_WEBHOOK is empty. Set it in environment variables.",
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
    tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Создать обычные задачи в Bitrix24 через Make.
    Передаёт в Make meeting_date, meeting_title и массив tasks.
    """
    payload = {
        "meeting_date": meeting_date,
        "meeting_title": meeting_title,
        "tasks": tasks,
        "unassigned_tasks": [],
    }
    return post_json(MAKE_WEBHOOK, payload)


@mcp.tool()
def send_unassigned_to_maxim(
    meeting_date: str,
    meeting_title: str,
    unassigned_tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Отправить спорные задачи в Make.
    Дальше Make сам направит их по своей ветке.
    """
    payload = {
        "meeting_date": meeting_date,
        "meeting_title": meeting_title,
        "tasks": [],
        "unassigned_tasks": unassigned_tasks,
    }
    return post_json(MAKE_WEBHOOK, payload)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
