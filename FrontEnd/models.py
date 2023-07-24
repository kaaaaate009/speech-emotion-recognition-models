from django.db import models

# Create your models here.


class Feedbacks(models.Model):
    contact = models.CharField(max_length=12)
    recordtime = models.TextField()
    audiofile = models.FileField(upload_to='audios')


class PriorityList(models.Model):
    contact2 = models.CharField(max_length=12)
    emotion = models.CharField(max_length=20)
    priority = models.CharField(max_length=2)