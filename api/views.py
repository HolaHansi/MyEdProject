from rest_framework.generics import ListAPIView, RetrieveAPIView
from pc.models import PC_Space
from .serializer import PC_Space_Serializer
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.shortcuts import render


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def index(request):
    # get_object_or_404(PC_Space, requests.POST.get('story'))
    context = {}
    return render(request, 'core/testerstuff.html', context)



class PCListView(ListAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'


class PCRetrieveView(RetrieveAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'



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



        #
        # print(request.GET['tutRoom'])
        # print(request.GET['nearby'])

