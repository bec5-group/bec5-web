from django.db import models
from . import utils

class TempController(models.Model):
    cid = models.CharField(max_length=1000, primary_key=True)
    name = models.CharField(max_length=1000)
    order = models.FloatField(default=0.0)
    default_temp = models.FloatField(default=0.0)
    url = models.URLField(max_length=1000)
    number = models.PositiveIntegerField()
    password = models.CharField(max_length=1000)
    class Meta:
        ordering = ['order']

class TempProfile(models.Model):
    pid = models.CharField(max_length=1000, primary_key=True)
    name = models.CharField(max_length=1000)
    order = models.FloatField(default=0.0)
    class Meta:
        ordering = ['order']

class TempSetPoint(models.Model):
    control = models.ForeignKey(TempController)
    temperature = models.FloatField(default=0.0)
    profile = models.ForeignKey(TempProfile)
    class Meta:
        ordering = ['control__order']
