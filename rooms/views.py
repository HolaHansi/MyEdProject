from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
import math
from rest_framework.renderers import JSONRenderer
from .models import Tutorial_Room
from .serializer import Bookable_Room_Serializer


def index(request):
    return render(request, 'rooms/index.html')


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def filter_suggestions(request):
    """
    Takes a GET request and returns a list of suggestions based
    on the parameters of the request.
    :param request:
    :return: JSON object
    """
    if request.method == "GET":
        data = Tutorial_Room.objects.all()
        # if searching for bookable spaces...
        if request.GET['bookable'] == 'true':
            data = data.filter(locally_allocated=0)
        # if searching for pc...
        if request.GET['pc'] == 'true':
            data = data.filter(pc='true')
        # if searching for printer...
        if request.GET['printer'] == 'true':
            data = data.filter(printer='true')
        # if searching for whiteboard...
        if request.GET['whiteboard'] == 'true':
            data = data.filter(whiteboard='true')
        # if searching for blackboard...
        if request.GET['blackboard'] == 'true':
            data = data.filter(blackboard='true')
        # if searching for projector...
        if request.GET['projector'] == 'true':
            data = data.filter(projector='true')

        # remove any campuses they didn't select
        campuses_to_remove = request.GET.getlist('campusesUnselected[]')
        # if 'other' needs removed...
        if 'Other' in campuses_to_remove:
            query = Q(campus='')
            # remove anything that isn't one of the four main options,
            # but also remove any of the four main options if they've been selected to be removed
            for campus in ['Central', "King's Buildings", "Lauriston", "Holyrood"]:
                if campus not in campuses_to_remove:
                    query = query | Q(campus=campus)
            data = data.filter(query)
        # otherwise, just remove any campuses they've selected to be removed
        else:
            for campus in campuses_to_remove:
                data = data.exclude(campus=campus)

        # if they're currently searching for a building:
        if request.GET['building'] == '':
            # work out how many rooms are available in each building
            building_details = {}
            for room in data:
                if not (room.abbreviation in building_details):
                    building_details[room.abbreviation] = {
                        'abbreviation': room.abbreviation,
                        'rooms': 1,
                        'building_name': room.building_name,
                        'latitude': room.latitude,
                        'longitude': room.longitude,
                        'campus': room.campus_name
                    }
                else:
                    building_details[room.abbreviation]['rooms'] += 1
            # convert it from a JSON of JSONs to a list of JSONs
            building_details = list(building_details.values())
            # if sorting by location
            if request.GET['nearby'] == 'true':
                # get the user's latitude and longitude
                usr_longitude = float(request.GET['longitude'])
                usr_latitude = float(request.GET['latitude'])
                # sort the buildings based on distance from user, closest first
                building_details = sorted(building_details, key=lambda x: get_distance(
                    x['longitude'], x['latitude'], long1=usr_longitude, lat1=usr_latitude))
            # if not sorting by location, sort by number of suitable rooms available
            else:
                building_details = sorted(building_details, key=lambda x: x['rooms'], reverse=True)

            return JSONResponse(building_details)

        # if they're searching for a room...

        # get only rooms within that building
        data = data.filter(abbreviation=request.GET['building'])

        # sort the rooms based on a simple heuristic function
        data = sorted(data, key=lambda x: calculate_heuristic(x), reverse=True)

        # return the rooms
        serializer = Bookable_Room_Serializer(data, many=True)
        return JSONResponse(serializer.data)


# calculate the distance between the current building and the inputted point
# parameters: long1 - the longitude of the user
#             lat1 - the latitude of the user
def get_distance(building_long, building_lat, long1, lat1):
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


# converts from degrees to radians
# parameters: x - the value in degrees to be converted
def to_radians(x):
    return x * math.pi / 180


# calculates how desirable a room is for a user
# the more features the room has, the more desirable it iss
def calculate_heuristic(room):
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
