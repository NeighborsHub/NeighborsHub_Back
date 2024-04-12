from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from users.serializers import UserSerializer


class ChatRoomSerializer(serializers.ModelSerializer):
    member = UserSerializer(many=True, read_only=True)
    members = serializers.ListField(write_only=True)

    def create(self, validated_data):
        member_obj = validated_data.pop('members')
        chat_rooms = ChatRoom.objects.create(**validated_data)
        chat_rooms.member.set(member_obj)
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
