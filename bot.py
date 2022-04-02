import os

from telegram import Bot

CHAT_ID = os.environ["CHAT_ID"]
TOKEN = os.environ["TELEGRAM_TOKEN"]


def send_message(message):
    bot = Bot(token=TOKEN)
    bot.sendMessage(chat_id=CHAT_ID, text=message)
