from django.test import TestCase
from model_bakery import baker
from rest_framework import status

from NeighborsHub.test_function import test_object_attributes_existence
from chat.models import ChatRoom, ChatMessage, UserSeenMessage
from users.models import CustomerUser
from users.tests import _create_user
from rest_framework.test import APIClient
from rest_framework.reverse import reverse


class TsetChatRoomModel(TestCase):

    def test_property_type_model_exists(self):
        a = ChatRoom()
        self.assertTrue(isinstance(a, ChatRoom))

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'type', 'room_id', 'created_at', 'member', 'name', 'admin'
        ]
        chat_room = ChatRoom
        test_object_attributes_existence(self, chat_room, attributes)

    def test_user_model(self):
        created_obj = baker.make(ChatRoom)
        test_obj = ChatRoom.objects.filter(id=created_obj.id).first()
        self.assertIsNotNone(test_obj)


class TsetChatMessageModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        ChatMessage()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'chat_id', 'message', 'user_id', 'post_id', 'reply_to_id',
            'updated_at', 'deleted_by', 'created_at'
        ]
        chat_message = ChatMessage
        test_object_attributes_existence(self, chat_message, attributes)

    def test_successfully_create(self):
        created_obj = baker.make(ChatMessage)
        test_obj = ChatMessage.objects.filter(id=created_obj.id).first()
        self.assertIsNotNone(test_obj)


class TestCreateDirectMessage(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.post(reverse('chatRoom'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_direct_chatroom(self):
        self.client.force_authenticate(self.user)
        tmp_user = baker.make(CustomerUser)
        tmp_user_2 = baker.make(CustomerUser)
        data = {
            'type': 'direct',
            'members': [{'id': tmp_user.id}],
            'name': 'Test Direct'
        }
        response = self.client.post(reverse('chatRoom'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('chatRoom'), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('error', response_json['status'])
        self.assertIn('members', response_json['data'])

    def test_create_group_chatroom(self):
        self.client.force_authenticate(self.user)
        tmp_user = baker.make(CustomerUser)
        tmp_user_2 = baker.make(CustomerUser)
        data = {
            'type': 'group',
            'members': [{'id': tmp_user.id}, {'id': tmp_user_2.id}],
            'name': 'Test Direct'
        }
        response = self.client.post(reverse('chatRoom'), data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('type', response_json['data'])
        self.assertIn('room_id', response_json['data'])


class TsetChatMessageModel(TestCase):
    @staticmethod
    def test_property_type_model_exists():
        ChatMessage()

    def test_property_type_model_has_all_required_attributes(self):
        attributes = [
            'chat_id', 'message', 'user_id', 'post_id', 'reply_to_id',
            'updated_at', 'deleted_by', 'created_at'
        ]
        chat_message = ChatMessage
        test_object_attributes_existence(self, chat_message, attributes)

    def test_successfully_create(self):
        created_obj = baker.make(ChatMessage)
        test_obj = ChatMessage.objects.filter(id=created_obj.id).first()
        self.assertIsNotNone(test_obj)


class TestListUserChatRoom(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.dummy_user = baker.make(CustomerUser, first_name='John', last_name='Doe')
        self.ch_1 = baker.make(ChatRoom, type='direct')
        self.ch_1.member.add(self.dummy_user)
        self.ch_1.member.add(self.user)
        self.message = baker.make(ChatMessage, chat=self.ch_1, user=self.dummy_user, message='Hello Milad')

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.get(reverse('chatRoom'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_user_chat_rooms(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('chatRoom'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual('direct', response_json['data'][0]['type'])
        self.assertEqual('John Doe', response_json['data'][0]['name'])
        self.assertIn('last_message', response_json['data'][0])
        self.assertIn('room_id', response_json['data'][0])

    def test_last_message_not_show_deleted(self):
        self.message.deleted_by.add(self.user)
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('chatRoom'), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertIn('last_message', response_json['data'][0])
        self.assertIsNone(response_json['data'][0]['last_message'])


class TestChatRoomMemberListMessage(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.tmp_user = baker.make(CustomerUser)
        self.chat_room = baker.make(ChatRoom, type='group')
        self.chat_room.member.set([self.tmp_user, self.user])
        self.chat_room.admin.set([self.user, self.tmp_user])

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.get(reverse('membersList', kwargs={'room_id': self.chat_room.room_id}),
                                   data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_updates_anonymous_user(self):
        anonymous_user = baker.make(CustomerUser)
        self.client.force_authenticate(anonymous_user)
        data = {
            'admins': [{'id': anonymous_user.id}]
        }
        response = self.client.put(reverse('membersList', kwargs={'room_id': self.chat_room.room_id}),
                                   data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_group_chatroom(self):
        self.client.force_authenticate(self.user)
        anonymous = baker.make(CustomerUser)
        data = {
            'members': [{'id': anonymous.id}],
            'admins': [{'id': anonymous.id}],
            'delete_admins': [{'id': self.tmp_user.id}]
        }
        response = self.client.put(reverse('membersList', kwargs={'room_id': self.chat_room.room_id}),
                                   data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('member', response_json['data']['chat_room_members'])
        self.assertEqual(3, len(response_json['data']['chat_room_members']['member']))
        self.assertIn('admin', response_json['data']['chat_room_members'])
        self.assertEqual(2, len(response_json['data']['chat_room_members']['admin']))


class TestSameChatRoomsMessage(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.tmp_user = baker.make(CustomerUser)
        for _ in range(10):
            chat_room = baker.make(ChatRoom, type='group')
            chat_room.member.set([self.tmp_user, self.user])
        direct_chat = baker.make(ChatRoom, type='direct')
        direct_chat.member.set([self.tmp_user, self.user])

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.get(reverse('same_chat_rooms_list',
                                           kwargs={'user_id': self.tmp_user.id}),
                                   data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_updates_anonymous_user(self):
        anonymous_user = baker.make(CustomerUser)
        self.client.force_authenticate(anonymous_user)
        response = self.client.get(reverse('same_chat_rooms_list',
                                           kwargs={'user_id': self.tmp_user.id}),
                                   data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, response_json['data']['chat_rooms']['count'])

    def test_create_group_chatroom(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('same_chat_rooms_list',
                                           kwargs={'user_id': self.tmp_user.id}),
                                   data={}, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertEqual(11, response_json['data']['chat_rooms']['count'])


class TestLeaveChatRoom(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.tmp_user = baker.make(CustomerUser)
        self.chat_room = baker.make(ChatRoom, type='group')
        self.chat_room.member.set([self.tmp_user, self.user])
        baker.make(ChatMessage, chat=self.chat_room, user=self.user, _quantity=10)
        baker.make(ChatMessage, chat=self.chat_room, user=self.tmp_user, _quantity=10)

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.delete(reverse('chat_room_leave',
                                              kwargs={'room_id': self.chat_room.room_id}),
                                      data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_left_group_successfully(self):
        data = {
            'delete_all_message_for_me': True,
            'delete_my_messages_for_all': True
        }
        self.client.force_authenticate(self.user)
        response = self.client.delete(reverse('chat_room_leave',
                                              kwargs={'room_id': self.chat_room.room_id}),
                                      data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        messages = ChatMessage.objects.filter(chat=self.chat_room, deleted_by=self.user)
        self.assertEqual(10, messages.count())
        messages = ChatMessage.objects.filter(chat=self.chat_room)
        self.assertEqual(10, messages.count())


class TestSeenMessages(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.tmp_user = baker.make(CustomerUser)
        self.chat_room = baker.make(ChatRoom, type='group')
        self.chat_room.member.set([self.tmp_user, self.user])

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.post(reverse('seen_message',
                                            kwargs={'room_id': self.chat_room.room_id}),
                                    data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_invalid_room_id(self):
        tmp_chatroom = baker.make(ChatRoom, type='direct')
        messages = baker.make(ChatMessage, chat=self.chat_room, user=self.tmp_user)
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('seen_message',
                                            kwargs={'room_id': tmp_chatroom.room_id}),
                                    data={'messages_id': [messages.id]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_seen_messages(self):
        self.client.force_authenticate(self.user)
        messages = baker.make(ChatMessage, chat=self.chat_room, user=self.tmp_user, _quantity=10)

        response = self.client.post(reverse('seen_message',
                                            kwargs={'room_id': self.chat_room.room_id}),
                                    data={'messages_id': [msg.id for msg in messages]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual('ok', response_json['status'])
        self.assertEqual(10, UserSeenMessage.objects.count())

    def test_not_seen_messages_owner(self):
        messages = baker.make(ChatMessage, chat=self.chat_room, user=self.user, _quantity=10)
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('seen_message',
                                            kwargs={'room_id': self.chat_room.room_id}),
                                    data={'messages_id': [msg.id for msg in messages]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual('ok', response_json['status'])
        self.assertEqual(0, UserSeenMessage.objects.count())


class TestListMessages(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.tmp_user = baker.make(CustomerUser, first_name='John', last_name='Doe')
        self.chat_room = baker.make(ChatRoom, type='group')
        self.chat_room.member.set([self.tmp_user, self.user])

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.get(reverse('message_list',
                                           kwargs={'room_id': self.chat_room.room_id}),
                                   data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_invalid_room_id(self):
        tmp_chatroom = baker.make(ChatRoom, type='direct')
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('message_list',
                                           kwargs={'room_id': tmp_chatroom.room_id}),
                                   data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_messages(self):
        self.client.force_authenticate(self.user)
        messages = baker.make(ChatMessage, chat=self.chat_room, user=self.user, _quantity=10)
        response = self.client.get(reverse('message_list',
                                           kwargs={'room_id': self.chat_room.room_id}),
                                   data={}, format='json')
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ok', response_json['status'])
        self.assertIn('chat_messages', response_json['data'])
        self.assertIn('count', response_json['data']['chat_messages'])
        self.assertIn('next', response_json['data']['chat_messages'])
        self.assertIn('previous', response_json['data']['chat_messages'])
        self.assertIn('results', response_json['data']['chat_messages'])
        self.assertIn('id', response_json['data']['chat_messages']['results'][0])
        self.assertIn('user_name', response_json['data']['chat_messages']['results'][0])
        self.assertIn('user_avatar', response_json['data']['chat_messages']['results'][0])
        self.assertIn('is_seen', response_json['data']['chat_messages']['results'][0])
        self.assertIn('created_at', response_json['data']['chat_messages']['results'][0])
        self.assertIn('updated_at', response_json['data']['chat_messages']['results'][0])
        self.assertEqual(10, response_json['data']['chat_messages']['count'])

    def test_is_seen_field(self):
        message = baker.make(ChatMessage, chat=self.chat_room, user=self.tmp_user)
        UserSeenMessage.objects.create(user_id=self.user.id, message=message)
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('message_list',
                                           kwargs={'room_id': self.chat_room.room_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual('ok', response_json['status'])
        self.assertIn('is_seen', response_json['data']['chat_messages']['results'][0])
        self.assertEqual(True, response_json['data']['chat_messages']['results'][0]['is_seen'])


class TestListSeenMessage(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = _create_user()
        self.tmp_users = baker.make(CustomerUser,  _quantity=12)
        self.chat_room = baker.make(ChatRoom, type='group')
        self.chat_room.member.set([tmp_user for tmp_user in self.tmp_users])
        self.chat_room.member.add(self.user)
        self.message = baker.make(ChatMessage, user=self.user, chat=self.chat_room)

    def test_api_exists_forbidden_anonymous(self):
        response = self.client.get(reverse('seen_message_list_users',
                                           kwargs={'room_id': self.chat_room.room_id,
                                                   'message_id':self.message.id}),
                                   data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_invalid_room_id(self):
        tmp_chatroom = baker.make(ChatRoom, type='direct')
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('seen_message_list_users',
                                           kwargs={'room_id': tmp_chatroom.room_id,
                                                   'message_id':self.message.id}),
                                   data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_not_creator_seen_messages(self):
        self.client.force_authenticate(self.tmp_users[0])
        response = self.client.get(reverse('seen_message_list_users',
                                           kwargs={'room_id': self.chat_room.room_id,
                                                   'message_id': self.message.id}),
                                   data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_seen_messages(self):
        self.client.force_authenticate(self.user)
        for tmp_user in self.tmp_users:
            UserSeenMessage.objects.create(message=self.message, user=tmp_user)
        response = self.client.get(reverse('seen_message_list_users',
                                           kwargs={'room_id': self.chat_room.room_id,
                                                   'message_id': self.message.id}),
                                   data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual('ok', response_json['status'])
        self.assertEqual(12, response_json['data']['user_seen_messages']['count'])
        self.assertIn('user_name', response_json['data']['user_seen_messages']['results'][0])
        self.assertIn('user_avatar', response_json['data']['user_seen_messages']['results'][0])
        self.assertIn('created_at', response_json['data']['user_seen_messages']['results'][0])