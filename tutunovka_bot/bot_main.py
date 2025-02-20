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


def get_keyboard(chat_id, back):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if login_checker(chat_id):
        if back:
            return telebot.types.InlineKeyboardMarkup().add(
                telebot.types.InlineKeyboardButton(text="Назад", callback_data='main'))

        button_flight = telebot.types.InlineKeyboardButton(text="Ближайшее путешествие",
                                                           callback_data='flight')
        button_notes = telebot.types.InlineKeyboardButton(text="Заметки ближайшего путешествия ",
                                                          callback_data='show_notes')
        button_logout = telebot.types.InlineKeyboardButton(text="Выйти",
                                                           callback_data='logout')
        keyboard.add(button_flight)
        keyboard.add(button_notes)
        keyboard.add(button_logout)
    else:
        button_auth = telebot.types.InlineKeyboardButton(text="Авторизоваться",
                                                         callback_data='auth')
        keyboard.add(button_auth)
    return keyboard


@bot.message_handler(commands=['start'])
def save_chat_id(message):
    bot.send_message(message.chat.id,
                     'Здравствуйте, я бот Тутуновка! Я здесь, чтобы напоминать вам о ваших путешествиях и багаже,'
                     ' который вы хотели взять с собой. Со мной вы точно ничего не забудуете!',
                     reply_to_message_id=message.message_id, reply_markup=get_keyboard(message.chat.id, False))


@bot.message_handler(content_types=["text"])
def send_text(message):
    try:
        payload = jwt.decode(jwt=message.text, key=os.getenv('SECRET_KEY_JWT'), algorithms=["HS256"])
        data = MODEL.get_user_fields(payload["username"])
        if data is not None:
            MODEL.update_tg_username(data[0], message.chat.id)
        bot.send_message(message.chat.id,
                         "Вы авторизованы!",
                         reply_to_message_id=message.message_id,
                         reply_markup=get_keyboard(message.chat.id, False)
                         )
    except jwt.ExpiredSignatureError:
        bot.send_message(message.chat.id,
                         f'Токен истёк',
                         reply_to_message_id=message.message_id)
    except jwt.InvalidTokenError:
        bot.send_message(message.chat.id,
                         f'Неверный токен',
                         reply_to_message_id=message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "main")
def main_menu(call):
    bot.send_message(call.message.chat.id,
                     'Я в Вашем распоряжении! Что бы Вы хотели?',
                     reply_markup=get_keyboard(call.message.chat.id, False))


@bot.callback_query_handler(func=lambda call: call.data == "flight")
def but_flight_pressed(call):
    try:
        context = MODEL.get_route_fields(MODEL.get_user_by_tg_username(call.message.chat.id)[0])
    except:
        bot.send_message(call.message.chat.id, "Ошибка: пользователь не найден.")
    if context is None:
        bot.send_message(call.message.chat.id, 'У Вас нет предстоящих путешествий(',
                         reply_markup=get_keyboard(call.message.chat.id, True))
    else:
        if context[5] == '' and context[4] == '':
            bot.send_message(call.message.chat.id,
                             "Ваше следующее путешествие: " + str(context[1]) + "\n"
                             + "Дата начала путешествия: " + str(context[2]) + "\n"
                             + "Дата возвращения: " + str(context[3]) + "\n"
                             + "Вы не записали что хотите взять с собой" + "\n"
                             + "Вы не оставили дополнительных сведений о маршруте",
                             reply_markup=get_keyboard(call.message.chat.id, True)
                             )
        elif context[5] != '' and context[4] == '':
            bot.send_message(call.message.chat.id,
                             "Ваше следующее путешествие: " + str(context[1]) + "\n"
                             + "Дата начала путешествия: " + str(context[2]) + "\n"
                             + "Дата возвращения: " + str(context[3]) + "\n"
                             + "Вы хотели взять: " + str(context[5]) + "\n"
                             + "Вы не оставили дополнительных сведений о маршруте",
                             reply_markup=get_keyboard(call.message.chat.id, True)
                             )
        elif context[5] == '' and context[4] != '':
            bot.send_message(call.message.chat.id,
                             "Ваше следующее путешествие: " + str(context[1]) + "\n"
                             + "Дата начала путешествия: " + str(context[2]) + "\n"
                             + "Дата возвращения: " + str(context[3]) + "\n"
                             + "Вы не оставили дополнительных сведений о маршруте" + "\n"
                             + "Комментарий: " + str(context[4]),
                             reply_markup=get_keyboard(call.message.chat.id, True)
                             )
        else:
            bot.send_message(call.message.chat.id,
                             "Ваше следующее путешествие: " + str(context[1]) + "\n"
                             + "Дата начала путешествия: " + str(context[2]) + "\n"
                             + "Дата возвращения: " + str(context[3]) + "\n"
                             + "Вы хотели взять: " + str(context[5]) + "\n"
                             + "Комментарий: " + str(context[4]),
                             reply_markup=get_keyboard(call.message.chat.id, True)
                             )


@bot.callback_query_handler(func=lambda call: call.data == "auth")
def but_auth_pressed(call):
    bot.send_message(call.message.chat.id, "Пришлите токен для автоизации, получить его Вы можете на нашем сайте.")


@bot.callback_query_handler(func=lambda call: call.data == "logout")
def but_logout_pressed(call):
    status = MODEL.delete_tg_username(call.message.chat.id)
    if status:
        bot.send_message(call.message.chat.id, "Вы успешно вышли из аккаунта, ждём Вас снова!",
                         reply_markup=get_keyboard(call.message.chat.id, False))
    else:
        bot.send_message(call.message.chat.id, "Произошла непредвиденная ошибка, попробуйте позже",
                         reply_markup=get_keyboard(call.message.chat.id, False))


@bot.callback_query_handler(func=lambda call: call.data.startswith("note_"))
def toggle_note_status(call):
    note_id = int(call.data.split("_")[1])
    status = MODEL.toggle_note_status(note_id)
    if status:
        bot.answer_callback_query(call.id, "Статус заметки изменён")
    else:
        bot.answer_callback_query(call.id, "Ошибка изменения статуса")

    show_notes(call)


@bot.callback_query_handler(func=lambda call: call.data == "show_notes")
def show_notes(call):
    try:
        context = MODEL.get_route_fields(MODEL.get_user_by_tg_username(call.message.chat.id)[0])
    except:
        bot.send_message(call.message.chat.id, "Ошибка: пользователь не найден.")
    if context is None:
        bot.send_message(call.message.chat.id, 'У Вас нет предстоящих путешествий(',
                         reply_markup=get_keyboard(call.message.chat.id))

    notes = MODEL.get_notes_for_route(context[0])
    if not notes:
        bot.send_message(call.message.chat.id, "У маршрута нет заметок.")
        return

    keyboard = telebot.types.InlineKeyboardMarkup()
    for note in notes:
        status_text = "✔️ " if note[1] else "❌ "
        button = telebot.types.InlineKeyboardButton(
            text=f"{status_text}{note[2]}", callback_data=f"note_{note[0]}"
        )
        keyboard.add(button)
    keyboard.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data='main'))
    bot.send_message(call.message.chat.id, "Ваши заметки:", reply_markup=keyboard)


schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()
bot.polling(none_stop=True, timeout=60)
