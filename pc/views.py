from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from .models import Computer_Labs
from .serializer import PC_Space_Serializer
from django.db.models import Q
from core import utilities
import datetime


def index(request):
    return render(request, 'pc/index.html')


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
        # don't suggest any full or almost full rooms
        data = Computer_Labs.objects.exclude(ratio__lt=0.1)

        # Exclude all rooms that we KNOW are currently closed. (taken from rooms.views)
        data = utilities.excludeClosedLocations(data)

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

        # if sorting by location
        if request.GET['nearby'] == 'true':
            # get the user's latitude and longitude
            usr_longitude = float(request.GET['longitude'])
            usr_latitude = float(request.GET['latitude'])
            # sort the buildings based on distance from user, closest first
            data = sorted(data, key=lambda x: x.get_distance(long1=usr_longitude, lat1=usr_latitude))

            # if sorting by both location and emptiness
            if request.GET['empty'] == 'true':
                # sort according to both location and emptiness using this core/utilities function.
                utilities.sortingByLocationAndEmptiness(data=data,
                                                        usr_longitude=usr_longitude,
                                                        usr_latitude=usr_latitude)

        # if sorting only by emptiness
        elif request.GET['empty'] == 'true':
            # sort by ratio, emptiest first
            data = sorted(data, key=lambda x: x.ratio, reverse=True)

        serializer = PC_Space_Serializer(data, many=True)
        return JSONResponse(serializer.data)
