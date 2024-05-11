import datetime
import os
import threading
import time
import jwt

import telebot
from dotenv import load_dotenv
import tg_analytic
from models import PostgreSQLQueries

load_dotenv('.env.bot')

# TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TOKEN = "6899212190:AAH9ljFqfIZxcvgUfD4OqXPlQ9x7ERf2DNg"

if TOKEN is None:
    raise ValueError("Telegram bot token is not defined. Please check your .env.bot file.")

bot = telebot.TeleBot(TOKEN)

MODEL = PostgreSQLQueries(os.getenv('DB_NAME'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_HOST'),
                          os.getenv('DB_PORT'))

encoded_jwt = jwt.encode({"password": "password", "tg_username": "vasya"}, "auth_in_bot", algorithm="HS256")
print(encoded_jwt)
users = []


def tic_tac():
    i = 0

    while True:

        this_moment = datetime.datetime.now()
        for user in users:
            if this_moment.hour == 12 and this_moment.minute == 0 and this_moment.second == 0 and this_moment.day == user.date_in.day and this_moment.month == user.date_in.month and this_moment.year == user.date_in.year:
                bot.send_message(user.tg_id, "Ваш вылет завтра!")

        i += 1
        time.sleep(1)


@bot.message_handler(commands=['start'])
def save_chat_id(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    #button_flight = telebot.types.KeyboardButton(text="Следующий вылет?", callback_data="f")
    #keyboard.add(button_flight)
    bot.send_message(message.chat.id,
                     'Здравствуйте, вы зарегестрировались на проекте Tutuorist! Я здесь, чтобы напоминать вам о ваших вылетах и багаже, который вы хотели взять с собой. Со мной вы точно ничего не забудуете!',
                     reply_to_message_id=message.message_id, reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def send_text(message):
    tg_analytic.statistics(message.chat.id, message.text)
    if message.text[:10] == "статистика" or message.text[:10] == "Статистика":
        st = message.text.split(" ")
        if "txt" in st or "тхт" in st:
            tg_analytic.analysis(st, message.chat.id)
            with open("%s.txt" % message.chat.id, "r", encoding="UTF-8") as file:
                bot.send_document(message.chat.id, file)
                tg_analytic.remove(message.chat.id)
        else:
            messages = tg_analytic.analysis(st, message.chat.id)
            bot.send_message(message.chat.id, messages)
    else:
        payload = jwt.decode(jwt=message.text, key=os.getenv('SECRET_KEY_JWT'), algorithms=["HS256"])
        #payload = jwt.decode(jwt=encoded_jwt, key="auth_in_bot", algorithms=["HS256"])
        data = MODEL.get_user_fields(payload["password"], payload["username"])
        #if data is not None:
        #    data["tg_id"] = message.chat.id
        #    users.append(data)
        bot.send_message(message.chat.id,
                         f'{str(payload)} \n {str(data)}',
                         reply_to_message_id=message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "f")
def but1_pressed(call):
    for user in users:
        if user["tg_id"] == call.message.chat.id:
            text = MODEL.get_route_fields(user['id'])
    bot.send_message(call.message.chat.id, text)


timThr = threading.Thread(target=tic_tac)
timThr.start()
bot.polling(none_stop=True)
