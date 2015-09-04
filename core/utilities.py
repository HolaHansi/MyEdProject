"""
This module contains all the utility functions needed for the views of pc and rooms.
When defining a new function that should work for more than one view, please define it here!
"""
import datetime
from itertools import chain
from django.utils import timezone
import math
from rooms.models import Activity
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from django.db.models import F
from django.utils.timezone import utc


# ======= general functions ======= #

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
    converts degrees to radians
    """
    return x * math.pi / 180


def get_distance(long0, lat0, long1, lat1):
    """
    calculate the distance between the current building and the inputted point
    parameters: long1 - the longitude of the user
    lat1 - the latitude of the user
    """
    earth_radius = 6371000  # metres
    # convert all coordinates to radians
    t1 = to_radians(lat1)
    t2 = to_radians(lat0)
    dt = to_radians(lat0 - lat1)
    dl = to_radians(long0 - long1)
    # do some clever maths which the internet told me was correct
    a = math.sin(dt / 2) * math.sin(dt / 2) + math.cos(t1) * math.cos(t2) * math.sin(dl / 2) * math.sin(dl / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # return the distance between the points
    return earth_radius * c


# ======= lab sorting functions ======= #

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
        average_distance += get_distance(pc_lab.longitude, pc_lab.latitude, usr_longitude, usr_latitude)
        average_ratio = average_ratio + pc_lab.ratio
        average_free = average_free + pc_lab.free
        i += 1
    if i != 0:
        average_distance = average_distance / i
        average_ratio = average_ratio / i
        average_free = average_free / i
        # calculate the standard deviation of distance and ratio
        for pc_lab in data:
            sd_distance += (get_distance(pc_lab.longitude, pc_lab.latitude, usr_longitude, usr_latitude)
                            - average_distance) ** 2
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


# ======= rooms sorting functions ======= #

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
        x['longitude'], x['latitude'], usr_longitude, usr_latitude))

    return building_details


# ======= location availability functions ======= #

def getOpenHours(location):
    """
    given a location the function returns a dictionary containing opening and closing hours on the current day.
    :param location:
    :return: dictionary
    """

    # get time now
    now = datetime.datetime.now().replace(tzinfo=utc)
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
    Takes a location and returns true if the location is currently open.
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
        return True
    # this is the second more unusual case where the room is open (e.g. closing hour: 2 am)
    elif closing_hour < open_hour <= now.time() or now.time() < closing_hour < open_hour:
        return True
    else:
        return False


def isBusy(room):
    # returns true if the room currently has an activity in it
    current_time = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    activities = Activity.objects.filter(tutorialRooms=room)
    activities = activities.filter(startTime__lte=current_time, endTime__gte=current_time)
    return activities.count() != 0


def exclude_busy_rooms(data, available_for_hours=1):
    """
    Exclude all the rooms that are hosting any activities in the next x hours.
    Does not take into account building opening hours.
    :param available_for_hours:
    :return: data of rooms that are not currently booked
    """
    # get the timespan that the user is interested in.
    current_time = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    wanted_end_time = current_time + datetime.timedelta(hours=available_for_hours)

    # if an event starts before end time, and ends after currentTime, then the room is booked
    busy_rooms = data.filter(activity__startTime__lte=wanted_end_time,
                             activity__endTime__gte=current_time)

    # exclude all rooms that are busy from the room suggestions (data)
    busy_rooms = [x.locationId for x in busy_rooms]
    data = data.exclude(locationId__in=busy_rooms)

    return data


def exclude_avail_rooms(data, available_for_hours=1):
    """
    Get all rooms that are currently booked
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


def exclude_closed_locations(data):
    """
    Given a queryset of either rooms or pc-labs, the function returns a queryset without any currently closed locations.
    It does NOT filter out buildings without opening hours, nor does it take activities into account.
    :param data:
    :return: data (without any closed PCs or Rooms)
    """

    # get current time and weekday
    now = datetime.datetime.now().replace(tzinfo=utc)
    current_time = now.time().isoformat()
    weekday = now.weekday()

    # this uses exclude instead of filter, so not to filter out all the rooms without opening times.
    # if it's a day between Mon-Fri, then filter out all closed rooms on these days.
    if 0 <= weekday <= 4:
        # case 1 : now < open < closing
        data = data.exclude(weekdayOpen__gt=current_time,
                            weekdayOpen__lt=F('weekdayClosed'))
        # case 2 : open < close < now
        data = data.exclude(weekdayClosed__lt=current_time,
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


def exclude_open_locations(data, typeOfSpace='PC'):
    """
    given a queryset of both closed and open locations, returns all the currently closed places.
    A parameter specifies whether the queryset is for PCs or rooms.
    Doesn't take activities into account, this is purely based on opening hours
    """
    open_places = exclude_closed_locations(data)
    if typeOfSpace == 'PC':
        open_places_list = [x.id for x in open_places]
        data = data.exclude(id__in=open_places_list)
    else:
        open_places_list = [x.locationId for x in open_places]
        data = data.exclude(locationId__in=open_places_list)
    return data


def time_until_available(room):
    """
    Given a room, will return a string detailing how long it is until the room is available.
    :param room:
    :return:
    """

    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    tomorrow = now + datetime.timedelta(hours=24)

    # get all of the rooms activities ending after now, but starting before tomorrow.
    activities = Activity.objects.filter(tutorialRooms=room,
                                         endTime__gt=now,
                                         startTime__lt=tomorrow)
    activities = activities.order_by("startTime")

    # if the place is open, then we know that the reason the place is unavailable is due
    # to an activity that is currently taking place.
    if isOpen(room):

        # go through the activities, and get the end time of the first activity whose endTime
        # is at least an hour prior to the next activity.
        avail_til_time = None
        for i in range(activities.count() - 1):
            if activities[i].endTime <= (activities[i + 1].startTime - datetime.timedelta(hours=1)):
                avail_til_time = activities[i].endTime
                break

        # if avail_til_time is still undefined, then every activity immediately follows the next.
        # Hence, take the last activity end time as when the room is available til
        if avail_til_time is None:
            avail_til_time = activities[activities.count() - 1].endTime

        # if we know that the building closes just after the final activity ends, return that it'll open tomorrow
        if (getOpenHours(room)['closingHour'] and
                avail_til_time.time() < (datetime.datetime.combine(now.date(), getOpenHours(room)['closingHour'])
                                         - datetime.timedelta(hours=1)).time()):
            return "Tomorrow"

        # get the time from now until avail_til_time.
        avail_for = avail_til_time - now

    # otherwise, the room is currently Closed, and this is why it's unavailable. Find out when it opens
    else:
        # get open hour - we know this is available because the room is closed.
        full_opening_times = getOpenHours(room)
        open_hour = full_opening_times['openHour']

        # if the room is about to open later same day, then avail_til_time is openHour + the duration
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
                avail_til_time = open_hour_date_time
            # Otherwise, find the endTime of the last activity in a potential consecutive streak of activities.
            # the code is the same as in the 'isOpen - condition'.
            else:
                activities = activities.filter(startTime__gte=open_hour_date_time)
                activities = activities.order_by("startTime")
                avail_til_time = None
                for i in range(activities.count() - 1):
                    if activities[i].endTime <= (activities[i + 1].startTime - datetime.timedelta(hours=1)):
                        avail_til_time = activities[i].endTime
                        break
                # if avail_till is undefined, then every activity immediately follows the next.
                # Hence, take the last activity end time as when the room is available til
                if avail_til_time is None:
                    avail_til_time = activities[activities.count() - 1].endTime
                # if we know that the building closes just after the final activity ends,return that it'll open tomorrow
                if (getOpenHours(room)['closingHour'] and
                        avail_til_time.time() < (
                            datetime.datetime.combine(now.date(), getOpenHours(room)['closingHour'])
                            - datetime.timedelta(hours=1)).time()):
                    return "Tomorrow"
            # get the difference between time it becomes available and now.
            avail_for = avail_til_time - datetime.datetime.combine(datetime.date.today(), now.time())

        # otherwise the room will open tomorrow
        else:
            return "Tomorrow"

    # get the hours and minutes
    avail_for_hours = avail_for.seconds // 3600
    if avail_for_hours > 23:
        return "Tomorrow"
    else:
        # return result as a string
        return format_time(avail_for)


def get_available_for(room):
    """
    Given a room, will return a datetime object detailing how long it is until the room is unavailable.
    Otherwise, for example if there is no activites or opening hours, or no opening hours an activity the following day.
    The field will be updated with the string value 'unknown'.
    :param room:
    :return: datetime object
    """
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())

    # get the closing hour of the room
    full_opening_times = getOpenHours(room)
    closing_hour = full_opening_times['closingHour']

    # if we don't know when the building closes, return 'unknown'
    if closing_hour is None:
        return "unknown"

    # get all activities for the room beginning after now.
    activities = Activity.objects.filter(tutorialRooms=room, startTime__gt=now)

    # work out the date when the room closes rather than just the time
    closing_datetime = datetime.datetime.combine(now.date(), closing_hour)
    # if the room has already closed today (early in the morn), then it closes tomorrow
    if closing_hour < now.time():
        closing_datetime = closing_datetime + datetime.timedelta(days=1)

    # if there are no activities, then the room must be unavailable when the building closes
    if activities.count() == 0:
        avail_till_time = timezone.make_aware(closing_datetime, now.tzinfo)
    else:
        # get the starting time of the earliest activity
        activities = activities.order_by("startTime")
        activity_start_time = activities[0].startTime
        # if room closes before the start of the next activity,
        # then the room must be unavailable first when the building closes
        if activity_start_time >= closing_datetime:
            avail_till_time = timezone.make_aware(closing_datetime, now.tzinfo)
        # otherwise, the room is unavailable when the next activity starts
        else:
            avail_till_time = timezone.make_aware(activity_start_time, datetime.timezone.utc)
    return avail_till_time - now


def time_until_unavailable(room):
    # return the time until the room is unavailable as a formatted string in the format "Xh Ym"
    return format_time(get_available_for(room))


def get_available_for_many_hours(rooms, available_for_hours):
    # filter out all rooms available for less than available_for_hours
    # note that this also unfortunately converts the queryset into a list

    # filter out all rooms unavailable now
    get_available_rooms(rooms, available_for_hours)
    # filter out all rooms available for less than the number of hours input
    return [room for room in rooms if room_is_available_for_x_hours(room, available_for_hours)]


def room_is_available_for_x_hours(room, available_for_hours):
    # helper function to prevent get_available_for() being called twice
    availability = get_available_for(room)
    return availability == 'unknown' or availability.seconds // 3600 >= available_for_hours


def format_time(time):
    # Takes a datetime object and returns it as a string in the format "Xh Ym"
    # get the hours and minutes
    if type(time) is str:
        return time
    hours = time.seconds // 3600
    minutes = (time.seconds // 60) % 60
    # return result as a string
    return str(hours) + "h " + str(minutes) + "m"


def get_availability(room):
    """
    Returns the availability status of the room
    """
    if not isOpen(room):
        return 'shut'
    if isBusy(room):
        return 'busy'
    elif room.locally_allocated:
        return 'localAvailable'
    else:
        return 'available'


def get_available_rooms(data, available_for_hours=0):
    # get all centrally allocated rooms which will be available for the next x hours
    data = data.filter(locally_allocated=False)
    data = exclude_busy_rooms(data, available_for_hours)
    data = exclude_closed_locations(data)
    return data


def get_open_local_rooms(data):
    # get all rooms which are locally booked but their building isn't closed
    data = data.filter(locally_allocated=True)
    data = exclude_closed_locations(data)
    return data


def get_unavailable_rooms(data):
    # get all rooms which are definitely shut
    rooms_globally_allocated = data.filter(locally_allocated=False)
    closed_rooms = exclude_open_locations(data, typeOfSpace='Room')
    rooms_currently_booked = exclude_avail_rooms(data=rooms_globally_allocated, available_for_hours=0)
    rooms_not_available_now = chain(closed_rooms, rooms_currently_booked)
    return rooms_not_available_now
