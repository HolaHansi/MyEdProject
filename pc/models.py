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

# Create your models here.
