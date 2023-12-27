from rest_framework import serializers

from albums.models import Media
from post.models import Post
from users.models import Address
from users.serializers import UserSerializer, ListCreateAddressSerializer


class MediaSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)
    class Meta:
        model = Media
        fields = ('id', 'file', 'created_at')
