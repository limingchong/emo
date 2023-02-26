from django.db import models


# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=16, unique=True)

    # password = models.CharField(max_length=4)

    class Meta:
        permissions = ()


class Sentence(models.Model):
    username = models.CharField(max_length=16)
    sentence = models.CharField(max_length=1024)
    time = models.DateTimeField()
    color = models.CharField(max_length=32)
    pos = models.FloatField()
    neg = models.FloatField()
    neu = models.FloatField()
    com = models.FloatField()
