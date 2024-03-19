from django.db import models
from django.contrib.auth.models import User

# from django.contrib.postgres.fields import ArrayField


User.add_to_class('tg_username', models.CharField(max_length=75, default=None, unique=True, null=True))


class PrivateDot(models.Model):
    class Meta:
        db_table = "Private_Dots"

    name = models.CharField(max_length=125, default='Untitled dot')
    api_vision = models.JSONField()
    note = models.CharField(max_length=700)
    information = models.CharField(max_length=700)


class PublicDot(models.Model):
    class Meta:
        db_table = "Public_Dots"

    name = models.CharField(max_length=125, default='Untitled dot')
    api_vision = models.JSONField()
    information = models.CharField(max_length=700)


class PrivateRoute(models.Model):
    class Meta:
        db_table = "Private_Routes"

    Name = models.CharField(max_length=125, default='Untitled')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    date_in = models.DateTimeField()
    date_out = models.DateTimeField()
    comment = models.CharField(max_length=700)
    # baggage = ArrayField(models.CharField(max_length=20))
    baggage = models.CharField(max_length=3000)
    note = models.CharField(max_length=700)
    rate = models.IntegerField(default='-1')
    dots = models.ManyToManyField(to=PrivateDot)


class PublicRoute(models.Model):
    class Meta:
        db_table = "Public_Routes"

    Name = models.CharField(max_length=125, default='Untitled')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=700)
    rate = models.IntegerField(default='-1')
    dots = models.ManyToManyField(to=PublicDot)
