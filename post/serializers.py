from rest_framework import serializers

from albums.models import Media
from post.models import Post


class ListCreateAddressSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, allow_null=True)
    body = serializers.CharField(allow_null=False)
    media = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        write_only=True, required=False
    )

    def create(self, validated_data):
        media_data = self.context.get('request').FILES.getlist('media')
        post = Post.objects.create(**validated_data)

        for media_file in media_data:
            Media.objects.create(post=post, file=media_file)
        return post

    class Meta:
        model = Post
        fields = ()