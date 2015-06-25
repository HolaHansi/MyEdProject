from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from .models import Bookable_Room
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

def index(request):
    return render(request, 'rooms/index.html')

def filter_suggestions(request):
    """
    Takes a GET request and returns a list of suggestions based
    on the parameters of the request.
    :param request:
    :return: JSON object
    """
    if request.method == "GET":
        # don't suggest any locally allocated rooms
        data = Bookable_Room.objects.exclude(locally_allocated=1)
        data = data.exclude(description="Theatre Style: Fixed tiered seating")

        # if searching for pc...
        if request.GET['pc'] == 'true':
            data=data.filter(pc='true')
        # if searching for whiteboard...
        if request.GET['whiteboard'] == 'true':
            data=data.filter(whiteboard='true')
        # if searching for projector...
        if request.GET['projector'] == 'true':
            data=data.filter(projector='true')

        # if sorting by location
        if request.GET['nearby'] == 'true':
            # get the user's latitude and longitude
            usr_longitude = float(request.GET['longitude'])
            usr_latitude = float(request.GET['latitude'])
            # sort the buildings based on distance from user, closest first
            data = sorted(data, key=lambda x: x.get_distance(long1=usr_longitude, lat1=usr_latitude))

        serializer = Bookable_Room_Serializer(data, many=True)
        return JSONResponse(serializer.data)

