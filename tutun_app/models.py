from django.db import models
#from django.contrib.postgres.fields import ArrayField


class User(models.Model):
    class Meta:
        db_table = "Users"

    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=150)
    password = models.CharField(max_length=75)
    is_superuser = models.BooleanField()
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    tg_username = models.CharField(max_length=75)


class Dot(models.Model):
    class Meta:
        db_table = "Dots"

    api_vision = models.JSONField()
    Note = models.CharField(max_length=700)
    information = models.CharField(max_length=700)


class Route(models.Model):
    class Meta:
        db_table = "Routes"

    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    date_in = models.DateTimeField()
    date_out = models.DateTimeField()
    comment = models.CharField(max_length=700)
    #baggage = ArrayField(models.CharField(max_length=20))
    baggage = models.CharField(max_length=3000)
    note = models.CharField(max_length=700)
    rate = models.IntegerField()
    dots = models.ForeignKey(to=Dot, on_delete=models.CASCADE)
