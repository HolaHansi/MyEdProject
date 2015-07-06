from django.db import models
import math

class PC_Space(models.Model):
    location = models.CharField(max_length=200)
    free = models.IntegerField(default=0)
    seats = models.IntegerField(default=0)
    group = models.CharField(max_length=200)
    ratio = models.FloatField(default=0) # the ratio of computers available to computers in use
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
        R = 6371000 # metres
        # convert all coordinates to radians
        t1 = self.toRadians(lat1)
        t2 = self.toRadians(self.latitude)
        dt = self.toRadians(self.latitude - lat1)
        dl = self.toRadians(self.longitude - long1)
        # do some clever maths which the internet told me was correct
        a = math.sin(dt / 2) * math.sin(dt / 2) + math.cos(t1) * math.cos(t2) * math.sin(dl / 2) * math.sin(dl / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        # return the distance between the points
        return R * c
    # converts from degrees to radians
    # parameters: x - the value in degrees to be converted
    def toRadians(self, x):
        return x*math.pi/180

    # heuristic function for when both distance and empty are selected
    # calculates a heuristic value based on the normalised distance and emptiness
    # parameters: averageDistance - the average distance to all the buildings
    #             averageRatio - the average emptiness ratio of all the buildings
    #             standardDeviationDistance - the standard deviation of the distance to all the buildings
    #             standardDeviationRatio - the standard deviation of the emptiness ratio of all the buildings
    #             long - the user's current longitude
    #             lat - the user's current latitude
    def get_heuristic(self,averageDistance,averageRatio,standardDeviationDistance,standardDeviationRatio, long, lat):
        # avoid dividing by 0
        if standardDeviationDistance==0:
            standardDeviationDistance=0.00001
        if standardDeviationRatio==0:
            standardDeviationRatio=0.00001
        # normalise the building's distance and ratio (normalised mean=0, normalised SD=1)
        normalisedDistance=(self.get_distance(long,lat)-averageDistance)/standardDeviationDistance
        normalisedRatio=(self.get_ratio()-averageRatio)/standardDeviationRatio
        # we want a small distance and a large ratio
        return normalisedDistance-normalisedRatio




class Building_PC(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return str(self.name)

# Create your models here.
