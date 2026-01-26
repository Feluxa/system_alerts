import os
import time
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def send_telegram_message(chat_id: str, text: str, bot_token: str | None = None):
    token = bot_token or BOT_TOKEN
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})


def format_panic(team_name: str, username: str) -> str:
    ts = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
    return f"🚨 PANIC в команде {team_name} от {username} ({ts})"
