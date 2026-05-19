"""Telegram notifier — sends daily stats and error alerts to your Telegram bot."""

import requests, logging, os
from datetime import date
from config import DATA_DIR

logger = logging.getLogger("pinbot.telegram")

TELEGRAM_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT   = os.getenv("TELEGRAM_CHAT_ID", "")


def _send(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
    except Exception as e:
        logger.warning(f"Telegram send failed: {e}")


def notify_batch_done(posted: int, total: int):
    _send(
        f"✅ *PinBot* — Batch complete\n"
        f"Posted: {posted} pins\n"
        f"Today total: {total}/{os.getenv('MAX_PINS_PER_DAY', 15)}\n"
        f"Date: {date.today()}"
    )


def notify_error(module: str, error: str):
    _send(
        f"🔴 *PinBot ERROR* — {module}\n"
        f"`{str(error)[:200]}`"
    )


def notify_token_expired():
    _send("⚠️ *PinBot* — Pinterest token expired! Refresh your access token.")


def notify_daily_summary(stats: dict):
    today = date.today().isoformat()
    s = stats.get(today, {})
    _send(
        f"📊 *PinBot Daily Summary* — {today}\n"
        f"Pins posted: {s.get('pins_posted', 0)}\n"
        f"Errors: {s.get('errors', 0)}\n"
        f"Status: {'✅ Clean' if s.get('errors', 0) == 0 else '⚠️ Check logs'}"
    )
