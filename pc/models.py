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

    def get_distance(self, long1, lat1):
        R = 6371000 # metres
        t1 = self.toRadians(lat1)
        t2 = self.toRadians(self.latitude)
        dt = self.toRadians(self.latitude - lat1)
        dl = self.toRadians(self.longitude - long1)

        a = math.sin(dt / 2) * math.sin(dt / 2) + math.cos(t1) * math.cos(t2) * math.sin(dl / 2) * math.sin(dl / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def toRadians(self, x):
        return x*math.pi/180




class Building_PC(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return str(self.name)

# Create your models here.
