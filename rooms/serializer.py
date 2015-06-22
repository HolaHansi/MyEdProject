from rest_framework import serializers
from rooms.models import Bookable_Room

class Bookable_Room_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Bookable_Room