from rest_framework import serializers

from albums.models import Media
from post.models import Post
from users.models import Address
from users.serializers import UserSerializer, ListCreateAddressSerializer


class CreatePostSerializer(serializers.ModelSerializer):
    user = UserSerializer(write_only=True)
    address = ListCreateAddressSerializer(read_only=True)
    address_id = serializers.IntegerField(required=False, write_only=True)
    title = serializers.CharField(max_length=100, allow_null=True)
    body = serializers.CharField(allow_null=False)
    media = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        write_only=True, required=False
    )

    def validate(self, data):
        address_id = data.get('address_id', None)
        user = data.get('user', None)
        if not Address.objects.filter(id=address_id, user=user).exists():
            raise serializers.ValidationError('Address is invalid')
        return data

    def create(self, validated_data):
        media_data = self.context.get('request').FILES.getlist('media')
        post = Post.objects.create(**validated_data, created_by=validated_data['user'],
                                   updated_by=validated_data['user'])

        for media_file in media_data:
            Media.objects.create(post=post, file=media_file, created_by=post.created_by, updated_by=post.updated_by)
        return post

    class Meta:
        model = Post
        fields = ('id', 'address', 'title', 'created_by', 'body', 'updated_by', 'body', 'media',
                  'address', 'created_at', 'created_by_id', 'user', 'address_id', 'address')
