# Указываем базовый образ
FROM python:3.8-slim

WORKDIR /tutunovka_bot
COPY . /tutunovka_bot/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "bot_main.py"]