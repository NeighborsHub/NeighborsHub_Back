from rest_framework import serializers

from albums.models import Media, UserAvatar


def get_truncate_post_serializer():
    from post.serializers import TruncatePostSerializer
    return TruncatePostSerializer()


class MediaSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = Media
        fields = ('id', 'file', 'created_at')


class MyListMediaSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)
    post = serializers.SerializerMethodField('get_post')

    def get_post(self, obj):
        from post.serializers import TruncatePostSerializer
        return TruncatePostSerializer(instance=obj.post.first(), many=False).data

    class Meta:
        model = Media
        fields = ('id', 'file', 'created_at', 'post')


class UserListMediaSerializer(MyListMediaSerializer):
    created_by = serializers.SerializerMethodField('get_created_by_info')

    def get_created_by_info(self, obj):
        from users.serializers import UserPublicSerializer
        return UserPublicSerializer(instance=obj.created_by, many=False).data

    class Meta:
        model = Media
        fields = ('id', 'file', 'created_at', 'post', 'created_by')


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(max_length=10000, allow_empty_file=False, required=True)
    avatar_thumbnail = serializers.ImageField(read_only=True)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = UserAvatar
        fields = ('id', 'created_at', 'avatar', 'avatar_thumbnail')
