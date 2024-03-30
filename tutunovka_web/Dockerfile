FROM python:3.11-slim

WORKDIR /tutunovka_web
COPY . /tutunovka_web/

RUN pip install -r requirements.txt

CMD python3 manage.py makemigrations
CMD python3 manange.py migrate \
    && python3 manage.py shell -c ""