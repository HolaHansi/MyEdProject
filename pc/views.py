from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from .models import PC_Space
from .serializer import PC_Space_Serializer

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



def test(request):
    return render(request, 'pc/jsonTest.html')


def filter_suggestions(request):
    if request.method == "GET":
        if request.GET['group'] != 'nopref':
            data = PC_Space.objects.filter(group=request.GET['group'])
        else:
            data = PC_Space.objects.all()


        if bool(request.GET['nearby']):
            usr_longitude = float(request.GET['longitude'])
            usr_latitude = float(request.GET['latitude'])
            data = sorted(data, key=lambda x: x.get_distance(long1=usr_longitude, lat1=usr_latitude))


        serializer = PC_Space_Serializer(data, many=True)
        return JSONResponse(serializer.data)

