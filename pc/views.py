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
    if request.method == "GET":
        print('nearby:')
        print(bool(request.GET['nearby']))


        if bool(request.GET['empty']):
            data = PC_Space.objects.all().order_by('-ratio')

        if bool(request.GET['nearby']):
            longitude = request.GET['longitude']
            latitude = request.GET['latitude']

            #some code for sorting according to proximity

        if request.GET['campus'] != 'nopref':
            data = PC_Space.objects.order_by('-ratio').filter(group=request.GET['campus'])



        serializer = PC_Space_Serializer(data, many=True)
        print(serializer.data[0])
        return JSONResponse(serializer.data)

