from rest_framework import serializers
from rooms.models import Tutorial_Room


class Bookable_Room_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial_Room
