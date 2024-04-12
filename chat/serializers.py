from rest_framework import serializers

from users.models import CustomerUser
from .models import ChatRoom, ChatMessage
from users.serializers import UserSerializer


class ChatRoomSerializer(serializers.ModelSerializer):
    member = UserSerializer(many=True, read_only=True)
    members = serializers.ListField(write_only=True)

    def create(self, validated_data):
        members = validated_data.pop('members')
        members.append({"id": self.context['request'].user.id})
        chat_rooms = ChatRoom.objects.create(**validated_data)
        chat_rooms.member.set([CustomerUser.objects.get(**user_data) for user_data in members])
        return chat_rooms

    class Meta:
        model = ChatRoom
        exclude = ['id']


class ChatMessageSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.ImageField(source='user.avatar')

    class Meta:
        model = ChatMessage
        exclude = ['id', 'chat']

    @staticmethod
    def get_user_name(obj):
        return obj.user.first_name + ' ' + obj.user.last_name
