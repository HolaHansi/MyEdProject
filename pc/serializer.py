from rest_framework import serializers
from pc.models import PC_Space

class PC_Space_Serializer(serializers.ModelSerializer):
    class Meta:
        model = PC_Space