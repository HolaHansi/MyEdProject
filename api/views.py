from rest_framework.generics import ListAPIView, RetrieveAPIView
from pc.models import PC_Space
from .serializer import PC_Space_Serializer
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse



class PCListView(ListAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'






class PCRetrieveView(RetrieveAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'

