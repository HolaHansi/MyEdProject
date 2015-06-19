from django.shortcuts import render
from django.http import HttpResponse
from .models import PC_Space
from django.views.generic import View

def index(request):
    return render(request, 'pc/index.html')


def get_group(request, group):
    roomList = PC_Space.objects.filter(group=group)
    context = {'roomList': roomList}
    return render(request, 'pc/index.html', context)

