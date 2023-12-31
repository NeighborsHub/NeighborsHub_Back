from django.db.models import Count
from rest_framework import serializers

from albums.models import Media
from albums.serializers import MediaSerializer
from post.models import Post, Comment, Like, LikePost
from users.models import Address
from users.serializers import UserSerializer, AddressSerializer


class TruncatedTextField(serializers.CharField):
    def to_representation(self, data):
        if self.max_length and data and len(data) > self.max_length:
            return data[: self.max_length - 3] + "..."
        return data


class RetrievePostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    title = serializers.CharField(max_length=100, allow_null=True)
    body = serializers.CharField(allow_null=False)
    media = MediaSerializer(many=True, read_only=True)
    is_owner = serializers.SerializerMethodField('get_is_owner')

    def get_is_owner(self, obj):
        user = self.context['request'].user
        return obj.created_by == user

    class Meta:
        model = Post
        fields = ('id', 'address', 'title', 'created_by', 'body', 'media',
                  'created_at', 'updated_at', 'is_owner')


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
                  'created_at', 'address_id')


class MyListPostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    title = serializers.CharField(max_length=100)
    body = TruncatedTextField(max_length=100)
    media = serializers.SerializerMethodField('get_truncated_medias')
    likes = serializers.SerializerMethodField('get_likes_count')
    is_user_liked = serializers.SerializerMethodField('get_is_user_like')

    def get_truncated_medias(self, obj):
        qs = obj.media.all()
        qs = qs[:2] if qs is not None and qs.count() > 2 else qs
        return MediaSerializer(instance=qs, many=True).data

    def get_likes_count(self, obj):
        res = LikePost.objects.filter(post_id=obj.id).values('type').annotate(count=Count('type'))
        res = res.values('type', 'count')
        return res
    def get_is_user_like(self, obj):
        res = LikePost.objects.filter(post_id=obj.id, created_by=self.context['request'].user).exists()
        return res

    class Meta:
        model = Post
        fields = ('id', 'created_by', 'address', 'body', 'title', 'media', 'likes', 'is_user_liked')


class CommentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = validated_data.pop('user')
        post = validated_data.pop('post')
        comment = Comment.objects.create(**validated_data,
                                         post=post, created_by=user, updated_by=user)
        comment.save()
        return comment

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_at', 'created_by', 'updated_at')


class ListCommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField('get_replies')
    is_owner = serializers.SerializerMethodField('get_is_owner')

    def get_replies(self, obj):
        replies = Comment.objects.filter(reply_to=obj)
        return ListCommentSerializer(instance=replies, context=self.context, many=True).data

    def get_is_owner(self, obj):
        user = self.context['request'].user
        return obj.created_by == user

    class Meta:
        model = Comment
        fields = ('id', 'body', 'replies', 'is_owner', 'created_at', 'created_by', 'updated_at')


class LikePostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    type = serializers.ChoiceField(default='like', choices=Like.LIKE_CHOICES)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = LikePost
        fields = ('id', 'type', 'created_by', 'created_at')


class LikeCommentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    type = serializers.ChoiceField(default='like', choices=Like.LIKE_CHOICES)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = LikePost
        fields = ('id', 'type', 'created_by', 'created_at')
