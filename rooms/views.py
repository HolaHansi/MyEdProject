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
    if request.method == "GET":

        if request.GET['group'] != 'nopref':
            data = Bookable_Room.filter(group=request.GET['group'])
        else:
            data = Bookable_Room.objects.all()

        if bool(request.GET['nearby']):
            usr_longitude = float(request.GET['longitude'])
            usr_latitude = float(request.GET['latitude'])
            data = sorted(data, key=lambda x: x.get_distance(usr_longitude=usr_longitude, usr_latitude=usr_latitude))


        serializer = Bookable_Room_Serializer(data, many=True)
        return JSONResponse(serializer.data)

