from django.db import models
from django.utils import timezone
import datetime


class Room_Feed(models.Model):
    # unique identifiers and essential facts
    locationId = models.CharField(max_length=50, primary_key=True)
    room_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    capacity = models.IntegerField()

    # suitabilities
    pc = models.BooleanField(default=False)
    whiteboard = models.BooleanField(default=False)
    blackboard = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    printer = models.BooleanField(default=False)

    # if true, this means the room can't be booked!
    locally_allocated = models.BooleanField(default=False)

    # relevant building info
    abbreviation = models.CharField(max_length=4)
    zoneId = models.CharField(max_length=50)
    campus_id = models.CharField(max_length=50)
    campus_name = models.CharField(max_length=100)


class Building_Feed(models.Model):
    building_name = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()

    # unique identifier: the abbreviation appears in the 4 first digits in the host_key
    abbreviation = models.CharField(max_length=30, primary_key=True)

    def __str__(self):
        return str(self.building_name)

class Open_Hours(models.Model):
    # building info that are not currently used
    building = models.OneToOneField(Building_Feed)
    abbreviation = models.CharField(max_length=8, primary_key=True)
    zoneId = models.CharField(max_length=50)
    building_name = models.CharField(max_length=100)

    # opening hours
    weekdayOpen = models.TimeField(null=True)
    weekdayClosed = models.TimeField(null=True)
    saturdayOpen = models.TimeField(null=True)
    saturdayClosed = models.TimeField(null=True)
    sundayOpen = models.TimeField(null=True)
    sundayClosed = models.TimeField(null=True)

    def __str__(self):
        return 'Opening Hours for building: ' + self.building_name


class Tutorial_Room(models.Model):
    # room attributes:
    locationId = models.CharField(max_length=50, primary_key=True)
    room_name = models.CharField(max_length=100)
    # description = models.CharField(max_length=100) # not used
    capacity = models.IntegerField()
    pc = models.BooleanField(default=False)
    whiteboard = models.BooleanField(default=False)
    blackboard = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    printer = models.BooleanField(default=False)
    locally_allocated = models.BooleanField(default=False)
    zoneId = models.CharField(max_length=50)
    # building attributes
    building_name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=4)
    longitude = models.FloatField()
    latitude = models.FloatField()
    # campus attributes
    campus_name = models.CharField(max_length=100)
    campus_id = models.CharField(max_length=50)

    # opening hours
    weekdayOpen = models.TimeField(null=True)
    weekdayClosed = models.TimeField(null=True)
    saturdayOpen = models.TimeField(null=True)
    saturdayClosed = models.TimeField(null=True)
    sundayOpen = models.TimeField(null=True)
    sundayClosed = models.TimeField(null=True)

    # available till/for updated in users views
    availableFor = models.CharField(max_length=15, default='unknown')
    unavailableFor = models.CharField(max_length=15, default='unknown')


    # availability status: this field must updated very often!
    # availableNow, notAvailable or localAvailable
    availability = models.CharField(max_length=30)


    def __str__(self):
        return self.building_name + ": " + self.room_name

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.locationId == other.locationId and
                self.room_name == other.room_name and
                self.pc == other.pc and
                self.whiteboard == other.whiteboard and
                self.projector == other.projector and
                self.printer == other.printer and
                self.locally_allocated == other.locally_allocated and
                self.zoneId == other.zoneId and
                self.building_name == other.building_name and
                self.abbreviation == other.abbreviation and
                self.longitude == other.longitude and
                self.latitude == other.latitude and
                self.campus_name == other.campus_name and
                self.campus_id == other.campus_id
                )


class Activity(models.Model):
    # Unique identifier in the RDB
    activityId = models.CharField(max_length=50, primary_key=True)
    # Essential attributes
    name = models.CharField(max_length=500)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()

    # the tutorial room in which the activity is taking place
    tutorialRooms = models.ManyToManyField(Tutorial_Room)

    def __str__(self):
        return 'Activity ' + str(self.activityId) + ', ' + str(self.startTime) + ' until' + str(self.endTime)


'''
    These are the available room attributes that we COULD include:

    dvd = models.BooleanField()
    induction_loop = models.BooleanField()
    laptop_connectivity = models.BooleanField()
    ohp = models.BooleanField()
    pa = models.BooleanField()
    prs_system = models.BooleanField()
    vcr = models.BooleanField()
    visualizer = models.BooleanField()
    pc = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    whiteboard = models.BooleanField(default=False)
    blackboard = models.BooleanField(default=False)
    lcd = models.BooleanField()
    webcam = models.BooleanField()
    smartboard = models.BooleanField()
    usb_conference_table_mic = models.BooleanField()
    wheelchair_accessible = models.BooleanField()
    control_system = models.BooleanField()
    stereo_audio_system = models.BooleanField()
    fm_induction_system = models.BooleanField()
    writing_tablet = models.BooleanField()
    compact_flash_recorder = models.BooleanField()
    lecture_capture = models.BooleanField()
    infrared_hearing_helper = models.BooleanField()
    plasma_screen = models.BooleanField()
'''