from django.shortcuts import render
from django.http import HttpResponse
from pc.models import PC_Space

def index(request):
    return render(request, 'frontpage/index.html')
