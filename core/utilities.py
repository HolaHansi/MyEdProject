"""
This module contains all the utility functions needed for the views of pc and rooms.
When defining a new function that should work for more than one view, please define it here!

Because there is a slight difference in how heuristic and ranking functions operate in rooms and pc,
most of the functions for pc have been defined in the model for PC_Lab in pc/models.py.

Though get distance is overall the same for both rooms and pc, we've decided against using the same function
in utilities. Partly, because this is how we initially went about developing the PC app and a lot of functions
would break if we moved the functions out of the model and into this module.

We've also kept things this way in recognition of the fact that PCs and rooms are fundamentally different with regards
to how their heuristic functions work, and so keeping their dependencies apart underlines this point to future
developers.
"""
import datetime
from django.utils import timezone
import math
from rooms.models import Activity as act
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse

# ======= functions used in both pc/views and rooms/views ======= #

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def to_radians(x):
    """
    converts to degrees to radians
    """
    return x * math.pi / 180


def excludeClosedLocations(data):
    """
    Given a queryset of either rooms or pc-labs, the function returns a queryset without any currently closed locations.
    It does NOT filter out rooms without opening hours!
    :param data:
    :return: data (without any closed PCs or Rooms)
    """

    # get current time and weekday
    now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())
    currentTime = now.time().isoformat()
    weekday = now.weekday()

    # I'm using exclude instead of filter, so not to filter out all the rooms without opening times.
    # if it's a day between Mon-Fri, then filter out all closed rooms on these days.
    if weekday >= 0 and weekday <= 4:
        data = data.exclude(weekdayOpen__gt=currentTime)
        data = data.exclude(weekdayClosed__lte=currentTime,
                            # to accommodate the case where the building closes after midnight
                            # a building is only excluded if the closing time is ALSO greater than
                            # 9 in the morning, so closing times like 02:30 are not filtered out.
                            weekdayClosed__gt="09:00:00"
                            )

    # the same thing for saturday.
    if weekday == 5:
        data = data.exclude(saturdayOpen__gt=currentTime)
        data = data.exclude(saturdayClosed__lte=currentTime,
                            # to accommodate the case where the building closes after midnight
                            # a building is only excluded if the closing time is ALSO greater than
                            # 9 in the morning, so closing times like 02:30 are not filtered out.
                            saturdayClosed__gt="09:00:00"
                            )

    # if it's sunday... etc.
    if weekday == 6:
        data = data.exclude(sundayOpen__gt=currentTime)
        data = data.exclude(sundayClosed__lte=currentTime,
                            # to accommodate the case where the building closes after midnight
                            # a building is only excluded if the closing time is ALSO greater than
                            # 9 in the morning, so closing times like 02:30 are not filtered out.
                            sundayClosed__gt="09:00:00"
                            )
    return data


# ======= rooms/views functions ======= #




def get_distance(building_long, building_lat, long1, lat1):
    """
    calculate the distance between the current building and the inputted point
    parameters: long1 - the longitude of the user
    lat1 - the latitude of the user
    """
    earth_radius = 6371000  # metres
    # convert all coordinates to radians
    t1 = to_radians(lat1)
    t2 = to_radians(building_lat)
    dt = to_radians(building_lat - lat1)
    dl = to_radians(building_long - long1)
    # do some clever maths which the internet told me was correct
    a = math.sin(dt / 2) * math.sin(dt / 2) + math.cos(t1) * math.cos(t2) * math.sin(dl / 2) * math.sin(dl / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # return the distance between the points
    return earth_radius * c


def calculate_heuristic(room):
    """
    calculates how desirable a room is for a user
    the more features the room has, the more desirable it iss
    """
    value = 2
    if room.locally_allocated:
        value -= 2
    if room.pc:
        value += 2
    if room.whiteboard:
        value += 1
    if room.blackboard:
        value += 1
    if room.projector:
        value += 1
    if room.printer:
        value += 1
    return value


def sortBuildingsByDistance(usr_longitude, usr_latitude, building_details):
    """
    Takes user coordinates and a list of buildings, and returns a sorted list of
    buildings according to distance.
    :param usr_longitude:
    :param usr_latitude:
    :param building_details:
    :return: list of buildings sorted according to distance.
    """
    # sort the buildings based on distance from user, closest first
    building_details = sorted(building_details, key=lambda x: get_distance(
        x['longitude'], x['latitude'], long1=usr_longitude, lat1=usr_latitude))

    return building_details


def filter_out_busy_rooms(data, available_for_hours=1):
    """
    Exclude all the rooms that are hosting an activity that overlaps the duration from now
    till a time after some specified amount of hours.
    :param available_for_hours:
    :return: data of rooms that are not currently booked
    """
    # get the timespan that the user is interested in.
    current_time = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())
    wanted_end_time = current_time + datetime.timedelta(hours=available_for_hours)

    # if an event starts before end time, and ends after currentTime, then the room is
    # already booked, and should be added to busy_rooms.

    busy_rooms = data.filter(activity__startTime__lte=wanted_end_time,
                            activity__endTime__gte=current_time)

    # now exclude all rooms that are busy from the room suggestions (data)
    busy_rooms = [x.locationId for x in busy_rooms]
    data = data.exclude(locationId__in=busy_rooms)

    return data

# ======= users/views functions ======= #

def unavailable_till_hours(unavailable_room):




def available_for_hours(available_rooms):
    """
    Given a queryset of rooms, the function will populate the availableFor field of every room in the queryset.
    If there is an activity or an closing on the same day, then the field is formatted e.g. 2h 30m
    Otherwise, for example if there is no activites or opening hours, or no opening hours an activity the following day.
    The field will be updated with the string value 'unknown'.
    :param available_room:
    :return: nothing - the function updates a field in every room of available_rooms.
    """
    now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())
    weekday = now.weekday()

    for available_room in available_rooms:

        activities = act.objects.filter(tutorialRooms=available_room,
                                        startTime__gt=now)

        # true if there is no activities for the room.
        noAct = False

        # true if activity decides available_till.
        actWins = False

        # check if there are any activities
        activities = activities.order_by("startTime")

        if activities.count() == 0:
            noAct = True
        else:
            next_activity = activities[0]
            # get the starting_time of this activity (type is datetime.datetime)
            startTime = next_activity.startTime



        # get the current closing hour of the room
        if weekday >= 0 and weekday <= 4:
           closingHour = available_room.weekdayClosed

        elif weekday == 5:
            closingHour = available_room.saturdayClosed

        elif weekday == 6:
            closingHour = available_room.sundayClosed


        # no closing hour nor activities for room - return unknown
        if not closingHour and noAct:
            available_room.availableFor = 'unknown'
            available_room.save()
            continue

        # closing hour, but no activities - closingHour becomes avail_till.
        elif closingHour and noAct:
            avail_till_time = closingHour

        # if there is no closing hour, but there is an activity, then activity wins.
        elif not closingHour and not noAct:
            avail_till_time = startTime
            actWins = True

        # otherwise (that means there are both activities and closing hours.)
        else:
            # if the activity starts another day, then the avail_till is bound by closing hour.
            if startTime.date() > now.date():
                avail_till_time = closingHour

            else:
                # if room closes before the start of the next activity, and is greater
                # than the current time, then the closing hour is
                # the available_till_time, otherwise it is the activity startTime.
                if closingHour <= startTime.time() and closingHour > now.time():
                    avail_till_time = closingHour
                else:
                    avail_till_time = startTime
                    actWins = True


        if actWins:
            # if an activity is on a late date, then return unknown.
            if avail_till_time.date() > now.date():
                available_room.availableFor = 'unknown'
                available_room.save()
                continue

            avail_for = avail_till_time - now
        # otherwise, if closingHour wins, then now must be formatted as a time object.
        else:
            avail_for = datetime.datetime.combine(datetime.date.today(), avail_till_time) - datetime.datetime.combine(datetime.date.today(), now.time())

        print('does activity win?', actWins)
        # get the hours and minutes
        avail_for_hours = avail_for.seconds // 3600
        avail_for_minutes = (avail_for.seconds // 60) % 60

        # return result as a string
        availForString = str(avail_for_hours) + "h " + str(avail_for_minutes) + "m"
        available_room.availableFor = availForString
        available_room.save()
        print(available_room, 'has avail_for', availForString)
        continue

    print('updated availableFor')


def get_currently_closed_locations(data, typeOfSpace='PC'):
    """
    given a queryset of both closed and open locations, returns all the currently closed places.
    A parameter specifies whether the queryset is for PCs or rooms.
    """
    openPlaces = excludeClosedLocations(data)
    if typeOfSpace == 'PC':
        openPlacesList = [x.id for x in openPlaces]
        data = data.exclude(id__in=openPlacesList)
    else:
        openPlacesList = [x.locationId for x in openPlaces]
        data = data.exclude(locationId__in=openPlacesList)
    return data

def filter_out_avail_rooms(data, available_for_hours=1):
    """
    Get all rooms that are currently unavailable - either closed or currently booked
    :param available_for_hours:
    :return: data of rooms that are currently booked
    """
    # get the timespan that the user is interested in.
    current_time = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())
    wanted_end_time = current_time + datetime.timedelta(hours=available_for_hours)

    # if an event starts before end time, and ends after currentTime, then the room is
    # already booked, and should be added to busy_rooms.

    busy_rooms = data.filter(activity__startTime__lte=wanted_end_time,
                             activity__endTime__gte=current_time)

    # rooms that are currently closed should also feature


    return busy_rooms


# ======= pc/views functions ======= #

def sortPCLabByDistance(usr_longitude, usr_latitude, data):
    """
    takes user coordinates and a list of PCs, sorts according to which are closest to the user.
    :param usr_longitude:
    :param usr_latitude:
    :param building_details:
    :return: sorted data according to proximity
    """
    data = sorted(data, key=lambda x: get_distance(usr_longitude, usr_latitude, x.longitude, x.latitude))
    return data


def sortPCLabByEmptiness(data):
    """
    sorts list of PC_labs according to their usage ratio. From empty to full.
    :param data:
    :return: sorted data according to emptiness
    """
    data = sorted(data, key=lambda x: x.ratio, reverse=True)
    return data


def sortingByLocationAndEmptiness(data, usr_longitude, usr_latitude):
    """
    Performs a weighted ranking of all the PC-labs and sorts them according to an heuristic-function,
    which is defined in pc/models.
    :param data:
    :param usr_longitude:
    :param usr_latitude:
    :return: sorted data
    """
    average_distance = 0
    average_ratio = 0
    sd_distance = 0
    sd_ratio = 0
    i = 0
    for pc_lab in data:
        average_distance = average_distance + pc_lab.get_distance(long1=usr_longitude, lat1=usr_latitude)
        average_ratio = average_ratio + pc_lab.get_ratio()
        i += 1
    if i != 0:
        average_distance = average_distance / i
        average_ratio = average_ratio / i
        # calculate the standard deviation of distance and ratio
        for pc_lab in data:
            sd_distance += (pc_lab.get_distance(long1=usr_longitude,
                                                lat1=usr_latitude) - average_distance) ** 2
            sd_ratio += (pc_lab.get_ratio() - average_ratio) ** 2
        sd_distance = (sd_distance / i) ** 0.5
        sd_ratio = (sd_ratio / i) ** 0.5
        # sort the data based on both distance and ratio using a heuristic function
        # of the normalised distance and ratio
        data = sorted(data,
                      key=lambda x: x.get_heuristic(average_distance, average_ratio, sd_distance, sd_ratio,
                                                    usr_longitude, usr_latitude))

    return data
