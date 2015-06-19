from django.db import models
import math

class PC_Space(models.Model):
    location = models.CharField(max_length=200)
    free = models.IntegerField(default=0)
    seats = models.IntegerField(default=0)
    group = models.CharField(max_length=200)
    ratio = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    id = models.AutoField(primary_key=True)

    class Meta:
        ordering = ['-ratio']

    def __str__(self):
        return self.location

    def get_distance(self, usr_longitude, usr_latitude):
        result = (self.longitude - usr_longitude)**2 + (self.latitude - usr_latitude)**2
        result = math.sqrt(result)
        return result

class Building_PC(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return str(self.name)

# Create your models here.
