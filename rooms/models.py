from django.db import models

''' Room attributes:
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


class Room_Feed(models.Model):
    locationId = models.CharField(max_length=50, primary_key=True)
    room_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    capacity = models.IntegerField()
    pc = models.BooleanField(default=False)
    whiteboard = models.BooleanField(default=False)
    blackboard = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    printer = models.BooleanField(default=False)
    locally_allocated = models.BooleanField(default=False)

    abbreviation = models.CharField(max_length=4)
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


class Tutorial_Room(models.Model):
    # room attributes:
    locationId = models.CharField(max_length=50, primary_key=True)
    room_name = models.CharField(max_length=100)
    # description = models.CharField(max_length=100) # not used
    # capacity = models.IntegerField() # not used
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

    def __str__(self):
        return self.building_name + ": " + self.room_name
