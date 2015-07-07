from django.db import models
import math


class PC_Space(models.Model):
    location = models.CharField(max_length=200)
    free = models.IntegerField(default=0)
    seats = models.IntegerField(default=0)
    group = models.CharField(max_length=200)
    ratio = models.FloatField(default=0)  # the ratio of computers available to computers in use
    # ie computersAvailable/computersInUse
    # so 1 is an empty room, 0 is a full room
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    id = models.AutoField(primary_key=True)

    class Meta:
        ordering = ['-ratio']

    def __str__(self):
        return self.location

    # ratio getter
    def get_ratio(self):
        return self.ratio

    # calculate the distance between the current building and the inputted point
    # parameters: long1 - the longitude of the user
    #             lat1 - the latitude of the user
    def get_distance(self, long1, lat1):
        earth_radius = 6371000  # metres
        # convert all coordinates to radians
        t1 = self.to_radians(lat1)
        t2 = self.to_radians(self.latitude)
        dt = self.to_radians(self.latitude - lat1)
        dl = self.to_radians(self.longitude - long1)
        # do some clever maths which the internet told me was correct
        a = math.sin(dt / 2) * math.sin(dt / 2) + math.cos(t1) * math.cos(t2) * math.sin(dl / 2) * math.sin(dl / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        # return the distance between the points
        return earth_radius * c

    # converts from degrees to radians
    # parameters: x - the value in degrees to be converted
    @staticmethod
    def to_radians(x):
        return x * math.pi / 180

    # heuristic function for when both distance and empty are selected
    # calculates a heuristic value based on the normalised distance and emptiness
    # parameters: averageDistance - the average distance to all the buildings
    #             averageRatio - the average emptiness ratio of all the buildings
    #             standardDeviationDistance - the standard deviation of the distance to all the buildings
    #             standardDeviationRatio - the standard deviation of the emptiness ratio of all the buildings
    #             long - the user's current longitude
    #             lat - the user's current latitude
    def get_heuristic(self, average_distance, average_ratio, standard_deviation_distance, standard_deviation_ratio,
                      long, lat):
        # avoid dividing by 0
        if standard_deviation_distance == 0:
            standard_deviation_distance = 0.00001
        if standard_deviation_ratio == 0:
            standard_deviation_ratio = 0.00001
        # normalise the building's distance and ratio (normalised mean=0, normalised SD=1)
        normalised_distance = (self.get_distance(long, lat) - average_distance) / standard_deviation_distance
        normalised_ratio = (self.get_ratio() - average_ratio) / standard_deviation_ratio
        # we want a small distance and a large ratio
        return normalised_distance - normalised_ratio


class Building_PC(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return str(self.name)

# Create your models here.
