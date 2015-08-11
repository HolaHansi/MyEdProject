from rest_framework import serializers
from rooms.models import Tutorial_Room, Activity


class Bookable_Room_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial_Room


class Activity_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Activity