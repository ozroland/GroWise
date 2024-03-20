from rest_framework import serializers
from hydroponic.models import OperatingData

class OperatingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatingData
        fields = '__all__'  
