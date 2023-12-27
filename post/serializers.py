from rest_framework import serializers

from albums.models import Media
from albums.serializers import MediaSerializer
from post.models import Post
from users.models import Address
from users.serializers import UserSerializer, AddressSerializer


class CreatePostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    address_id = serializers.IntegerField(required=True, write_only=True)
    title = serializers.CharField(max_length=100, allow_null=True)
    body = serializers.CharField(allow_null=False)
    medias = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True
    )
    media = MediaSerializer(many=True, read_only=True)

    def create(self, validated_data):
        medias_data = validated_data.pop('medias')
        media_files = self.context.get('request').FILES.getlist('medias')
        user = validated_data.pop('user')
        post = Post.objects.create(**validated_data,
                                   created_by=user,
                                   updated_by=user)
        post.save()

        for file in medias_data:
            media_instance = Media.objects.create(file=file, created_by=user, updated_by=user)
            post.media.add(media_instance)

        return post

    class Meta:
        model = Post
        fields = ('id', 'address', 'title', 'created_by', 'body', 'updated_by', 'body', 'media', 'medias',
                  'address', 'created_at', 'user', 'address_id', 'address')
