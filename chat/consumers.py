import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, ChatMessage
from users.models import CustomerUser, OnlineUser


class ChatConsumer(AsyncWebsocketConsumer):
    user_id = None
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

    @staticmethod
    def save_message(self, message, user_id, room_id):
        user_obj = CustomerUser.objects.get(id=user_id)
        chat_obj = ChatRoom.objects.get(roomId=room_id)
        chat_message_obj = ChatMessage.objects.create(
            chat=chat_obj, user=user_obj, message=message
        )
        return {
            'action': 'message',
            'user': user_id,
            'roomId': room_id,
            'message': message,
            'userImage': user_obj.image.url,
            'userName': user_obj.first_name + " " + user_obj.last_name,
            'timestamp': str(chat_message_obj.timestamp)
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
        self.user_id = self.scope['url_route']['kwargs']['userId']
        self.user_rooms = await database_sync_to_async(
            list
        )(ChatRoom.objects.filter(member=self.user_id))
        for room in self.user_rooms:
            await self.channel_layer.group_add(
                room.roomId,
                self.channel_name
            )
        await self.channel_layer.group_add('onlineUser', self.channel_name)
        self.user = await database_sync_to_async(self.get_user)(self.user_id)
        await database_sync_to_async(self.add_online_user)(self.user)
        await self.sendOnlineUserList()
        await self.accept()

    async def disconnect(self, close_code):
        await database_sync_to_async(self.delete_online_user)(self.user)
        await self.sendOnlineUserList()
        for room in self.user_rooms:
            await self.channel_layer.group_discard(
                room.roomId,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        room_id = text_data_json['roomId']
        chat_message = {}
        if action == 'message':
            message = text_data_json['message']
            user_id = text_data_json['user']
            chat_message = await database_sync_to_async(
                self.save_message
            )(message, user_id, room_id)
        elif action == 'typing':
            chat_message = text_data_json
        await self.channel_layer.group_send(
            room_id,
            {
                'type': 'chat_message',
                'message': chat_message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
