FROM python:3.11-slim

WORKDIR /tutunovka_web
COPY . /tutunovka_web/

RUN pip install -r requirements.txt

CMD python3 manage.py makemigrations \
    && python3 manage.py migrate \
    && python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='root').exists() or User.objects.create_superuser('root', 'root@example.com', 'root')" \
    && python3 manage.py runserver 0.0.0.0:8000