# src/tg_bot.py

import os, csv, logging
from dotenv import load_dotenv
from telegram import Bot  # synchronous client
from html import escape

# ─── Config & Logging ───────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "feedback.csv")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

bot = Bot(BOT_TOKEN)

# ─── Feedback CSV ────────────────────────────────────────────
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="") as f:
        csv.writer(f).writerow(["url", "liked"])


def _load_feedback():
    fb = {}
    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            fb[row["url"]] = int(row["liked"])
    return fb


def _save_feedback(fb):
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["url", "liked"])
        for u, l in fb.items():
            w.writerow([u, l])


# ─── Send Telegram Digest ────────────────────────────────────
# feedback CSV code unchanged…

async def send_tg(picks):
    """
    Async: picks is a list of dicts with 'title','url','summary'.
    """
    logging.info(f"▶︎ Sending {len(picks)} articles via Telegram")
    for art in picks:
        safe_title = escape(art["title"])
        safe_summary = escape(art["summary"])
        url = art["url"]

        html_msg = (
            f"<b>{safe_title}</b>\n"
            f"{safe_summary}\n"
            f"<a href=\"{url}\">Read more</a>"
        )

        await bot.send_message(
            chat_id=CHAT_ID,
            text=html_msg,
            parse_mode="HTML"
        )
    logging.info("✓ Digest sent")