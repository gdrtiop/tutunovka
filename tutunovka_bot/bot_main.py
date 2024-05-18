import datetime
import os
import threading
import time
import jwt
import telebot
import schedule
from dotenv import load_dotenv
from models import PostgreSQLQueries

load_dotenv('.env.bot')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Telegram bot token is not defined. Please check your .env.bot file.")

bot = telebot.TeleBot(TOKEN)

MODEL = PostgreSQLQueries(os.getenv('DB_NAME'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_HOST'),
                          os.getenv('DB_PORT'))


def tic_tac():
    while True:

        this_moment = datetime.datetime.now()
        routes = MODEL.get_routes()
        for route in list(routes):
            if (this_moment.hour == 12 and this_moment.minute == 0 and this_moment.second == 0 and
                    this_moment - datetime.timedelta(days=1) == route[2].day):
                for user in MODEL.get_users():
                    if route[7] == user[0]:
                        bot.send_message(user[12], "Завтра Вас ждёт путешествие!")


def run_schedule():
    schedule.every().day.at("12:00").do(tic_tac)
    while True:
        schedule.run_pending()
        time.sleep(1)


def login_checker(chat_id):
    user = MODEL.get_user_by_tg_username(chat_id)
    if user is None:
        return False
    else:
        return True


def get_keyboard(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if login_checker(chat_id):
        button_flight = telebot.types.InlineKeyboardButton(text="Ближайшее путешествие",
                                                           callback_data='flight')
        button_logout = telebot.types.InlineKeyboardButton(text="Выйти",
                                                           callback_data='logout')
        keyboard.add(button_flight)
        keyboard.add(button_logout)
    else:
        button_auth = telebot.types.InlineKeyboardButton(text="Авторизоваться",
                                                         callback_data='auth')
        keyboard.add(button_auth)
    return keyboard


@bot.message_handler(commands=['start'])
def save_chat_id(message):
    bot.send_message(message.chat.id,
                     f'Здравствуйте, я бот Тутуновка! Я здесь, чтобы напоминать вам о ваших путешествиях и багаже, который вы хотели взять с собой. Со мной вы точно ничего не забудуете!{message.chat.id}',
                     reply_to_message_id=message.message_id, reply_markup=get_keyboard(message.chat.id))


@bot.message_handler(content_types=["text"])
def send_text(message):
    try:
        payload = jwt.decode(jwt=message.text, key=os.getenv('SECRET_KEY_JWT'), algorithms=["HS256"])
        data = MODEL.get_user_fields(payload["password"], payload["username"])
        if data is not None:
            MODEL.update_tg_username(data[0], message.chat.id)
        bot.send_message(message.chat.id,
                         "Вы авторизованы!",
                         reply_to_message_id=message.message_id,
                         reply_markup=get_keyboard(message.chat.id)
                         )
    except jwt.ExpiredSignatureError:
        bot.send_message(message.chat.id,
                         f'Токен истёк',
                         reply_to_message_id=message.message_id)
    except jwt.InvalidTokenError:
        bot.send_message(message.chat.id,
                         f'Неверный токен',
                         reply_to_message_id=message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "flight")
def but_flight_pressed(call):
    context = MODEL.get_route_fields(MODEL.get_user_by_tg_username(call.message.chat.id)[0])
    if context is None:
        bot.send_message(call.message.chat.id, 'У Вас нет предстоящих путешествий(',
                         reply_markup=get_keyboard(call.message.chat.id))
    else:
        if context[5] == '' and context[4] == '':
            bot.send_message(call.message.chat.id,
                             "Ваше следующее: " + str(context[1]) + "\n"
                             + "Дата начала путешествия: " + str(context[2]) + "\n"
                             + "Дата возвращения: " + str(context[3]) + "\n"
                             + "Вы не записали что хотите взять с собой" + "\n"
                             + "Вы не оставили дополнительных сведений о маршруте",
                             reply_markup=get_keyboard(call.message.chat.id)
                             )
        elif context[5] != '' and context[4] == '':
            bot.send_message(call.message.chat.id,
                             "Ваш следующий вылет: " + str(context[1]) + "\n"
                             + "Дата начала путешествия: " + str(context[2]) + "\n"
                             + "Дата возвращения: " + str(context[3]) + "\n"
                             + "Вы хотели взять: " + str(context[5]) + "\n"
                             + "Вы не оставили дополнительных сведений о маршруте",
                             reply_markup=get_keyboard(call.message.chat.id)
                             )
        elif context[5] == '' and context[4] != '':
            bot.send_message(call.message.chat.id,
                             "Ваш следующий вылет: " + str(context[1]) + "\n"
                             + "Дата начала путешествия: " + str(context[2]) + "\n"
                             + "Дата возвращения: " + str(context[3]) + "\n"
                             + "Вы не оставили дополнительных сведений о маршруте" + "\n"
                             + "Комментарий: " + str(context[4]),
                             reply_markup=get_keyboard(call.message.chat.id)
                             )
        else:
            bot.send_message(call.message.chat.id,
                             "Ваш следующий вылет: " + str(context[1]) + "\n"
                             + "Дата начала путешествия: " + str(context[2]) + "\n"
                             + "Дата возвращения: " + str(context[3]) + "\n"
                             + "Вы хотели взять: " + str(context[5]) + "\n"
                             + "Комментарий: " + str(context[4]),
                             reply_markup=get_keyboard(call.message.chat.id)
                             )


@bot.callback_query_handler(func=lambda call: call.data == "auth")
def but_auth_pressed(call):
    bot.send_message(call.message.chat.id, "Пришлите токен для автоизации, получить его Вы можете на нашем сайте.")


@bot.callback_query_handler(func=lambda call: call.data == "logout")
def but_logout_pressed(call):
    status = MODEL.delete_tg_username(call.message.chat.id)
    if status:
        bot.send_message(call.message.chat.id, "Вы успешно вышли из аккаунта, ждём Вас снова!",
                         reply_markup=get_keyboard(call.message.chat.id))
    else:
        bot.send_message(call.message.chat.id, "Произошла непредвиденная ошибка, попробуйте позже",
                         reply_markup=get_keyboard(call.message.chat.id))


schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()
bot.polling(none_stop=True)
