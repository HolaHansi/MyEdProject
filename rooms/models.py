from django.db import models
import math

# class Room_Feed(models.Model):
#     abbreviation = models.CharField(max_length=30)
#     field_building_name = models.CharField(max_length=200)
#     title = models.CharField(max_length=200, primary_key=True)
#     capacity = models.IntegerField(default=0)
#
#     ##attributes
#
#     #dvd = models.BooleanField()
#     #induction_loop = models.BooleanField()
#     #laptop_connectivity = models.BooleanField()
#     #ohp = models.BooleanField()
#     #pa = models.BooleanField()
#
#     #prs_system = models.BooleanField()
#     #vcr = models.BooleanField()
#     #visualizer = models.BooleanField()
#     pc = models.BooleanField(default=False)
#     projector = models.BooleanField(default=False)
#     whiteboard = models.BooleanField(default=False)
#     blackboard = models.BooleanField(default=False)
#     #lcd = models.BooleanField()
#     #webcam = models.BooleanField()
#     #smartboard = models.BooleanField()
#     #usb_conference_table_mic = models.BooleanField()
#     #wheelchair_accessible = models.BooleanField()
#     #control_system = models.BooleanField()
#     #stereo_audio_system = models.BooleanField()
#     #fm_induction_system = models.BooleanField()
#     #writing_tablet = models.BooleanField()
#     #compact_flash_recorder = models.BooleanField()
#     #lecture_capture = models.BooleanField()
#     #infrared_hearing_helper = models.BooleanField()
#     #plasma_screen = models.BooleanField()
#
#     def __str__(self):
#         return self.field_building_name + ": " + self.title



class Room_Feed(models.Model):
    locationId = models.CharField(max_length=50, primary_key=True)
    abbreviation = models.CharField(max_length=50)
    room_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    capacity = models.IntegerField()
    pc = models.BooleanField(default=False)
    whiteboard = models.BooleanField(default=False)
    blackboard = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    printer = models.BooleanField(default=False)

    locally_allocated = models.BooleanField(default=False)
    zoneId = models.CharField(max_length=50)

    campus_id = models.CharField(max_length=50)
    campus_name = models.CharField(max_length=100)

class Building_Feed(models.Model):
    building_name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=30, primary_key=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return str(self.name)


class Bookable_Room(models.Model):
    #room attributes:
    locationId = models.CharField(max_length=50, primary_key=True)
    abbreviation = models.CharField(max_length=50)
    room_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    capacity = models.IntegerField()
    pc = models.BooleanField(default=False)
    whiteboard = models.BooleanField(default=False)
    blackboard = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    locally_allocated = models.BooleanField(default=False)
    zoneId = models.CharField(max_length=50)
    printer = models.BooleanField(default=False)
    # building attributes
    building_name = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()
    # campus attributes
    campus_name = models.CharField(max_length=100)
    campus_id = models.CharField(max_length=50)


    def __str__(self):
        return self.building_name + ": " + self.room_name

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