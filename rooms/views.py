from django.shortcuts import render

def index(request):
    return render(request, 'rooms/index.html')

# Create your views here.
