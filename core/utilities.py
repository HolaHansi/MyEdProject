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
from django.db.models import F

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
        # case 1 : now < open < closing
        data = data.exclude(weekdayOpen__gt=currentTime,
                            weekdayClosed__gt=currentTime,
                            weekdayOpen__lt=F('weekdayClosed'))
        # case 2 : open < close < now
        data = data.exclude(weekdayOpen__lt=currentTime,
                            weekdayClosed__lt=currentTime,
                            weekdayClosed__gt=F('weekdayOpen'))

        # case 3 : close < now < open
        data = data.exclude(weekdayOpen__gt=currentTime,
                            weekdayClosed__lt=currentTime)


    # saturday
    if weekday == 5:
        # case 1 : now < open < closing
        data = data.exclude(saturdayOpen__gt=currentTime,
                            saturdayClosed__gt=currentTime,
                            saturdayOpen__lt=F('saturdayClosed'))
        # case 2 : open < close < now
        data = data.exclude(saturdayOpen__lt=currentTime,
                            saturdayClosed__lt=currentTime,
                            saturdayClosed__gt=F('saturdayOpen'))

        # case 3 : close < now < open
        data = data.exclude(saturdayOpen__gt=currentTime,
                            saturdayClosed__lt=currentTime)

    # sunday
    if weekday == 6:
        # case 1 : now < open < closing
        data = data.exclude(sundayOpen__gt=currentTime,
                            sundayClosed__gt=currentTime,
                            sundayOpen__lt=F('sundayClosed'))

        # case 2 : open < close < now
        data1 = data.exclude(sundayOpen__lt=currentTime,
                            sundayClosed__lt=currentTime,
                            sundayClosed__gt=F('sundayOpen'))

        # case 3 : close < now < open
        data = data1.exclude(sundayOpen__gt=currentTime,
                            sundayClosed__lt=currentTime)

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

def getOpenHours(location):
    """
    given a location the function returns a dictionary containing opening and closing hours on the current
    day.
    :param location:
    :return: dictionary
    """
    now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())
    weekday = now.weekday()

    # get the current opening hours of the room
    if weekday >= 0 and weekday <= 4:
       closingHour = location.weekdayClosed
       openHour = location.weekdayOpen

    elif weekday == 5:
        closingHour = location.saturdayClosed
        openHour = location.saturdayOpen
    else:
        closingHour = location.sundayClosed
        openHour = location.sundayOpen

    dict = {'openHour': openHour, 'closingHour': closingHour}

    return dict


def isOpen(location):
    """
    Takes a location and returns true if the location is currently open. Sensitive to weekdays!
    :param location:
    :return: boolean
    """
    now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())

    # get the current opening hours of the room
    dict = getOpenHours(location)
    openHour = dict['openHour']
    closingHour = dict['closingHour']

    # if opening hours are None, then just return True (they are not closed for all we know!)
    if openHour is None or closingHour is None:
        return True

     # determine if the place is currently open.
    if openHour < now.time() < closingHour:
        isOpenVar = True
    # this is the second more unusual case where the room is open (e.g. closing hour: 2 am)
    elif closingHour < openHour <= now.time() or now.time() < closingHour < openHour:
        isOpenVar = True
    else:
        isOpenVar = False

    return isOpenVar


def unavailable_till_hours(unavailable_rooms):
    """
    given a queryset of rooms, the function will populate the unavailableFor field of every room in the queryset.
    :param unavailable_room:
    :return:
    """

    now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())
    tomorrow = now + datetime.timedelta(hours=24)

    for unavailable_room in unavailable_rooms:
        # get all of the rooms activities ending after now, but starting before tomorrow.
        activities = act.objects.filter(tutorialRooms=unavailable_room,
                                        endTime__gt=now,
                                        startTime__lt=tomorrow)

        # check if location is open
        isOpenVar = isOpen(unavailable_room)


        # if the place is open, then we know that the reason the place is unavailable is due
        # to an activity that is currently taking place.
        if isOpenVar:
            # go through the activities, and get the end time of the first activity whose endTime
            # is at least an hour prior to the next activity.
            # first, initialize avail_till
            avail_till_time = None
            for i in range(activities.count()-1):
                if activities[i].endTime <= (activities[i+1].startTime - datetime.timedelta(hours=1)):
                    avail_till_time = activities[i].endTime
                    break
            # if avail_till is undefined, then every activity except the final one has been checked, and
            # has failed this condition. Hence, take the last activity.endTime as avail_till.

            print('activity', activities)
            print('room is ', unavailable_room)
            print('room is open, ', isOpenVar)

            if avail_till_time is None:
                avail_till_time = activities[activities.count()-1].endTime


            # now get the time from now until avail_till_time.
            avail_for = avail_till_time - now

            # get the hours and minutes
            avail_for_hours = avail_for.seconds // 3600
            avail_for_minutes = (avail_for.seconds // 60) % 60

            # return result as a string
            unavailForString = str(avail_for_hours) + "h " + str(avail_for_minutes) + "m"
            unavailable_room.unavailableFor = unavailForString
            unavailable_room.save()
            continue



        # otherwise, the room is currently Closed, and this is why it's unavailable. Find out when it opens
        else:
            # get open and closing hour - we know these are available because the room is closed.
            dict = getOpenHours(unavailable_room)
            openHour = dict['openHour']
            closingHour = dict['closingHour']


            # if the room is about to open later same day, then avail_till_time is openHour + the duration
            # of any potential activities starting from openHour.
            if now.time() < openHour:
                # get openHour as datetime object and initialize variable which is an hour after opening.
                openHourDateTime = datetime.datetime.combine(datetime.date.today(), openHour)
                anHourLater = openHourDateTime + datetime.timedelta(hours=1)

                # get all activities starting in the first hour of the room being open.
                activities = activities.filter(startTime__lt=anHourLater,
                                               startTime__gte=openHourDateTime)

                # In case, there are no such activities, then the room will surely be available on opening
                if activities.count() == 0:
                    avail_till_time = openHourDateTime

                # Otherwise, find the endTime of the last activity in a potential consecutive streak of activities.
                # the code is the same as in the 'isOpen - condition'.
                else:
                    avail_till_time = None
                    for i in range(activities.count()-1):
                        if activities[i].endTime <= (activities[i+1].startTime - datetime.timedelta(hours=1)):
                            avail_till_time = activities[i].endTime
                            break
                    # if avail_till is undefined, then every activity except the final one has been checked, and
                    # has failed this condition. Hence, take the last activity.endTime as avail_till.
                    if avail_till_time is None:
                        avail_till_time = activities[activities.count()-1].endTime


                # get the difference between time it becomes available and now.
                avail_for = avail_till_time - datetime.datetime.combine(datetime.date.today(), now.time())


                # get the hours and minutes
                avail_for_hours = avail_for.seconds // 3600
                avail_for_minutes = (avail_for.seconds // 60) % 60

                # return result as string
                unavailForString = str(avail_for_hours) + "h " + str(avail_for_minutes) + "m"
                unavailable_room.unavailableFor = unavailForString
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
    :param available_room:
    :return: nothing - the function updates a field in every room of available_rooms.
    """
    now = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())
    weekday = now.weekday()

    for available_room in available_rooms:
        # get all activities for the room beginning after now.
        activities = act.objects.filter(tutorialRooms=available_room,
                                        startTime__gt=now)

        # order from most recent till most distant
        activities = activities.order_by("startTime")

        # true if there is no activities for the room.
        noAct = False

        # true if activity decides available_till.
        actWins = False

        # check if there are any activities

        if activities.count() == 0:
            noAct = True
        else:
            next_activity = activities[0]
            # get the starting_time of this activity (type is datetime.datetime)
            startTime = next_activity.startTime


        # get the current closing hour of the room
        dict = getOpenHours(available_room)
        closingHour = dict['closingHour']

        # no closing hour nor activities for room - return unknown
        if closingHour is None and noAct:
            available_room.availableFor = 'unknown'
            available_room.save()
            continue

        # closing hour, but no activities - closingHour becomes avail_till.
        elif closingHour is not None and noAct:
            avail_till_time = closingHour

        # if there is no closing hour, but there is an activity, then activity wins.
        elif closingHour is None and not noAct:
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

    # rooms that are currently closed should also feature in busy_rooms.


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
