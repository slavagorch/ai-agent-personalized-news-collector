import os, asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = int(os.getenv("CHAT_ID"))
bot = Bot(BOT_TOKEN)

async def main():
    await bot.send_message(chat_id=CHAT_ID, text="Test ping from bot")
    print("ping sent")

if __name__ == "__main__":
    asyncio.run(main())