from rest_framework import serializers
from .models import *

class ViolatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Violator
        fields = [
            'id',
            'image',
            'missing_ppe',
            'timestamp'
        ]