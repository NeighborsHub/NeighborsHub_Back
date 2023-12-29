from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from core.models import City, Country, State, Hashtag


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        geo_field = "location"
        fields = ['emoji', 'name', 'name_code', 'capital', 'phone_code', 'emoji', 'location', 'id']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        geo_field = "location"
        fields = ['name', 'name_code', 'abbreviation', 'capital', 'location', 'country', 'id']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        geo_field = "location"
        fields = ['name', 'name_code', 'population', 'location', 'id']


class HashtagSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField('get_count_hashtags')

    def get_count_hashtags(self, obj):
        qs = obj.post_set.all().count()
        return qs

    class Meta:
        model = Hashtag
        fields = ['id', 'hashtag_title', 'count']
