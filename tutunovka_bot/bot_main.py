import os
from dotenv import load_dotenv
import telebot
import time, datetime
import threading
from tutun.tutunovka_bot import tg_analytic, config

load_dotenv('.env.bot')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Telegram bot token is not defined. Please check your .env.bot file.")


bot = telebot.TeleBot(config.TOKEN)


chat_id = None

def tic_tac():

    i = 0

    while True:

        this_moment = datetime.datetime.now()

        if this_moment.hour == 12 and this_moment.minute == 0 and this_moment.second == 0 and this_moment.day == 12 and this_moment.month == 12 and this_moment.year == 2024:
            if chat_id:
                bot.send_message(chat_id, "Ваш вылет завтра!")

        i += 1
        time.sleep(1)


@bot.message_handler(commands=['start'])
def save_chat_id(message):
    global chat_id
    chat_id = message.chat.id
    bot.send_message(message.chat.id, 'Здравствуйте, вы зарегестрировались на проекте Tutuorist! Я здесь, чтобы напоминать вам о ваших вылетах и багаже, который вы хотели взять с собой. Со мной вы точно ничего не забудуете!', reply_to_message_id=message.message_id)

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
        tg_analytic.statistics(message.chat.id, message.text)
        bot.send_message(message.chat.id, "Ой, ой... Я тебя не понял. 😳")
        bot.send_sticker(
            message.chat.id,
            "CAACAgIAAxkBAAIP4F92EYCC4n5T7uepsto0eIO_EAABqwACBAADll-TFeM60_pUapUTGwQ",
        )
        bot.send_message(
            message.chat.id,
            "Я обязательно ✍️ передам моим создателям твой запрос и смогу в будущем лучше тебя понимать. 👌"
            + "\n"
            + "\n"
            + "Чтобы продолжить разговор, нажми на серые кнопки выше.",
        )

timThr = threading.Thread(target=tic_tac)
timThr.start()
bot.polling(none_stop=True)