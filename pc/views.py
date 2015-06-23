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

        # filter by group:
        if request.GET['group'] != 'nopref':
            data = PC_Space.objects.filter(group=request.GET['group'])
        else:
            data = PC_Space.objects.all()

        # don't suggest any full rooms:
        data = data.exclude(ratio=0)

        # if sorting by location
        if (request.GET['nearby']=='true'):
            # get the user's latitude and longitude
            usr_longitude = float(request.GET['longitude'])
            usr_latitude = float(request.GET['latitude'])
            # sort the buildings based on distance from user, closest first
            data = sorted(data, key=lambda x: x.get_distance(long1=usr_longitude, lat1=usr_latitude))

            # if sorting by both location and emptiness
            if (request.GET['empty']=='true'):
                # calculate the average distance and ratio:
                averageDistance=0
                averageRatio=0
                i=0
                for x in data:
                    averageDistance=averageDistance + x.get_distance(long1=usr_longitude, lat1=usr_latitude)
                    averageRatio=averageRatio + x.get_ratio()
                    i+=1
                averageDistance=averageDistance/i
                averageRatio=averageRatio/i
                # calculate the standard deviation of distance and ratio
                sdDistance=0
                sdRatio=0
                for x in data:
                    sdDistance=sdDistance + (x.get_distance(long1=usr_longitude, lat1=usr_latitude)-averageDistance)**2
                    sdRatio=sdRatio + (x.get_ratio()-averageRatio)**2
                sdDistance=(sdDistance/i)**0.5
                sdRatio=(sdRatio/i)**0.5
                # sort the data based on both distance and ratio using a heuristic function of the normalised distance and ratio
                data = sorted(data,key=lambda x:x.get_heuristic(averageDistance,averageRatio,sdDistance,sdRatio,usr_longitude,usr_latitude))

        # if sorting only by emptiness
        elif (request.GET['empty']=='true'):
            # sort by ratio, emptiest first
            data = sorted(data, key=lambda x:x.ratio, reverse=True)

        serializer = PC_Space_Serializer(data, many=True)
        return JSONResponse(serializer.data)

