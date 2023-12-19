from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from core.models import City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City()
        geo_field = "location"
        fields = ['name', 'name_code', 'population', 'location', 'id']
