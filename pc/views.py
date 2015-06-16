from django.shortcuts import render
import requests
from django.http import HttpResponse
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .models import PC_Space
from .serializer import PC_Space_Serializer



def index(request):
    roomList = PC_Space.objects.order_by('ratio').reverse()
    context = {'roomList': roomList}
    return render(request, 'pc/index.html', context)


def get_group(request, group):
    roomList = PC_Space.objects.filter(group=group).order_by('ratio').reverse()
    context = {'roomList': roomList}
    return render(request, 'pc/index.html', context)


class PCCreateReadView(ListCreateAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'location'


class PCReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'location'



