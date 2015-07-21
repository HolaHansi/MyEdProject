import datetime
import math

# functions used in both pc/views and rooms/views

def to_radians(x):
    return x * math.pi / 180

def excludeClosedLocations(data):
    """
    Given a queryset of either rooms or pc-labs, the function returns a queryset without any currently closed rooms.
    :param data:
    :return:
    """

    # get current time and weekday
    now = datetime.datetime.now()
    currentTime = now.time().isoformat()
    weekday = now.weekday()

    # I'm using exclude instead of filter, so not to filter out all the rooms without opening times.
    # if it's a day between Mon-Fri, then filter out all closed rooms on these days.
    if weekday >= 0 and weekday <= 4:
        data = data.exclude(weekdayOpen__gt=currentTime)
        data = data.exclude(weekdayClosed__lt=currentTime,
                            # to accomodate the case where the building closes after midnight
                            # a building is only excluded if the closing time is ALSO greater than
                            # 9 in the morning, so closing times like 02:30 are not filtered out.
                            weekdayClosed__gt="09:00:00"
                            )

    # the same thing for saturday.
    if weekday == 5:
        data = data.exclude(saturdayOpen__gt=currentTime)
        data = data.exclude(saturdayClosed__lt=currentTime,
                            # to accomodate the case where the building closes after midnight
                            # a building is only excluded if the closing time is ALSO greater than
                            # 9 in the morning, so closing times like 02:30 are not filtered out.
                            saturdayClosed__gt="09:00:00"
                            )

    # if it's sunday... etc.
    if weekday == 6:
        data = data.exclude(sundayOpen__gt=currentTime)
        data = data.exclude(sundayClosed__lt=currentTime,
                            # to accomodate the case where the building closes after midnight
                            # a building is only excluded if the closing time is ALSO greater than
                            # 9 in the morning, so closing times like 02:30 are not filtered out.
                            sundayClosed__gt="09:00:00"
                            )
    return data



# rooms/views functions

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


# pc/views functions

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
