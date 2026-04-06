from dotenv import load_dotenv
import os
import telegram

# Load .env variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telegram.Bot(token=TELEGRAM_TOKEN)

bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Telegram Bot Test Successful!")
print("Message sent!")