from rest_framework import serializers

from albums.models import Media
from albums.serializers import MediaSerializer
from post.models import Post
from users.models import Address
from users.serializers import UserSerializer, AddressSerializer


class TruncatedTextField(serializers.CharField):
    def to_representation(self, data):
        if self.max_length and data and len(data) > self.max_length:
            return data[: self.max_length - 3] + "..."
        return data


class PostSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    address_id = serializers.IntegerField(required=True, write_only=True)
    title = serializers.CharField(max_length=100, allow_null=True)
    body = serializers.CharField(allow_null=False)
    medias = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )
    media = MediaSerializer(many=True, read_only=True)

    def create(self, validated_data):
        medias_data = validated_data.pop('medias') if 'medias' in validated_data else []
        user = validated_data.pop('user')
        post = Post.objects.create(**validated_data,
                                   created_by=user,
                                   updated_by=user)
        post.save()

        for file in medias_data:
            media_instance = Media.objects.create(file=file, created_by=user, updated_by=user)
            post.media.add(media_instance)

        return post

    def update(self, instance, validated_data):
        medias_data = validated_data.pop('medias') if 'medias' in validated_data else []
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for file in medias_data:
            media_instance = Media.objects.create(file=file,
                                                  created_by=instance.created_by,
                                                  updated_by=instance.created_by)
            instance.media.add(media_instance)
        return instance

    class Meta:
        model = Post
        fields = ('id', 'address', 'title', 'created_by', 'body', 'updated_by', 'body', 'media', 'medias',
                  'address', 'created_at', 'address_id', 'address')


class MyListPostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    title = serializers.CharField(max_length=100)
    body = TruncatedTextField(max_length=100)
    media = serializers.SerializerMethodField('get_truncated_medias')

    def get_truncated_medias(self, obj):
        qs = obj.media.all()
        qs = qs[:2] if qs is not None and qs.count() > 2 else qs
        return MediaSerializer(instance=qs, many=True).data

    class Meta:
        model = Post
        fields = ('id', 'created_by', 'address', 'body', 'title', 'media',)
