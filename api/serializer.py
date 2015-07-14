from rest_framework import serializers
from pc.models import Computer_Labs


class PC_Space_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Computer_Labs
