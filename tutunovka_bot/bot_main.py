import os
from dotenv import load_dotenv
import telebot

load_dotenv('.env.bot')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Telegram bot token is not defined. Please check your .env.bot file.")


bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Как дела?")


bot.polling()