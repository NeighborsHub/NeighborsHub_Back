from rest_framework import serializers

from albums.models import Media, UserAvatar


class MediaSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = Media
        fields = ('id', 'file', 'created_at')


class UserAvatarSerializer(serializers.ModelSerializer):
    media = MediaSerializer()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = UserAvatar
        fields = ('id', 'created_at', 'media')
