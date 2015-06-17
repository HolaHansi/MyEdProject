from rest_framework.generics import ListAPIView, RetrieveAPIView
from pc.models import PC_Space
from .serializer import PC_Space_Serializer
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser



from django.shortcuts import render

def index(request):
    return render(request, 'core/base.html')




class PCListView(ListAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'


class PCRetrieveView(RetrieveAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'


@csrf_exempt
def pc_filter(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        HttpResponse(data)

