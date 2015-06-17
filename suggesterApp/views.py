from django.shortcuts import render
from django.http import HttpResponse
from pc.models import PC_Space

def index(request):
    roomList = PC_Space.objects.order_by('ratio').reverse()
    context = {'roomList': roomList}
    return render(request, 'core/firstview.html', context)
