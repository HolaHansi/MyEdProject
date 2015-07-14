from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from .models import Computer_Labs
from .serializer import PC_Space_Serializer
from django.db.models import Q


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
                # perform a weighted ranking based on distance and ratio
                # calculate the average distance and ratio:
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

        # if sorting only by emptiness
        elif request.GET['empty'] == 'true':
            # sort by ratio, emptiest first
            data = sorted(data, key=lambda x: x.ratio, reverse=True)

        serializer = PC_Space_Serializer(data, many=True)
        return JSONResponse(serializer.data)
