import datetime

from rest_framework import serializers

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
        from_days = self.context['request'].query_params.get('from_days')
        if from_days is not None:
            from_datetime = datetime.datetime.now() - datetime.timedelta(days=int(from_days))
            return obj.post_set.filter(created_at__gte=from_datetime).count()
        return obj.post_set.all().count()

    class Meta:
        model = Hashtag
        fields = ['id', 'hashtag_title', 'count']
