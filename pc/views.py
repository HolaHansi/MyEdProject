from django.shortcuts import render
from django.http import HttpResponse
from .models import PC_Space
from django.views.generic import View
import json

def index(request):
    roomList = PC_Space.objects.all()
    context = {'roomList': roomList}
    return render(request, 'pc/index.html', context)


def get_group(request, group):
    roomList = PC_Space.objects.filter(group=group)
    context = {'roomList': roomList}
    return render(request, 'pc/index.html', context)

