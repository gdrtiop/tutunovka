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

users = []


def tic_tac():
    i = 0

    while True:

        this_moment = datetime.datetime.now()
        routes = MODEL.get_routes()
        for route in list(routes):
            if this_moment.hour == 12 and this_moment.minute == 0 and this_moment.second == 0 and this_moment.day == (route.date_in.day - 1) and this_moment.month == route.date_in.month and this_moment.year == route.date_in.year:
                for user in users:
                    if route.author_id == user.id:
                        bot.send_message(user.tg_id, "Ваш вылет завтра!")

        i += 1
        time.sleep(1)


@bot.message_handler(commands=['start'])
def save_chat_id(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_flight = telebot.types.InlineKeyboardButton(text="Вылет?",
                                                     callback_data='flight')
    keyboard.add(button_flight)
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
        try:
            payload = jwt.decode(jwt=message.text, key='abc', algorithms=["HS256"])
            data = MODEL.get_user_fields(payload["password"], payload["username"])
            if data is not None: # Если данные не пустые
                user = {"tg_id":message.chat.id, "data":data}
                users.append(user) # Пока сохраняем пользователя в массив
            bot.send_message(message.chat.id,
                             "Спасибо за регистрацию!",
                             # f'{str(payload)} \n {str(data)}',
                             reply_to_message_id=message.message_id)
        except jwt.ExpiredSignatureError:
            bot.send_message(message.chat.id,
                             f'Токен истёк',
                             reply_to_message_id=message.message_id)
        except jwt.InvalidTokenError:
            bot.send_message(message.chat.id,
                             f'Неверный токен',
                             reply_to_message_id=message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "flight")
def but1_pressed(call):
    for user in users:
        tg_id = user["tg_id"]
        if tg_id == call.message.chat.id:
            text = MODEL.get_route_fields(user["data"][0])
            if text[5] is None and text[4] is None:
                bot.send_message(call.message.chat.id,
                    "Ваш следующий вылет:" + str(text[1]) + "\n"
                    + "Дата вылета: " + str(text[2].day) + "." + str(text[2].month) + "." + str(text[2].year) + "\n"
                    + "Дата прилета: " + str(text[3].day) + "." + str(text[3].month) + "." + str(text[3].year) + "\n"
                    + "Вы не записали что хотите взять с собой" + "\n"
                    + "Вы не оставили дополнительных сведений о маршруте"
                ),
            elif text[5] is not None and text[4] is None:
                bot.send_message(call.message.chat.id,
                    "Ваш следующий вылет:" + str(text[1]) + "\n"
                    + "Дата вылета: " + str(text[2].day) + "." + str(text[2].month) + "." + str(text[2].year) + "\n"
                    + "Дата прилета: " + str(text[3].day) + "." + str(text[3].month) + "." + str(text[3].year) + "\n"
                    + "Вы хотели взять:" + text[5] + "\n"
                    + "Вы не оставили дополнительных сведений о маршруте"
                    ),
            else:
                bot.send_message(call.message.chat.id,
                    "Ваш следующий вылет:" + str(text[1]) + "\n"
                    + "Дата вылета: " + str(text[2].day) + "." + str(text[2].month) + "." + str(text[2].year) + "\n"
                    + "Дата прилета: " + str(text[3].day) + "." + str(text[3].month) + "." + str(text[3].year) + "\n"
                    + "Вы хотели взять:" + text[5] + "\n"
                    + "Вы оставили комментарий:" + text[4]
                    ),
        else:
            bot.send_message(call.message.chat.id, "Прости, я тебя не знаю(")


timThr = threading.Thread(target=tic_tac)
timThr.start()
bot.polling(none_stop=True)
