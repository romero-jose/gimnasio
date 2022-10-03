import os

from telegram import Bot

TOKEN = os.environ["TELEGRAM_TOKEN"]


def send_message(message, chat_id):
    bot = Bot(token=TOKEN)
    bot.sendMessage(chat_id, text=message)
