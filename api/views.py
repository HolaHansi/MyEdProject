from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from pc.models import PC_Space
from .serializer import PC_Space_Serializer


class PCCreateReadView(ListCreateAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'


class PCReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'

