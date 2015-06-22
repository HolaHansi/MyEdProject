from django.db import models
import math

class Room_Feed(models.Model):
    abbreviation = models.CharField(max_length=30)
    field_building_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, primary_key=True)
    capacity = models.IntegerField(default=0)

    ##attributes

    #dvd = models.BooleanField()
    #induction_loop = models.BooleanField()
    #laptop_connectivity = models.BooleanField()
    #ohp = models.BooleanField()
    #pa = models.BooleanField()

    #prs_system = models.BooleanField()
    #vcr = models.BooleanField()
    #visualizer = models.BooleanField()
    pc = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    whiteboard = models.BooleanField(default=False)
    blackboard = models.BooleanField(default=False)
    #lcd = models.BooleanField()
    #webcam = models.BooleanField()
    #smartboard = models.BooleanField()
    #usb_conference_table_mic = models.BooleanField()
    #wheelchair_accessible = models.BooleanField()
    #control_system = models.BooleanField()
    #stereo_audio_system = models.BooleanField()
    #fm_induction_system = models.BooleanField()
    #writing_tablet = models.BooleanField()
    #compact_flash_recorder = models.BooleanField()
    #lecture_capture = models.BooleanField()
    #infrared_hearing_helper = models.BooleanField()
    #plasma_screen = models.BooleanField()

    def __str__(self):
        return self.field_building_name + ": " + self.title


class Building_Feed(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=30, primary_key=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return str(self.name)


class Bookable_Room(models.Model):
    abbreviation = models.CharField(max_length=30)
    field_building_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, primary_key=True)
    capacity = models.IntegerField(default=0)
    pc = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    whiteboard = models.BooleanField(default=False)
    blackboard = models.BooleanField(default=False)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return self.field_building_name + ": " + self.title

    def get_distance(self, usr_longitude, usr_latitude):
        result = (self.longitude - usr_longitude)**2 + (self.latitude - usr_latitude)**2
        result = math.sqrt(result)
        return result
