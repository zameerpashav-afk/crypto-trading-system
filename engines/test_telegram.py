import asyncio
import os
from telegram import Bot

# Load from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

async def send_test():
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Telegram Bot Test Successful!")

# Run the async function
asyncio.run(send_test())