from django.db import models
from django.contrib.auth.models import User
#from django.contrib.postgres.fields import ArrayField


User.add_to_class('tg_username', models.CharField(max_length=75, default=None, unique=True, null=True))

class Dot(models.Model):
    class Meta:
        db_table = "Dots"

    name = models.CharField(max_length=125, default='Untitled dot')
    api_vision = models.JSONField()
    note = models.CharField(max_length=700)
    information = models.CharField(max_length=700)


class Route(models.Model):
    class Meta:
        db_table = "Routes"
    Name = models.CharField(max_length=125, default='Untitled')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    date_in = models.DateTimeField()
    date_out = models.DateTimeField()
    comment = models.CharField(max_length=700)
    #baggage = ArrayField(models.CharField(max_length=20))
    baggage = models.CharField(max_length=3000)
    note = models.CharField(max_length=700)
    rate = models.IntegerField(default='-1')
    dots = models.ManyToManyField(to=Dot)

class Route_for_list(models.Model):
    class Meta:
        db_table = "Routes_for_list"
    Name = models.CharField(max_length=125, default='Untitled')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=700)
    rate = models.IntegerField(default='-1')
    dots = models.ManyToManyField(to=Dot)
