import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, ChatMessage
from users.models import CustomerUser, OnlineUser


class ChatConsumer(AsyncWebsocketConsumer):
    user = None
    room_id = None
    user_rooms = None

    @staticmethod
    def get_user(user_id):
        return CustomerUser.objects.get(id=user_id)

    @staticmethod
    def get_online_users():
        online_users = OnlineUser.objects.all()
        return [onlineUser.user.id for onlineUser in online_users]

    @staticmethod
    def add_online_user(user):
        try:
            OnlineUser.objects.create(user=user)
        except:
            pass

    @staticmethod
    def delete_online_user(user):
        try:
            OnlineUser.objects.get(user=user).delete()
        except:
            pass

    def save_message(self, message, room_id):
        user_obj = self.user
        chat_obj = ChatRoom.objects.get(room_id=room_id)
        chat_message_obj = ChatMessage.objects.create(
            chat=chat_obj, user=user_obj, message=message
        )
        user_avatar = self.user.get_avatar()
        return {
            'action': 'message',
            'user': user_obj.id,
            'roomId': room_id,
            'message': message,
            'userImage': {
                'thumbnail': user_avatar.avatar_thumbnail.url if user_avatar else None,
            },
            'userName': user_obj.first_name + " " + user_obj.last_name,
            'timestamp': str(chat_message_obj.created_at)
        }

    async def sendOnlineUserList(self):
        online_user_list = await database_sync_to_async(self.get_online_users)()
        chat_messages = {
            'type': 'chat_message',
            'message': {
                'action': 'onlineUser',
                'userList': online_user_list
            }
        }
        await self.channel_layer.group_send('onlineUser', chat_messages)

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        if int(self.user_id) != self.scope.get('user').id:
            await self.close(403, reason='You are not authorized.')
        self.user_rooms = await database_sync_to_async(
            list
        )(ChatRoom.objects.filter(member=self.user_id))
        for room in self.user_rooms:
            await self.channel_layer.group_add(
                room.room_id,
                self.channel_name
            )
        await self.channel_layer.group_add('onlineUser', self.channel_name)
        self.user = self.scope.get('user')
        await database_sync_to_async(self.add_online_user)(self.user)
        await self.sendOnlineUserList()
        await self.accept()

    async def disconnect(self, close_code):
        await database_sync_to_async(self.delete_online_user)(self.user)
        await self.sendOnlineUserList()
        for room in self.user_rooms:
            await self.channel_layer.group_discard(
                room.room_id,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        room_id = text_data_json['roomId']
        chat_message = {}
        if action == 'message':
            message = text_data_json['message']
            user_id = self.scope.get('user').id

            chat_message = await database_sync_to_async(
                self.save_message
            )(message, room_id)
        elif action == 'typing':
            chat_message = text_data_json
        await self.channel_layer.group_send(
            room_id,
            {
                'user': {'username': self.user.username,
                         'first_name': self.user.first_name,
                         'last_name': self.user.last_name},
                'type': 'chat_message',
                'message': chat_message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
