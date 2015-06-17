from rest_framework.generics import ListAPIView, RetrieveAPIView
from pc.models import PC_Space
from .serializer import PC_Space_Serializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django



class PCFilters(APIView):
    """
    Retrive lists of PCs that meet given criteria
    """
    def post(self, request, format='json'):
        params = request.query_params
        return


class PCListView(ListAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'






class PCReadUpdateDeleteView(ListAPIView):
    queryset = PC_Space.objects.all().order_by('ratio').reverse()
    serializer_class = PC_Space_Serializer
    lookup_field = 'id'

