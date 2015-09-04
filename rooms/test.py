"""
TO RUN THE TEST SIMPLY RUN ./manage.py test rooms.test.ActivityTestCase.filter_out_busy_rooms
OR ANY OTHER OF THE TESTS..
"""

from django.test import TestCase
from rooms.models import Activity, Tutorial_Room
import datetime
from django.utils import timezone
from core import utilities


def makeClosedRoom(name="locallyAllocatedButClosed"):
    """
    Will make a currently closed room (in weekdays) and save it to the database
    :param name:
    :return: nothing
    """

    startTime = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    startTime -= datetime.timedelta(hours=2)

    endTime = startTime + datetime.timedelta(hours=1)

    a = Tutorial_Room(locationId=name, room_name=name, capacity=20, longitude=200.3, latitude=20003.3, whiteboard=True,
                      weekdayOpen=startTime, weekdayClosed=endTime, locally_allocated=True)

    a.save()

    return a


class ActivityTestCase(TestCase):
    """
    This is a test pertaining to the utilities.exclude_busy_rooms function that is
    crucial to the filter_suggestions function in rooms/views. It creates three rooms and two activities.
    busyRoom is busy, and should be excluded from the data of suggestions after the function call.
    nonBusyRoom has an activitu associated with it, but this activity is not clashing, and hence
    this room should not be excluded.
    roomNoAct does not have any activities, and hence should not be excluded.

    """

    def setUp(self):
        # set up two rooms
        busyRoom = Tutorial_Room(locationId="busyRoom",
                                 longitude=-3.18914651870728,
                                 latitude=55.9427113171065,
                                 abbreviation="0224",
                                 capacity=20)

        nonBusyRoom = Tutorial_Room(locationId="NonBusyRoom",
                                    longitude=-3.17972660064697,
                                    latitude=55.9501219441208,
                                    abbreviation="0551",
                                    capacity=30)

        roomNoAct = Tutorial_Room(locationId="roomNoAct",
                                  longitude=-3.17972660064697,
                                  latitude=55.9501219441208,
                                  abbreviation="0552",
                                  capacity=30)

        busyRoom.save()
        nonBusyRoom.save()
        roomNoAct.save()

        # starts now and ends in 3 hours
        startTimeA = timezone.now()
        endTimeA = startTimeA + datetime.timedelta(hours=3)

        # started 2 hours ago, and ended an hour ago
        startTimeB = timezone.now() - datetime.timedelta(hours=2)
        endTimeB = startTimeB + datetime.timedelta(hours=1)

        # set up two activities: one that is going on now and one that is not

        activityA = Activity(activityId="activityThatObstructs",
                             name="activityA",
                             startTime=startTimeA,
                             endTime=endTimeA)

        activityB = Activity(activityId="activityHarmless",
                             name="activityB",
                             startTime=startTimeB,
                             endTime=endTimeB)

        activityA.save()
        activityB.save()

        # add busy room to this activity
        activityA.tutorialRooms.add(busyRoom)
        activityB.tutorialRooms.add(nonBusyRoom)

    def filter_out_busy_rooms(self):
        """
        this function tests utilities.exclude_busy_rooms that is used in the
        filter suggestions room view.
        :return:
        """
        # get all rooms
        data = Tutorial_Room.objects.all()

        # initialize the roomNoAct
        roomNoAct = data.get(locationId="roomNoAct")

        # check if number of rooms is 3
        numberOfRooms = data.count()
        self.assertEqual(numberOfRooms, 3)

        # check if the rooms have the intended activities associated with them
        roomBusyRoom = data.get(locationId="busyRoom")

        self.assertEqual(roomBusyRoom.activity_set.all()[0], Activity.objects.get(activityId="activityThatObstructs"))

        nonBusyRoom = data.get(locationId="NonBusyRoom")

        self.assertEqual(nonBusyRoom.activity_set.all()[0], Activity.objects.get(activityId="activityHarmless"))


        # filter out the rooms that are currently booked and check if the only room left
        # will be room NonBusyRoom and roomNoAct
        data = utilities.exclude_busy_rooms(data, available_for_hours=1)

        # check that there are two rooms left in data
        x = data.count()
        self.assertEqual(x, 2)

        # check that the nonBusyRoom is still in data
        self.assertEqual(data.get(locationId="NonBusyRoom"), nonBusyRoom)

        # check that the noActRoom is still in data
        self.assertEqual(data.get(locationId="roomNoAct"), roomNoAct)

        # now we know that only rooms that are currently busy are removed from data,
        # and that rooms that either have no activities or no obstructing activities
        # are NOT excluded.
