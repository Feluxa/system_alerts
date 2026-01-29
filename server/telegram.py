import os
import html
import httpx
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def send_telegram_message(chat_id: str, text: str, bot_token: str | None = None):
    token = bot_token or BOT_TOKEN
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


def format_alert(team_name: str, username: str, text: str | None = None) -> str:
    try:
        ts = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    title = text.strip() if text else "PANIC"
    title_html = html.escape(title)
    team_html = html.escape(team_name)
    user_html = html.escape(username)
    return (
        f"\U0001F6A8 <b><u>{title_html}</u></b>\n"
        f"\u0432 \u043a\u043e\u043c\u0430\u043d\u0434\u0435 {team_html}\n"
        f"\u043e\u0442 {user_html}\n"
        f"({ts})"
    )
