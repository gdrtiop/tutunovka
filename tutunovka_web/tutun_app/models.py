"""
models for the tutun_app application
"""

from django.db import models
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

User.add_to_class('tg_username', models.CharField(
    max_length=75,
    default=None,
    unique=True,
    null=True
))


class PrivateDot(models.Model):
    """
    Точки приватных маршрутов

    @param: name: название точки
    @type: name: basestring

    @param: date: время создания точки
    @type: date: datetime

    @param: note: заметка для точке
    @type: note: basestring

    @param: information: информация о точке
    @type: information: basestring
    """

    class Meta:
        db_table = "Private_Dots"

    name = models.CharField(max_length=125, default='Untitled dot')
    date = models.DateField(default=None, null=True)
    note = models.CharField(max_length=700, null=True)
    information = models.CharField(max_length=700)


class PublicDot(models.Model):
    """
    Точки публичных маршрутов

    @param: name: название точки
    @type: name: basestring

    @param: information: информация о точке
    @type: information: basestring
    """

    class Meta:
        db_table = "Public_Dots"

    name = models.CharField(max_length=125, default='Untitled dot')
    information = models.CharField(max_length=700)


class Note(models.Model):
    """
    Заметки для маршрутов

    @param: done: отмеченна ли заметка
    @type: done: bool

    @param: text: текст заметки
    @type: text: basestring
    """

    class Meta:
        db_table = "Notes"

    done = models.BooleanField(default=False)
    text = models.CharField(max_length=200)


class PrivateRoute(models.Model):
    """
    Приватные маршруты

    @param: Name: название маршрута
    @type: Name: basestring

    @param: author: автор маршрута
    @type: author: object

    @param: date_in: время начала маршрута
    @type: date_in: datetime.datetime

    @param: date_out: время окончания маршрута
    @type: date_out: datetime.datetime

    @param: comment: коментарий маршрута
    @type: comment: basestring

    @param: baggage: вещи в путь
    @type: baggage: basestring

    @param: note: заметки маршрута
    @type: note: list

    @param: rate: рейтинг маршрута
    @type: rate: int

    @param: dots: точки маршрута
    @type: dots: list

    @param: tags: теги маршрута

    @param: length: длинна маршрута
    @type: length: basestring

    @param: month: месяц поездки
    @type: month: basestring

    @param: year: год поездки
    @type: year: basestring
    """

    class Meta:
        db_table = "Private_Routes"

    Name = models.CharField(max_length=125, default='Untitled')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)

    date_in = models.DateField(null=True, default=None)
    date_out = models.DateField(null=True, default=None)

    comment = models.CharField(max_length=700, null=True)
    baggage = models.CharField(max_length=3000, null=True)

    note = models.ManyToManyField(to=Note)
    rate = models.IntegerField(default='0')
    dots = models.ManyToManyField(to=PrivateDot)

    tags = TaggableManager()

    length = models.CharField(max_length=10, default=None, null=True)
    month = models.CharField(max_length=20, default=None, null=True)
    year = models.CharField(max_length=20, default=None, null=True)


class PublicRoute(models.Model):
    """
    Публичные маршруты

    @param: Name: название маршрута
    @type: Name: basestring

    @param: author: автор маршрута
    @type: author: object

    @param: comment: коментарий маршрута
    @type: comment: basestring

    @param: rate: рейтинг маршрута
    @type: rate: int

    @param: dots: точки маршрута
    @type: dots: list

    @param: tags: теги маршрута

    @param: length: длинна маршрута
    @type: length: basestring

    @param: month: месяц поездки
    @type: month: basestring

    @param: year: год поездки
    @type: year: basestring
    """

    class Meta:
        db_table = "Public_Routes"

    Name = models.CharField(max_length=125, default='Untitled')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=700)

    rate = models.IntegerField(default='-1')
    dots = models.ManyToManyField(to=PublicDot)

    tags = TaggableManager()

    length = models.CharField(max_length=10, default=None, null=True)
    month = models.CharField(max_length=20, default=None, null=True)
    year = models.CharField(max_length=20, default=None, null=True)


class Complaint(models.Model):
    """
        Публичные маршруты

        @param: text: текст жалобы
        @type: text: basestring

        @param: author: автор жалобы
        @type: author: object

        @param: answer: ответ на жалобу
        @type: answer: basestring

        @param: data: дата написания далобы
        @type: data: datetime.datetime
        """

    class Meta:
        db_table = "Complaints"

    text = models.CharField(max_length=1000, default='')

    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1000, default='')

    data = models.DateField()
