from django.db import models
from core.utilities import get_distance


class Computer_Labs(models.Model):
    # The lab's name
    name = models.CharField(max_length=200)
    # The number of computers currently free
    free = models.IntegerField(default=0)
    # The total number of computers in the lab
    seats = models.IntegerField(default=0)
    # The campus where the lab is located
    campus = models.CharField(max_length=200)
    # The ratio of computers available to computers in use
    # ie computersAvailable/computersInUse
    # so 1 is an empty room, 0 is a full room
    ratio = models.FloatField(default=0)
    # The coordinates of the lab
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    # Only used as a primary key, is a different id to the other databases so can't be used to help merge
    id = models.CharField(max_length=20, primary_key=True)

    # opening hours
    weekdayOpen = models.TimeField(null=True)
    weekdayClosed = models.TimeField(null=True)
    saturdayOpen = models.TimeField(null=True)
    saturdayClosed = models.TimeField(null=True)
    sundayOpen = models.TimeField(null=True)
    sundayClosed = models.TimeField(null=True)

    # By default, order based on number of computers available
    class Meta:
        ordering = ['-free']

    def __str__(self):
        return self.name

    # heuristic function for when both distance and empty are selected
    # calculates a heuristic value based on the normalised values for distance, emptiness and number of computers free
    # parameters: average_distance - the average distance to all the buildings
    #             average_ratio - the average emptiness ratio of all the buildings
    #             average_free - the average number of computers free in all the buildings
    #             standard_deviation_distance - the standard deviation of the distance to all the buildings
    #             standard_deviation_ratio - the standard deviation of the emptiness ratio of all the buildings
    #             standard_deviation_free - the standard deviation of the number of computers free in all the buildings
    #             long - the user's current longitude
    #             lat - the user's current latitude
    def get_heuristic(self, average_distance, average_ratio, average_free,
                      standard_deviation_distance, standard_deviation_ratio, standard_deviation_free,
                      long, lat):
        # avoid dividing by 0
        if standard_deviation_distance == 0:
            standard_deviation_distance = 0.00001
        if standard_deviation_ratio == 0:
            standard_deviation_ratio = 0.00001
        if standard_deviation_free == 0:
            standard_deviation_free = 0.00001
        # normalise the building's distance, ratio and number of free computers (normalised mean=0, normalised SD=1)
        normalised_distance = (get_distance(self.longitude, self.latitude, long, lat) - average_distance) / standard_deviation_distance
        normalised_ratio = (self.ratio - average_ratio) / standard_deviation_ratio
        normalised_free = (self.free - average_free) / standard_deviation_free
        # we want a small distance, a large ratio and a large number of seats free, though the latter is least important
        # Note these scale factors are simply what seemed to work nicely rather than anything mathematically perfect
        return normalised_distance - (normalised_ratio*.75) - (normalised_free*.25)
