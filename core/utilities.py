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
from rooms.models import Activity
from rooms.models import Tutorial_Room
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from django.db.models import F


# ======= availability of rooms functions ================

def update_status_rooms():
    """
    update_status receives all the rooms in the database, and updates the field value of availability.
    :return: nothing
    """
    # set up
    rooms = Tutorial_Room.objects.all()

    rooms_locally_allocated = rooms.filter(locally_allocated=True)

    rooms_globally_allocated = rooms.filter(locally_allocated=False)

    closed_rooms = get_currently_closed_locations(rooms, typeOfSpace='Room')

    # availableNow : rooms available now =============================

    # All rooms that are not currently booked.
    rooms_not_currently_booked = filter_out_busy_rooms(data=rooms_globally_allocated, available_for_hours=1)

    # Exclude all the closed rooms from this set.
    rooms_available_now = excludeClosedLocations(rooms_not_currently_booked)

    # Update the availability field and the available_for field.
    available_for_hours(rooms_available_now)

    # Update availability Field.
    rooms_available_now.update(availability='availableNow')

    # notAvailable : room NOT available now. ===========================

    # get all the currently booked rooms
    rooms_currently_booked = filter_out_avail_rooms(data=rooms_globally_allocated, available_for_hours=1)

    # a room is not available if it's either closed or currently booked
    rooms_not_available_now = closed_rooms | rooms_currently_booked

    # Update the unavailableFor field
    unavailable_till_hours(rooms_not_available_now)

    # Update the availability field
    rooms_not_available_now.update(availability='notAvailable')

    # localAvailable : locally allocated, but open ===========================

    # exclude all closed locally allocated rooms.
    rooms_open_locally_allocated = excludeClosedLocations(rooms_locally_allocated)

    # update every availability field in this queryset:
    rooms_open_locally_allocated.update(availability='localAvailable')

    return 'updated the status of all rooms'


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
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    current_time = now.time().isoformat()
    weekday = now.weekday()

    # I'm using exclude instead of filter, so not to filter out all the rooms without opening times.
    # if it's a day between Mon-Fri, then filter out all closed rooms on these days.
    if 0 <= weekday <= 4:
        # case 1 : now < open < closing
        data = data.exclude(weekdayOpen__gt=current_time,
                            weekdayClosed__gt=current_time,
                            weekdayOpen__lt=F('weekdayClosed'))
        # case 2 : open < close < now
        data = data.exclude(weekdayOpen__lt=current_time,
                            weekdayClosed__lt=current_time,
                            weekdayClosed__gt=F('weekdayOpen'))

        # case 3 : close < now < open
        data = data.exclude(weekdayOpen__gt=current_time,
                            weekdayClosed__lt=current_time)

    # saturday
    if weekday == 5:
        # case 1 : now < open < closing
        data = data.exclude(saturdayOpen__gt=current_time,
                            saturdayClosed__gt=current_time,
                            saturdayOpen__lt=F('saturdayClosed'))
        # case 2 : open < close < now
        data = data.exclude(saturdayOpen__lt=current_time,
                            saturdayClosed__lt=current_time,
                            saturdayClosed__gt=F('saturdayOpen'))

        # case 3 : close < now < open
        data = data.exclude(saturdayOpen__gt=current_time,
                            saturdayClosed__lt=current_time)

    # sunday
    if weekday == 6:
        # case 1 : now < open < closing
        data = data.exclude(sundayOpen__gt=current_time,
                            sundayClosed__gt=current_time,
                            sundayOpen__lt=F('sundayClosed'))

        # case 2 : open < close < now
        data1 = data.exclude(sundayOpen__lt=current_time,
                             sundayClosed__lt=current_time,
                             sundayClosed__gt=F('sundayOpen'))

        # case 3 : close < now < open
        data = data1.exclude(sundayOpen__gt=current_time,
                             sundayClosed__lt=current_time)

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
    current_time = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
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


def getOpenHours(location):
    """
    given a location the function returns a dictionary containing opening and closing hours on the current
    day.
    :param location:
    :return: dictionary
    """
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    weekday = now.weekday()

    # get the current opening hours of the room
    if 0 <= weekday <= 4:
        closing_hour = location.weekdayClosed
        open_hour = location.weekdayOpen

    elif weekday == 5:
        closing_hour = location.saturdayClosed
        open_hour = location.saturdayOpen
    else:
        closing_hour = location.sundayClosed
        open_hour = location.sundayOpen

    to_return = {'openHour': open_hour, 'closingHour': closing_hour}

    return to_return


def isOpen(location):
    """
    Takes a location and returns true if the location is currently open. Sensitive to weekdays!
    :param location:
    :return: boolean
    """
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())

    # get the current opening hours of the room
    full_opening_times = getOpenHours(location)
    open_hour = full_opening_times['openHour']
    closing_hour = full_opening_times['closingHour']

    # if opening hours are None, then just return True (they are not closed for all we know!)
    if open_hour is None or closing_hour is None:
        return True

    # determine if the place is currently open.
    if open_hour < now.time() < closing_hour:
        is_open_var = True
    # this is the second more unusual case where the room is open (e.g. closing hour: 2 am)
    elif closing_hour < open_hour <= now.time() or now.time() < closing_hour < open_hour:
        is_open_var = True
    else:
        is_open_var = False

    return is_open_var


def unavailable_till_hours(unavailable_rooms):
    """
    given a queryset of rooms, the function will populate the unavailableFor field of every room in the queryset.
    :param unavailable_room:
    :return:
    """

    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    tomorrow = now + datetime.timedelta(hours=24)

    for unavailable_room in unavailable_rooms:

        # get all of the rooms activities ending after now, but starting before tomorrow.
        activities = Activity.objects.filter(tutorialRooms=unavailable_room,
                                             endTime__gt=now,
                                             startTime__lt=tomorrow)

        # check if location is open
        is_open_var = isOpen(unavailable_room)

        # if the place is open, then we know that the reason the place is unavailable is due
        # to an activity that is currently taking place.
        if is_open_var:
            # go through the activities, and get the end time of the first activity whose endTime
            # is at least an hour prior to the next activity.
            # first, initialize avail_till
            avail_till_time = None
            for i in range(activities.count() - 1):
                if activities[i].endTime <= (activities[i + 1].startTime - datetime.timedelta(hours=1)):
                    avail_till_time = activities[i].endTime
                    break
            # if avail_till is undefined, then every activity except the final one has been checked, and
            # has failed this condition. Hence, take the last activity.endTime as avail_till.

            if avail_till_time is None:
                avail_till_time = activities[activities.count() - 1].endTime

            # now get the time from now until avail_till_time.
            avail_for = avail_till_time - now

            # get the hours and minutes
            avail_for_hours = avail_for.seconds // 3600
            avail_for_minutes = (avail_for.seconds // 60) % 60

            # return result as a string
            unavail_for_string = str(avail_for_hours) + "h " + str(avail_for_minutes) + "m"
            unavailable_room.unavailableFor = unavail_for_string
            unavailable_room.save()
            continue

        # otherwise, the room is currently Closed, and this is why it's unavailable. Find out when it opens
        else:
            # get open hour - we know this is available because the room is closed.
            full_opening_times = getOpenHours(unavailable_room)
            open_hour = full_opening_times['openHour']

            # if the room is about to open later same day, then avail_till_time is openHour + the duration
            # of any potential activities starting from openHour.
            if now.time() < open_hour:
                # get openHour as datetime object and initialize variable which is an hour after opening.
                open_hour_date_time = datetime.datetime.combine(datetime.date.today(), open_hour)
                an_hour_later = open_hour_date_time + datetime.timedelta(hours=1)

                # get all activities starting in the first hour of the room being open.
                activities = activities.filter(startTime__lt=an_hour_later,
                                               startTime__gte=open_hour_date_time)

                # In case, there are no such activities, then the room will surely be available on opening
                if activities.count() == 0:
                    avail_till_time = open_hour_date_time

                # Otherwise, find the endTime of the last activity in a potential consecutive streak of activities.
                # the code is the same as in the 'isOpen - condition'.
                else:
                    avail_till_time = None
                    for i in range(activities.count() - 1):
                        if activities[i].endTime <= (activities[i + 1].startTime - datetime.timedelta(hours=1)):
                            avail_till_time = activities[i].endTime
                            break
                    # if avail_till is undefined, then every activity except the final one has been checked, and
                    # has failed this condition. Hence, take the last activity.endTime as avail_till.
                    if avail_till_time is None:
                        avail_till_time = activities[activities.count() - 1].endTime

                # get the difference between time it becomes available and now.
                avail_for = avail_till_time - datetime.datetime.combine(datetime.date.today(), now.time())

                # get the hours and minutes
                avail_for_hours = avail_for.seconds // 3600
                avail_for_minutes = (avail_for.seconds // 60) % 60

                # return result as string
                unavail_for_string = str(avail_for_hours) + "h " + str(avail_for_minutes) + "m"
                unavailable_room.unavailableFor = unavail_for_string
                unavailable_room.save()

            # the room is closed for today, and so just return: tomorrow.
            else:
                unavailable_room.unavailableFor = 'tomorrow'
                unavailable_room.save()

    print('updated unavailableFor')


def available_for_hours(available_rooms):
    """
    Given a queryset of rooms, the function will populate the availableFor field of every room in the queryset.
    If there is an activity or an closing on the same day, then the field is formatted e.g. 2h 30m
    Otherwise, for example if there is no activites or opening hours, or no opening hours an activity the following day.
    The field will be updated with the string value 'unknown'.
    :param available_rooms:
    :return: nothing - the function updates a field in every room of available_rooms.
    """
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())

    for available_room in available_rooms:
        # first update the availability field:
        available_room.availability = 'availableNow'

        # get all activities for the room beginning after now.
        activities = Activity.objects.filter(tutorialRooms=available_room, startTime__gt=now)

        # order from most recent till most distant
        activities = activities.order_by("startTime")

        # true if there is no activities for the room.
        no_activities = False

        # true if activity decides available_till.
        activity_wins = False

        # check if there are any activities

        if activities.count() == 0:
            no_activities = True
        else:
            next_activity = activities[0]
            # get the starting_time of this activity (type is datetime.datetime)
            start_time = next_activity.startTime

        # get the current closing hour of the room
        full_opening_times = getOpenHours(available_room)
        closing_hour = full_opening_times['closingHour']

        # no closing hour nor activities for room - return unknown
        if closing_hour is None and no_activities:
            available_room.availableFor = 'unknown'
            available_room.save()
            continue

        # closing hour, but no activities - closingHour becomes avail_till.
        elif closing_hour is not None and no_activities:
            avail_till_time = closing_hour

        # if there is no closing hour, but there is an activity, then activity wins.
        elif closing_hour is None and not no_activities:
            avail_till_time = start_time
            activity_wins = True

        # otherwise (that means there are both activities and closing hours.)
        else:
            # if the activity starts another day, then the avail_till is bound by closing hour.
            if start_time.date() > now.date():
                avail_till_time = closing_hour

            else:
                # if room closes before the start of the next activity, and is greater
                # than the current time, then the closing hour is
                # the available_till_time, otherwise it is the activity startTime.
                if start_time.time() >= closing_hour > now.time():
                    avail_till_time = closing_hour
                else:
                    avail_till_time = start_time
                    activity_wins = True

        if activity_wins:
            # if an activity is on a late date, then return unknown.
            if avail_till_time.date() > now.date():
                available_room.availableFor = 'unknown'
                available_room.save()
                continue

            avail_for = avail_till_time - now
        # otherwise, if closingHour wins, then now must be formatted as a time object.
        else:
            avail_for = datetime.datetime.combine(datetime.date.today(), avail_till_time) - datetime.datetime.combine(
                datetime.date.today(), now.time())

        # get the hours and minutes
        avail_for_hours = avail_for.seconds // 3600
        avail_for_minutes = (avail_for.seconds // 60) % 60

        # return result as a string
        avail_for_string = str(avail_for_hours) + "h " + str(avail_for_minutes) + "m"
        available_room.availableFor = avail_for_string
        available_room.save()
        continue

    print('updated availableFor')


def get_currently_closed_locations(data, typeOfSpace='PC'):
    """
    given a queryset of both closed and open locations, returns all the currently closed places.
    A parameter specifies whether the queryset is for PCs or rooms.
    """
    open_places = excludeClosedLocations(data)
    if typeOfSpace == 'PC':
        open_places_list = [x.id for x in open_places]
        data = data.exclude(id__in=open_places_list)
    else:
        open_places_list = [x.locationId for x in open_places]
        data = data.exclude(locationId__in=open_places_list)
    return data


def filter_out_avail_rooms(data, available_for_hours=1):
    """
    Get all rooms that are currently unavailable - either closed or currently booked
    :param available_for_hours:
    :return: data of rooms that are currently booked
    """
    # get the timespan that the user is interested in.
    current_time = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    wanted_end_time = current_time + datetime.timedelta(hours=available_for_hours)

    # if an event starts before end time, and ends after currentTime, then the room is
    # already booked, and should be added to busy_rooms.

    busy_rooms = data.filter(activity__startTime__lte=wanted_end_time,
                             activity__endTime__gte=current_time)

    # rooms that are currently closed should also feature in busy_rooms.

    return busy_rooms


# ======= pc/views functions ======= #

def sortPCLabByDistance(usr_longitude, usr_latitude, data):
    """
    takes user coordinates and a list of PCs, sorts purely according to which are closest to the user.
    :param usr_longitude:
    :param usr_latitude:
    :param data:
    :return: sorted data according to proximity
    """
    data = sorted(data, key=lambda x: get_distance(usr_longitude, usr_latitude, x.longitude, x.latitude))
    return data


def sortPCLabByEmptiness(data):
    """
    sorts list of PC_labs purely according to their usage ratio. From empty to full.
    :param data:
    :return: sorted data according to emptiness
    """
    data = sorted(data, key=lambda x: x.ratio, reverse=True)
    return data


def sortingByLocationAndEmptiness(data, usr_longitude, usr_latitude):
    """
    Performs a weighted ranking of all the PC-labs and sorts them according to a heuristic function,
    which is defined in pc/models.
    :param data:
    :param usr_longitude:
    :param usr_latitude:
    :return: sorted data
    """
    average_distance = 0
    average_ratio = 0
    average_free = 0
    sd_distance = 0
    sd_ratio = 0
    sd_free = 0
    i = 0
    for pc_lab in data:
        average_distance = average_distance + pc_lab.get_distance(long1=usr_longitude, lat1=usr_latitude)
        average_ratio = average_ratio + pc_lab.ratio
        average_free = average_free + pc_lab.free
        i += 1
    if i != 0:
        average_distance = average_distance / i
        average_ratio = average_ratio / i
        average_free = average_free / i
        # calculate the standard deviation of distance and ratio
        for pc_lab in data:
            sd_distance += (pc_lab.get_distance(long1=usr_longitude,
                                                lat1=usr_latitude) - average_distance) ** 2
            sd_ratio += (pc_lab.ratio - average_ratio) ** 2
            sd_free += (pc_lab.free - average_free) ** 2
        sd_distance = (sd_distance / i) ** 0.5
        sd_ratio = (sd_ratio / i) ** 0.5
        sd_free = (sd_free / i) ** 0.5
        # sort the data based on both distance and ratio using a heuristic function
        # of the normalised distance and ratio
        data = sorted(data,
                      key=lambda x: x.get_heuristic(average_distance, average_ratio, average_free, sd_distance,
                                                    sd_ratio, sd_free,
                                                    usr_longitude, usr_latitude))

    return data
