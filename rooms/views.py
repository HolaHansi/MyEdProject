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
        # don't suggest any lecture theatres
        data = Bookable_Room.objects.exclude(description__icontains="Theatre Style")
        data=data.exclude(room_name__icontains="Lecture Theatre")

        # if searching for bookable spaces...
        if request.GET['bookable'] == 'true':
            data = data.filter(locally_allocated=0)
        # if searching for pc...
        if request.GET['pc'] == 'true':
            data=data.filter(pc='true')
        # if searching for printer...
        if request.GET['printer'] == 'true':
            data=data.filter(printer='true')
        # if searching for whiteboard...
        if request.GET['whiteboard'] == 'true':
            data=data.filter(whiteboard='true')
        # if searching for blackboard...
        if request.GET['blackboard'] == 'true':
            data=data.filter(blackboard='true')
        # if searching for projector...
        if request.GET['projector'] == 'true':
            data=data.filter(projector='true')

        groups = request.GET.getlist('groupsUnselected[]')
        for group in groups:
            data = data.exclude(campus_name=group)

        # if they're currently searching for a building:
        if request.GET['building']=='':
            # work out how many rooms are available in each building
            buildingDetails={}
            for room in data:
                if not (room.abbreviation in buildingDetails):
                    buildingDetails[room.abbreviation]={
                        'abbreviation':room.abbreviation,
                        'rooms':1,
                        'building_name':room.building_name,
                        'latitude':room.latitude,
                        'longitude':room.longitude,
                        'campus':room.campus_name
                    }
                else:
                    buildingDetails[room.abbreviation]['rooms']+=1
            # if sorting by location
            if request.GET['nearby'] == 'true':
                ''''''# TODO:sort the list by location

            return JSONResponse(buildingDetails.values())

        # if they're searching for a room
        # get only rooms within that building
        data = data.filter(abbreviation=request.GET['building'])
        # if sorting by location
        if request.GET['nearby'] == 'true':
            # get the user's latitude and longitude
            usr_longitude = float(request.GET['longitude'])
            usr_latitude = float(request.GET['latitude'])
            # sort the buildings based on distance from user, closest first
            data = sorted(data, key=lambda x: x.get_distance(long1=usr_longitude, lat1=usr_latitude))
        serializer = Bookable_Room_Serializer(data, many=True)
        return JSONResponse(serializer.data)




