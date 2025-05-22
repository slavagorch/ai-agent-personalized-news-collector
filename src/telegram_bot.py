# src/telegram_bot.py

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logging.basicConfig(level=logging.INFO)

import os
import csv
from dotenv import load_dotenv
from pipeline import run
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()  # now BOT_TOKEN and CHAT_ID will be read
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = int(os.getenv("CHAT_ID"))
CSV_PATH  = os.path.join(os.path.dirname(__file__), "..", "feedback.csv")

# 1. Create feedback.csv if missing
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "liked"])

def _load_feedback():
    fb = {}
    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            fb[row["url"]] = int(row["liked"])
    return fb

def _save_feedback(fb: dict):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "liked"])
        for url, liked in fb.items():
            writer.writerow([url, liked])

# Echo handler to grab your chat ID (one-time)
async def echo_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    logging.info(f"Echoed chat ID: {cid}")
    await update.message.reply_text(f"Your chat ID is: {cid}")

# /digest command handler
async def send_digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    articles = run()
    for art in articles:
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("👍", callback_data=f"like|{art['url']}"),
            InlineKeyboardButton("👎", callback_data=f"dislike|{art['url']}")
        ]])
        text = f"*{art['title']}*\n{art['summary']}\n{art['url']}"
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=text,
            parse_mode="Markdown",
            reply_markup=kb
        )

# Button callback handler
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action, url = update.callback_query.data.split("|", 1)
    fb = _load_feedback()
    fb[url] = 1 if action == "like" else 0
    _save_feedback(fb)
    await update.callback_query.answer("👍 saved" if fb[url] else "👎 saved")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # register handlers
    app.add_handler(CommandHandler("digest", send_digest))
    app.add_handler(CallbackQueryHandler(handle_feedback))
    app.add_handler(MessageHandler(filters.ALL, echo_id))  # one-time

    app.run_polling()

if __name__ == "__main__":
    main()