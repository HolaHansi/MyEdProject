from django.shortcuts import render
import requests
from django.http import HttpResponse
from .models import Room


def index(request):
    roomList = Room.objects.order_by('ratio').reverse()
    context = {'roomList': roomList}
    return render(request, 'pc/index.html', context)


def get_group(request, group):
    roomList = Room.objects.filter(group=group).order_by('ratio').reverse()
    context = {'roomList': roomList}
    return render(request, 'pc/index.html', context)
