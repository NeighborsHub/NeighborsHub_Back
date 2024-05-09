from rest_framework import serializers

from users.models import CustomerUser
from .models import ChatRoom, ChatMessage
from users.serializers import UserSerializer


class ChatRoomMembersSerializer(serializers.ModelSerializer):
    member = UserSerializer(many=True, read_only=True)
    admin = UserSerializer(many=True, read_only=True)
    members = serializers.ListField(write_only=True, allow_null=True, required=False)
    admins = serializers.ListField(write_only=True, allow_null=True, required=False)
    delete_members = serializers.ListField(write_only=True, allow_null=True, required=False)
    delete_admins = serializers.ListField(write_only=True, allow_null=True, required=False)

    def validate(self, attrs):

        if self.instance.type == 'direct' and \
                (len(attrs.get('members', [])) > 0 or len(attrs.get('delete_members', [])) > 0):
            raise serializers.ValidationError({'members': 'In direct message can`t be more or less than one member'})

        if self.instance.type == 'direct' and \
                (len(attrs.get('admins', [])) > 0 or len(attrs.get('delete_admins', [])) > 0):
            raise serializers.ValidationError({'members': 'In direct message can`t have any admin'})

        if len(attrs.get('members', [])) > 0:
            attrs['members'] = [CustomerUser.objects.get(**user_data) for user_data in attrs.get('members')]

        if len(attrs.get('delete_members', [])) > 0:
            attrs['delete_members'] = [CustomerUser.objects.get(**user_data) for user_data in
                                       attrs.get('delete_members')]

        if len(attrs.get('admins', [])) > 0:
            attrs['admins'] = [CustomerUser.objects.get(**user_data) for user_data in attrs.get('admins')]

        if len(attrs.get('delete_admins', [])) > 0:
            attrs['delete_admins'] = [CustomerUser.objects.get(**user_data) for user_data in attrs.get('delete_admins')]
        return attrs

    def update(self, instance, validated_data):
        members = validated_data.pop('members') if 'members' in validated_data else None
        delete_members = validated_data.pop('delete_members') if 'delete_members' in validated_data else None
        admins = validated_data.pop('admins') if 'admins' in validated_data else None
        delete_admins = validated_data.pop('delete_admins') if 'delete_admins' in validated_data else None

        if members is not None:
            for member in members:
                instance.member.add(member)
        if delete_members is not None:
            for delete_member in delete_members:
                instance.member.remove(delete_member)

        if admins is not None and self.instance.type != 'direct':
            for admin in admins:
                instance.admin.add(admin)
        if delete_admins is not None and self.instance.type != 'direct':
            for admin in admins:
                instance.admin.remove(admin)
        return super().update(instance, validated_data)

    class Meta:
        model = ChatRoom
        fields = ['members', 'member', 'admins', 'admin', 'delete_members', 'delete_admins']


class ChatMessageSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.ImageField(source='user.avatar')

    class Meta:
        model = ChatMessage
        exclude = ['chat', 'deleted_by']

    @staticmethod
    def get_user_name(obj):
        return obj.user.first_name + ' ' + obj.user.last_name


class IDFieldSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)


class LeaveChatRoomSerializer(serializers.Serializer):
    delete_my_messages_for_all = serializers.BooleanField(default=False, required=False)
    delete_all_message_for_me = serializers.BooleanField(default=False, required=False)


class RemoveChatMessageSerializer(serializers.Serializer):
    delete_my_messages_for_all = serializers.BooleanField(default=False, required=False)
    delete_all_message_for_me = serializers.BooleanField(default=True, required=False)
    message_ids = serializers.ListField(required=True, child=IDFieldSerializer(required=True), min_length=1)


class ChatRoomSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(required=True, choices=ChatRoom.CHAT_ROOM_CHOICES)
    members = serializers.ListField(write_only=True, min_length=1)
    last_message = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField('get_name')

    def get_name(self, obj):
        if obj.type == 'direct':
            member = obj.member.all().exclude(id=self.context['request'].user.id).last()
            return f'{member.first_name} {member.last_name}'
        return obj.name

    def get_last_message(self, obj):
        message = obj.messages.order_by('-id').exclude(deleted_by=self.context['request'].user).first()
        return ChatMessageSerializer(message, many=False, context=self.context).data if message else None

    def validate(self, attrs):
        if attrs.get('type') == 'direct' and len(attrs.get('members')) > 1:
            raise serializers.ValidationError({'members': 'In direct message can`t be more than one member'})

        attrs.get('members').append({"id": self.context['request'].user.id})
        members = [CustomerUser.objects.get(**user_data) for user_data in attrs.get('members')]

        if attrs.get('type') == 'direct' and ChatRoom.objects.filter(type=attrs.get('type'),
                                                                     member__in=[m.id for m in members]).exists():
            raise serializers.ValidationError({'members': 'You have already Direct Message for This person'})

        attrs['members'] = members
        return attrs

    def create(self, validated_data):
        members = validated_data.pop('members')
        # members.append({"id": self.context['request'].user.id})
        chat_rooms = ChatRoom.objects.create(**validated_data)
        chat_rooms.member.set(members)
        if self.validated_data['type'] != 'direct':
            chat_rooms.admin.set([self.context.get('request').user])
        return chat_rooms

    class Meta:
        model = ChatRoom
        exclude = ['id', 'member', 'admin', ]

