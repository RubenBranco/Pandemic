from rest_framework.serializers import ModelSerializer
from .models import District, Municipality

class DistrictSerializer(ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"

class MunicipalitySerializer(ModelSerializer):
    class Meta:
        model = Municipality
        fields = "__all__"