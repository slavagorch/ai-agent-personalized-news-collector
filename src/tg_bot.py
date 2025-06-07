# src/tg_bot.py

import os, csv, logging
from dotenv import load_dotenv
from telegram import Bot, Update
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import hashlib


# ─── Config & Logging ───────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
FEEDBACK_CSV = 'src/feedback.csv'
MAPPING_CSV     = 'src/url_map.csv'


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

bot = Bot(BOT_TOKEN)


# ─── Feedback CSV ────────────────────────────────────────────
if not os.path.exists(FEEDBACK_CSV):
    with open(FEEDBACK_CSV, "w", newline="") as f:
        csv.writer(f).writerow(["url", "liked"])

if not os.path.exists(MAPPING_CSV):
    with open(MAPPING_CSV, "w", newline="") as f:
        csv.writer(f).writerow(["hash", "url"])

def get_url_hash(url):
    """Generate a short hash for a URL."""
    return hashlib.md5(url.encode()).hexdigest()[:8]


# ─── Send Telegram Digest ────────────────────────────────────

# Global variable to store current batch of articles
current_articles = {}


async def send_tg(picks):
    """
    Async: picks is a list of dicts with 'title','url','summary'.
    Persists hash→url mapping and sends each article with callback_data=hash.
    """
    # 1) Persist the hash→url map
    with open(MAPPING_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["hash", "url"])
        for art in picks:
            h = get_url_hash(art["url"])
            writer.writerow([h, art["url"]])

    logging.info(f"▶︎ Sending {len(picks)} articles via Telegram")

    # 2) Send each message using the same hash
    for art in picks:
        url = art["url"]
        h = get_url_hash(url)
        safe_title = escape(art["title"])
        safe_summary = escape(art["summary"])

        html_msg = f"<b>{safe_title}</b>\n{safe_summary}"

        keyboard = [
            [InlineKeyboardButton("Read more", url=url)],
            [
                InlineKeyboardButton("👍", callback_data=f"like|{h}"),
                InlineKeyboardButton("👎", callback_data=f"dislike|{h}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await bot.send_message(
            chat_id=CHAT_ID,
            text=html_msg,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    logging.info("✓ Digest sent")

async def handle_feedback(update):
    logging.info("Handling feedback")
    action, article_hash = update.callback_query.data.split("|", 1)
    liked = 1 if action == "like" else 0

    # Lookup URL by hash from mapping CSV
    url = None
    with open(MAPPING_CSV, newline="") as f:
        for row in csv.DictReader(f):
            if row["hash"] == article_hash:
                url = row["url"]
                break

    if not url:
        logging.error(f"Hash {article_hash} not found in mapping")
        await update.callback_query.answer("Error: Article not found")
        return

    # Read existing feedback
    rows = []
    if os.path.exists(FEEDBACK_CSV):
        with open(FEEDBACK_CSV, newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)

    # Update or append feedback
    updated = False
    for row in rows:
        if row[0] == url:
            row[1] = str(liked)
            updated = True
            break
    if not updated:
        rows.append([url, str(liked)])

    # Write back all feedback
    with open(FEEDBACK_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "liked"])
        writer.writerows(rows)

    await update.callback_query.answer("Saved 👍" if liked else "Saved 👎")


async def poll_updates():
    offset = 0
    while True:
        try:
            updates = await bot.get_updates(offset=offset, timeout=30)
            for update in updates:
                offset = update.update_id + 1
                if update.callback_query:
                    await handle_feedback(update)
        except Exception as e:
            logging.error(f"Error in polling: {e}")
            await asyncio.sleep(1)

async def main():
    # Ensure webhook is deleted
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(2)
    
    logging.info("Starting bot...")
    try:
        await poll_updates()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())