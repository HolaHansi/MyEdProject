from django.db import models

class PC_Space(models.Model):
    location = models.CharField(max_length=200, primary_key=True)
    free = models.IntegerField(default=0)
    seats = models.IntegerField(default=0)
    group = models.CharField(max_length=200)
    ratio = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)

    def __str__(self):
        return self.location


class Building_PC(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return str(self.name)

# Create your models here.
